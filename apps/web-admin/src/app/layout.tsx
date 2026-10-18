import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin", "vietnamese"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "AITA - Hệ Thống Chấm Điểm AI | FPT University",
  description: "Web Admin Portal dành cho cán bộ quản lý hệ thống AITA",
  icons: {
    icon: "/aita-avatar.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi" className={inter.variable}>
        <body className="font-sans antialiased text-slate-800 bg-slate-50 selection:bg-primary selection:text-white">
        {children}
      </body>
    </html>
  );
}
