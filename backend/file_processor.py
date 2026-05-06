import pandas as pd
import pdfplumber
from docx import Document
from PIL import Image
import pytesseract

def extract_text(file_path: str, filename: str) -> str:
    ext = filename.lower().split(".")[-1]

    if ext == "txt":
        return _extract_txt(file_path)
    elif ext == "pdf":
        return _extract_pdf(file_path)
    elif ext in ("docx", "doc"):
        return _extract_docx(file_path)
    elif ext == "csv":
        return _extract_csv(file_path)
    elif ext in ("xlsx", "xls"):
        return _extract_xlsx(file_path)
    elif ext in ("png", "jpg", "jpeg"):
        return _extract_image(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def _extract_txt(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def _extract_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "") + "\n"
    return text

def _extract_docx(path):
    doc = Document(path)
    return "\n".join([para.text for para in doc.paragraphs])

def _extract_csv(path):
    try:
        # Try UTF-8 first, then fall back to other encodings
        try:
            df = pd.read_csv(path, encoding="utf-8")
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(path, encoding="utf-16")
            except UnicodeDecodeError:
                df = pd.read_csv(path, encoding="latin-1")

        print(f"CSV shape: {df.shape}")
        if df.empty:
            return ""
        return df.to_string(index=False)

    except pd.errors.EmptyDataError:
        print("CSV is empty!")
        return ""
    except Exception as e:
        print(f"CSV error: {e}")
        return ""

def _extract_xlsx(path):
    try:
        df = pd.read_excel(path)
        if df.empty:
            return ""
        return df.to_string(index=False)
    except Exception as e:
        print(f"XLSX error: {e}")
        return ""

def _extract_image(path):
    try:
        img = Image.open(path)
        text = pytesseract.image_to_string(img)
        print(f"Image text extracted: {len(text)} chars")
        return text
    except Exception as e:
        print(f"Image error: {e}")
        return ""