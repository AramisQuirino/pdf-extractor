from fastapi import FastAPI, UploadFile, File
import pdfplumber

app = FastAPI()

def extract_with_pdfplumber(pdf_bytes: bytes) -> dict:
    text_pages = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            # extract_text tolerates many encodings better than basic tools
            t = page.extract_text() or ""
            text_pages.append(t)
    full_text = "\n\n---PAGE---\n\n".join(text_pages).strip()
    return {
        "pages": len(text_pages),
        "text": full_text,
        "chars": len(full_text),
        "chars_per_page": [len(t) for t in text_pages],
    }

import io

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    result = extract_with_pdfplumber(pdf_bytes)
    # Señal: si chars muy bajo, probablemente es un PDF raro/vectores/imagen
    result["needs_ocr"] = result["chars"] < 50
    return result
