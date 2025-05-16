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
import httpx

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
# NOTE: For pipeline testing, we use 'distilgpt2' (a small model). To switch back to the large model, set the environment variable HF_MODEL_NAME to 'ACATECH/ncos' or your desired model name.
MODEL_NAME = os.getenv("HF_MODEL_NAME", "distilgpt2")  # Use distilgpt2 for testing; switch back to ACATECH/ncos after
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
# Use the provided Redis Cloud endpoint as the default for testing
REDIS_URL = os.getenv("REDIS_URL", "redis://:password@redis-19567.c300.eu-central-1-1.ec2.redns.redis-cloud.com:19567/0")  # Set your Redis Cloud URL in env
redis_client = redis.Redis.from_url(REDIS_URL)

# --- Job Queue Logic ---
JOB_QUEUE = "ncos_job_queue"
JOB_RESULT_PREFIX = "ncos_job_result:"

# --- Model Cache ---
model_cache = {"name": None, "pipeline": None}

# --- Supabase REST API Helper Functions ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def insert_inference_result(data: dict) -> bool:
    """
    Insert a row into the inference_results table using Supabase REST API.
    Returns True if successful, False otherwise.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("Supabase credentials not set. Skipping Supabase integration.")
        return False
    url = f"{SUPABASE_URL}/rest/v1/inference_results"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    try:
        response = httpx.post(url, json=data, headers=headers)
        if response.status_code == 201:
            logger.info(f"Stored job {data.get('job_id')} result in Supabase via REST API.")
            return True
        else:
            logger.error(f"Failed to store job {data.get('job_id')} in Supabase: {response.status_code} {response.text}")
            return False
    except Exception as e:
        logger.error(f"Exception during Supabase REST API call: {e}")
        return False

def select_inference_results(filters: dict = None) -> list:
    """
    Select rows from the inference_results table using Supabase REST API.
    filters: dict of query params (e.g., {"job_id": "eq.test123"})
    Returns a list of results or an empty list.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("Supabase credentials not set. Skipping Supabase integration.")
        return []
    url = f"{SUPABASE_URL}/rest/v1/inference_results"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    params = {"select": "*"}
    if filters:
        params.update(filters)
    try:
        response = httpx.get(url, headers=headers, params=params)
        if response.status_code == 200:
            logger.info(f"Selected results from Supabase via REST API.")
            return response.json()
        else:
            logger.error(f"Failed to select from Supabase: {response.status_code} {response.text}")
            return []
    except Exception as e:
        logger.error(f"Exception during Supabase REST API select: {e}")
        return []

def update_inference_result(job_id: str, update_data: dict) -> bool:
    """
    Update a row in the inference_results table using Supabase REST API.
    job_id: the job_id to match
    update_data: dict of fields to update
    Returns True if successful, False otherwise.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("Supabase credentials not set. Skipping Supabase integration.")
        return False
    url = f"{SUPABASE_URL}/rest/v1/inference_results"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    params = {"job_id": f"eq.{job_id}"}
    try:
        response = httpx.patch(url, json=update_data, headers=headers, params=params)
        if response.status_code in (200, 204):
            logger.info(f"Updated job {job_id} in Supabase via REST API.")
            return True
        else:
            logger.error(f"Failed to update job {job_id} in Supabase: {response.status_code} {response.text}")
            return False
    except Exception as e:
        logger.error(f"Exception during Supabase REST API update: {e}")
        return False

def delete_inference_result(job_id: str) -> bool:
    """
    Delete a row from the inference_results table using Supabase REST API.
    job_id: the job_id to match
    Returns True if successful, False otherwise.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("Supabase credentials not set. Skipping Supabase integration.")
        return False
    url = f"{SUPABASE_URL}/rest/v1/inference_results"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    params = {"job_id": f"eq.{job_id}"}
    try:
        response = httpx.delete(url, headers=headers, params=params)
        if response.status_code in (200, 204):
            logger.info(f"Deleted job {job_id} from Supabase via REST API.")
            return True
        else:
            logger.error(f"Failed to delete job {job_id} from Supabase: {response.status_code} {response.text}")
            return False
    except Exception as e:
        logger.error(f"Exception during Supabase REST API delete: {e}")
        return False

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
                # --- Store result in Supabase ---
                if SUPABASE_URL and SUPABASE_KEY:
                    data = {
                        "job_id": job_id,
                        "input_text": input_text,
                        "parameters": str(parameters),
                        "model_name": model_name,
                        "result": result_text
                    }
                    insert_inference_result(data)
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