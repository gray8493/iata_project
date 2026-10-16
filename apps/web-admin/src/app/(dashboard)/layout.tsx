"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  Cpu,
  FileSpreadsheet,
  Search,
  Bell,
  LogOut,
  Menu,
  X,
} from "lucide-react";

interface UserProfile {
  id?: string | number;
  username: string;
  fullName?: string;
  email?: string;
  role: string;
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const [searchHeader, setSearchHeader] = useState("");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [user, setUser] = useState<UserProfile>({
    username: "Nguyễn Hoàng Đức",
    email: "admin@fe.edu.vn",
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
              email: fetched.email || "admin@fe.edu.vn",
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
      title: "Tổng quan Dashboard",
      href: "/dashboard",
      icon: LayoutDashboard,
    },
    {
      title: "Quản lý Giảng viên",
      href: "/users",
      icon: Users,
    },
    {
      title: "Giám sát Hạn ngạch AI",
      href: "/ai-quota",
      icon: Cpu,
    },
    {
      title: "Báo cáo & Kiểm toán",
      href: "/reports",
      icon: FileSpreadsheet,
    },
  ];

  const firstLetter = (user.username || "A").charAt(0).toUpperCase();

  const renderNavLinks = () => (
    <nav className="space-y-1">
      {menuItems.map((item) => {
        const Icon = item.icon;
        const isActive =
          pathname === item.href ||
          (item.href !== "/dashboard" && pathname?.startsWith(item.href));

        return (
          <Link
            key={item.href}
            href={item.href}
            className={`flex items-center gap-3 px-3 h-10 rounded-lg text-sm font-medium transition-colors min-h-[40px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 ${
              isActive
                ? "bg-indigo-50 text-indigo-600 font-semibold"
                : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
            }`}
          >
            <Icon className={`w-5 h-5 shrink-0 ${isActive ? "text-indigo-600" : "text-slate-400"}`} />
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
          <div className="flex items-center gap-2.5 px-2 pb-5 mb-4 border-b border-slate-100">
            <Image
              src="/fptulogo_transparent.png"
              alt="FPT University Logo"
              width={120}
              height={32}
              priority
              className="h-8 w-auto object-contain"
            />
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider pl-2 border-l border-slate-200">
              AITA
            </span>
          </div>

          {/* Section Label */}
          <div className="text-xs font-medium text-slate-400 px-3 mb-2">
            Hệ thống quản trị
          </div>

          {/* Navigation Links */}
          {renderNavLinks()}
        </div>

        {/* Sidebar Footer: Rút gọn chỉ còn Tên & Phiên bản, không còn SWD392 */}
        <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs flex items-center justify-between text-slate-500">
          <span className="font-medium text-slate-700">FPT University</span>
          <span className="font-mono text-[11px] text-slate-500">v1.0.0</span>
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
                    src="/fptulogo_transparent.png"
                    alt="FPT University Logo"
                    width={112}
                    height={28}
                    className="h-7 w-auto object-contain"
                  />
                  <span className="text-xs font-semibold text-slate-500 uppercase pl-2 border-l border-slate-200">
                    AITA
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => setMobileMenuOpen(false)}
                  className="p-2 text-slate-500 hover:text-slate-800 rounded-lg min-h-[40px] min-w-[40px] flex items-center justify-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                  aria-label="Đóng menu"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="text-xs font-medium text-slate-400 px-3 mb-2">
                Hệ thống quản trị
              </div>
              {renderNavLinks()}
            </div>

            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs flex items-center justify-between text-slate-500">
              <span className="font-medium text-slate-700">FPT University</span>
              <span className="font-mono text-[11px] text-slate-500">v1.0.0</span>
            </div>
          </aside>
        </div>
      )}

      {/* ================= RIGHT WORKSPACE ================= */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Topbar */}
        <header className="bg-white border-b border-slate-200 px-4 sm:px-6 h-16 flex items-center justify-between gap-4 sticky top-0 z-20">
          {/* Mobile Menu Button & Search */}
          <div className="flex items-center gap-3 flex-1 max-w-md">
            <button
              type="button"
              onClick={() => setMobileMenuOpen(true)}
              className="lg:hidden p-2 text-slate-600 hover:bg-slate-100 rounded-lg min-h-[40px] min-w-[40px] flex items-center justify-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
              aria-label="Mở menu điều hướng"
            >
              <Menu className="w-5 h-5" />
            </button>

            {/* Ô tìm kiếm */}
            <div className="relative w-full hidden sm:block">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
              <input
                type="text"
                value={searchHeader}
                onChange={(e) => setSearchHeader(e.target.value)}
                placeholder="Tìm kiếm giảng viên, báo cáo, khóa học..."
                className="w-full pl-9 pr-3 h-9 text-xs bg-slate-50 border border-slate-200 rounded-lg placeholder:text-slate-400 focus:outline-none focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
              />
            </div>
          </div>

          {/* User Controls */}
          <div className="flex items-center gap-3 shrink-0">
            {/* Chuông thông báo */}
            <button
              type="button"
              onClick={() => alert("Hệ thống hiện không có cảnh báo mới.")}
              className="relative p-2 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors min-h-[40px] min-w-[40px] flex items-center justify-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
              aria-label="Thông báo hệ thống"
            >
              <Bell className="w-5 h-5" />
              <span className="absolute top-2 right-2 w-2 h-2 bg-indigo-600 rounded-full ring-2 ring-white" />
            </button>

            {/* Profile: Nhãn ADMIN xuất hiện 1 lần duy nhất tại đây */}
            <div className="flex items-center gap-3 pl-3 border-l border-slate-200">
              <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 font-semibold text-xs flex items-center justify-center shrink-0">
                {firstLetter}
              </div>
              <div className="hidden sm:flex flex-col text-left">
                <div className="flex items-center gap-1.5 leading-none">
                  <span className="text-sm font-medium text-slate-900">
                    {user.username}
                  </span>
                  <span className="text-[10px] font-semibold bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded uppercase">
                    {user.role}
                  </span>
                </div>
                <span className="text-xs text-slate-500 leading-tight mt-1">
                  {user.email}
                </span>
              </div>
            </div>

            {/* Nút Đăng xuất */}
            <button
              type="button"
              onClick={handleLogout}
              className="p-2 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors min-h-[40px] min-w-[40px] flex items-center justify-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
              aria-label="Đăng xuất khỏi hệ thống"
            >
              <LogOut className="w-5 h-5" />
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
