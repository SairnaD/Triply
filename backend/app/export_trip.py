from io import BytesIO
from openpyxl import Workbook
from datetime import datetime
import json

def create_trip_excel(documents, trip_name: str):
    wb = Workbook()
    ws = wb.active
    ws.title = "Expenses"

    ws.append(["Datums", "Apraksts", "Kategorija", "Summa"])

    total = 0
    categories_sum = {}

    for doc in documents:
        try:
            data = json.loads(doc.extracted_data)
        except:
            data = {}

        datums = data.get("date", "")
        if datums:
            try:
                datums = datetime.fromisoformat(datums).strftime("%d.%m.%Y")
            except:
                pass

        try:
            amount = float(str(data.get("amount", 0)).replace("$", "").replace("€", ""))
        except:
            amount = 0
        total += amount

        cat = data.get("category", "Other")
        categories_sum[cat] = categories_sum.get(cat, 0) + amount

        apraksts = data.get("description", doc.filename)

        ws.append([datums, apraksts, cat, amount])

    summary_ws = wb.create_sheet(title="Summary")
    summary_ws.append(["Kategorija", "Summa"])
    for cat, amt in categories_sum.items():
        summary_ws.append([cat, amt])
    summary_ws.append(["Total", total])

    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)
    return stream, f"{trip_name.replace(' ', '_')}_report.xlsx"