"use client";

import React, { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

// Mock data berdasarkan struktur endpoint GET /api/documents
const mockDocuments = [
    { id: "doc-1", title: "Kebijakan Pengembalian Dana.pdf", status: "indexed", date: "2026-08-23" },
    { id: "doc-2", title: "FAQ_Produk_v2.docx", status: "processing", date: "2026-08-23" },
    { id: "doc-3", title: "Syarat_Ketentuan.html", status: "failed", date: "2026-08-22" },
];

export default function KnowledgeBasePage() {
    const [isUploading, setIsUploading] = useState(false);

    const getStatusBadge = (status: str) => {
        switch (status) {
            case "indexed":
                return <span className="rounded-full bg-success/10 px-2.5 py-1 text-xs font-medium text-success">Indexed</span>;
            case "processing":
                return <span className="rounded-full bg-warning/10 px-2.5 py-1 text-xs font-medium text-warning">Processing</span>;
            case "failed":
                return <span className="rounded-full bg-error/10 px-2.5 py-1 text-xs font-medium text-error">Failed</span>;
            default:
                return <span className="rounded-full bg-mc-soft px-2.5 py-1 text-xs font-medium text-mc-dark">Queued</span>;
        }
    };

    return (
        <div className="p-8 max-w-6xl mx-auto space-y-6">
            {/* Page Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-mc-dark">Knowledge Base</h1>
                    <p className="text-sm text-mc-dark/70">Kelola sumber data dan dokumen yang digunakan oleh bot AI.</p>
                </div>
                <div className="flex gap-3">
                    <Button variant="outline" size="sm">Sinkronisasi Confluence</Button>
                    <Button variant="primary" size="sm" onClick={() => setIsUploading(true)}>
                        + Unggah Dokumen
                    </Button>
                </div>
            </div>

            {/* Main Content: Data Table */}
            <Card padding="none" className="overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-mc-soft text-mc-dark font-semibold border-b border-mc-dark/10">
                            <tr>
                                <th className="px-6 py-4">Judul Dokumen</th>
                                <th className="px-6 py-4">Tanggal Diperbarui</th>
                                <th className="px-6 py-4">Status Indexing</th>
                                <th className="px-6 py-4 text-right">Aksi</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-mc-soft/50">
                            {mockDocuments.map((doc) => (
                                <tr key={doc.id} className="hover:bg-mc-soft/30 transition-colors">
                                    <td className="px-6 py-4 font-medium text-mc-dark flex items-center gap-3">
                                        📄 {doc.title}
                                    </td>
                                    <td className="px-6 py-4 text-mc-dark/70">{doc.date}</td>
                                    <td className="px-6 py-4">{getStatusBadge(doc.status)}</td>
                                    <td className="px-6 py-4 text-right">
                                        <button className="text-mc-primary hover:underline font-medium mr-3 text-sm">Edit</button>
                                        <button className="text-error hover:underline font-medium text-sm">Hapus</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </Card>

            {/* Placeholder form upload (akan diganti dengan UI Modal yang sesuai UI.md) */}
            {isUploading && (
                <div className="mt-4 p-4 border border-dashed border-mc-primary/50 bg-mc-primary/5 rounded-lg text-center">
                    <p className="text-sm text-mc-dark mb-3">Area Drop File PDF/DOCX (Simulasi Upload)</p>
                    <Button variant="secondary" size="sm" onClick={() => setIsUploading(false)}>Batal</Button>
                </div>
            )}
        </div>
    );
}