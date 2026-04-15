# Triply

Finanšu dokumentu apstrādes platforma

<img width="3240" height="1485" alt="logo" src="https://github.com/user-attachments/assets/9383866b-455e-4616-bf59-98a353e6cf21" />

![Ollama](https://img.shields.io/badge/ollama-%23000000.svg?style=for-the-badge&logo=ollama&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Ant-Design](https://img.shields.io/badge/-AntDesign-%230170FE?style=for-the-badge&logo=ant-design&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-%23D71F00.svg?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

---
## 📌 Projekta apraksts

Šī platforma ir izstrādāta, lai automatizētu finanšu dokumentu (čeku) apstrādi. Lietotājs var augšupielādēt čekus attēlu vai PDF formātā, pēc kā sistēma automātiski iegūst no tiem strukturētus datus, izmantojot OCR un mākslīgā intelekta modeli.

Platforma ļauj analizēt izdevumus, grupēt tos pa kategorijām un eksportēt rezultātus Excel formātā.

---
## ⚙️ Funkcionalitāte

### 🧳 Ceļojumu pārvaldība
- Izveidot jaunu ceļojumu
- Izvēlēties esošu ceļojumu
- Dzēst ceļojumu (kopā ar dokumentiem)

### 📄 Dokumentu apstrāde
- Augšupielādēt čekus (PNG, JPG, PDF)
- Automātiska dokumentu analīze
- Statusa attēlošana (processing, done, error)

### ✏️ Dokumentu pārvaldība
- Apskatīt dokumentu sarakstu
- Rediģēt datus (summa, kategorija, datums)
- Dzēst dokumentus

### 📊 Datu analīze
- Izdevumu sadalījums pa kategorijām (diagramma)
- Kopējā summa
- Dokumentu skaits

### 📥 Datu eksports
- Eksportēt datus Excel failā
- Iekļautie dati:
    + datums
    + kategorija
    + summa
- Kopsavilkuma lapa ar kopējo summu un kategorijām

---
## 🛠️ Tehnoloģiju steks

| Komponents             | Tehnoloģija             |
| ---------------------- | ----------------------- |
| **Backend**            | FastAPI, Python, SQLAlchemy, PostgreSQL    |
| **Datu apstrāde**      | Pandas, NumPy           |
| **AI modulis**         | Ollama (LLaVA), pytesseract, pdf2image          |
| **Frontend**           | React, Ant Design, Axios  |
| **Datu vizualizācija** | Docker, docker-compose  |

---
## 🧱 Sistēmas arhitektūra

```mermaid
flowchart LR

    User["Lietotājs"]
    Frontend["Frontend (React)"]
    Backend["Backend (FastAPI)"]
    DB["PostgreSQL"]
    OCR["OCR (pytesseract)"]
    AI["Ollama (LLaVA)"]

    User --> Frontend
    Frontend --> Backend
    Backend --> DB

    Backend --> OCR
    Backend --> AI

    OCR --> Backend
    AI --> Backend

    Backend --> Frontend
```
---
## 🚀 Uzstādīšana un palaišana

### 🔧 Prasības

- Docker
- Docker Compose

### 📥 1. Klonēt repozitoriju
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### ⚙️ 2. Palaist sistēmu
```bash
docker-compose up --build
```

### ⏳ 3. Sagaidīt inicializāciju

Pirmajā palaišanas reizē:

- tiks lejupielādēts LLaVA modelis (tas var aizņemt laiku);
- tiks izveidota datu bāze.

### 🌐 4. Atvērt aplikāciju

Frontend būs pieejams:

```bash
http://localhost:3000
```

Backend API:

```bash
http://localhost:8000
```

### 🧪 5. Lietošana

1. Izveido jaunu ceļojumu
2. Augšupielādē čeku
3. Sagaidi apstrādi
4. Skaties analīzi un diagrammas
5. Eksportē datus Excel formātā

---
## 📌 Piezīmes
- Pirmais dokumenta apstrādes laiks var būt ilgāks (AI modelis inicializējas)
- Sistēma izmanto polling mehānismu, lai pārbaudītu dokumenta statusu
- Visi dati tiek saglabāti PostgreSQL datu bāzē

---
## 📈 Nākotnes uzlabojumi
- Modeļa optimizācija
- Lietotāju autentifikācija
- Vairāku valūtu atbalsts
- Paplašināta analītika
- Mobilā versija
