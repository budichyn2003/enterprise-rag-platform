# 🚀 Budi Cahyono — Maincore

> **Reusable Fullstack & AI Project Foundation**

Maincore adalah template foundation yang digunakan sebagai titik awal untuk membangun berbagai aplikasi **Fullstack, AI, dan Web System**.

Tujuan utama Maincore:

> **Clone → Setup → Start Coding**

Maincore menangani struktur dasar dan konfigurasi umum agar waktu development dapat difokuskan pada fitur dan business logic.

---

# 🧠 Philosophy

Maincore bukan aplikasi jadi.

Maincore adalah **fondasi project** yang dapat digunakan kembali untuk project baru.

Prinsip utama:

* Keep the architecture simple.
* Reuse existing structure.
* Avoid unnecessary complexity.
* Business logic belongs to modules/services.
* Add new dependencies only when necessary.
* Do not duplicate existing functionality.
* Optional features should not become mandatory dependencies.

Maincore akan berkembang berdasarkan kebutuhan project nyata.

---

# 🏗️ Architecture

```text
                         MAINCORE
                            │
             ┌──────────────┴──────────────┐
             │                             │
            CORE                       OPTIONAL
             │                             │
      ┌──────┼──────┐             ┌────────┼────────┐
      │      │      │             │        │        │
    Web     API   Database        LLM      RAG     Agent
```

## Core

Komponen dasar yang digunakan oleh hampir semua project:

* Frontend
* Backend
* Configuration
* Environment
* Database
* API communication
* Reusable components
* Utilities
* Validation
* Error handling

## Optional Modules

Fitur yang hanya digunakan jika project membutuhkannya:

* LLM
* RAG
* AI Agent
* Machine Learning
* Computer Vision
* Other AI services

---

# 📂 Project Structure

```text
maincore/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   └── routes.py
│   │   │
│   │   ├── core/
│   │   │   └── config.py
│   │   │
│   │   ├── services/
│   │   │   ├── llm_service.py
│   │   │   ├── rag_service.py
│   │   │   └── agent_service.py
│   │   │
│   │   ├── vectorstore/
│   │   │   └── chroma_db.py
│   │   │
│   │   └── models/
│   │       └── schemas.py
│   │
│   └── ...
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── hooks/
│   ├── lib/
│   └── public/
│
├── .env.example
├── .gitignore
└── README.md
```

> Struktur dapat berkembang mengikuti kebutuhan project. Jangan membuat struktur baru jika struktur yang sudah ada masih dapat digunakan.

---

# ⚙️ Tech Stack

## Backend

* Python 3.10+
* FastAPI
* Pydantic
* LangChain
* ChromaDB
* Poetry

## Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS

## Database

* PostgreSQL
* Neon Database

## AI

* OpenAI
* LangChain
* ChromaDB
* PyTorch
* Machine Learning models

AI dependencies bersifat **optional** dan hanya digunakan ketika project membutuhkan fitur AI.

---

# 🚀 Getting Started

## 1. Clone Maincore

```bash
git clone <repository-url> my-project
cd my-project
```

## 2. Setup Backend

```bash
cd backend
poetry install
```

Create environment:

```bash
cp .env.example .env
```

Run:

```bash
poetry run uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

API Documentation:

```text
http://localhost:8000/docs
```

---

# 🎨 Frontend Setup

```bash
cd frontend
npm install
```

Create:

```text
.env.local
```

Example:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Run:

```bash
npm run dev
```

Frontend:

```text
http://localhost:3000
```

---

# 🔐 Environment

Gunakan `.env.example` sebagai template.

Contoh:

```env
# Application
PROJECT_NAME="My Project"
VERSION="1.0.0"
APP_ENV="development"

# Backend
PORT=8000

# Database
DATABASE_URL=""

