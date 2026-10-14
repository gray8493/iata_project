import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AITA - Hệ Thống Chấm Điểm AI | FPT University",
  description: "Web Admin Portal dành cho cán bộ quản lý hệ thống AITA",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi">
      <body className="antialiased selection:bg-orange-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}
