"use client";

import React, { useState, useEffect } from "react";
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

    // Call GET /auth/me from Backend if token exists
    const token = localStorage.getItem("aita_access_token");
    if (token) {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000";
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
          // Backend offline - giữ nguyên fallback
        });
    }
  }, []);

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
      href: "/ai-quotas",
      icon: Cpu,
    },
    {
      title: "Báo cáo & Kiểm toán",
      href: "/reports",
      icon: FileSpreadsheet,
    },
  ];

  const firstLetter = (user.username || "A").charAt(0).toUpperCase();

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex text-slate-800 font-sans">
      {/* ================= LEFT SIDEBAR ================= */}
      <aside className="w-64 bg-white border-r border-slate-200/80 flex flex-col justify-between p-5 shrink-0 hidden lg:flex sticky top-0 h-screen">
        <div>
          {/* Logo Area */}
          <div className="flex items-center justify-between pb-6 mb-6 border-b border-slate-100">
            <div className="flex items-center gap-2.5">
              {/* FPT 3-color icon representation */}
              <div className="flex items-center gap-0.5">
                <span className="w-2 h-5 rounded-full bg-[#0054A6] transform -skew-x-12" />
                <span className="w-2 h-5 rounded-full bg-[#F26F21] transform -skew-x-12" />
                <span className="w-2 h-5 rounded-full bg-[#70B92B] transform -skew-x-12" />
              </div>
              <div className="flex flex-col">
                <span className="font-extrabold text-sm text-[#0054A6] leading-none">
                  FPT Education
                </span>
                <span className="text-[9px] text-slate-400 font-bold tracking-wider uppercase mt-1">
                  AITA ADMIN PORTAL
                </span>
              </div>
            </div>
            <span className="px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200/60 font-bold text-[10px] tracking-wider uppercase">
              AITA ADMIN
            </span>
          </div>

          {/* Section Heading */}
          <div className="text-[11px] font-bold tracking-wider text-slate-400 uppercase mb-3 px-2">
            HỆ THỐNG QUẢN TRỊ
          </div>

          {/* Navigation Menu */}
          <nav className="space-y-1.5">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive =
                pathname === item.href ||
                (item.href !== "/dashboard" && pathname?.startsWith(item.href));

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-medium text-xs transition-all ${
                    isActive
                      ? "bg-[#FFF4EC] text-[#F26F21] font-bold shadow-sm"
                      : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                  }`}
                >
                  <Icon
                    className={`w-4 h-4 ${
                      isActive ? "text-[#F26F21]" : "text-slate-400"
                    }`}
                  />
                  <span>{item.title}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Sidebar Footer Box */}
        <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 flex flex-col gap-1">
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-slate-700">FPT University</span>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-200 text-slate-600">
              v1.0.0
            </span>
          </div>
          <span className="text-[10px] text-slate-400">
            SWD392 - AI-Assisted Assessment
          </span>
        </div>
      </aside>

      {/* ================= RIGHT WORKSPACE ================= */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Navbar */}
        <header className="bg-white border-b border-slate-200/80 px-6 py-3.5 flex items-center justify-between gap-4 sticky top-0 z-20">
          {/* Search bar */}
          <div className="relative w-full max-w-md hidden sm:block">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchHeader}
              onChange={(e) => setSearchHeader(e.target.value)}
              placeholder="Tìm kiếm giảng viên, báo cáo, khóa học..."
              className="w-full pl-9 pr-4 py-2 rounded-full text-xs bg-slate-50 border border-slate-200/80 placeholder:text-slate-400 focus:outline-none focus:bg-white focus:border-[#F26F21] transition-all"
            />
          </div>

          {/* User & Status Controls */}
          <div className="flex items-center gap-3 sm:gap-4 ml-auto">
            {/* Gemini Status Chip */}
            <div className="hidden md:flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-50 border border-slate-200/80 text-xs font-medium text-slate-600">
              <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
              <span>Gemini 1.5 Pro Active</span>
            </div>

            {/* Notification Bell */}
            <button
              onClick={() => alert("Hệ thống hiện không có cảnh báo mới.")}
              className="relative p-2 rounded-full hover:bg-slate-100 text-slate-600 transition-colors"
              title="Thông báo"
            >
              <Bell className="w-4 h-4" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full ring-2 ring-white" />
            </button>

            {/* User Profile */}
            <div className="flex items-center gap-2.5 pl-2 border-l border-slate-200">
              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[#0054A6] to-[#F26F21] p-0.5 flex-shrink-0">
                <div className="w-full h-full rounded-full bg-white flex items-center justify-center font-bold text-xs text-[#0054A6]">
                  {firstLetter}
                </div>
              </div>
              <div className="hidden sm:flex flex-col text-left">
                <div className="flex items-center gap-1.5">
                  <span className="text-xs font-bold text-slate-800 leading-none">
                    {user.username}
                  </span>
                  <span className="text-[9px] font-bold bg-amber-100 text-amber-800 px-1 py-0.2 rounded uppercase">
                    {user.role}
                  </span>
                </div>
                <span className="text-[10px] text-slate-400 leading-tight mt-0.5">
                  {user.email}
                </span>
              </div>
            </div>

            {/* Logout Button */}
            <button
              onClick={handleLogout}
              className="p-2 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors"
              title="Đăng xuất"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </header>

        {/* Content Body */}
        <main className="p-4 sm:p-6 lg:p-8 flex-1">{children}</main>
      </div>
    </div>
  );
}
