from firebase_admin import storage, firestore
from datetime import timedelta
from utils.models import fileAccessPayload
from fastapi.responses import JSONResponse


def generate_signed_url(blob_path):

    bucket = storage.bucket()
    blob = bucket.blob(blob_path)
    return blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=10),
        method="GET",
    )


async def get_files(fileAccessPayload):

    role = fileAccessPayload.role
    email = fileAccessPayload.email

    db = firestore.client()
    user_doc = db.collection("testentry").document(email).get()
    if not user_doc.exists:
        return JSONResponse(
            status_code=404,
            content={
                "error": "User not found. Please generate the certificate and badge first."
            },
        )
    user_data = user_doc.to_dict()

    if not role or not email:
        return JSONResponse(
            status_code=400, content={"error": "Role and email are required."}
        )

    urls = {}

    if role == "attendee":
        # Return both certificate and badge
        certi_id = user_data.get("certificateId")
        badge_id = user_data.get("badgeId")
        cert_path = f"certificates/{certi_id}.svg"
        badge_path = f"badges/{badge_id}.svg"
        urls["certificate"] = generate_signed_url(cert_path)
        urls["badge"] = generate_signed_url(badge_path)

    elif role == "speaker":
        # Return only badge
        badge_id = user_data.get("badgeId")
        badge_path = f"badges/{badge_id}.svg"
        urls["badge"] = generate_signed_url(badge_path)

    elif role == "organizer":
        # Return only badge
        badge_id = user_data.get("badgeId")
        badge_path = f"badges/{badge_id}.svg"
        urls["badge"] = generate_signed_url(badge_path)

    elif role == "voulnteer":
        # Return only badge
        badge_id = user_data.get("badgeId")
        badge_path = f"badges/{badge_id}.svg"
        urls["badge"] = generate_signed_url(badge_path)

    else:
        return JSONResponse(
            status_code=400,
            content={"error": "Falied to generate file URLs. Invalid role provided."},
        )

    print("Urls generated successfully:")
    return JSONResponse(
        status_code=200,
        content={
            "message": "File URLs generated successfully.",
            "urls": urls,
        },
    )
