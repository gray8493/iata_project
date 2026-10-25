"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  Gauge,
  ScrollText,
  type LucideIcon,
} from "lucide-react";
import {
  API_URL,
  getAccessToken,
  getStoredUser,
  updateStoredUser,
  clearSession,
} from "@/lib/api";

interface UserProfile {
  id?: string | number;
  username: string;
  fullName?: string;
  full_name?: string;
  email?: string;
  role: string;
}

const ROLE_LABELS: Record<string, string> = {
  ADMIN: "Quản trị viên",
  INSTRUCTOR: "Giảng viên",
};

const FALLBACK_USER: UserProfile = {
  username: "Nguyễn Hoàng Đức",
  email: "admin@aita.edu.vn",
  role: "ADMIN",
};

const MENU_ITEMS: { title: string; href: string; icon: LucideIcon }[] = [
  { title: "Tổng quan", href: "/dashboard", icon: LayoutDashboard },
  { title: "Quản lý giảng viên", href: "/users", icon: Users },
  { title: "Giám sát hạn ngạch AI", href: "/ai-quota", icon: Gauge },
  { title: "Báo cáo & kiểm toán", href: "/reports", icon: ScrollText },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [user, setUser] = useState<UserProfile>(FALLBACK_USER);

  // Bảo vệ route: chưa có phiên đăng nhập thì chuyển về /login
  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      router.replace("/login");
      return;
    }

    const storedUser = getStoredUser<UserProfile>();
    if (storedUser) {
      setUser({
        ...FALLBACK_USER,
        username:
          storedUser.full_name || storedUser.fullName || storedUser.username || FALLBACK_USER.username,
        email: storedUser.email || FALLBACK_USER.email,
        role: storedUser.role || FALLBACK_USER.role,
      });
    }

    // Đồng bộ hồ sơ mới nhất từ Backend
    fetch(`${API_URL}/auth/me`, {
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
            username:
              fetched.full_name || fetched.fullName || fetched.username || FALLBACK_USER.username,
            email: fetched.email || FALLBACK_USER.email,
            role: fetched.role || FALLBACK_USER.role,
          });
          updateStoredUser(fetched);
        }
      })
      .catch(() => {
        // Giữ dữ liệu cache làm fallback an toàn
      });
  }, [router]);

  // Cập nhật tiêu đề tab theo trang đang mở
  useEffect(() => {
    const active = MENU_ITEMS.find(
      (item) =>
        pathname === item.href ||
        (item.href !== "/dashboard" && pathname?.startsWith(item.href))
    );
    document.title = active ? `${active.title} • AITA Quản trị` : "AITA Quản trị";
  }, [pathname]);

  // Đóng mobile menu khi chuyển trang
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [pathname]);

  const handleLogout = () => {
    clearSession();
    router.push("/login");
  };

  const firstLetter = (user.username || "A").charAt(0).toUpperCase();
  const roleLabel = ROLE_LABELS[user.role] || user.role;

  const renderNavLinks = () => (
    <nav aria-label="Điều hướng chính" className="space-y-1">
      {MENU_ITEMS.map((item) => {
        const isActive =
          pathname === item.href ||
          (item.href !== "/dashboard" && pathname?.startsWith(item.href));
        const Icon = item.icon;

        return (
          <Link
            key={item.href}
            href={item.href}
            aria-current={isActive ? "page" : undefined}
            className={`flex items-center gap-2.5 px-3 h-10 rounded-lg text-sm transition-colors min-h-[40px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary ${
              isActive
                ? "bg-primary-bg text-primary font-semibold"
                : "text-slate-600 hover:bg-slate-50 hover:text-slate-900 font-medium"
            }`}
          >
            <Icon className="w-4 h-4 shrink-0" aria-hidden="true" />
            <span className="truncate">{item.title}</span>
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
