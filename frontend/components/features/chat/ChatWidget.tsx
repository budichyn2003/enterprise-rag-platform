"use client";

import React, { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { sendChatMessage } from "@/lib/api";

interface Message {
    role: "user" | "ai";
    content: string;
    citations?: { title: string; url?: string }[];
}

export const ChatWidget: React.FC = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [input, setInput] = useState("");
    const [messages, setMessages] = useState<Message[]>([
        { role: "ai", content: "Halo! Ada yang bisa saya bantu hari ini?" }
    ]);
    const [isLoading, setIsLoading] = useState(false);

    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll ke bawah saat pesan bertambah atau sedang loading
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, isLoading]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage = input.trim();
        setInput("");
        setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
        setIsLoading(true);

        try {
            // Memanggil API backend
            const response = await sendChatMessage({ message: userMessage });
            setMessages((prev) => [
                ...prev,
                {
                    role: "ai",
                    content: response.answer,
                    citations: response.citations
                }
            ]);
        } catch (error) {
            setMessages((prev) => [
                ...prev,
                { role: "ai", content: "Maaf, terjadi kesalahan komunikasi dengan server." }
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter") {
            handleSend();
        }
    };

    if (!isOpen) {
        return (
            <button
                onClick={() => setIsOpen(true)}
                className="fixed bottom-6 right-6 h-14 w-14 rounded-full bg-mc-primary text-white shadow-lg transition-transform hover:scale-105 flex items-center justify-center z-50"
                aria-label="Open Chat"
            >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" /></svg>
            </button>
        );
    }

    return (
        <div className="fixed bottom-6 right-6 w-full max-w-sm sm:max-w-md h-[500px] max-h-[80vh] glass-panel-strong rounded-xl flex flex-col shadow-2xl z-50 overflow-hidden transition-all">
            {/* Header */}
            <div className="flex items-center justify-between border-b border-white/20 bg-mc-dark/5 p-4 backdrop-blur-md">
                <div>
                    <h3 className="font-semibold text-mc-dark">Support Assistant</h3>
                    <p className="text-xs text-mc-dark/70">Powered by Enterprise RAG</p>
                </div>
                <button onClick={() => setIsOpen(false)} className="text-mc-dark hover:text-mc-primary transition-colors">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                </button>
            </div>

            {/* Conversation Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}>
                        <div className={`text-sm px-4 py-2 max-w-[85%] inline-block ${msg.role === "user"
                            ? "bg-mc-primary/10 border border-mc-primary/20 text-mc-dark rounded-2xl rounded-tr-none"
                            : "glass-panel text-mc-dark rounded-2xl rounded-tl-none"
                            }`}>
                            {msg.content}

                            {/* Render Citations if any */}
                            {msg.citations && msg.citations.length > 0 && (
                                <div className="mt-2 pt-2 border-t border-mc-dark/10 flex flex-wrap gap-1">
                                    {msg.citations.map((cite, cIdx) => (
                                        <span key={cIdx} className="rounded-full bg-mc-soft px-2 py-0.5 text-[10px] font-medium text-mc-dark">
                                            📄 {cite.title}
                                        </span>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {/* Loading State Skeleton */}
                {isLoading && (
                    <div className="flex flex-col items-start">
                        <div className="glass-panel px-4 py-3 rounded-2xl rounded-tl-none max-w-[85%] flex gap-1 items-center">
                            <div className="w-2 h-2 rounded-full bg-mc-dark/40 animate-pulse"></div>
                            <div className="w-2 h-2 rounded-full bg-mc-dark/40 animate-pulse delay-75"></div>
                            <div className="w-2 h-2 rounded-full bg-mc-dark/40 animate-pulse delay-150"></div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Prompt Input */}
            <div className="p-3 bg-white/40 border-t border-white/50 backdrop-blur-md">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        disabled={isLoading}
                        placeholder="Ketik pertanyaan Anda..."
                        className="flex-1 rounded-lg border border-mc-soft bg-white/60 px-4 py-2 text-sm text-mc-dark outline-none transition focus:border-mc-primary focus:ring-2 focus:ring-mc-primary/20 disabled:opacity-50"
                    />
                    <Button
                        variant="primary"
                        size="sm"
                        className="px-4"
                        onClick={handleSend}
                        disabled={isLoading || !input.trim()}
                    >
                        Kirim
                    </Button>
                </div>
            </div>
        </div>
    );
};