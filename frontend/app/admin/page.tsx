"use client";

import Link from "next/link";
import React, { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { downloadAnalyticsCsv, getAnalyticsOverview, getKnowledgeGaps } from "@/lib/api";
import type { AnalyticsOverview } from "@/lib/api";

export default function AdminDashboardPage() {
    const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
    const [gaps, setGaps] = useState<Array<{ question: string; occurrences: number }>>([]);
    const [errorMessage, setErrorMessage] = useState<string | null>(null);

    useEffect(() => {
        Promise.all([getAnalyticsOverview(), getKnowledgeGaps()])
            .then(([summary, knowledgeGaps]) => {
                setOverview(summary);
                setGaps(knowledgeGaps);
            })
            .catch((error: unknown) => {
                console.error("Gagal memuat dashboard:", error);
                setErrorMessage("Dashboard belum dapat dimuat. Pastikan API lokal aktif.");
            });
    }, []);

    const handleExport = async () => {
        try {
            const file = await downloadAnalyticsCsv();
            const url = URL.createObjectURL(file);
            const link = document.createElement("a");
            link.href = url;
            link.download = "enterprise-rag-analytics.csv";
            link.click();
            URL.revokeObjectURL(url);
        } catch (error) {
            console.error("Gagal mengekspor analytics:", error);
            setErrorMessage("Laporan tidak dapat diekspor.");
        }
    };

    const metrics = overview
        ? [
            ["Percakapan", overview.conversations.toLocaleString("id-ID")],
            ["Containment rate", `${(overview.containment_rate * 100).toFixed(1)}%`],
            ["CSAT rata-rata", overview.average_csat.toFixed(2)],
            ["Dokumen terindeks", overview.indexed_documents.toLocaleString("id-ID")],
            ["Waktu penanganan rata-rata", `${overview.average_handling_time_seconds.toFixed(1)} dtk`],
            ["Eskalasi", overview.escalated_conversations.toLocaleString("id-ID")],
        ]
        : [];

    return (
        <div className="mx-auto max-w-6xl space-y-6 p-6 md:p-8">
            <header className="flex flex-wrap items-end justify-between gap-3">
                <div>
                    <h1 className="text-2xl font-bold text-mc-dark">Dashboard Support</h1>
                    <p className="mt-1 text-sm text-mc-dark/70">
                        Metrik dihitung dari data demo lokal; bukan metrik production.
                    </p>
                </div>
                <button
                    type="button"
                    onClick={() => void handleExport()}
                    className="rounded-lg border border-mc-primary px-4 py-2 text-sm font-medium text-mc-primary hover:bg-mc-primary/5"
                >
                    Ekspor CSV
                </button>
            </header>
            {errorMessage && <p className="rounded-lg bg-error/10 p-3 text-sm text-error" role="alert">{errorMessage}</p>}
            {!overview && !errorMessage && <p role="status">Memuat metrik...</p>}
            {overview && (
                <>
                    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                        {metrics.map(([label, value]) => (
                            <Card key={label}>
                                <p className="text-sm text-mc-dark/70">{label}</p>
                                <p className="mt-2 text-3xl font-bold text-mc-dark">{value}</p>
                            </Card>
                        ))}
                    </section>
                    <section className="grid gap-4 lg:grid-cols-2">
                        <Card>
                            <div className="mb-3 flex items-center justify-between">
                                <h2 className="text-lg font-semibold">Pertanyaan yang belum terjawab</h2>
                                <Link href="/admin/conversations" className="text-sm text-mc-primary underline">
                                    Lihat transkrip
                                </Link>
                            </div>
                            {gaps.length ? (
                                <ul className="space-y-2">
                                    {gaps.map((gap) => (
                                        <li key={gap.question} className="flex justify-between gap-3 rounded-lg bg-mc-soft/50 p-3 text-sm">
                                            <span>{gap.question}</span>
                                            <span className="shrink-0 font-semibold">{gap.occurrences}×</span>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <p className="text-sm text-mc-dark/70">Belum ada gap knowledge tercatat.</p>
                            )}
                        </Card>
                        <Card>
                            <h2 className="mb-3 text-lg font-semibold">Mode dan batasan demo</h2>
                            <ul className="list-inside list-disc space-y-2 text-sm text-mc-dark/80">
                                <li>Retrieval lokal menggunakan pencocokan kata kunci dan aturan sederhana.</li>
                                <li>Konten dan konektor yang disediakan adalah sintetis.</li>
                                <li>Tidak ada LLM, vector database, SSO, atau helpdesk vendor yang dipanggil.</li>
                                <li>Header role admin hanya untuk development dan bukan autentikasi production.</li>
                            </ul>
                        </Card>
                    </section>
                </>
            )}
        </div>
    );
}
