// Mengambil URL backend dari environment variable
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface RequestOptions extends RequestInit {
    params?: Record<string, string>; // Untuk query parameters seperti ?q=keyword
}

export async function fetchAPI<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const { params, headers, ...customConfig } = options;

    // Formatting URL dengan query parameters jika ada
    const queryString = params ? `?${new URLSearchParams(params).toString()}` : "";
    const url = `${API_BASE_URL}${endpoint}${queryString}`;

    // Konfigurasi default headers
    const config: RequestInit = {
        ...customConfig,
        headers: {
            "Content-Type": "application/json",
            ...headers,
        },
    };

    try {
        const response = await fetch(url, config);

        // Menangani error dari backend FastAPI yang sudah kita standarkan tadi
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `API request failed with status ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error(`[API Error] ${endpoint}:`, error);
        throw error;
    }
}