from fastapi import FastAPI, UploadFile, File, HTTPException
import csv
import os
from firebase_admin import firestore

UPLOAD_DIR = "attendee_data_temp"
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def upload_attendees(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a valid CSV file.")

    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        db = firestore.client()
        added = 0
        skipped = 0
        total = 0

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                total += 1
                name = row.get("name")
                email = row.get("email")

                if not name or not email:
                    skipped += 1
                    continue

                doc_ref = db.collection("attendee").document(email)
                if doc_ref.get().exists:
                    skipped += 1
                    continue

                doc_ref.set(
                    {
                        "name": name,
                        "email": email,
                        "role": "attendee",
                        "isCertificateGenerated": False,
                        "generateddate": None,
                        "certificateId": None,
                        "badgeId": None,
                    }
                )

                added += 1

        os.remove(file_path)

        return {
            "message": "CSV processed successfully.",
            "total_rows": total,
            "uploaded_to_firestore": added,
            "skipped_due_to_issues_or_duplicates": skipped,
            "file_deleted": True,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process CSV: {str(e)}")
