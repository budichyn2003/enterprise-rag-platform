"use client";

import React, { FormEvent, useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { getAuditLogs, getBotConfiguration, saveBotConfiguration } from "@/lib/api";
import type { BotConfiguration } from "@/lib/api";

type AuditEntry = Awaited<ReturnType<typeof getAuditLogs>>[number];

const DEFAULT_CONFIG: BotConfiguration = {
    confidence_threshold: 0.35,
    max_context_chunks: 4,
    allowed_topics: ["returns", "shipping", "support", "accounts", "billing"],
};

export default function AdminSettingsPage() {
    const [configuration, setConfiguration] = useState<BotConfiguration>(DEFAULT_CONFIG);
    const [topics, setTopics] = useState(DEFAULT_CONFIG.allowed_topics.join(", "));
    const [auditLogs, setAuditLogs] = useState<AuditEntry[]>([]);
    const [message, setMessage] = useState<string | null>(null);
    const [errorMessage, setErrorMessage] = useState<string | null>(null);
    const [isSaving, setIsSaving] = useState(false);

    useEffect(() => {
        Promise.all([getBotConfiguration(), getAuditLogs()])
            .then(([config, logs]) => {
                setConfiguration(config);
                setTopics(config.allowed_topics.join(", "));
                setAuditLogs(logs);
            })
            .catch((error: unknown) => {
                console.error("Gagal memuat pengaturan:", error);
                setErrorMessage("Pengaturan atau audit log tidak dapat dimuat.");
            });
    }, []);

    const handleSave = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setIsSaving(true);
        setMessage(null);
        setErrorMessage(null);
        try {
            const saved = await saveBotConfiguration({
                ...configuration,
                allowed_topics: topics.split(",").map((topic) => topic.trim()).filter(Boolean),
            });
            setConfiguration(saved);
            setTopics(saved.allowed_topics.join(", "));
            setMessage("Konfigurasi demo berhasil disimpan dan dicatat di audit log.");
            setAuditLogs(await getAuditLogs());
        } catch (error) {
            console.error("Gagal menyimpan konfigurasi:", error);
            setErrorMessage(error instanceof Error ? error.message : "Konfigurasi gagal disimpan.");
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <div className="mx-auto max-w-5xl space-y-6 p-6 md:p-8">
            <header>
                <h1 className="text-2xl font-bold text-mc-dark">Konfigurasi & audit</h1>
                <p className="mt-1 text-sm text-mc-dark/70">Pengaturan tersimpan hanya pada database demo lokal.</p>
            </header>
            {message && <p className="rounded-lg bg-success/10 p-3 text-sm text-success" role="status">{message}</p>}
            {errorMessage && <p className="rounded-lg bg-error/10 p-3 text-sm text-error" role="alert">{errorMessage}</p>}
            <Card>
                <form className="space-y-4" onSubmit={handleSave}>
                    <label className="block space-y-1 text-sm">
                        <span>Ambang confidence untuk eskalasi ({configuration.confidence_threshold.toFixed(2)})</span>
                        <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.05"
                            value={configuration.confidence_threshold}
                            onChange={(event) =>
                                setConfiguration({ ...configuration, confidence_threshold: Number(event.target.value) })
                            }
                            className="w-full"
                        />
                    </label>
                    <label className="block space-y-1 text-sm">
                        <span>Maksimum sumber konteks</span>
                        <input
                            type="number"
                            min={1}
                            max={10}
                            value={configuration.max_context_chunks}
                            onChange={(event) =>
                                setConfiguration({ ...configuration, max_context_chunks: Number(event.target.value) })
                            }
                            className="w-full rounded-lg border border-mc-soft p-2"
                        />
                    </label>
                    <label className="block space-y-1 text-sm">
                        <span>Kategori knowledge yang boleh digunakan chatbot (dipisahkan koma)</span>
                        <input
                            value={topics}
                            onChange={(event) => setTopics(event.target.value)}
                            maxLength={500}
                            className="w-full rounded-lg border border-mc-soft p-2"
                        />
                    </label>
                    <button
                        type="submit"
                        disabled={isSaving}
                        className="rounded-lg bg-mc-primary px-4 py-2 font-medium text-white disabled:opacity-50"
                    >
                        {isSaving ? "Menyimpan..." : "Simpan konfigurasi demo"}
                    </button>
                </form>
            </Card>
            <Card>
                <h2 className="mb-4 text-lg font-semibold">Audit log administratif</h2>
                {auditLogs.length === 0 ? (
                    <p className="text-sm text-mc-dark/70">Belum ada aksi administratif.</p>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm">
                            <thead>
                                <tr className="border-b border-mc-soft">
                                    <th scope="col" className="px-2 py-2">Waktu</th>
                                    <th scope="col" className="px-2 py-2">Role</th>
                                    <th scope="col" className="px-2 py-2">Aksi</th>
                                    <th scope="col" className="px-2 py-2">Resource</th>
                                </tr>
                            </thead>
                            <tbody>
                                {auditLogs.map((entry) => (
                                    <tr key={entry.id} className="border-b border-mc-soft/60">
                                        <td className="px-2 py-2">{new Date(entry.created_at).toLocaleString("id-ID")}</td>
                                        <td className="px-2 py-2">{entry.actor_role}</td>
                                        <td className="px-2 py-2">{entry.action}</td>
                                        <td className="px-2 py-2">{entry.resource_type} {entry.resource_id || ""}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </Card>
        </div>
    );
}
