from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from utils.firebase_init import initialize_firebase
from firebase_admin import firestore
from utils.generator import generateCertificate, generateBadge
from utils.file_access import get_files
from utils.upload_attendees_csv import upload_attendees
from utils.models import DetailsPayload, fileAccessPayload, loginPayload
from dotenv import load_dotenv

import os

app = FastAPI()

load_dotenv()
frontend_urls = os.getenv("FRONTEND_URL", "").split(",")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_urls,  # Allow all origins for simplicity; adjust as needed
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


@app.on_event("startup")
async def startup_event():
    initialize_firebase()
    print("Firebase initialized successfully.")


@app.get("/")
async def root():
    return {"message": "Welcome to the Certificate and Badge Generator API!"}


@app.post("/upload_attendees")
async def upload_attendees_manual(file: UploadFile = File(...)):
    try:
        return await upload_attendees(file)
    except Exception as e:
        print(f"Error processing CSV file: {e}")
        raise HTTPException(status_code=500, detail="Failed to process CSV file.")


@app.post("/login")
async def login(payload: loginPayload):
    db = firestore.client()
    user_doc = db.collection("testentry").document(payload.email).get()
    if not user_doc.exists:
        raise HTTPException(
            status_code=404,
            detail="User not found. Please register or generate a certificate and badge first.",
        )
    user_data = user_doc.to_dict()
    return {
        "message": "success",
        "document": {
            "name": user_data.get("name"),
            "role": user_data.get("role"),
            "isCertificateGenerated": user_data.get("isCertificateGenerated", False),
        },
    }


@app.post("/generate")
async def generate(payload: DetailsPayload):
    try:
        await generateCertificate(payload)
    except Exception as e:
        print(f"Error uploading certificate: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload certificate.")

    try:
        await generateBadge(payload)
    except Exception as e:
        print(f"Error uploading badge: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload badge.")

    return {"success": "Certificate and badge uploaded successfully."}


@app.post("/get_file_url")
async def get_file_url(payload: fileAccessPayload):
    try:
        return await get_files(payload)
    except Exception as e:
        print(f"Error generating file URLs: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate file URLs.")
