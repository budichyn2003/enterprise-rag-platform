import type { Config } from "tailwindcss";

const config: Config = {
    content: [
        "./pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./components/**/*.{js,ts,jsx,tsx,mdx}",
        "./app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                mc: {
                    base: "#FFFFFC",
                    soft: "#DFE7F7",
                    primary: "#234CF9",
                    dark: "#1C277B",
                },
                success: "#16A34A",
                warning: "#F59E0B",
                error: "#EF4444",
                info: "#2563EB",
            },
            fontFamily: {
                sans: ["var(--font-jakarta)", "sans-serif"],
            },
        },
    },
    plugins: [],
};
export default config;