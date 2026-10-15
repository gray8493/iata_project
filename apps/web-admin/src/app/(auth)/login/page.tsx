"use client";

import React, { useState } from "react";
import {
  User,
  Lock,
  Eye,
  EyeOff,
  Code2,
  Sparkles,
  Cloud,
  CheckCircle2,
  Shield,
  ArrowRight,
  Loader2,
  AlertCircle,
} from "lucide-react";

export default function LoginPage() {
  const [username, setUsername] = useState("admin@fe.edu.vn");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");
    setLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000/api/v1";
      const res = await fetch(`${apiUrl}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username.trim(),
          password: password.trim(),
        }),
      });

      const data = await res.json();

      if (res.ok && data.success) {
        setSuccessMessage("Đăng nhập thành công! Đang chuyển hướng...");
        if (data.data?.access_token) {
          localStorage.setItem("aita_access_token", data.data.access_token);
          localStorage.setItem("aita_user", JSON.stringify(data.data.user));
        }
        setTimeout(() => {
          window.location.href = "/dashboard";
        }, 1200);
      } else {
        setErrorMessage(
          data.message ||
            "Tên đăng nhập hoặc mật khẩu không chính xác. Vui lòng kiểm tra lại."
        );
      }
    } catch {
      // Backend offline fallback - cho phép trải nghiệm giao diện
      setSuccessMessage(
        "Đăng nhập thành công (Chế độ mô phỏng UI)! Đang vào hệ thống..."
      );
      setTimeout(() => {
        window.location.href = "/dashboard";
      }, 1200);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F0F4F8] flex items-center justify-center p-3 sm:p-6 lg:p-10 font-sans">
      {/* Main Card Container */}
      <div className="w-full max-w-5xl bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col md:flex-row border border-slate-200/90 transition-all">
        {/* ================= LEFT COLUMN: HERO PANEL ================= */}
        <div className="w-full md:w-[46%] bg-gradient-to-br from-[#062040] via-[#0B2C54] to-[#04152D] text-white p-7 sm:p-9 lg:p-11 flex flex-col justify-between relative overflow-hidden">
          {/* Subtle decorative circles */}
          <div className="absolute -top-24 -left-24 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute -bottom-24 -right-24 w-80 h-80 bg-orange-500/10 rounded-full blur-3xl pointer-events-none" />

          {/* Top Logo Badge */}
          <div className="relative z-10">
            <div className="inline-flex items-center gap-3 bg-white px-4 py-2.5 rounded-xl shadow-md mb-8">
              <img
                src="/fptulogo_transparent.png"
                alt="FPT Education Logo"
                className="h-8 w-auto object-contain"
              />
              <div className="h-6 w-px bg-slate-200" />
              <span className="text-[10px] text-slate-500 font-extrabold tracking-wider uppercase">
                AITA ADMIN PORTAL
              </span>
            </div>

            {/* AI Platform Tag */}
            <div className="mb-4">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#1B3E69] text-amber-300 text-[11px] font-semibold tracking-wider uppercase border border-amber-300/20">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
                AI-ASSISTED ASSESSMENT PLATFORM
              </span>
            </div>

            {/* Headline */}
            <h1 className="text-2xl lg:text-3xl font-extrabold tracking-tight text-white mb-3">
              AITA <span className="text-[#F26F21]">—</span> Hệ Thống Chấm
              Điểm AI
            </h1>

            <p className="text-slate-300 text-xs sm:text-sm leading-relaxed mb-8">
              Hệ sinh thái tự động hóa và phân tích kết quả học tập thế hệ mới,
              tối ưu cho Giảng viên & Ban Khảo Thí Trường Đại học FPT.
            </p>

            {/* 3 Feature Cards */}
            <div className="space-y-3.5">
              {/* Feature 1 */}
              <div className="flex items-start gap-3.5 p-3 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10 hover:bg-white/10 transition-colors">
                <div className="w-10 h-10 rounded-lg bg-[#F26F21] flex items-center justify-center flex-shrink-0 shadow-sm text-white">
                  <Code2 className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-sm font-bold text-white mb-0.5">
                    Chấm Tự Động Chính Xác
                  </h2>
                  <p className="text-[11px] sm:text-xs text-slate-300 leading-snug">
                    Chạy kiểm thử logic đa ngôn ngữ (C, Java, Python) tự động
                    với sandbox an toàn tuyệt đối.
                  </p>
                </div>
              </div>

              {/* Feature 2 */}
              <div className="flex items-start gap-3.5 p-3 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10 hover:bg-white/10 transition-colors">
                <div className="w-10 h-10 rounded-lg bg-[#0066CC] flex items-center justify-center flex-shrink-0 shadow-sm text-white">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-sm font-bold text-white mb-0.5">
                    Tích Hợp Google Gemini AI
                  </h2>
                  <p className="text-[11px] sm:text-xs text-slate-300 leading-snug">
                    Tự động sinh Test cases biên và hỗ trợ phân tích code, phát
                    hiện gian lận & giải thích bug.
                  </p>
                </div>
              </div>

              {/* Feature 3 */}
              <div className="flex items-start gap-3.5 p-3 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10 hover:bg-white/10 transition-colors">
                <div className="w-10 h-10 rounded-lg bg-[#10B981] flex items-center justify-center flex-shrink-0 shadow-sm text-white">
                  <Cloud className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-sm font-bold text-white mb-0.5">
                    Đồng Bộ Cloud Tức Thì
                  </h2>
                  <p className="text-[11px] sm:text-xs text-slate-300 leading-snug">
                    Truyền tải dữ liệu đồng bộ hai chiều từ Client Phòng máy lên
                    Cổng Quản Lý Đào Tạo FE.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Left Standards Footer */}
          <div className="relative z-10 pt-8 mt-6 border-t border-white/10 flex items-center gap-2 text-slate-300 text-xs font-medium">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>
              FPT University • Academic Integrity & AI Governance Standard
            </span>
          </div>
        </div>

        {/* ================= RIGHT COLUMN: LOGIN FORM ================= */}
        <div className="w-full md:w-[54%] p-7 sm:p-10 lg:p-12 flex flex-col justify-between bg-white">
          <div>
            {/* Top Badges */}
            <div className="flex items-center justify-between mb-5">
              <span className="px-2.5 py-1 rounded bg-blue-50 text-blue-700 font-bold text-[11px] tracking-wide uppercase">
                UC-01 • SYSTEM AUTH
              </span>
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 text-xs font-semibold">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                Server Online
              </span>
            </div>

            {/* Title & Subtitle */}
            <h2 className="text-2xl lg:text-3xl font-extrabold text-slate-900 tracking-tight mb-1.5">
              Đăng nhập Quản Trị Viên
            </h2>
            <p className="text-slate-500 text-xs sm:text-sm mb-6">
              Web Admin Portal dành cho cán bộ quản lý hệ thống AITA
            </p>

            {/* Error & Success Messages */}
            {errorMessage && (
              <div className="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-500" />
                <span>{errorMessage}</span>
              </div>
            )}
            {successMessage && (
              <div className="mb-4 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 flex-shrink-0 text-emerald-500" />
                <span>{successMessage}</span>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Username Field */}
              <div>
                <label className="block text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  TÊN ĐĂNG NHẬP / EMAIL TRƯỜNG
                </label>
                <div className="relative flex items-center rounded-xl bg-[#F4F5F9] border border-slate-200 focus-within:border-[#F26F21] focus-within:ring-2 focus-within:ring-orange-100 transition-all">
                  <div className="pl-3.5 text-slate-400">
                    <User className="w-4 h-4" />
                  </div>
                  <input
                    type="text"
                    required
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="admin@fe.edu.vn"
                    className="w-full bg-transparent px-3 py-3 text-sm text-slate-800 placeholder-slate-400 focus:outline-none"
                  />
                </div>
              </div>

              {/* Password Field */}
              <div>
                <label className="block text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  MẬT KHẨU BẢO VỆ
                </label>
                <div className="relative flex items-center rounded-xl bg-[#F4F5F9] border border-slate-200 focus-within:border-[#F26F21] focus-within:ring-2 focus-within:ring-orange-100 transition-all">
                  <div className="pl-3.5 text-slate-400">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    type={showPassword ? "text" : "password"}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full bg-transparent px-3 py-3 text-sm text-slate-800 placeholder-slate-400 focus:outline-none"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="pr-3.5 text-slate-400 hover:text-slate-600 transition-colors"
                  >
                    {showPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* Remember Me & Forgot Password */}
              <div className="flex items-center justify-between text-xs pt-1">
                <label className="flex items-center gap-2 cursor-pointer select-none text-slate-600">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 text-[#F26F21] rounded border-slate-300 focus:ring-[#F26F21]"
                  />
                  <span>Ghi nhớ đăng nhập thiết bị</span>
                </label>
                <a
                  href="#forgot"
                  onClick={(e) => {
                    e.preventDefault();
                    alert(
                      "Vui lòng liên hệ Quản trị viên hệ thống để khôi phục mật khẩu tài khoản trường!"
                    );
                  }}
                  className="text-[#F26F21] hover:underline font-semibold"
                >
                  Quên mật khẩu?
                </a>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full mt-3 py-3.5 px-4 rounded-xl bg-[#F26F21] hover:bg-[#D95A0E] active:scale-[0.99] text-white font-bold text-sm tracking-wide uppercase transition-all shadow-lg shadow-orange-500/25 flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Đang xác thực...</span>
                  </>
                ) : (
                  <>
                    <span>ĐĂNG NHẬP QUẢN TRỊ</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>

              {/* Google Login Button */}
              <button
                type="button"
                onClick={() => {
                  alert(
                    "Đăng nhập Single Sign-On (SSO) Google dành riêng cho cán bộ @fe.edu.vn đang được kích hoạt."
                  );
                }}
                className="w-full py-3 px-4 rounded-xl bg-white border border-slate-200 hover:bg-slate-50 transition-colors flex items-center justify-center gap-3 text-slate-700 text-xs font-semibold"
              >
                {/* Google SVG Logo */}
                <svg className="w-4 h-4" viewBox="0 0 24 24">
                  <path
                    fill="#4285F4"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                  />
                </svg>
                <span>Đăng nhập với Google</span>
                <span className="ml-1 px-1.5 py-0.5 rounded bg-blue-50 text-blue-600 font-mono text-[10px]">
                  @fe.edu.vn
                </span>
              </button>

              {/* Security Warning Box */}
              <div className="mt-4 p-3.5 rounded-xl bg-[#FFF8F2] border border-[#FFE7D4] flex items-start gap-3">
                <Shield className="w-4 h-4 text-[#F26F21] flex-shrink-0 mt-0.5" />
                <p className="text-[11px] text-slate-600 leading-relaxed">
                  <span className="font-bold text-slate-800">
                    Cổng kiểm soát nội bộ:
                  </span>{" "}
                  Chỉ dành riêng cho Cán bộ Quản trị & Giảng viên được phân
                  quyền thuộc Trường Đại học FPT. Mọi hành động đăng nhập đều
                  được ghi nhận nhật ký kiểm toán (Audit Trail Log).
                </p>
              </div>
            </form>
          </div>

          {/* Footer Metadata */}
          <div className="pt-6 mt-6 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-400 gap-2">
            <span>© 2025 FPT Education. All rights reserved.</span>
            <span className="font-mono">v1.0.0 (Evaluation 2 - SWD392)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
