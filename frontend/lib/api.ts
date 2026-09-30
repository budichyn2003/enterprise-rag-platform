// Mengambil Base URL dari environment variables (sesuai aturan keamanan README.md)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export interface ChatRequestPayload {
    session_id?: string;
    message: string;
    language?: string;
}

export interface Citation {
    document_id: string;
    title: string;
    url?: string;
}

export interface ChatResponsePayload {
    session_id: string;
    answer: string;
    citations: Citation[];
    confidence_score: number;
    needs_escalation: boolean;
}

/**
 * Mengirim pesan ke RAG Backend dan mengembalikan jawaban AI.
 */
export async function sendChatMessage(payload: ChatRequestPayload): Promise<ChatResponsePayload> {
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error("Gagal mengirim pesan chat:", error);
        throw error;
    }
}