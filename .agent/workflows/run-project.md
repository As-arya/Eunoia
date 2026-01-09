---
description: How to run the Euonia project (backend + frontend)
---

# Running Euonia Project

## Prerequisites
- Python 3.x installed
- Node.js and npm installed

## Steps

### 1. Backend Setup (First Terminal)

```bash
cd d:\BINUZ\BINUS Assigntment\Semester 3\AI\Euonia\EuoniaFresh\backend

# Activate virtual environment (if exists)
.\venv\Scripts\activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Run backend server
python run.py
```

Backend will run on: `http://localhost:5000`

---

### 2. Frontend Setup (Second Terminal)

```bash
cd d:\BINUZ\BINUS Assigntment\Semester 3\AI\Euonia\EuoniaFresh\frontend

# Install dependencies (first time only)
npm install

# Run frontend dev server
npm run dev
```

Frontend will run on: `http://localhost:5173`

---

### 3. Optional: Reseed Database

If you need fresh questions data:

```bash
cd d:\BINUZ\BINUS Assigntment\Semester 3\AI\Euonia\EuoniaFresh\backend
python reseed_questions.py
```

---

## Quick Start (After Setup Done)

// turbo-all

**Terminal 1:**
```bash
cd d:\BINUZ\BINUS Assigntment\Semester 3\AI\Euonia\EuoniaFresh\backend
.\venv\Scripts\activate
python run.py
```

**Terminal 2:**
```bash
cd d:\BINUZ\BINUS Assigntment\Semester 3\AI\Euonia\EuoniaFresh\frontend
npm run dev
```

Then open: http://localhost:5173
