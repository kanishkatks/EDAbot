import numpy as np
import os
import shutil
import logging
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from edabot.eda_multiagent_pipeline import run_eda



app = FastAPI()

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Directory setup for uploads
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_to_native_types(obj):
    """Convert NumPy types to native Python types (for JSON compatibility)."""
    if isinstance(obj, np.generic):
        return obj.item()  # Converts NumPy types to native Python types
    elif isinstance(obj, dict):
        return {key: convert_to_native_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native_types(item) for item in obj]
    else:
        return obj

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file and run EDA on it."""
    try:
        # Validate file type
        if not file.filename.endswith(('.csv', '.json')):
            return JSONResponse(status_code=400, content={"error": "Invalid file type. Only CSV and JSON are supported."})

        # Save the uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        if os.path.exists(file_path):
            base, ext = os.path.splitext(file.filename)
            file_path = os.path.join(UPLOAD_DIR, f"{base}_copy{ext}")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"File uploaded: {file.filename}")

        # Run EDA on the file
        result = run_eda(file_path)

        # Ensure that result is JSON-serializable
        result = convert_to_native_types(result)

        # Optionally delete the file after processing
        os.remove(file_path)

        # Return the result
        return JSONResponse(content=result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error_code": "EDA_PIPELINE_ERROR", "message": str(e), "stack_trace": traceback.format_exc()}
        )

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"status": "EDA API is running"}
