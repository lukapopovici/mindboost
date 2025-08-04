from fastapi import FastAPI, UploadFile, File
from PyPDF2 import PdfReader
import io

app = FastAPI()

@app.post("/parse-pdf/")
def parse_pdf(file: UploadFile = File(...)):
    contents = file.file.read()
    reader = PdfReader(io.BytesIO(contents))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return {"text": text}
