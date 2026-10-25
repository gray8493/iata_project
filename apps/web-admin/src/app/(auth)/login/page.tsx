"use client";

import React, { useEffect, useState } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { API_URL, getAccessToken, storeSession } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [infoMessage, setInfoMessage] = useState("");

  // Đã có phiên đăng nhập thì không cần đăng nhập lại
  useEffect(() => {
    if (getAccessToken()) {
      router.replace("/dashboard");
    }
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");
    setInfoMessage("");
    setLoading(true);

    try {
      if (!API_URL) {
        setErrorMessage("Hệ thống chưa được cấu hình địa chỉ máy chủ (NEXT_PUBLIC_API_URL).");
        return;
      }
      const res = await fetch(`${API_URL}/auth/login`, {
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
          storeSession(data.data.access_token, data.data.user, rememberMe);
        }
        setTimeout(() => {
          router.replace("/dashboard");
        }, 800);
      } else {
        setErrorMessage(
          data.message || "Tên đăng nhập hoặc mật khẩu không chính xác."
        );
      }
    } catch {
      setErrorMessage("Không thể kết nối đến máy chủ. Vui lòng kiểm tra lại kết nối mạng hoặc thử lại sau.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="aita-login min-h-screen bg-[#F8FAFC] flex flex-col items-center justify-center px-4 py-12 font-sans relative overflow-hidden">
      {/* Vòng sáng nền mờ tạo chiều sâu tối giản */}
      <div className="absolute top-1/4 -left-32 w-96 h-96 bg-blue-400/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 -right-32 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Khung Đăng Nhập Chính: tối đa 480px, chừa 16px mỗi bên trên màn hình nhỏ (360px OK) */}
      <div className="w-full max-w-[480px] relative z-10">
        {/* Header: Logo & Tiêu đề */}
        <div className="flex flex-col items-center text-center mb-8">
          <div className="flex items-center gap-3 mb-5">
            <Image
              src="/fpt-education-logo.png"
              alt="FPT Education"
              width={248}
              height={85}
              priority
              className="h-11 w-auto object-contain"
            />
            <div className="h-8 w-px bg-slate-300" />
            <span className="text-lg font-bold text-[#1E293B] tracking-tight">
              AITA
            </span>
          </div>

          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Đăng nhập Quản Trị
          </h1>
          <p className="text-[13px] text-slate-500 mt-2 max-w-[400px]">
            Dành cho quản trị viên. Giảng viên vui lòng dùng ứng dụng AITA trên
            máy tính.
          </p>
        </div>

        {/* Card Form */}
        <div className="bg-white rounded-2xl p-7 sm:p-8 shadow-xl shadow-slate-200/50 border border-slate-200/80">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Trường Tài khoản / Email */}
            <div>
              <label
                htmlFor="username"
                className="block text-xs font-semibold text-slate-700 mb-1.5"
              >
                Tài khoản hoặc Email
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                autoFocus
                autoComplete="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Nhập tài khoản hoặc email"
                className="aita-input w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 placeholder-slate-400 transition"
              />
            </div>

            {/* Trường Mật khẩu */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label
                  htmlFor="password"
                  className="text-xs font-semibold text-slate-700"
                >
                  Mật khẩu
                </label>
                <a
                  href="#forgot"
                  onClick={(e) => {
                    e.preventDefault();
                    setInfoMessage("Vui lòng liên hệ Quản trị viên phòng IT để được cấp lại mật khẩu.");
                  }}
                  className="text-xs font-medium text-primary hover:text-primary-hover transition"
                >
                  Quên mật khẩu?
                </a>
              </div>
              <div className="relative flex items-center">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  required
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="aita-input w-full pl-4 pr-14 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 placeholder-slate-400 transition"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-0 py-1.5 px-2 text-xs font-medium text-slate-500 hover:text-slate-700 transition"
                  aria-label={showPassword ? "Ẩn mật khẩu" : "Hiện mật khẩu"}
                >
                  {showPassword ? "Ẩn" : "Hiện"}
                </button>
              </div>
            </div>

            {/* Checkbox Ghi nhớ đăng nhập */}
            <div className="flex items-center pt-1">
              <label
                htmlFor="rememberMe"
                className="flex items-center gap-2 cursor-pointer select-none text-xs text-slate-600"
              >
                <input
                  id="rememberMe"
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 rounded border-slate-300 accent-primary"
                />
                <span>Ghi nhớ phiên đăng nhập</span>
              </label>
              {!rememberMe && (
                <p className="text-[13px] text-slate-500 mt-1">
                  Phiên sẽ tự kết thúc khi bạn đóng trình duyệt.
                </p>
              )}
            </div>

            {/* Nút Đăng nhập */}
            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-2.5 px-4 rounded-xl bg-primary hover:bg-primary-hover disabled:hover:bg-primary active:scale-[0.99] text-white font-semibold text-xs transition-all shadow-md disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Đang đăng nhập...</span>
                </>
              ) : (
                <span>Đăng nhập</span>
              )}
            </button>
          </form>

          {/* Thông báo lỗi — hiển thị dưới form */}
          {errorMessage && (
            <div
              role="alert"
              className="mt-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs"
            >
              {errorMessage}
            </div>
          )}

          {/* Thông báo thành công — hiển thị dưới form */}
          {successMessage && (
            <div
              role="status"
              className="mt-4 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs"
            >
              {successMessage}
            </div>
          )}

          {/* Thông báo thông tin — hiển thị dưới form */}
          {infoMessage && (
            <div
              role="status"
              className="mt-4 p-3 rounded-xl bg-sky-50 border border-sky-200 text-sky-800 text-xs"
            >
              {infoMessage}
            </div>
          )}
        </div>

        {/* Footer bản quyền */}
        <div className="text-center mt-6 text-[13px] text-[#64748B]">
          <span>Trường Đại học FPT • Ban Khảo Thí & Đào Tạo</span>
        </div>
      </div>
    </div>
  );
}
