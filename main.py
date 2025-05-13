from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Any
import os
import logging
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from huggingface_hub import login
import threading
import time
import uuid
import redis

app = FastAPI(
    title="NCOS Compliance LLM API",
    description="API contract for inference, health checks, and job queueing.",
    version="1.0.0"
)

# --- Pydantic models for request/response ---

class InferRequest(BaseModel):
    input_text: str  # The text to run inference on
    parameters: Optional[dict] = None  # Optional model parameters (e.g., temperature, max_tokens)

class InferResponse(BaseModel):
    result: str  # The model's output
    status: str  # 'success' or 'error'
    error: Optional[str] = None  # Error message if status is 'error'

class QueueRequest(BaseModel):
    input_text: str  # The text to enqueue for inference
    parameters: Optional[dict] = None  # Optional model parameters

class QueueResponse(BaseModel):
    job_id: str  # Unique job identifier
    status: str  # 'queued', 'pending', 'done', or 'error'
    result: Optional[str] = None  # Model output if available
    error: Optional[str] = None  # Error message if status is 'error'

# --- Model Loading (Cloud-Ready) ---

# Read model name and token from environment variables for security
MODEL_NAME = os.getenv("HF_MODEL_NAME", "gpt2")  # Use gpt2 for testing; switch back to ACATECH/ncos after
HF_TOKEN = os.getenv("HF_TOKEN")  # Should be set in Hugging Face Space secrets

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ncos-backend")

# Login to Hugging Face Hub if token is provided
if HF_TOKEN:
    try:
        login(token=HF_TOKEN)
        logger.info("Logged in to Hugging Face Hub.")
    except Exception as e:
        logger.error(f"Failed to login to Hugging Face Hub: {e}")

# Load model and tokenizer at startup
try:
    logger.info(f"Loading model: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    # Use pipeline for simple inference
    ncos_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer, device=0)
    logger.info("Model and tokenizer loaded successfully.")
except Exception as e:
    logger.error(f"Model loading failed: {e}")
    ncos_pipeline = None

# --- Redis Connection ---
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")  # Set your cloud Redis URL in env
redis_client = redis.Redis.from_url(REDIS_URL)

# --- Job Queue Logic ---
JOB_QUEUE = "ncos_job_queue"
JOB_RESULT_PREFIX = "ncos_job_result:"

# --- Model Cache ---
model_cache = {"name": None, "pipeline": None}

# --- Background Worker Thread ---
def job_worker():
    while True:
        job_data = redis_client.lpop(JOB_QUEUE)
        if job_data:
            job = eval(job_data)  # In production, use json.loads for safety
            job_id = job["job_id"]
            input_text = job["input_text"]
            parameters = job.get("parameters", {})
            model_name = job.get("model_name", "gpt2")
            try:
                # Load model if needed
                if model_cache["name"] != model_name:
                    logger.info(f"Loading model for job: {model_name}")
                    tokenizer = AutoTokenizer.from_pretrained(model_name)
                    model = AutoModelForCausalLM.from_pretrained(model_name)
                    model_cache["pipeline"] = pipeline("text-generation", model=model, tokenizer=tokenizer, device=0)
                    model_cache["name"] = model_name
                pipe = model_cache["pipeline"]
                params = parameters or {}
                params.setdefault("max_new_tokens", 128)
                params.setdefault("temperature", 0.7)
                output = pipe(input_text, **params)
                result_text = output[0]["generated_text"] if output and "generated_text" in output[0] else str(output)
                redis_client.set(JOB_RESULT_PREFIX + job_id, result_text)
            except Exception as e:
                logger.error(f"Job {job_id} failed: {e}")
                redis_client.set(JOB_RESULT_PREFIX + job_id, f"ERROR: {e}")
        else:
            time.sleep(1)

# Start background worker thread
threading.Thread(target=job_worker, daemon=True).start()

# --- Endpoints ---

@app.post("/infer", response_model=InferResponse, summary="Run model inference", description="Run LLM inference on the input text and return the result.")
def infer(request: InferRequest):
    """
    Run model inference on the input text.
    - **input_text**: The text to run inference on.
    - **parameters**: Optional model parameters (e.g., temperature, max_tokens).
    Returns the model's output or an error message.
    """
    if ncos_pipeline is None:
        # Model failed to load
        logger.error("Inference requested but model is not loaded.")
        return InferResponse(result="", status="error", error="Model not loaded.")
    try:
        # Prepare parameters for the pipeline
        params = request.parameters or {}
        # Set sensible defaults if not provided
        params.setdefault("max_new_tokens", 128)
        params.setdefault("temperature", 0.7)
        # Run inference
        logger.info(f"Running inference for input: {request.input_text}")
        output = ncos_pipeline(request.input_text, **params)
        # output is a list of dicts with 'generated_text'
        result_text = output[0]["generated_text"] if output and "generated_text" in output[0] else str(output)
        return InferResponse(result=result_text, status="success")
    except Exception as e:
        logger.error(f"Error during inference: {e}")
        return InferResponse(result="", status="error", error=str(e))

@app.get("/healthz", summary="Health check", description="Check if the backend service is healthy.")
def healthz():
    """
    Health check endpoint.
    Returns 200 OK if the service is healthy.
    """
    return {"status": "ok"}

@app.post("/queue", response_model=QueueResponse, summary="Submit job to queue", description="Submit a job to the Redis queue for asynchronous processing.")
def submit_job(request: QueueRequest):
    """
    Submit a job to the queue (e.g., Redis).
    - **input_text**: The text to enqueue for inference.
    - **parameters**: Optional model parameters.
    Returns a job ID and status.
    """
    job_id = str(uuid.uuid4())
    job = {
        "job_id": job_id,
        "input_text": request.input_text,
        "parameters": request.parameters,
        "model_name": os.getenv("HF_MODEL_NAME", "gpt2")  # Allow override per job in future
    }
    redis_client.rpush(JOB_QUEUE, str(job))
    return QueueResponse(job_id=job_id, status="queued")

@app.get("/queue", response_model=QueueResponse, summary="Get job status/result", description="Get the status or result of a queued job by job_id.")
def get_job_status(job_id: str):
    """
    Get the status/result of a queued job.
    - **job_id**: The job identifier.
    Returns the job status and result if available.
    """
    result = redis_client.get(JOB_RESULT_PREFIX + job_id)
    if result:
        result_str = result.decode("utf-8")
        if result_str.startswith("ERROR:"):
            return QueueResponse(job_id=job_id, status="error", error=result_str)
        return QueueResponse(job_id=job_id, status="done", result=result_str)
    else:
        return QueueResponse(job_id=job_id, status="pending")

@app.get("/")
def root():
    return {
        "message": "Welcome to the NCOS_S3 FastAPI backend!",
        "docs": "/docs",
        "health": "/healthz"
    }

# Add middleware to log every incoming request path and method
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    return response

# --- End of API contract skeleton ---

# FastAPI will auto-generate OpenAPI docs at /docs and /openapi.json
#
# To test endpoints:
# - Use curl, httpie, or Postman to send requests to /infer, /healthz, /queue
# - Visit /docs for interactive API documentation