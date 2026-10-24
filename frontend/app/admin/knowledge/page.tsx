"use client";

import React, { useCallback, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
    deleteDocument,
    listDocuments,
    syncMockConnector,
    testDocumentQuery,
    uploadDocument,
} from "@/lib/api";
import type { DocumentRecord } from "@/lib/api";

const MAX_UPLOAD_BYTES = 5_000_000;

function encodeBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    let binary = "";
    const batchSize = 0x8000;
    for (let index = 0; index < bytes.length; index += batchSize) {
        binary += String.fromCharCode(...bytes.subarray(index, index + batchSize));
    }
    return window.btoa(binary);
}

function getStatusBadge(status: DocumentRecord["status"]) {
    const classes: Record<DocumentRecord["status"], string> = {
        indexed: "bg-success/10 text-success",
        processing: "bg-warning/10 text-warning",
        queued: "bg-mc-soft text-mc-dark",
        failed: "bg-error/10 text-error",
        deleted: "bg-mc-soft text-mc-dark/60",
    };
    return (
        <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${classes[status]}`}>
            {status}
        </span>
    );
}

export default function KnowledgeBasePage() {
    const [documents, setDocuments] = useState<DocumentRecord[]>([]);
    const [file, setFile] = useState<File | null>(null);
    const [category, setCategory] = useState("general");
    const [language, setLanguage] = useState<"id" | "en">("id");
    const [sensitivity, setSensitivity] = useState<"public" | "internal" | "restricted">("public");
    const [testQuery, setTestQuery] = useState("");
    const [testDocumentId, setTestDocumentId] = useState<string | null>(null);
    const [testResults, setTestResults] = useState<Array<{ title: string; score: number; content: string }>>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isUploading, setIsUploading] = useState(false);
    const [errorMessage, setErrorMessage] = useState<string | null>(null);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);

    const refreshDocuments = useCallback(async () => {
        setErrorMessage(null);
        try {
            const response = await listDocuments();
            setDocuments(response.items);
        } catch (error) {
            console.error("Gagal memuat dokumen:", error);
            setErrorMessage("Daftar dokumen tidak dapat dimuat. Pastikan API aktif.");
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        let active = true;
        listDocuments()
            .then((response) => {
                if (active) setDocuments(response.items);
            })
            .catch((error: unknown) => {
                console.error("Gagal memuat dokumen:", error);
                if (active) setErrorMessage("Daftar dokumen tidak dapat dimuat. Pastikan API aktif.");
            })
            .finally(() => {
                if (active) setIsLoading(false);
            });
        return () => {
            active = false;
        };
    }, []);

    const handleUpload = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        const form = event.currentTarget;
        if (!file) {
            setErrorMessage("Pilih dokumen terlebih dahulu.");
            return;
        }
        if (file.size > MAX_UPLOAD_BYTES) {
            setErrorMessage("Ukuran file maksimal 5 MB.");
            return;
        }
        setIsUploading(true);
        setErrorMessage(null);
        setSuccessMessage(null);
        try {
            await uploadDocument({
                filename: file.name,
                content_base64: encodeBase64(await file.arrayBuffer()),
                metadata: {
                    source_type: "upload",
                    category,
                    language,
                    product: "general",
                    region: "global",
                    sensitivity,
                },
            });
            setFile(null);
            form.reset();
            setSuccessMessage("Dokumen berhasil diindeks dalam mode demo.");
            await refreshDocuments();
        } catch (error) {
            console.error("Gagal mengunggah dokumen:", error);
            setErrorMessage(error instanceof Error ? error.message : "Dokumen gagal diunggah.");
        } finally {
            setIsUploading(false);
        }
    };

    const handleDelete = async (document: DocumentRecord) => {
        if (!window.confirm(`Hapus "${document.title}" dari index aktif?`)) return;
        setErrorMessage(null);
        setSuccessMessage(null);
        try {
            await deleteDocument(document.id);
            setSuccessMessage("Dokumen dihapus dari index aktif.");
            await refreshDocuments();
        } catch (error) {
            console.error("Gagal menghapus dokumen:", error);
            setErrorMessage(error instanceof Error ? error.message : "Dokumen gagal dihapus.");
        }
    };

    const handleSync = async (connector: "confluence" | "google_drive") => {
        setErrorMessage(null);
        setSuccessMessage(null);
        try {
            const result = await syncMockConnector(connector);
            setSuccessMessage(
                `Sinkronisasi ${connector} demo selesai. Dokumen baru: ${result.documents_created.length}.`,
            );
            await refreshDocuments();
        } catch (error) {
            console.error("Gagal sinkronisasi mock:", error);
            setErrorMessage(error instanceof Error ? error.message : "Sinkronisasi gagal.");
        }
    };

    const handleTestQuery = async (documentId: string) => {
        if (testQuery.trim().length < 2) {
            setErrorMessage("Masukkan pertanyaan minimal 2 karakter untuk menguji dokumen.");
            return;
        }
        setErrorMessage(null);
        setTestDocumentId(documentId);
        try {
            const result = await testDocumentQuery(documentId, testQuery.trim());
            setTestResults(result.results);
        } catch (error) {
            console.error("Gagal menguji query dokumen:", error);
            setErrorMessage(error instanceof Error ? error.message : "Query test gagal.");
            setTestResults([]);
        }
    };

    return (
        <div className="mx-auto max-w-6xl space-y-6 p-6 md:p-8">
            <header>
                <h1 className="text-2xl font-bold text-mc-dark">Knowledge Base</h1>
                <p className="mt-1 text-sm text-mc-dark/70">
                    Kelola dokumen sintetis dan uji retrieval. Tidak ada konektor eksternal aktif.
                </p>
            </header>

            {errorMessage && <p className="rounded-lg bg-error/10 p-3 text-sm text-error" role="alert">{errorMessage}</p>}
            {successMessage && <p className="rounded-lg bg-success/10 p-3 text-sm text-success" role="status">{successMessage}</p>}

            <Card>
                <h2 className="mb-4 text-lg font-semibold">Tambah dokumen</h2>
                <form className="grid gap-4 md:grid-cols-2" onSubmit={handleUpload}>
                    <label className="space-y-1 text-sm">
                        <span>File (PDF, DOCX, HTML, Markdown, CSV, TXT; maks. 5 MB)</span>
                        <input
                            type="file"
                            accept=".pdf,.docx,.html,.htm,.md,.markdown,.csv,.txt"
                            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
                            className="block w-full rounded-lg border border-mc-soft p-2"
                            required
                        />
                    </label>
                    <label className="space-y-1 text-sm">
                        <span>Kategori</span>
                        <input
                            value={category}
                            onChange={(event) => setCategory(event.target.value)}
                            maxLength={80}
                            className="w-full rounded-lg border border-mc-soft p-2"
                        />
                    </label>
                    <label className="space-y-1 text-sm">
                        <span>Bahasa dokumen</span>
                        <select
                            value={language}
                            onChange={(event) => setLanguage(event.target.value as "id" | "en")}
                            className="w-full rounded-lg border border-mc-soft p-2"
                        >
                            <option value="id">Bahasa Indonesia</option>
                            <option value="en">English</option>
                        </select>
                    </label>
                    <label className="space-y-1 text-sm">
                        <span>Sensitivitas</span>
                        <select
                            value={sensitivity}
                            onChange={(event) =>
                                setSensitivity(event.target.value as "public" | "internal" | "restricted")
                            }
                            className="w-full rounded-lg border border-mc-soft p-2"
                        >
                            <option value="public">Publik (dapat dipakai chatbot)</option>
                            <option value="internal">Internal</option>
                            <option value="restricted">Terbatas</option>
                        </select>
                    </label>
                    <div className="md:col-span-2">
                        <Button type="submit" variant="primary" disabled={isUploading || !file}>
                            {isUploading ? "Memproses..." : "Unggah & indeks"}
                        </Button>
                    </div>
                </form>
            </Card>

            <Card>
                <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
                    <div>
                        <h2 className="text-lg font-semibold">Sumber demo</h2>
                        <p className="text-sm text-mc-dark/70">Fixture Confluence dan Google Drive sintetis.</p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        <Button variant="outline" size="sm" onClick={() => void handleSync("confluence")}>
                            Sinkronisasi Confluence demo
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => void handleSync("google_drive")}>
                            Sinkronisasi Drive demo
                        </Button>
                    </div>
                </div>

                {isLoading ? (
                    <p role="status">Memuat dokumen...</p>
                ) : documents.length === 0 ? (
                    <p className="rounded-lg bg-mc-soft/60 p-4 text-sm">Belum ada dokumen di knowledge base.</p>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm">
                            <thead className="border-b border-mc-dark/10 bg-mc-soft text-mc-dark">
                                <tr>
                                    <th scope="col" className="px-3 py-3">Judul</th>
                                    <th scope="col" className="px-3 py-3">Kategori / bahasa</th>
                                    <th scope="col" className="px-3 py-3">Sensitivitas</th>
                                    <th scope="col" className="px-3 py-3">Status</th>
                                    <th scope="col" className="px-3 py-3 text-right">Aksi</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-mc-soft">
                                {documents.map((document) => (
                                    <tr key={document.id}>
                                        <td className="px-3 py-4 font-medium">{document.title}</td>
                                        <td className="px-3 py-4">{document.category} / {document.language}</td>
                                        <td className="px-3 py-4">{document.sensitivity}</td>
                                        <td className="px-3 py-4">{getStatusBadge(document.status)}</td>
                                        <td className="space-x-3 px-3 py-4 text-right">
                                            {document.status === "indexed" && (
                                                <button
                                                    type="button"
                                                    onClick={() => void handleTestQuery(document.id)}
                                                    className="font-medium text-mc-primary underline"
                                                >
                                                    Uji query
                                                </button>
                                            )}
                                            {document.status !== "deleted" && (
                                                <button
                                                    type="button"
                                                    onClick={() => void handleDelete(document)}
                                                    className="font-medium text-error underline"
                                                >
                                                    Hapus
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </Card>

            <Card>
                <h2 className="mb-3 text-lg font-semibold">Uji retrieval</h2>
                <div className="flex flex-col gap-3 sm:flex-row">
                    <label className="sr-only" htmlFor="document-test-query">Pertanyaan uji</label>
                    <input
                        id="document-test-query"
                        value={testQuery}
                        onChange={(event) => setTestQuery(event.target.value)}
                        maxLength={300}
                        placeholder="Contoh: Bagaimana cara mengajukan refund?"
                        className="min-w-0 flex-1 rounded-lg border border-mc-soft p-2"
                    />
                    <span className="self-center text-sm text-mc-dark/70">
                        Pilih “Uji query” pada baris dokumen untuk mencoba.
                    </span>
                </div>
                {testDocumentId && (
                    <div className="mt-4 space-y-3" aria-live="polite">
                        {testResults.length ? testResults.map((result) => (
                            <article key={`${result.title}-${result.score}`} className="rounded-lg bg-mc-soft/50 p-3">
                                <h3 className="font-medium">{result.title} · skor {result.score.toFixed(2)}</h3>
                                <p className="mt-1 text-sm">{result.content}</p>
                            </article>
                        )) : <p className="text-sm text-mc-dark/70">Tidak ada hasil yang cocok dari dokumen ini.</p>}
                    </div>
                )}
            </Card>
        </div>
    );
}