# AI - Optional
OPENAI_API_KEY=""
```

### Rules

* Jangan commit `.env`.
* Jangan menyimpan API key di source code.
* Tambahkan environment variable baru ke `.env.example`.
* Gunakan environment variable untuk configuration.

---

# 📦 Common Commands

## Backend

```bash
poetry install
poetry run uvicorn app.main:app --reload
```

## Frontend

```bash
npm install
npm run dev
npm run build
npm run lint
```

---

# 🧩 Development Rules

## Backend

* `main.py` hanya menangani application initialization.
* API routes harus tetap sederhana.
* Business logic berada di `services`.
* Configuration berada di `core`.
* Schema berada di `models`.
* AI logic berada di AI services.
* Vector database logic berada di `vectorstore`.

## Frontend

* Gunakan reusable components.
* UI components berada di `components`.
* API communication berada di `lib`.
* Gunakan hooks untuk reusable client-side logic.
* Hindari business logic besar di page/component.

---

# 📐 General Rules

1. **Follow the existing architecture first.**
2. Reuse existing files/functions before creating new ones.
3. Jangan membuat duplicate utility/service.
4. Jangan membuat folder baru tanpa alasan yang jelas.
5. Jangan menambahkan dependency jika belum diperlukan.
6. Jangan mengubah core architecture hanya untuk satu fitur.
7. Pisahkan business logic dari UI dan entry point.
8. Gunakan environment variables untuk secrets/configuration.
9. Keep modules small and understandable.
10. Prefer simple solutions over complex abstractions.

---

# 🤖 AI Coding Instructions

When working inside Maincore:

```text
You are working inside Budi Cahyono Maincore.

Before creating or modifying code:

1. Inspect the existing project structure.
2. Follow the existing architecture.
3. Reuse existing utilities, services and components.
4. Do not create duplicate functionality.
5. Do not create unnecessary folders.
6. Do not introduce unnecessary dependencies.

Backend:
- FastAPI
- Keep main.py for initialization only.
- Keep API routes thin.
- Put business logic inside services.
- Keep configuration inside core.
- Keep schemas inside models.

Frontend:
- Next.js
- Use reusable components.
- Keep API communication separated.
- Avoid large business logic inside UI components.

AI:
- AI modules are optional.
- Do not introduce AI dependencies unless the requested feature requires them.

General:
- Preserve the existing architecture.
- Make the smallest reasonable change.
- Prefer simple and maintainable solutions.
- Do not rewrite unrelated code.
```

---

# 🧪 Development Checklist

Before considering a feature complete:

```text
[ ] Application runs successfully
[ ] Existing architecture is preserved
[ ] No duplicate functionality
[ ] Environment variables are documented
[ ] API works correctly
[ ] Frontend works correctly
[ ] No unnecessary dependencies added
[ ] Existing functionality is not broken
```

---

# 🔄 Creating a New Project

Maincore is intended to be reused for future projects.

Recommended workflow:

```text
MAINCORE
   │
   ▼
Clone Repository
   │
   ▼
Rename Project
   │
   ▼
Configure .env
   │
   ▼
Remove Unused Optional Modules
   │
   ▼
Install Dependencies
   │
   ▼
Start Development
```

Example:

```bash
git clone <maincore-repository> bank-sampah
cd bank-sampah
```

Then configure the project-specific:

* Project name
* Environment variables
* Database
* Business modules
* UI
* Features

The existing Maincore architecture should remain the foundation.

---

# 🚧 What Should NOT Be Added to Core

Do not add project-specific features directly into Maincore unless they are repeatedly useful across multiple projects.

Examples:

```text
❌ Bank Sampah business logic
❌ E-commerce business logic
❌ School-specific features
❌ One-project payment implementation
❌ One-project workflow
```

Instead:

```text
Maincore
   │
   ├── Core
   │
   └── Project
        ├── Bank Sampah
        ├── E-Commerce
        ├── School System
        └── AI Application
```

---

# 🎯 Purpose

Maincore exists to eliminate repetitive project setup.

The goal is simple:

```text
OLD WAY

New Project
    ↓
Setup Backend
    ↓
Setup Frontend
    ↓
Setup Configuration
    ↓
Setup Structure
    ↓
Setup API
    ↓
Setup AI
    ↓
Finally Start Coding


MAINCORE WAY

Clone
  ↓
Configure
  ↓
Start Coding
```

> **Build features, not boilerplate.**

---

# 👨‍💻 Author

## Budi Cahyono

AI Engineer | Fullstack Developer

Building:

* Fullstack Applications
* AI Applications
* LLM Systems
* RAG Systems
* AI Agents
* Machine Learning Systems
* Modern Web Applications

---

# ⭐ Maincore Principle

```text
Keep it simple.
Keep it reusable.
Keep it maintainable.

Clone.
Configure.
Build.
```
