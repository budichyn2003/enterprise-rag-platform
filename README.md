# Enterprise RAG Platform

Platform customer support berbasis Retrieval-Augmented Generation (RAG), dengan aplikasi web Next.js dan API FastAPI. Repository ini sedang dikembangkan mengikuti [PRD](./docs/PRD_Enterprise_RAG_Platform.docx).

> **Status: local mock MVP — hanya untuk development.** Aplikasi menggunakan dokumen dan integrasi sintetis. Retrieval saat ini memakai pencocokan kata kunci/aturan lokal, bukan embedding atau LLM. Backend menolak berjalan jika `APP_ENV` bukan `development`; jangan gunakan untuk pelanggan atau data production.

## Cakupan yang tersedia

- Widget chat berbahasa Indonesia dengan sitasi sumber, riwayat sesi, feedback, permintaan agent, penutupan, dan penghapusan data sesi.
- Seed dokumen sintetis dalam Bahasa Indonesia dan Inggris.
- Unggah dan ekstraksi teks PDF, DOCX, HTML, Markdown, CSV, dan TXT; ukuran maksimum default 5 MB.
- Chunking teks, metadata bahasa/kategori/produk/region/sensitivitas, status indexing, versioning, rollback, penghapusan dari index aktif, dan uji query.
- Konektor **mock manual** untuk fixture Confluence dan Google Drive.
- Guardrail berbasis aturan untuk beberapa pola PII, prompt injection yang dikenal, topik sensitif, batas ukuran request, serta rate limit lokal.
- Eskalasi ke tiket lokal mock dengan ringkasan dan konteks percakapan.
- Dashboard percakapan, pencarian/replay transkrip, knowledge gap sederhana, CSAT, containment rate, ekspor CSV, konfigurasi bot, dan audit log.
- Retensi percakapan default 365 hari serta endpoint permintaan penghapusan sesi.
- Mock role untuk console admin yang hanya aktif saat `APP_ENV=development`.

Fixture awal dibuat di [backend/app/services/mock_data.py](./backend/app/services/mock_data.py). Seluruh judul, kebijakan, URL `.invalid`, dan isi fixture adalah data sintetis untuk pengujian, bukan kebijakan perusahaan sungguhan.

## Batasan penting

Implementasi ini membuat alur lokal dapat diuji, tetapi **belum memenuhi seluruh kriteria P0 production di PRD**. Beberapa dependensi PRD masih menunggu keputusan vendor/sign-off:

- Belum ada vector database, embedding, semantic search, cross-encoder re-ranking, LLM, failover provider, atau streaming. Jawaban demo mengambil kutipan teks yang cocok; skor confidence adalah heuristik.
- Konektor Confluence/Google Drive hanya fixture manual; tidak ada akses vendor, webhook, crawl URL, atau sinkronisasi terjadwal. Tidak ada request server-side ke URL sumber sehingga input URL tidak dapat dipakai untuk SSRF.
- Handoff hanya membuat tiket lokal. Belum terhubung ke Zendesk/Freshdesk/Intercom, SSO/OIDC/SAML, OAuth/API key production, maupun mobile SDK/WhatsApp.
- `X-Mock-Role` dapat dipalsukan dan **bukan autentikasi**. Backend sengaja menolak start di luar `development`; jangan membuka port mock admin ke jaringan publik.
- PII detection, prompt-injection detection, topik sensitif, dan output moderation berbasis pola terbatas; ini bukan DLP/moderasi menyeluruh atau jaminan bebas serangan.
- Tidak ada enkripsi at-rest, malware scanning, OCR, load test skala PRD, penetration test, disaster-recovery, atau sertifikasi UU PDP/GDPR. SQLite dan rate limit proses lokal tidak dirancang untuk multi-worker/production.
- Data analitik masih lokal dan sederhana; ekspor PDF, koneksi BI, approval workflow, dan sinkronisasi otomatis belum tersedia.

Sebelum production, tentukan cloud, LLM, vector database, helpdesk, identity provider, data residency, kebijakan retensi, serta proses legal/privacy. Selanjutnya lakukan review keamanan independen, evaluasi jawaban dengan test set kurasi PRD, dan load test. Jangan anggap hasil unit test sebagai pengganti kegiatan tersebut.

## Teknologi

