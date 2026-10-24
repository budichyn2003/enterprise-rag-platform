const API_BASE_URL = (
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"
).replace(/\/+$/, "");
const MOCK_ROLE =
    process.env.NEXT_PUBLIC_MOCK_ROLE ||
    (process.env.NODE_ENV === "development" ? "admin" : undefined);

export interface ChatRequestPayload {
    session_id?: string;
    message: string;
    language?: "id" | "en";
    product?: string;
    region?: string;
}

export interface Citation {
    document_id: string;
    title: string;
    url?: string | null;
}

export interface ChatResponsePayload {
    session_id: string;
    message_id?: string | null;
    answer: string;
    citations: Citation[];
    confidence_score: number;
    needs_escalation: boolean;
    handoff_id?: string | null;
}

export interface DocumentRecord {
    id: string;
    title: string;
    source_type: string;
    status: "queued" | "processing" | "indexed" | "failed" | "deleted";
    category: string;
    language: "id" | "en";
    product: string;
    region: string;
    sensitivity: "public" | "internal" | "restricted";
    source_url?: string | null;
    created_at: string;
    updated_at: string;
}

export interface DocumentUploadPayload {
    filename: string;
    content_base64: string;
    metadata: {
        source_type: "upload";
        category: string;
        language: "id" | "en";
        product: string;
        region: string;
        sensitivity: "public" | "internal" | "restricted";
    };
}

export interface AnalyticsOverview {
    conversations: number;
    containment_rate: number;
    escalated_conversations: number;
    resolved_conversations: number;
    average_csat: number;
    average_handling_time_seconds: number;
    indexed_documents: number;
    messages: number;
    conversation_status: Record<string, number>;
    mode: "local_mock";
}

export interface ChatMessageRecord {
    id: string;
    role: "user" | "ai" | "agent";
    content: string;
    confidence_score: number | null;
    citations: Citation[];
    needs_escalation: boolean;
    created_at: string;
}

export interface ConversationRecord {
    session_id: string;
    status: string;
    language: string;
    updated_at: string;
    messages: ChatMessageRecord[];
}

export interface BotConfiguration {
    confidence_threshold: number;
    max_context_chunks: number;
    allowed_topics: string[];
}

export class ApiError extends Error {
    constructor(
        message: string,
        public readonly status: number,
    ) {
        super(message);
        this.name = "ApiError";
    }
}

async function apiRequest<T>(
    path: string,
    init: RequestInit = {},
): Promise<T> {
    const headers = new Headers(init.headers);
    if (!headers.has("Content-Type") && init.body) {
        headers.set("Content-Type", "application/json");
    }
    if (MOCK_ROLE) {
        headers.set("X-Mock-Role", MOCK_ROLE);
    }

    const response = await fetch(`${API_BASE_URL}${path}`, {
        ...init,
        headers,
        cache: "no-store",
        credentials: "omit",
    });
    if (!response.ok) {
        let message = `API error: ${response.status}`;
        try {
            const body = (await response.json()) as { detail?: string; message?: string };
            message = body.detail || body.message || message;
        } catch {
            message = `API error: ${response.status}`;
        }
        throw new ApiError(message, response.status);
    }
    return (await response.json()) as T;
}

export function sendChatMessage(payload: ChatRequestPayload): Promise<ChatResponsePayload> {
    return apiRequest<ChatResponsePayload>("/chat", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

export function submitChatFeedback(
    sessionId: string,
    messageId: string,
    rating: number,
): Promise<{ status: string }> {
    return apiRequest(`/chat/${encodeURIComponent(sessionId)}/feedback`, {
        method: "POST",
        body: JSON.stringify({ message_id: messageId, rating }),
    });
}

export function requestHumanHandoff(
    sessionId: string,
): Promise<{ handoff_id: string; status: string; estimated_wait_minutes: number; message: string }> {
    return apiRequest(`/chat/${encodeURIComponent(sessionId)}/handoff`, {
        method: "POST",
        body: JSON.stringify({ reason: "customer_requested" }),
    });
}

export function resolveConversation(sessionId: string): Promise<{ status: string }> {
    return apiRequest(`/chat/${encodeURIComponent(sessionId)}/resolve`, {
        method: "POST",
    });
}

export function deleteConversationData(sessionId: string): Promise<{ status: string }> {
    return apiRequest(`/chat/${encodeURIComponent(sessionId)}`, {
        method: "DELETE",
    });
}

export function listDocuments(): Promise<{
    items: DocumentRecord[];
    total: number;
    limit: number;
    offset: number;
}> {
    return apiRequest("/documents");
}

export function uploadDocument(payload: DocumentUploadPayload): Promise<{
    document_id: string;
    status: string;
    chunks_processed: number;
    message: string;
}> {
    return apiRequest("/documents/upload", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

export function deleteDocument(documentId: string): Promise<{ status: string }> {
    return apiRequest(`/documents/${encodeURIComponent(documentId)}`, {
        method: "DELETE",
    });
}

export function syncMockConnector(
    connector: "confluence" | "google_drive",
): Promise<{ connector: string; mode: string; documents_created: string[] }> {
    return apiRequest(`/documents/sync/${connector}`, { method: "POST" });
}

export function testDocumentQuery(
    documentId: string,
    query: string,
): Promise<{ query: string; results: Array<{ title: string; score: number; content: string }> }> {
    return apiRequest(
        `/documents/${encodeURIComponent(documentId)}/test?q=${encodeURIComponent(query)}`,
    );
}

export function getAnalyticsOverview(): Promise<AnalyticsOverview> {
    return apiRequest("/analytics/overview");
}

export function getKnowledgeGaps(): Promise<Array<{ question: string; occurrences: number }>> {
    return apiRequest("/analytics/knowledge-gaps");
}

export async function downloadAnalyticsCsv(): Promise<Blob> {
    const headers = new Headers();
    if (MOCK_ROLE) headers.set("X-Mock-Role", MOCK_ROLE);
    const response = await fetch(`${API_BASE_URL}/analytics/export.csv`, {
        headers,
        cache: "no-store",
        credentials: "omit",
    });
    if (!response.ok) throw new ApiError(`API error: ${response.status}`, response.status);
    return response.blob();
}

export function searchConversations(q = ""): Promise<{
    items: ConversationRecord[];
    total: number;
}> {
    const query = q ? `?q=${encodeURIComponent(q)}` : "";
    return apiRequest(`/analytics/conversations${query}`);
}

export function getBotConfiguration(): Promise<BotConfiguration> {
    return apiRequest("/admin/config");
}

export function saveBotConfiguration(
    config: BotConfiguration,
): Promise<BotConfiguration> {
    return apiRequest("/admin/config", {
        method: "PUT",
        body: JSON.stringify(config),
    });
}

export function getAuditLogs(): Promise<
    Array<{
        id: string;
        actor_role: string;
        action: string;
        resource_type: string;
        resource_id: string | null;
        created_at: string;
    }>
> {
    return apiRequest("/admin/audit");
}
