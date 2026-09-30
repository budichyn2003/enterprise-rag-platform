from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.exceptions import global_exception_handler
from app.api.routes import router
from contextlib import asynccontextmanager

# Import service untuk memastikan koneksi DB terbuka saat startup
from app.core.config import settings
from app.models.database import engine, Base
# from app.services.database_service import database_service # (Pastikan file ini sudah ada jika ingin digunakan)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle hook untuk inisialisasi DB dan koneksi lainnya."""
    print(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}...")
    
    # 1. Koneksi ke Database & Migrasi Skema
    print(f"📦 Connecting to PostgreSQL at {settings.DATABASE_URL[:20]}...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database schema initialized/connected.")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        raise

    # 2. Inisialisasi Vector DB & LLM (jika diperlukan)
    print("🧠 Initializing AI Services...")
    # database_service.initialize_vector_store()

    yield

    # Cleanup (Opsional untuk aplikasi yang long-lived)
    print("🛑 Shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan # Menghubungkan fungsi lifespan ke aplikasi
)

app.exception_handler(Exception)(global_exception_handler)  

# CORS untuk Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PERUBAHAN: Menambahkan prefix /api agar sesuai dengan frontend (lib/api.ts)
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "Welcome to Enterprise RAG Platform API"
    }