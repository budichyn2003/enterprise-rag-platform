# Enterprise RAG Platform

Platform AI untuk customer support dan knowledge management berbasis Retrieval Augmented Generation (RAG), terdiri dari backend FastAPI dan frontend Next.js. Proyek ini dirancang untuk mengelola dokumen, melakukan indexing, dan menyediakan chatbot yang menjawab pertanyaan pelanggan berdasarkan basis pengetahuan internal.

## Ringkasan Proyek

Proyek ini dibangun sebagai monorepo dengan dua bagian utama:

- Backend: FastAPI untuk API, logika RAG, dan integrasi database
- Frontend: Next.js untuk dashboard dan antarmuka chat/knowledge base
- DevOps: Docker Compose untuk menjalankan backend dan frontend dalam satu ekosistem

Struktur ini memungkinkan pengembangan modular untuk:

- ingest dokumen ke knowledge base
- query dan retrieval informasi relevan
- menampilkan hasil answer ke user melalui chat interface
- mengelola data dokumen di admin panel

## Fitur Utama

- Chat API berbasis RAG dengan request/response schema yang jelas
- Endpoint upload dokumen dan daftar dokumen
- Skema database untuk dokumen, percakapan, dan pesan
- Dashboard admin knowledge base untuk melihat status indexing dokumen
- Landing page modern untuk customer support AI
- Support konfigurasi environment dan deployment berbasis Docker

## Status Implementasi

Repository ini masih dalam tahap pengembangan awal. Beberapa bagian sudah disediakan sebagai blueprint dan struktur modular, namun beberapa logika RAG dan ingestion masih bersifat placeholder / mock-up dan siap dikembangkan lebih lanjut, misalnya:

- `backend/app/services/rag_service.py`
- `backend/app/services/ingestion_service.py`
- `backend/app/services/llm_service.py` (belum diimplementasikan secara penuh)

Artinya, proyek sudah memiliki arsitektur dasar yang benar dan siap untuk dikembangkan ke production-grade dengan integrasi model LLM, vector DB, dan penyimpanan data yang lengkap.

## Teknologi yang Digunakan

### Backend

- Python 3.10+
- FastAPI
- SQLAlchemy (async)
- Pydantic v2
- OpenAI / LangChain-ready integration
- Uvicorn

### Frontend

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS

### Infrastructure / Tooling

- Docker Compose
- Poetry (Python dependency management)
- npm / package-lock
- SQLite fallback untuk local development

## Struktur Folder

```text
enterprise-rag-platform/
├─ backend/
│  ├─ app/
│  │  ├─ api/
│  │  │  └─ routes.py
│  │  ├─ core/
│  │  │  ├─ config.py
│  │  │  ├─ exceptions.py
│  │  │  └─ logger.py
│  │  ├─ models/
│  │  │  ├─ database.py
│  │  │  └─ schemas.py
│  │  ├─ services/
│  │  │  ├─ agent.py
│  │  │  ├─ ingestion_service.py
│  │  │  ├─ llm_service.py
│  │  │  └─ rag_service.py
│  │  ├─ __init__.py
│  │  └─ main.py
│  ├─ .env.example
│  ├─ Dockerfile
│  ├─ pyproject.toml
│  ├─ poetry.lock
│  └─ sql_app.db
├─ frontend/
│  ├─ app/
│  │  ├─ admin/
│  │  │  └─ knowledge/
│  │  │     └─ page.tsx
│  │  ├─ globals.css
│  │  ├─ layout.tsx
│  │  └─ page.tsx
│  ├─ components/
│  ├─ lib/
│  │  └─ api.ts
│  ├─ Dockerfile
│  ├─ package.json
│  ├─ next.config.ts
│  ├─ tsconfig.json
│  └─ eslint.config.mjs
├─ docs/
│  ├─ handover.md
│  ├─ ui.md
│  └─ PRD_Enterprise_RAG_Platform.docx
├─ docker-compose.yml
├─ .gitignore
├─ README.md
└─ .vscode/
```

## Arsitektur Aplikasi

### 1. Backend API

Backend dibangun dengan FastAPI dan terhubung ke aplikasi melalui `app/main.py`.

Fungsi utama:

- mendaftarkan router API di `/api`
- menjalankan startup lifecycle untuk init database
- menyediakan CORS untuk frontend Next.js di `http://localhost:3000`
- mensupport response model untuk chat dan dokumen

### 2. Service Layer

Struktur service sudah dibagi untuk kebutuhan RAG dan ingestion:

- `rag_service.py`: logika retrieval dan generation
- `ingestion_service.py`: pemrosesan dokumen dan indexing
- `llm_service.py`: integrasi model LLM (belum lengkap)
- `agent.py`: kemungkinan pengembangan AI agent / orchestration

### 3. Database Layer

File `app/models/database.py` mendefinisikan model utama:

- `DocumentRecord` untuk metadata dokumen
- `Conversation` untuk sesi chat
- `Message` untuk log percakapan dan citation

DB config membaca `DATABASE_URL` dari environment. Jika tidak ada, aplikasi akan fallback ke SQLite untuk pengembangan lokal.

### 4. Frontend UI

Frontend menggunakan Next.js dengan fokus pada:

- landing page produk
- chat widget
- admin knowledge base page
- styling yang konsisten dengan `docs/ui.md`

## Prasyarat

Pastikan perangkat Anda sudah memiliki:

- Python 3.10+
- Node.js 18+
- npm
- Poetry
- Docker & Docker Compose (opsional, jika ingin menjalankan semua service sekaligus)
- API key OpenAI bila ingin mengaktifkan integrasi LLM real

## Persiapan Environment

### Backend

Buat file `.env` di folder `backend/` berdasarkan contoh:

```bash
cp backend/.env.example backend/.env
```

Contoh isi `.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/enterprise_rag
PROJECT_NAME="Enterprise RAG Platform"
VERSION="1.0.0"
```

Catatan:

- Jika `DATABASE_URL` kosong, aplikasi memakai SQLite fallback (`sql_app.db`)
- Untuk pengembangan lokal, Anda juga bisa langsung isi ke SQLite bila ingin cepat setup

### Frontend

Buat file `.env.local` di folder `frontend/`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Menjalankan Aplikasi

### Opsi 1: Jalankan backend dan frontend secara terpisah

#### Backend

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

Setelah itu:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

### Opsi 2: Jalankan dengan Docker Compose

Dari root project:

```bash
docker compose up --build
```

Ini akan menjalankan:

- backend di port 8000
- frontend di port 3000

## Endpoint API Utama

### Chat

`POST /api/chat`

Request body:

```json
{
  "session_id": "session-123",
  "message": "Bagaimana cara pengembalian dana?",
  "language": "id"
}
```

Response model:

```json
{
  "session_id": "session-123",
  "answer": "...",
  "citations": [
    {
      "document_id": "doc-1",
      "title": "FAQ Pengiriman",
      "url": null
    }
  ],
  "confidence_score": 0.92,
  "needs_escalation": false
}
```

### Upload Dokumen

`POST /api/documents/upload`

Mengembalikan status dokumen dalam antrean untuk diproses lebih lanjut.

### Daftar Dokumen

`GET /api/documents`

Mengembalikan metadata dokumen dan status indexing.

## Dokumentasi Pendukung

- `docs/ui.md`: design system dan guidelines visual
- `docs/handover.md`: catatan workflow dan arsitektur proyek
- `docs/PRD_Enterprise_RAG_Platform.docx`: product requirements document

## Struktur Kode Penting

- `backend/app/main.py`: entry point aplikasi FastAPI
- `backend/app/api/routes.py`: endpoint utama backend
- `backend/app/models/schemas.py`: schema request/response
- `backend/app/models/database.py`: model SQLAlchemy
- `backend/app/services/rag_service.py`: logika generative retrieval
- `frontend/lib/api.ts`: wrapper API client untuk frontend
- `frontend/app/admin/knowledge/page.tsx`: halaman admin knowledge base
- `frontend/app/page.tsx`: landing page utama

## Catatan Pengembangan

Proyek ini sudah mengadopsi pendekatan modular, namun masih memerlukan penguatan pada bagian berikut agar siap production:

- integrasi LLM yang nyata
- penyimpanan vector database
- pipeline ingestion dokumen dari PDF/DOCX/Confluence
- autentikasi dan authorization
- observability dan logging
- test coverage
- deployment staging/production

## Perintah Berguna

### Backend

```bash
cd backend
poetry install
poetry run pytest
poetry run uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run lint
npm run build
npm run dev
```

## Lisensi

Belum ada file lisensi yang ditambahkan pada repository ini. Jika proyek akan dipublikasikan atau dibagikan ke tim/klien, disarankan untuk menambahkan lisensi yang sesuai (misalnya MIT atau Apache-2.0).

## Kesimpulan

Repository ini merupakan fondasi yang solid untuk sistem customer support AI berbasis RAG. Dengan struktur backend/frontend yang rapi, dokumentasi desain, dan skema data yang sudah dibuat, proyek ini siap untuk dikembangkan menjadi aplikasi knowledge assistant yang lebih lengkap dan siap produksi.
