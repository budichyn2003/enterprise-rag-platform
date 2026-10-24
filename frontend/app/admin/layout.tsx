import React from "react";
import { Sidebar } from "@/components/layout/Sidebar";

export default function AdminLayout({ children }: Readonly<{ children: React.ReactNode }>) {
    return (
        <div className="min-h-screen md:flex">
            <Sidebar />
            <main className="min-w-0 flex-1">{children}</main>
        </div>
    );
}
