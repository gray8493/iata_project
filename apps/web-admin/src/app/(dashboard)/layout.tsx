"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

interface UserProfile {
  id?: string | number;
  username: string;
  fullName?: string;
  email?: string;
  role: string;
}

const ROLE_LABELS: Record<string, string> = {
  ADMIN: "Quản trị viên",
  INSTRUCTOR: "Giảng viên",
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [user, setUser] = useState<UserProfile>({
    username: "Nguyễn Hoàng Đức",
    email: "admin@aita.edu.vn",
    role: "ADMIN",
  });

  // Fetch current user from Backend or LocalStorage
  useEffect(() => {
    const storedUser = localStorage.getItem("aita_user");
    if (storedUser) {
      try {
        const parsed = JSON.parse(storedUser);
        setUser((prev) => ({
          ...prev,
          username: parsed.fullName || parsed.username || prev.username,
          email: parsed.email || prev.email,
          role: parsed.role || prev.role,
        }));
      } catch (e) {
        console.error("Lỗi đọc dữ liệu người dùng từ cache", e);
      }
    }

    const token = localStorage.getItem("aita_access_token");
    if (token) {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000/api/v1";
      fetch(`${apiUrl}/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
        .then((res) => (res.ok ? res.json() : null))
        .then((data) => {
          if (data?.success && data?.data) {
            const fetched = data.data;
            setUser({
              id: fetched.id,
              username: fetched.fullName || fetched.username || "Nguyễn Hoàng Đức",
              email: fetched.email || "admin@aita.edu.vn",
              role: fetched.role || "ADMIN",
            });
            localStorage.setItem("aita_user", JSON.stringify(fetched));
          }
        })
        .catch(() => {
          // Giữ fallback an toàn
        });
    }
  }, []);

  // Đóng mobile menu khi chuyển trang
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [pathname]);

  const handleLogout = () => {
    localStorage.removeItem("aita_access_token");
    localStorage.removeItem("aita_user");
    router.push("/login");
  };

  const menuItems = [
    {
      title: "Tổng quan",
      href: "/dashboard",
    },
    {
      title: "Quản lý giảng viên",
      href: "/users",
    },
    {
      title: "Giám sát hạn ngạch AI",
      href: "/ai-quota",
    },
    {
      title: "Báo cáo & kiểm toán",
      href: "/reports",
    },
  ];

  const firstLetter = (user.username || "A").charAt(0).toUpperCase();
  const roleLabel = ROLE_LABELS[user.role] || user.role;

  const renderNavLinks = () => (
    <nav className="space-y-1">
      {menuItems.map((item) => {
        const isActive =
          pathname === item.href ||
          (item.href !== "/dashboard" && pathname?.startsWith(item.href));

        return (
          <Link
            key={item.href}
            href={item.href}
            className={`flex items-center px-3 h-10 rounded-lg text-sm transition-colors min-h-[40px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary ${
              isActive
                ? "bg-primary-bg text-primary font-semibold"
                : "text-slate-600 hover:bg-slate-50 hover:text-slate-900 font-medium"
            }`}
          >
            <span>{item.title}</span>
          </Link>
        );
      })}
    </nav>
  );

  return (
    <div className="min-h-screen bg-slate-50 flex text-slate-800 font-sans">
      {/* ================= DESKTOP SIDEBAR ================= */}
      <aside className="w-64 bg-white border-r border-slate-200 flex flex-col justify-between p-4 shrink-0 hidden lg:flex sticky top-0 h-screen">
        <div>
          {/* Logo Brand Header */}
          <div className="flex items-center gap-3 px-2 pb-5 mb-4 border-b border-slate-100">
            <Image
              src="/fpt-education-logo.png"
              alt="FPT Education"
              width={465}
              height={160}
              priority
              className="h-9 w-auto object-contain"
            />
            <span className="text-lg font-bold text-[#1E293B] tracking-tight pl-2 border-l border-slate-200">
              AITA
            </span>
          </div>

          {/* Section Label */}
          <div className="text-[13px] font-medium text-slate-500 px-3 mb-2">
            Hệ thống quản trị
          </div>

          {/* Navigation Links */}
          {renderNavLinks()}
        </div>

        {/* Sidebar Footer */}
        <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-[13px] flex items-center justify-between text-slate-500">
          <span className="font-medium text-slate-700">FPT University</span>
          <span className="text-slate-500">v1.0.0</span>
        </div>
      </aside>

      {/* ================= MOBILE DRAWER BACKDROP & SIDEBAR ================= */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity"
            onClick={() => setMobileMenuOpen(false)}
          />
          <aside className="fixed inset-y-0 left-0 w-64 bg-white p-4 shadow-xl flex flex-col justify-between z-50">
            <div>
              <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-100">
                <div className="flex items-center gap-2">
                  <Image
                    src="/fpt-education-logo.png"
                    alt="FPT Education"
                    width={465}
                    height={160}
                    className="h-8 w-auto object-contain"
                  />
                  <span className="text-base font-bold text-[#1E293B] tracking-tight pl-2 border-l border-slate-200">
                    AITA
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => setMobileMenuOpen(false)}
                  className="px-2.5 py-1.5 text-sm font-medium text-slate-600 hover:text-slate-900 rounded-lg min-h-[36px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
                  aria-label="Đóng menu"
                >
                  Đóng
                </button>
              </div>

              <div className="text-[13px] font-medium text-slate-500 px-3 mb-2">
                Hệ thống quản trị
              </div>
              {renderNavLinks()}
            </div>

            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-[13px] flex items-center justify-between text-slate-500">
              <span className="font-medium text-slate-700">FPT University</span>
              <span className="text-slate-500">v1.0.0</span>
            </div>
          </aside>
        </div>
      )}

      {/* ================= RIGHT WORKSPACE ================= */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Topbar */}
        <header className="bg-white border-b border-slate-200 px-4 sm:px-6 h-16 flex items-center justify-between gap-4 sticky top-0 z-20">
          {/* Mobile Menu Button */}
          <div className="flex items-center gap-3 flex-1">
            <button
              type="button"
              onClick={() => setMobileMenuOpen(true)}
              className="lg:hidden px-3 h-9 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 text-sm font-medium transition-colors min-h-[36px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
              aria-label="Mở menu điều hướng"
            >
              Menu
            </button>
          </div>

          {/* User Controls */}
          <div className="flex items-center gap-3 shrink-0">
            <div className="w-8 h-8 rounded-full bg-primary-bg text-primary font-semibold text-sm flex items-center justify-center shrink-0">
              {firstLetter}
            </div>

            {/* Tên và vai trò hiển thị một lần duy nhất */}
            <div className="hidden sm:flex flex-col text-left">
              <span className="text-sm font-medium text-slate-900 leading-tight">
                {user.username}
              </span>
              <span className="text-[13px] text-slate-500 leading-tight mt-0.5">
                {roleLabel}
              </span>
            </div>

            {/* Nút Đăng xuất */}
            <button
              type="button"
              onClick={handleLogout}
              className="px-3 h-9 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 text-sm font-medium transition-colors min-h-[36px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
              aria-label="Đăng xuất khỏi hệ thống"
            >
              Đăng xuất
            </button>
          </div>
        </header>

        {/* Content Body */}
        <main className="p-4 sm:p-6 lg:p-8 flex-1 max-w-7xl w-full mx-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
