"use client";

import { ChatWidget } from "@/components/features/chat/ChatWidget";

export default function Home() {
    return (
        <main className="min-h-screen relative flex items-center justify-center overflow-hidden">
            {/* Background Decorative Gradient (sesuai panduan UI.md untuk hero/decorative) */}
            <div className="absolute inset-0 z-0 bg-gradient-to-br from-mc-soft/40 via-mc-base to-mc-primary/5"></div>

            <section className="relative z-10 text-center max-w-3xl px-6">
                <span className="rounded-full bg-mc-soft px-3 py-1 text-sm font-medium text-mc-dark mb-6 inline-block">
                    Versi 1.0 - Beta Terbatas
                </span>

                <h1 className="text-4xl md:text-5xl font-bold text-mc-dark leading-tight mb-6">
                    Layanan Pelanggan Instan dengan <span className="text-mc-primary">Enterprise RAG</span>
                </h1>

                <p className="text-lg text-mc-dark/70 mb-10">
                    Platform AI-Powered Customer Support untuk menjawab pertanyaan Anda secara otomatis, akurat, dan bersumber dari basis pengetahuan resmi kami.
                </p>

                <div className="flex justify-center gap-4">
                    <button
                        type="button"
                        onClick={() => window.dispatchEvent(new Event("enterprise-rag:open-chat"))}
                        className="rounded-lg bg-mc-primary px-6 py-3 font-medium text-white shadow-sm transition-colors duration-200 hover:bg-mc-dark"
                    >
                        Mulai percakapan
                    </button>
                    <a
                        href="http://localhost:8000/docs"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="glass-panel rounded-lg px-6 py-3 font-medium text-mc-dark transition-colors duration-200 hover:bg-white/60"
                    >
                        Dokumentasi API
                    </a>
                </div>
            </section>

            {/* Injeksi Chat Widget yang kita buat sebelumnya */}
            <ChatWidget />
        </main>
    );
}