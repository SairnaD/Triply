import requests, base64, json, os, re, time
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import dateparser
from datetime import datetime

OLLAMA_URL = os.getenv("OLLAMA_API_URL", "http://ollama:11434/api/generate")

# Category
CATEGORY_MAP = {
    "еда": "Food", "nourriture": "Food", "food": "Food",
    "транспорт": "Transport", "transport": "Transport",
    "отель": "Hotel", "hôtel": "Hotel", "hotel": "Hotel",
    "прочее": "Other", "autre": "Other", "other": "Other"
}

def detect_currency(raw: str, ocr_text: str = "") -> str:
    text = (raw + " " + ocr_text).upper()

    if "$" in text or "USD" in text:
        return "USD"
    if "€" in text or "EUR" in text:
        return "EUR"
    if "£" in text or "GBP" in text:
        return "GBP"
    if "₽" in text or "RUB" in text:
        return "RUB"

    return "EUR"


def extract_amount(raw: str) -> float:
    raw = raw.replace(",", ".")
    raw = re.sub(r"[^0-9.]", "", raw)
    try:
        return float(raw) if raw else 0.0
    except:
        return 0.0


def map_category(cat: str) -> str:
    if not cat:
        return "Other"
    return CATEGORY_MAP.get(cat.lower(), "Other")


# Currency exchange
def convert_to_eur(amount: float, currency: str) -> float:
    currency = currency.upper()

    if amount is None or amount == 0:
        return 0.0

    if currency == "EUR":
        return round(amount, 2)

    try:
        url = f"https://api.frankfurter.dev/v2/rates?base={currency}&quotes=EUR"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()

        data = resp.json()

        if isinstance(data, list) and len(data) > 0:
            rate = data[0].get("rate")

            if rate is None:
                raise ValueError("Missing rate in API response")

            return round(amount * float(rate), 2)

        raise ValueError("Invalid API response format")

    except Exception as e:
        print(f"Currency conversion error: {e}")
        return None


# PDF → IMAGE
def pdf_to_image(pdf_path: str) -> str:
    pages = convert_from_path(pdf_path)
    page = pages[0]
    scale_factor = 0.5
    page = page.resize((int(page.width * scale_factor), int(page.height * scale_factor)))
    output_path = Path("uploads") / f"{Path(pdf_path).stem}_page0.png"
    page.save(output_path, "PNG")
    return str(output_path)


# OCR
def extract_text_ocr(image_path: str) -> str:
    try:
        img = Image.open(image_path)
        return pytesseract.image_to_string(img, lang="eng+rus+fra+deu+spa")
    except Exception as e:
        return f"OCR_ERROR: {str(e)}"


# Cleaning the LLaVA respond
def clean_llava_response(text: str) -> dict:
    pattern = r"```json\s*(.*?)\s*```"
    match = re.search(pattern, text, flags=re.DOTALL)
    if match:
        cleaned = match.group(1).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {"raw_text": cleaned}
    else:
        return {"raw_text": text}


# Normalize
def normalize_data(data: dict, ocr_text: str = "") -> dict:
    if not isinstance(data, dict):
        return {"raw_text": str(data)}

    raw = str(data.get("amount", "")).strip()

    currency = detect_currency(raw, ocr_text)
    amount = extract_amount(raw)

    amount_eur = convert_to_eur(amount, currency)

    data["amount"] = round(amount_eur, 2) if amount_eur is not None else None

    # Category
    cat = data.get("category", "")
    data["category"] = map_category(cat.strip().lower())

    # Date
    raw_date = data.get("date", "")
    if raw_date:
        parsed_date = dateparser.parse(raw_date, settings={'DATE_ORDER': 'DMY'})
        data["date"] = parsed_date.strftime("%d/%m/%Y") if parsed_date else None
    else:
        data["date"] = None

    return data


# Main analyze
def analyze_document(file_path: str) -> dict:
    # 1. PDF → IMAGE
    if file_path.lower().endswith(".pdf"):
        file_path = pdf_to_image(file_path)

    # 2. OCR
    ocr_text = extract_text_ocr(file_path)

    # 3. IMAGE → base64
    with open(file_path, "rb") as f:
        img_bytes = f.read()
    img_b64 = base64.b64encode(img_bytes).decode()

    # 4. Prompt
    prompt = f"""
You are a strict receipt parser. The OCR text may be in any language.

Rules:
- Extract ONLY the FINAL TOTAL amount (number) with currency
- Extract date of purchase
- ALWAYS output date in format DD/MM/YYYY
- Detect category and map it to: Food, Transport, Hotel, Other
Return ONLY JSON: {{ "amount": "...", "date": "...", "category": "..." }}

OCR TEXT:
{ocr_text}
"""

    payload = {
        "model": "llava",
        "prompt": prompt,
        "images": [img_b64],
        "stream": False
    }

    MAX_RETRIES = 2
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=180)
            response.raise_for_status()

            data = response.json()
            text = data.get("response", "")

            parsed = clean_llava_response(text)

            return normalize_data(parsed, ocr_text)

        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                time.sleep(2)
                continue
            return {"error": "timeout while contacting Ollama"}

        except Exception as e:
            return {"error": str(e)}