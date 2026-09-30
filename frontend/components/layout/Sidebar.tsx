"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const menuItems = [
    { name: "Dashboard", path: "/admin", icon: "📊" },
    { name: "Knowledge Base", path: "/admin/knowledge", icon: "📚" },
    { name: "Conversations", path: "/admin/conversations", icon: "💬" },
    { name: "Settings", path: "/admin/settings", icon: "⚙️" },
];

export const Sidebar: React.FC = () => {
    const pathname = usePathname();

    return (
        <aside className="w-64 min-h-screen glass-panel-dark flex flex-col py-6 px-4 border-r border-mc-dark/10">
            <div className="mb-8 px-2">
                <h1 className="text-xl font-bold text-mc-dark">Enterprise RAG</h1>
                <p className="text-xs text-mc-dark/60 font-medium tracking-wide">ADMIN CONSOLE</p>
            </div>

            <nav className="flex-1 space-y-1.5">
                {menuItems.map((item) => {
                    const isActive = pathname === item.path;
                    return (
                        <Link
                            key={item.path}
                            href={item.path}
                            className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${isActive
                                ? "bg-mc-primary text-white shadow-sm"
                                : "text-mc-dark/80 hover:bg-white/40 hover:text-mc-dark"
                                }`}
                        >
                            <span className="text-base">{item.icon}</span>
                            {item.name}
                        </Link>
                    );
                })}
            </nav>

            {/* User Profile / Logout Placeholder */}
            <div className="mt-auto border-t border-mc-dark/10 pt-4 px-2">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-mc-soft flex items-center justify-center text-mc-dark text-xs font-bold">
                        AD
                    </div>
                    <div className="flex flex-col">
                        <span className="text-sm font-semibold text-mc-dark">Admin User</span>
                        <span className="text-xs text-mc-dark/60">Logout</span>
                    </div>
                </div>
            </div>
        </aside>
    );
};