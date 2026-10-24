"use client";

import React, { useEffect, useRef, useState } from "react";
import {
    ApiError,
    deleteConversationData,
    requestHumanHandoff,
    resolveConversation,
    sendChatMessage,
    submitChatFeedback,
} from "@/lib/api";
import type { Citation, ChatResponsePayload } from "@/lib/api";
import { Button } from "@/components/ui/button";

interface Message {
    id: string;
    role: "user" | "ai";
    content: string;
    citations?: Citation[];
    messageId?: string | null;
    needsEscalation?: boolean;
}

function safeCitationUrl(url: string | null | undefined): string | undefined {
    if (!url) return undefined;
    try {
        const parsed = new URL(url);
        return parsed.protocol === "https:" || parsed.protocol === "http:" ? parsed.href : undefined;
    } catch {
        return undefined;
    }
}

export const ChatWidget: React.FC = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [input, setInput] = useState("");
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [messages, setMessages] = useState<Message[]>([
        {
            id: "welcome",
            role: "ai",
            content: "Halo! Silakan tanyakan informasi produk atau bantuan.",
        },
    ]);
    const [isLoading, setIsLoading] = useState(false);
    const [busyMessageId, setBusyMessageId] = useState<string | null>(null);
    const [ratedMessageIds, setRatedMessageIds] = useState<Set<string>>(new Set());
    const [errorMessage, setErrorMessage] = useState<string | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const openChat = () => setIsOpen(true);
        window.addEventListener("enterprise-rag:open-chat", openChat);
        return () => window.removeEventListener("enterprise-rag:open-chat", openChat);
    }, []);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, isLoading]);

    const appendResponse = (response: ChatResponsePayload) => {
        setSessionId(response.session_id);
        setMessages((previous) => [
            ...previous,
            {
                id: response.message_id || crypto.randomUUID(),
                role: "ai",
                content: response.answer,
                citations: response.citations,
                messageId: response.message_id,
                needsEscalation: response.needs_escalation,
            },
        ]);
    };

    const handleSend = async () => {
        const message = input.trim();
        if (!message || isLoading) return;
        setInput("");
        setErrorMessage(null);
        setMessages((previous) => [
            ...previous,
            { id: crypto.randomUUID(), role: "user", content: message },
        ]);
        setIsLoading(true);
        try {
            let response: ChatResponsePayload;
            try {
                response = await sendChatMessage({
                    session_id: sessionId || undefined,
                    message,
                    language: "id",
                });
            } catch (error) {
                if (!(error instanceof ApiError) || error.status !== 404 || !sessionId) {
                    throw error;
                }
                setSessionId(null);
                response = await sendChatMessage({ message, language: "id" });
            }
            appendResponse(response);
        } catch (error) {
            console.error("Gagal mengirim pesan chat:", error);
            setErrorMessage("Pesan belum terkirim. Periksa koneksi server lalu coba lagi.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleFeedback = async (message: Message, rating: number) => {
        const messageId = message.messageId;
        if (!sessionId || !messageId) return;
        setBusyMessageId(messageId);
        setErrorMessage(null);
        try {
            await submitChatFeedback(sessionId, messageId, rating);
            setRatedMessageIds((previous) => new Set(previous).add(messageId));
        } catch (error) {
            console.error("Gagal menyimpan feedback:", error);
            setErrorMessage("Feedback belum tersimpan. Silakan coba lagi.");
        } finally {
            setBusyMessageId(null);
        }
    };

    const handleHandoff = async () => {
        if (!sessionId || isLoading) return;
        setIsLoading(true);
        setErrorMessage(null);
        try {
            const result = await requestHumanHandoff(sessionId);
            setMessages((previous) => [
                ...previous,
                {
                    id: result.handoff_id,
                    role: "ai",
                    content: `${result.message} Estimasi waktu tunggu: sekitar ${result.estimated_wait_minutes} menit.`,
                    needsEscalation: true,
                },
            ]);
        } catch (error) {
            console.error("Gagal meminta bantuan agent:", error);
            setErrorMessage("Permintaan agent belum terkirim. Silakan coba lagi.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleResolve = async () => {
        if (!sessionId || isLoading) return;
        setIsLoading(true);
        setErrorMessage(null);
        try {
            await resolveConversation(sessionId);
            setMessages((previous) => [
                ...previous,
                {
                    id: crypto.randomUUID(),
                    role: "ai",
                    content: "Percakapan ditandai selesai. Terima kasih telah menghubungi kami.",
                },
            ]);
        } catch (error) {
            console.error("Gagal menutup percakapan:", error);
            setErrorMessage("Percakapan belum dapat ditutup. Silakan coba lagi.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleDeleteSession = async () => {
        if (!sessionId || isLoading) return;
        if (!window.confirm("Hapus riwayat percakapan dan feedback sesi ini secara permanen?")) return;
        setIsLoading(true);
        setErrorMessage(null);
        try {
            await deleteConversationData(sessionId);
            setSessionId(null);
            setMessages([
                {
                    id: "welcome",
                    role: "ai",
                    content: "Riwayat sesi demo telah dihapus. Silakan mulai percakapan baru.",
                },
            ]);
        } catch (error) {
            console.error("Gagal menghapus percakapan:", error);
            setErrorMessage("Data sesi belum dapat dihapus. Silakan coba lagi.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            void handleSend();
        }
    };

    if (!isOpen) {
        return (
            <button
                type="button"
                onClick={() => setIsOpen(true)}
                className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-mc-primary text-white shadow-lg transition-transform hover:scale-105 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-mc-dark"
                aria-label="Buka chat support"
            >
                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
            </button>
        );
    }

    return (
        <section
            className="glass-panel-strong fixed bottom-6 right-4 z-50 flex h-[min(600px,80vh)] w-[calc(100vw-2rem)] max-w-md flex-col overflow-hidden rounded-xl shadow-2xl sm:right-6"
            aria-label="Chat support"
        >
            <header className="flex items-center justify-between border-b border-white/20 bg-mc-dark/5 p-4 backdrop-blur-md">
                <div>
                    <h2 className="font-semibold text-mc-dark">Support Assistant</h2>
                    <p className="text-xs text-mc-dark/70">Mode demo dengan data sintetis</p>
                </div>
                <button
                    type="button"
                    onClick={() => setIsOpen(false)}
                    className="rounded p-2 text-mc-dark hover:text-mc-primary focus-visible:outline-2 focus-visible:outline-mc-primary"
                    aria-label="Tutup chat"
                >
                    <span aria-hidden="true">×</span>
                </button>
            </header>

            <div className="flex-1 space-y-4 overflow-y-auto p-4" aria-live="polite">
                {messages.map((message) => (
                    <article
                        key={message.id}
                        className={`flex flex-col ${message.role === "user" ? "items-end" : "items-start"}`}
                    >
                        <div
                            className={`max-w-[88%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm ${
                                message.role === "user"
                                    ? "rounded-tr-none border border-mc-primary/20 bg-mc-primary/10 text-mc-dark"
                                    : "glass-panel rounded-tl-none text-mc-dark"
                            }`}
                        >
                            {message.content}
                            {message.citations && message.citations.length > 0 && (
                                <div className="mt-3 flex flex-wrap gap-2 border-t border-mc-dark/10 pt-2">
                                    {message.citations.map((citation) => {
                                        const url = safeCitationUrl(citation.url);
                                        return url ? (
                                            <a
                                                key={citation.document_id}
                                                href={url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="rounded-full bg-mc-soft px-2 py-1 text-xs font-medium text-mc-dark underline"
                                            >
                                                {citation.title}
                                            </a>
                                        ) : (
                                            <span
                                                key={citation.document_id}
                                                className="rounded-full bg-mc-soft px-2 py-1 text-xs font-medium text-mc-dark"
                                            >
                                                {citation.title}
                                            </span>
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                        {message.role === "ai" && message.messageId && (
                            <div className="mt-1 flex gap-2 text-xs text-mc-dark/70">
                                <button
                                    type="button"
                                    onClick={() => void handleFeedback(message, 5)}
                                    disabled={busyMessageId === message.messageId || ratedMessageIds.has(message.messageId)}
                                    className="rounded px-2 py-1 underline hover:text-mc-primary disabled:opacity-50"
                                    aria-label="Jawaban membantu"
                                >
                                    Membantu
                                </button>
                                <button
                                    type="button"
                                    onClick={() => void handleFeedback(message, 1)}
                                    disabled={busyMessageId === message.messageId || ratedMessageIds.has(message.messageId)}
                                    className="rounded px-2 py-1 underline hover:text-mc-primary disabled:opacity-50"
                                    aria-label="Jawaban tidak membantu"
                                >
                                    Tidak membantu
                                </button>
                            </div>
                        )}
                        {message.role === "ai" && message.messageId && ratedMessageIds.has(message.messageId) && (
                            <p className="mt-1 text-xs text-mc-dark/60" role="status">Terima kasih atas feedback Anda.</p>
                        )}
                    </article>
                ))}
                {isLoading && <p className="text-sm text-mc-dark/60" role="status">Sedang mencari jawaban...</p>}
                {errorMessage && <p className="text-sm text-error" role="alert">{errorMessage}</p>}
                <div ref={messagesEndRef} />
            </div>

            <footer className="space-y-2 border-t border-white/50 bg-white/40 p-3 backdrop-blur-md">
                {sessionId && (
                    <div className="flex flex-wrap gap-x-4 gap-y-1">
                        <button
                            type="button"
                            onClick={() => void handleHandoff()}
                            disabled={isLoading}
                            className="text-xs font-medium text-mc-primary underline disabled:opacity-50"
                        >
                            Hubungi agent manusia
                        </button>
                        <button
                            type="button"
                            onClick={() => void handleResolve()}
                            disabled={isLoading}
                            className="text-xs font-medium text-mc-dark underline disabled:opacity-50"
                        >
                            Tandai selesai
                        </button>
                        <button
                            type="button"
                            onClick={() => void handleDeleteSession()}
                            disabled={isLoading}
                            className="text-xs font-medium text-error underline disabled:opacity-50"
                        >
                            Hapus data sesi
                        </button>
                    </div>
                )}
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(event) => setInput(event.target.value)}
                        onKeyDown={handleKeyDown}
                        disabled={isLoading}
                        maxLength={4_000}
                        aria-label="Pertanyaan untuk support"
                        placeholder="Ketik pertanyaan Anda..."
                        className="min-w-0 flex-1 rounded-lg border border-mc-soft bg-white/70 px-4 py-2 text-sm text-mc-dark outline-none transition focus:border-mc-primary focus:ring-2 focus:ring-mc-primary/20 disabled:opacity-50"
                    />
                    <Button
                        variant="primary"
                        size="sm"
                        className="px-4"
                        onClick={() => void handleSend()}
                        disabled={isLoading || !input.trim()}
                    >
                        Kirim
                    </Button>
                </div>
            </footer>
        </section>
    );
};
