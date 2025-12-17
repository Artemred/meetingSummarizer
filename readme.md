# AI Audio Summarizer

This project is an automated service for transcribing audio files and generating summaries using a fine-tuned Large Language Model (LLM).

**Tech Stack:** FastAPI, Celery, Redis, Whisper, Ollama, Docker.

---

## How to Run

To start the project, you first need to prepare the ML model, and then launch the services using Docker.

### Step 1: Prepare the Model (Train & Export)

Before running the containers, you must create a dataset and generate the GGUF model file.

1.  **Generate Dataset:**
    Navigate to the `ai/summarizer_train` directory.
    Create a `.env` file inside this folder and add your **Gemini API Key** (required for data generation).
    Run the generation script:
    ```bash
    python gen.py
    ```

2.  **Train/Fine-tune:**
    Open and run the `train_colab.ipynb` notebook (recommended to run on Google Colab or a GPU-enabled machine).
    Ensure it uses the dataset generated in the previous step.

3.  **Export to GGUF:**
    Follow the steps in the notebook to merge the adapters and convert the model to `.gguf` format.
    You should end up with a file named `qwen2.5-7b-finetuned.gguf`.

4.  **Place the Model:**
    Move the generated `.gguf` file into the deployment directory:
    ```bash
    mv qwen2.5-7b-finetuned.gguf ./ai/summarizer_deploy/
    ```

5.  **Verify Configuration:**
    Ensure `ai/summarizer_deploy/Modelfile7` references the correct model filename:
    ```dockerfile
    FROM ./qwen2.5-7b-finetuned.gguf
    # ...
    ```

### Step 2: Environment Setup

Create the main environment file from the example:

```bash
cp .example.env .env
```
*Make sure to review the variables in `.env` (Redis URL, upload paths, etc.).*

### Step 3: Run with Docker

Build and start the services:

```bash
docker-compose up --build -d
```

This will spin up:
* **Web API** (FastAPI)
* **Worker** (Celery + Whisper)
* **Redis** (Message Broker)
* **Ollama** (LLM Inference Service)

---

## API Usage

### 1. Upload Audio (Create Session)

Upload an audio file to start the processing pipeline.

**Endpoint:** `POST /create-session/`

```bash
curl -X POST "http://localhost:8000/create-session/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/audio.mp3"
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 2. Get Result

Check the status or retrieve the summary using the Session ID (`uid`).

**Endpoint:** `GET /session/{uid}`

```bash
curl -X GET "http://localhost:8000/session/550e8400-e29b-41d4-a716-446655440000"
```

**Possible Statuses:**
* `QUEUED`: Task is waiting in Redis.
* `STARTED`: Transcription or summarization is in progress.
* `SUCCESS`: Processing complete.
* `FAILURE`: An error occurred.

**Example Response:**
```json
{
  "transcription_status": "SUCCESS",
  "summary_status": "SUCCESS",
  "summary": "This audio discusses the deployment strategies for ML models..."
}
```

---

## Project Structure

* `ai/` - ML resources (Dataset generation, Training notebooks, Deployment configs).
* `tests/` - Test files.
* `main.py` - FastAPI entry point.
* `tasks.py` - Celery tasks (Whisper processing & Ollama requests).
* `whisper.py` - Whisper ASR wrapper.
* `docker-compose.yaml` - Container orchestration.