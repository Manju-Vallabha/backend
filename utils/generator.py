import os
import uuid
from datetime import datetime
from lxml import etree
from firebase_admin import storage, firestore
from pydantic import BaseModel
from PIL import ImageFont


class DetailsPayload(BaseModel):
    # Define fields common for both certificate and badge
    name: str
    email: str


async def generateCertificate(DetailsPayload):

    print("Generating certificate...")
    name = DetailsPayload.name
    email = DetailsPayload.email
    with open(f"assets/templates/Cerificate_template.svg", "r", encoding="utf-8") as f:
        svg_content = f.read()

    # Parse and modify SVG
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.fromstring(svg_content.encode(), parser)

    # ====== DYNAMIC FONT SIZE CALCULATION ======

    # Configuration
    MAX_TEXT_WIDTH = 800  # in pixels, adjust based on your template
    BASE_FONT_SIZE = 40
    FONT_PATH = "assets/fonts/ProductSans-Medium.ttf"  # Update path if needed

    # Load font at base size
    font = ImageFont.truetype(FONT_PATH, size=BASE_FONT_SIZE)
    text_width = font.getbbox(name.title())[2]  # width in pixels

    # Scale font size down if needed
    if text_width > MAX_TEXT_WIDTH:
        scale = MAX_TEXT_WIDTH / text_width
        adjusted_font_size = int(BASE_FONT_SIZE * scale)
    else:
        adjusted_font_size = BASE_FONT_SIZE

    # Update SVG content
    text_element = root.xpath('//*[@id="name"]')[0]
    tspan = text_element.find("{http://www.w3.org/2000/svg}tspan")

    # Set the adjusted font size
    text_element.attrib["font-size"] = str(adjusted_font_size)
    if tspan is not None:
        tspan.text = name.title()
    else:
        text_element.text = name.title()

    # Write updated SVG to temp file
    id = uuid.uuid4()
    temp_file = f"tmp/{id}.svg"
    os.makedirs(os.path.dirname(temp_file), exist_ok=True)
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(etree.tostring(root, pretty_print=True, encoding="unicode"))

    # Upload to Firebase Storage
    bucket = storage.bucket()
    blob_path = f"certificates/{id}.svg"
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(temp_file, content_type="image/svg+xml")

    # Update Firestore
    db = firestore.client()
    doc_ref = db.collection("testentry").document(email)
    doc_ref.update(
        {
            "isCertificateGenerated": True,
            "generateddate": datetime.utcnow(),
            "certificateId": str(id),
        }
    )

    print(f"Certificate uploaded to {blob_path}")

    # Cleanup
    os.remove(temp_file)


async def generateBadge(DetailsPayload):
    print("Generating badge...")
    name = DetailsPayload.name
    email = DetailsPayload.email

    with open("assets/templates/badge.svg", "r", encoding="utf-8") as f:
        svg_content = f.read()

    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.fromstring(svg_content.encode(), parser)

    xpath_expr = '//*[@id="name"]'
    name_text_elements = root.xpath(xpath_expr)

    if not name_text_elements:
        print(f"No <text> element with id='name' found in SVG.")
        return

    name_text_el = name_text_elements[0]

    # Clear children and direct text
    for child in list(name_text_el):
        name_text_el.remove(child)
    name_text_el.text = None

    # Base font size and max chars threshold
    base_font_size = 96
    max_chars = 20

    # Calculate new font size based on length, min font size 30
    if len(name) > max_chars:
        new_font_size = max(30, int(base_font_size * max_chars / len(name)))
    else:
        new_font_size = base_font_size

    # Set font-size attribute on the <text> element
    name_text_el.attrib["font-size"] = str(new_font_size)
    # Adjust vertical position of the text block
    name_text_el.attrib["y"] = "30%"

    parts = name.split()
    n = len(parts)

    for i, part in enumerate(parts):
        if n == 2:
            # Two tspans with specific positions
            if i == 0:
                tspan = etree.SubElement(name_text_el, "tspan", x="70%", y="30%")
            else:
                tspan = etree.SubElement(name_text_el, "tspan", x="90%", dy="1.2em")
        elif n == 3:
            # Three tspans with specific positions
            if i == 0:
                tspan = etree.SubElement(name_text_el, "tspan", x="70%", y="30%")
            else:
                tspan = etree.SubElement(name_text_el, "tspan", x="70%", dy="1.2em")
        else:
            # Default: centered tspans stacked vertically
            tspan = etree.SubElement(
                name_text_el, "tspan", x="50%", dy="0" if i == 0 else "1.2em"
            )
        tspan.text = part.title()

    id = uuid.uuid4()

    # Save updated SVG locally
    temp_file_bade = f"tmp/{id}.svg"
    os.makedirs(os.path.dirname(temp_file_bade), exist_ok=True)
    with open(temp_file_bade, "w", encoding="utf-8") as f:
        f.write(etree.tostring(root, pretty_print=True, encoding="unicode"))

    print(f"Badge saved to {temp_file_bade}")

    # Upload to Firebase Storage
    bucket = storage.bucket()
    blob_path = f"badges/{id}.svg"
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(temp_file_bade, content_type="image/svg+xml")

    # Update Firestore
    db = firestore.client()
    doc_ref = db.collection("testentry").document(email)
    doc_ref.update(
        {
            "isCertificateGenerated": True,
            "generateddate": datetime.utcnow(),
            "badgeId": str(id),
        }
    )

    print(f"Badge uploaded to {blob_path}")

    # Cleanup
    os.remove(temp_file_bade)