| Area | Teknologi |
|---|---|
| Backend | Python 3.10–3.12, FastAPI, Pydantic v2, SQLAlchemy async, SQLite untuk mock lokal |
| Ekstraksi PDF | pypdf |
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS |
| Package manager | Poetry untuk backend; npm untuk frontend |
| Container | Docker Compose |

## Struktur repository

```text
enterprise-rag-platform/
├── backend/
│   ├── app/
│   │   ├── api/routes.py
│   │   ├── core/                 # konfigurasi dan error handler
│   │   ├── models/               # SQLAlchemy, schema API, migrasi aditif
│   │   ├── services/             # guardrail, ingestion, mock data, RAG, retensi
│   │   └── main.py
│   ├── tests/
│   ├── .env.example
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── poetry.lock
├── frontend/
│   ├── app/
│   │   ├── admin/                # dashboard, knowledge, transkrip, konfigurasi
│   │   └── page.tsx              # landing page dan chat widget
│   ├── components/
│   ├── lib/api.ts
│   ├── Dockerfile
│   └── package.json
├── docs/
│   ├── handover.md
│   ├── ui.md
│   └── PRD_Enterprise_RAG_Platform.docx
├── docker-compose.yml
└── README.md
```

## Menjalankan secara lokal

### Prasyarat

- Python 3.10, 3.11, atau 3.12
- Node.js 22 dan npm
- Docker Desktop (opsional)
- Poetry 2.x hanya diperlukan jika perlu membuat/memasang ulang environment backend; tidak diperlukan untuk menjalankan backend dari `.venv` yang sudah tersedia.

### 1. Konfigurasi backend

Di PowerShell dari direktori repository:

```powershell
Copy-Item backend\.env.example backend\.env
```

Biarkan `DATABASE_URL` kosong untuk memakai `backend/sql_app.db` lokal. Backend development mock memaksa SQLite dan tidak menghubungi database eksternal. Biarkan `MOCK_AUTH_ENABLED=true` dan `APP_ENV=development`.

### 2. Jalankan backend

Jika folder `backend\.venv` sudah tersedia, aktifkan environment tersebut di PowerShell:

```powershell
Set-Location backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Jika aktivasi script diblokir oleh kebijakan PowerShell, jalankan executable environment secara langsung tanpa mengubah kebijakan:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Poetry tidak perlu dipasang untuk langkah di atas. Jika `.venv` belum ada atau dependensinya belum terpasang, pasang Poetry 2.x terlebih dahulu, lalu dari direktori `backend` jalankan:

```powershell
poetry install
poetry run python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Pada startup, backend membuat tabel, menambahkan kolom yang belum ada pada schema lokal lama, menanam fixture hanya bila belum ada dokumen, dan membersihkan percakapan yang melewati retensi.

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Health/sambutan: http://localhost:8000/

### 3. Jalankan frontend

Buka terminal kedua:

```powershell
Set-Location frontend
npm ci
npm run dev
```

- Aplikasi pelanggan: http://localhost:3000
- Console admin: http://localhost:3000/admin
- Knowledge base: http://localhost:3000/admin/knowledge
- Transkrip: http://localhost:3000/admin/conversations
- Konfigurasi dan audit: http://localhost:3000/admin/settings

`NEXT_PUBLIC_API_URL` dapat diatur bila backend berjalan di alamat berbeda. Pada development lokal, frontend menggunakan role demo `admin` secara otomatis; jangan gunakan mekanisme ini sebagai kontrol akses production.

### Menjalankan dengan Docker Compose

Dari root repository:

```powershell
docker compose up --build
```

Compose menjalankan API pada port 8000 dan frontend pada port 3000. Database demo disimpan di named volume `backend-data`. Hapus volume hanya jika memang ingin menghapus database demo dan seluruh sesi lokal.

## API utama

Endpoint internal console memerlukan header `X-Mock-Role` selama development. Nilai yang tersedia: `admin`, `knowledge_manager`, `agent`, `viewer`. Header ini hanya simulasi RBAC lokal; nilainya mudah dipalsukan.

