# Product Requirements Document (PRD)
# Project: NCOS_S1 (Large Compliance LLM Pipeline)

## 1. Project Overview
Deploy a large compliance LLM (ACATECH/ncos, Llama-2-70B) on Hugging Face Spaces, with a Next.js frontend (Vercel), Supabase for test cases, and Redis for queueing. The backend is a FastAPI app running in a Docker container for full control (CUDA, dependencies, etc.).

---

## 2. Current State Analysis
- **Backend:**
  - FastAPI app in Hugging Face Space, Dockerized.
  - CUDA and torch set up for GPU inference.
  - Permissions and cache issues resolved.
  - Requirements are mostly correct and reproducible.
- **Frontend:**
  - Next.js app on Vercel (not tightly integrated yet).
- **Test/Queue:**
  - Supabase for test cases.
  - Redis for queueing (not fully integrated).
- **Issues:**
  - Dependency hell (CUDA, torch, flash-attn, numpy, etc.).
  - File permission and cache issues.
  - Model/tokenizer loading errors (corrupt/incompatible files).
  - Manual syncing of requirements and Dockerfile.
  - No robust, end-to-end pipeline from test case → queue → model → result → storage.
  - No clear API contract between frontend, backend, and test/queue system.
  - No health checks, monitoring, or error reporting.
  - No automated deployment or CI/CD for the Space.
  - Monolithic codebase, hard to debug.

---

## 3. Goals
- Modular, robust, and reproducible pipeline for LLM compliance testing.
- Clean separation of backend, frontend, and queue/storage.
- Automated, reliable deployment and monitoring.
- Clear API contract and documentation.

---

## 4. Recommended Architecture
### A. Modular Structure
- **Backend (Hugging Face Space):**
  - FastAPI app, Dockerized, REST API for inference.
  - Handles model loading, inference, health checks.
  - Connects to Redis for job queueing.
  - Optionally connects to Supabase for test/result storage.
- **Frontend (Vercel/Next.js):**
  - Calls backend API for inference.
  - Displays results, test case status, health info.
- **Queue/Storage:**
  - Redis for job queueing (decouples frontend/backend).
  - Supabase for storing test cases/results.

### B. Key Features
- Robust error handling and logging in backend.
- Health check endpoints (`/healthz`, `/readyz`).
- Clear API contract (OpenAPI/Swagger for FastAPI).
- Automated Docker build and deployment (version pinning).
- CI/CD pipeline for backend and frontend.
- Documentation for setup, usage, troubleshooting.

---

## 5. Action Plan
### Step 1: Design the API Contract
- Define endpoints for:
  - `/infer` (POST): Accepts input, returns model output.
  - `/healthz` (GET): Returns service health.
  - `/queue` (POST/GET): For job submission/status (if using Redis).
- Use FastAPI's OpenAPI docs for clarity.

### Step 2: Clean Backend Implementation
- Start a new repo or clean branch.
- Write a minimal FastAPI app:
  - Loads model/tokenizer (with robust error handling).
  - Exposes `/infer` and `/healthz`.
  - Logs errors and requests.
- Add Redis integration for queueing (optional, but recommended for scale).
- Add Supabase integration for test/result storage (optional, can be added after core works).

### Step 3: Dockerize the Backend
- Use a clean, minimal Dockerfile:
  - Start from `nvidia/cuda:12.1.0-devel-ubuntu22.04`.
  - Install Python, torch, dependencies in correct order.
  - Set up cache and permissions.
  - Pin all versions in `requirements.txt`.
  - Add a health check in Dockerfile (`HEALTHCHECK`).

### Step 4: Model/Tokenizer Management
- Ensure model/tokenizer files are valid and compatible.
- Test loading locally before pushing to Hugging Face.
- Document the process for updating model files.

### Step 5: Frontend Integration
- Update Next.js frontend to call the new backend API.
- Show job status, results, and health info.
- Add error handling and user feedback.

### Step 6: Queue and Storage Integration
- Set up Redis for job queueing.
- Set up Supabase for test case/result storage.
- Ensure backend can pull jobs from Redis, process, and store results in Supabase.

### Step 7: Monitoring and Health
- Add logging and error reporting (e.g., to stdout, or a logging service).
- Implement `/healthz` and `/readyz` endpoints.
- Optionally, add Prometheus/Grafana metrics.

### Step 8: CI/CD and Documentation
- Add GitHub Actions or similar for automated build/test/deploy.
- Write clear README and API docs.

---

## 6. Success Criteria
- End-to-end pipeline works: test case → queue → model → result → storage.
- Robust error handling and health checks in place.
- Automated, reproducible builds and deployments.
- Clear, up-to-date documentation for all components. 