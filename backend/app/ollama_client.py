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

def map_category(cat: str) -> str:
    if not cat:
        return "Other"
    return CATEGORY_MAP.get(cat.lower(), "Other")

# Currency exchange
def convert_to_usd(amount: float, currency: str) -> float:
    currency = currency.upper()
    if currency == "USD":
        return amount
    try:
        url = f"https://api.exchangerate.host/convert?from={currency}&to=USD&amount={amount}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get("success"):
            return round(data["result"], 2)
        else:
            return amount
    except:
        return amount

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
def normalize_data(data: dict) -> dict:
    if not isinstance(data, dict):
        return {"raw_text": str(data)}

    amount = 0
    currency = "USD"
    if "amount" in data and data["amount"]:
        raw = str(data["amount"]).strip()
        raw = raw.replace(",", ".")
        if raw.startswith("$"):
            currency = "USD"
            raw = raw.replace("$", "")
        elif raw.startswith("€"):
            currency = "EUR"
            raw = raw.replace("€", "")
        elif raw.startswith("₽"):
            currency = "RUB"
            raw = raw.replace("₽", "")
        elif raw.startswith("£"):
            currency = "GBP"
            raw = raw.replace("£", "")
        try:
            amount = float(raw)
        except:
            amount = 0
    amount_usd = convert_to_usd(amount, currency)
    data["amount"] = round(amount_usd, 2)

    # Category
    cat = data.get("category", "")
    cat = cat.strip().lower()
    data["category"] = map_category(cat)

    # Date
    raw_date = data.get("date", "")
    if raw_date:
        parsed_date = dateparser.parse(raw_date, settings={'DATE_ORDER': 'DMY'})
        if parsed_date:
            data["date"] = parsed_date.strftime("%d/%m/%Y")
        else:
            data["date"] = None
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
- Detect category in any language and map it to one of: Food, Transport, Hotel, Other
- ALWAYS capitalize category
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

    # Retry and fallback
    MAX_RETRIES = 2
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=180)
            response.raise_for_status()
            data = response.json()
            text = data.get("response", "")
            parsed = clean_llava_response(text)
            return normalize_data(parsed)
        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                time.sleep(2)
                continue
            else:
                return {"error": "timeout while contacting Ollama"}
        except Exception as e:
            return {"error": str(e)}