| Method | Path | Fungsi |
|---|---|---|
| `POST` | `/api/chat` | Chat, retrieval lokal, sitasi, serta eskalasi otomatis |
| `POST` | `/api/chat/{session_id}/feedback` | Simpan rating 1–5 untuk jawaban bot |
| `POST` | `/api/chat/{session_id}/handoff` | Buat tiket handoff mock |
| `POST` | `/api/chat/{session_id}/resolve` | Tandai percakapan selesai |
| `DELETE` | `/api/chat/{session_id}` | Hapus pesan, feedback, dan tiket sesi |
| `GET` | `/api/documents` | Daftar dokumen terindeks |
| `POST` | `/api/documents/upload` | Unggah dokumen sebagai JSON base64 |
| `PATCH` / `DELETE` | `/api/documents/{document_id}` | Perbarui metadata/versi atau keluarkan dari index aktif |
| `POST` | `/api/documents/{document_id}/rollback/{version}` | Pulihkan versi dokumen |
| `GET` | `/api/documents/{document_id}/test?q=...` | Uji retrieval terhadap dokumen |
| `POST` | `/api/documents/sync/confluence` | Sinkronisasi fixture Confluence |
| `POST` | `/api/documents/sync/google_drive` | Sinkronisasi fixture Drive |
| `GET` | `/api/analytics/overview` | Metrik demo |
| `GET` | `/api/analytics/knowledge-gaps` | Pertanyaan yang berulang kali dieskalasi |
| `GET` | `/api/analytics/conversations?q=...` | Cari dan replay transkrip |
| `GET` | `/api/analytics/export.csv` | Ekspor ringkasan CSV |
| `GET` / `PUT` | `/api/admin/config` | Baca/simpan konfigurasi demo |
| `GET` | `/api/admin/audit` | Audit aksi administratif |

Contoh request chat:

```json
{
  "message": "Bagaimana cara mengajukan pengembalian dana?",
  "language": "id"
}
```

Balasan memuat `session_id`, `message_id`, jawaban, sitasi, skor heuristik, dan flag eskalasi. Gunakan `session_id` dari balasan untuk melanjutkan sesi.

Untuk unggah, kirim `filename`, `content_base64`, dan metadata kategori/bahasa/produk/region/sensitivitas ke `/api/documents/upload`. Endpoint internal perlu header `X-Mock-Role: admin` atau `X-Mock-Role: knowledge_manager`. Sensitivitas selain `public` tidak digunakan untuk jawaban pelanggan.

## Data nyata yang dibutuhkan sebelum integrasi

Untuk mengganti fixture, siapkan dan minta persetujuan pemilik data atas:

1. FAQ dan artikel bantuan resmi, kebijakan pengembalian, pengiriman, pembayaran, akun, serta dokumentasi produk dalam Bahasa Indonesia dan Inggris.
2. Metadata setiap dokumen: pemilik/sumber, URL resmi, tanggal berlaku/perubahan, versi, bahasa, kategori, produk, region, dan tingkat sensitivitas.
3. Pertanyaan-jawaban evaluasi terkurasi (PRD menyarankan 200–500 pertanyaan) beserta jawaban benar dan sumber yang diharapkan.
4. Bila memakai tiket historis, ekspor yang sudah dianonimkan dan disetujui Legal/Privacy; jangan unggah nama, email, nomor telepon, nomor kartu, password, token, atau data transaksi nyata ke demo.
5. Keputusan vendor dan kredensial melalui secret manager untuk cloud, IdP/SSO, LLM, vector database, serta helpdesk. Kredensial tersebut tidak diperlukan dan tidak boleh dimasukkan ke mode mock.

## Testing dan pemeriksaan

Backend menggunakan test runner bawaan Python:

```powershell
Set-Location backend
.\.venv\Scripts\Activate.ps1
python -m unittest discover -s tests -v
```

Frontend:

```powershell
Set-Location frontend
npm run lint
npm run build
```

Test backend mencakup guardrail PII/prompt injection, parsing dokumen, filtering dokumen non-publik, citation/abstention, migrasi SQLite lama, role mock, alur upload-chat-feedback-handoff, penghapusan data, dan header keamanan. Test ini bukan penetration test, load test, audit compliance, atau validasi terhadap seluruh kriteria non-fungsional PRD.

## Dokumen acuan

- [PRD Enterprise RAG Platform](./docs/PRD_Enterprise_RAG_Platform.docx) — kebutuhan produk dan kriteria keberhasilan.
- [UI design system](./docs/ui.md) — warna, tipografi, komponen, aksesibilitas.
- [Handover](./docs/handover.md) — alur kerja dan instruksi proyek.

Belum ada file lisensi pada repository ini.
