"use client";

import React, { FormEvent, useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { searchConversations } from "@/lib/api";
import type { ConversationRecord } from "@/lib/api";

export default function ConversationsPage() {
    const [query, setQuery] = useState("");
    const [conversations, setConversations] = useState<ConversationRecord[]>([]);
    const [errorMessage, setErrorMessage] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    const loadConversations = async (search: string) => {
        setIsLoading(true);
        setErrorMessage(null);
        try {
            const response = await searchConversations(search);
            setConversations(response.items);
        } catch (error) {
            console.error("Gagal memuat transkrip:", error);
            setErrorMessage("Transkrip tidak dapat dimuat. Pastikan API lokal aktif.");
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        let active = true;
        searchConversations()
            .then((response) => {
                if (active) setConversations(response.items);
            })
            .catch((error: unknown) => {
                console.error("Gagal memuat transkrip:", error);
                if (active) setErrorMessage("Transkrip tidak dapat dimuat. Pastikan API lokal aktif.");
            })
            .finally(() => {
                if (active) setIsLoading(false);
            });
        return () => {
            active = false;
        };
    }, []);

    const handleSearch = (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        void loadConversations(query.trim());
    };

    return (
        <div className="mx-auto max-w-6xl space-y-6 p-6 md:p-8">
            <header>
                <h1 className="text-2xl font-bold text-mc-dark">Transkrip percakapan</h1>
                <p className="mt-1 text-sm text-mc-dark/70">Cari dan tinjau percakapan demo yang tersimpan.</p>
            </header>
            <Card>
                <form className="flex flex-col gap-3 sm:flex-row" onSubmit={handleSearch}>
                    <label htmlFor="transcript-search" className="sr-only">Cari isi transkrip</label>
                    <input
                        id="transcript-search"
                        value={query}
                        onChange={(event) => setQuery(event.target.value)}
                        maxLength={120}
                        placeholder="Cari kata atau pertanyaan..."
                        className="min-w-0 flex-1 rounded-lg border border-mc-soft px-3 py-2"
                    />
                    <button type="submit" className="rounded-lg bg-mc-primary px-4 py-2 font-medium text-white">
                        Cari
                    </button>
                </form>
            </Card>
            {errorMessage && <p className="rounded-lg bg-error/10 p-3 text-sm text-error" role="alert">{errorMessage}</p>}
            {isLoading ? <p role="status">Memuat transkrip...</p> : conversations.length === 0 ? (
                <Card><p className="text-sm text-mc-dark/70">Tidak ada percakapan yang cocok.</p></Card>
            ) : conversations.map((conversation) => (
                <Card key={conversation.session_id}>
                    <details>
                        <summary className="cursor-pointer font-semibold">
                            {conversation.status} · {conversation.language} ·{" "}
                            {new Date(conversation.updated_at).toLocaleString("id-ID")}
                        </summary>
                        <ol className="mt-4 space-y-3">
                            {conversation.messages.map((message) => (
                                <li key={message.id} className="rounded-lg bg-mc-soft/40 p-3">
                                    <div className="flex flex-wrap justify-between gap-2 text-xs font-semibold uppercase text-mc-dark/60">
                                        <span>{message.role}</span>
                                        {message.confidence_score !== null && (
                                            <span>Confidence {message.confidence_score.toFixed(2)}</span>
                                        )}
                                    </div>
                                    <p className="mt-1 whitespace-pre-wrap text-sm">{message.content}</p>
                                    {message.citations.length > 0 && (
                                        <p className="mt-2 text-xs">Sumber: {message.citations.map((item) => item.title).join(", ")}</p>
                                    )}
                                </li>
                            ))}
                        </ol>
                    </details>
                </Card>
            ))}
        </div>
    );
}
