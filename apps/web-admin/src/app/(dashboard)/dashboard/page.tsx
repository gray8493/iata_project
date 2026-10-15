"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  Home,
  RefreshCw,
  FileDown,
  Download,
  Printer,
  ChevronDown,
  FileSpreadsheet,
  Users,
  Cpu,
  CheckCircle2,
  BookOpen,
  Info,
  Clock,
  ChevronLeft,
  ChevronRight,
  Loader2,
  AlertCircle,
  Activity,
  Layers,
} from "lucide-react";

interface OverviewData {
  total_instructors: number;
  ai_token_usage: {
    total_tokens_consumed_month: number;
    total_budget_limit: number;
    top_consuming_feature: string | null;
  };
}

interface AiUsageItem {
  id: string;
  user_id: string;
  username: string;
  full_name: string;
  feature_type: string;
  model_name: string;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  created_at: string;
}

interface PaginationData {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
}

export default function DashboardOverviewPage() {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [lastSyncText, setLastSyncText] = useState("Đang kết nối...");
  const [currentPage, setCurrentPage] = useState(1);

  // Real backend states
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [usageItems, setUsageItems] = useState<AiUsageItem[]>([]);
  const [pagination, setPagination] = useState<PaginationData>({
    page: 1,
    page_size: 10,
    total_items: 0,
    total_pages: 0,
  });

  // Fetch real data from NestJS Backend APIs
  const fetchDashboardData = useCallback(async (pageNumber = 1) => {
    setErrorMessage("");
    const token = localStorage.getItem("aita_access_token");
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000/api/v1";

    if (!token) {
      setErrorMessage("Chưa tìm thấy token đăng nhập. Vui lòng đăng nhập lại!");
      setLoading(false);
      return;
    }

    try {
      const headers = {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      };

      // Gọi đồng thời cả 2 API thật: Overview và AI Usage Logs
      const [resOverview, resUsage] = await Promise.all([
        fetch(`${apiUrl}/admin/reports/overview`, { method: "GET", headers }),
        fetch(`${apiUrl}/admin/reports/ai-usage?page=${pageNumber}&page_size=10`, {
          method: "GET",
          headers,
        }),
      ]);

      if (resOverview.status === 401 || resUsage.status === 401) {
        setErrorMessage("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại!");
        localStorage.removeItem("aita_access_token");
        setLoading(false);
        return;
      }

      if (resOverview.ok) {
        const jsonOverview = await resOverview.json();
        if (jsonOverview.success && jsonOverview.data) {
          setOverview(jsonOverview.data);
        }
      } else {
        const err = await resOverview.json().catch(() => ({}));
        setErrorMessage(err.message || "Không thể tải báo cáo tổng quan từ server.");
      }

      if (resUsage.ok) {
        const jsonUsage = await resUsage.json();
        if (jsonUsage.success && jsonUsage.data) {
          setUsageItems(jsonUsage.data.items || []);
          setPagination(
            jsonUsage.data.pagination || {
              page: pageNumber,
              page_size: 10,
              total_items: 0,
              total_pages: 0,
            }
          );
        }
      }

      const now = new Date();
      setLastSyncText(`${now.getHours()}:${String(now.getMinutes()).padStart(2, "0")}:${String(now.getSeconds()).padStart(2, "0")}`);
    } catch {
      setErrorMessage("Không thể kết nối đến máy chủ Backend (http://localhost:3000). Vui lòng kiểm tra lại server NestJS!");
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData(currentPage);
  }, [fetchDashboardData, currentPage]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await fetchDashboardData(currentPage);
  };

  // Tính toán tỷ lệ phần trăm hạn ngạch AI tiêu thụ thực tế
  const totalTokensUsed = overview?.ai_token_usage?.total_tokens_consumed_month ?? 0;
  const totalBudgetLimit = overview?.ai_token_usage?.total_budget_limit ?? 0;
  const usagePercentage =
    totalBudgetLimit > 0
      ? Math.min(Math.round((totalTokensUsed / totalBudgetLimit) * 1000) / 10, 100)
      : 0;

  const [showExportMenu, setShowExportMenu] = useState(false);

  // Xuất file CSV mở trên Excel (UTF-8 BOM tiếng Việt)
  const handleExportCsv = () => {
    setShowExportMenu(false);
    const nowStr = new Date().toLocaleString("vi-VN");
    const dateStr = new Date().toISOString().slice(0, 10);
    const fileName = `Bao_cao_AITA_tong_quan_${dateStr}.csv`;

    const totalConsumed = overview?.ai_token_usage?.total_tokens_consumed_month ?? 0;
    const totalBudget = overview?.ai_token_usage?.total_budget_limit ?? 0;
    const topFeature = overview?.ai_token_usage?.top_consuming_feature || "Chưa có lượt gọi";

    let csv = "\uFEFF"; // Byte Order Mark giúp Microsoft Excel hiển thị tiếng Việt có dấu chuẩn
    csv += "BÁO CÁO TỔNG QUAN HỆ THỐNG AITA\n";
    csv += `Thời điểm xuất:,"${nowStr}"\n`;
    csv += `Cổng quản trị:,Hệ thống Khảo thí AITA - Đại học FPT\n\n`;

    csv += "--- 1. CHỈ SỐ HỆ THỐNG & HẠN NGẠCH AI ---\n";
    csv += `Tổng số giảng viên hoạt động:,${overview?.total_instructors ?? 0}\n`;
    csv += `Tổng token đã tiêu thụ trong tháng:,${totalConsumed}\n`;
    csv += `Ngân sách token toàn hệ thống:,${totalBudget}\n`;
    csv += `Tỷ lệ sử dụng thực tế:,${totalBudget > 0 ? ((totalConsumed / totalBudget) * 100).toFixed(2) : 0}%\n`;
    csv += `Tính năng AI chiếm tỷ trọng lớn nhất:,"${topFeature}"\n\n`;

    csv += "--- 2. NHẬT KÝ SỬ DỤNG AI GẦN NHẤT (AUDIT TRAIL) ---\n";
    csv += "Mã Log,Giảng viên,Tài khoản,Tính năng (Feature Type),Mô hình AI,Prompt Tokens,Completion Tokens,Tổng Tokens,Thời gian ghi nhận\n";

    if (usageItems && usageItems.length > 0) {
      usageItems.forEach((log) => {
        csv += `"${log.id}","${log.full_name}","${log.username}","${log.feature_type}","${log.model_name}",${log.prompt_tokens},${log.completion_tokens},${log.total_tokens},"${new Date(log.created_at).toLocaleString("vi-VN")}"\n`;
      });
    } else {
      csv += "Chưa có bản ghi nhật ký nào trong cơ sở dữ liệu.\n";
    }

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handlePrintPdf = () => {
    setShowExportMenu(false);
    window.print();
  };

  return (
    <div className="flex flex-col w-full gap-6">
      {/* ================= HEADER & BREADCRUMB ================= */}
      <section className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
        <div className="flex flex-col gap-1.5">
          {/* Breadcrumb */}
          <nav className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-wider text-slate-400">
            <Link
              href="/dashboard"
              className="hover:text-[#F26F21] transition-colors flex items-center gap-1"
            >
              <Home className="w-3.5 h-3.5" />
              <span>TRANG CHỦ</span>
            </Link>
            <span>/</span>
            <span className="text-slate-600 font-extrabold">
              TỔNG QUAN HỆ THỐNG (UC-05)
            </span>
          </nav>

          {/* Heading & Live Status */}
          <div className="flex items-center gap-3 flex-wrap mt-0.5">
            <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">
              Bảng Điều Khiển Tổng Quan AITA
            </h1>
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 text-xs font-semibold border border-emerald-200/60">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>Đồng bộ CSDL thực: {lastSyncText}</span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-3 self-start lg:self-auto relative">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-100 text-slate-700 font-semibold text-xs hover:bg-slate-200 active:scale-95 transition-all disabled:opacity-60"
          >
            <RefreshCw
              className={`w-3.5 h-3.5 transition-transform duration-500 ${
                isRefreshing ? "rotate-180 animate-spin text-[#F26F21]" : ""
              }`}
            />
            <span>{isRefreshing ? "Đang đồng bộ..." : "Làm mới dữ liệu"}</span>
          </button>

          {/* Menu Xuất Báo Cáo Thực Tế */}
          <div className="relative">
            <button
              onClick={() => setShowExportMenu(!showExportMenu)}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#3B2D6D] hover:bg-[#31255C] text-white font-semibold text-xs shadow-md shadow-indigo-900/10 active:scale-95 transition-all"
            >
              <FileDown className="w-3.5 h-3.5" />
              <span>Xuất báo cáo PDF/Excel</span>
              <ChevronDown className="w-3 h-3 ml-0.5 opacity-80" />
            </button>

            {showExportMenu && (
              <div className="absolute right-0 mt-2 w-52 bg-white rounded-2xl shadow-xl border border-slate-100 p-1.5 z-30 animate-in fade-in zoom-in-95 duration-150">
                <button
                  onClick={handleExportCsv}
                  className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-50 hover:text-emerald-700 transition-colors text-left"
                >
                  <FileSpreadsheet className="w-4 h-4 text-emerald-600" />
                  <div>
                    <div>Xuất file Excel (.csv)</div>
                    <div className="text-[10px] text-slate-400 font-normal">Dữ liệu tổng hợp UTF-8</div>
                  </div>
                </button>

                <button
                  onClick={handlePrintPdf}
                  className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-50 hover:text-purple-700 transition-colors text-left"
                >
                  <Printer className="w-4 h-4 text-purple-600" />
                  <div>
                    <div>In / Lưu PDF</div>
                    <div className="text-[10px] text-slate-400 font-normal">Định dạng xem in trình duyệt</div>
                  </div>
                </button>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Error Banner nếu có lỗi API */}
      {errorMessage && (
        <section className="p-4 rounded-2xl bg-red-50 border border-red-200 flex items-center justify-between gap-4 text-xs text-red-700">
          <div className="flex items-center gap-2.5">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
            <span className="font-medium">{errorMessage}</span>
          </div>
          <Link
            href="/login"
            className="px-3 py-1.5 rounded-lg bg-red-600 text-white font-bold hover:bg-red-700 transition-colors shrink-0"
          >
            Đăng nhập lại
          </Link>
        </section>
      )}

      {/* ================= 4 METRIC STAT CARDS (REAL DATA TỪ BACKEND) ================= */}
      <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5">
        {/* Card 1: Tổng Giảng Viên (Database Count Thật) */}
        <div className="p-5 bg-white rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-between hover:shadow-md transition-shadow">
          <div className="flex items-start justify-between">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                GIẢNG VIÊN HỆ THỐNG
              </span>
              <h3 className="text-xs font-medium text-slate-600 mt-0.5">
                Tổng Giảng Viên Hoạt Động
              </h3>
              <div className="mt-3 flex items-baseline gap-2">
                {loading ? (
                  <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
                ) : (
                  <span className="text-3xl font-extrabold text-slate-900">
                    {overview?.total_instructors ?? 0}
                  </span>
                )}
                <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                  Dữ liệu CSDL Neon
                </span>
              </div>
            </div>
            <div className="w-11 h-11 rounded-xl flex items-center justify-center bg-blue-50 text-[#0054A6]">
              <Users className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 pt-3 flex items-center justify-between text-[11px] text-slate-500 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-100">
            <span>Vai trò xác thực</span>
            <span className="font-bold text-slate-800">ROLE: INSTRUCTOR</span>
          </div>
        </div>

        {/* Card 2: Hạn Ngạch AI Tiêu Thụ Trong Tháng */}
        <div className="p-5 bg-white rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-between hover:shadow-md transition-shadow">
          <div className="flex items-start justify-between">
            <div className="w-full mr-2">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                TIÊU THỤ TOKEN TRONG THÁNG
              </span>
              <h3 className="text-xs font-medium text-slate-600 mt-0.5">
                Tổng Token Đã Sử Dụng
              </h3>
              <div className="mt-3 flex items-baseline gap-1">
                {loading ? (
                  <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
                ) : (
                  <>
                    <span className="text-2xl font-black text-slate-900 tracking-tight">
                      {totalTokensUsed.toLocaleString()}
                    </span>
                    <span className="text-xs font-semibold text-slate-400">
                      / {totalBudgetLimit.toLocaleString()} Tokens
                    </span>
                  </>
                )}
              </div>
            </div>
            <div className="w-11 h-11 shrink-0 rounded-xl flex items-center justify-center bg-orange-50 text-[#F26F21]">
              <Cpu className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex flex-col gap-1.5">
            <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
              <div
                className="bg-[#F26F21] h-full rounded-full transition-all duration-700"
                style={{ width: `${Math.min(usagePercentage, 100)}%` }}
              />
            </div>
            <div className="flex items-center justify-between text-[11px]">
              <span className="text-emerald-700 font-semibold flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-600" />
                Tỷ lệ sử dụng thực tế
              </span>
              <span className="font-bold text-slate-800">
                {usagePercentage}%
              </span>
            </div>
          </div>
        </div>

        {/* Card 3: Tổng Lượt Gọi AI / Nhật Ký Đã Ghi Nhận */}
        <div className="p-5 bg-white rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-between hover:shadow-md transition-shadow">
          <div className="flex items-start justify-between">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                AUDIT LOGS
              </span>
              <h3 className="text-xs font-medium text-slate-600 mt-0.5">
                Tổng Lượt Gọi AI Ghi Nhận
              </h3>
              <div className="mt-3 flex items-baseline gap-2">
                {loading ? (
                  <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
                ) : (
                  <span className="text-3xl font-extrabold text-slate-900">
                    {pagination.total_items}
                  </span>
                )}
                <span className="text-xs font-bold text-slate-500">
                  Lượt request
                </span>
              </div>
            </div>
            <div className="w-11 h-11 rounded-xl flex items-center justify-center bg-emerald-50 text-emerald-600">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 pt-3 flex items-center justify-between text-[11px] text-slate-500 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-100">
            <span>Bảng ghi nhận</span>
            <span className="font-bold text-emerald-700">ai_quota_logs</span>
          </div>
        </div>

        {/* Card 4: Tính Năng Tiêu Thụ Nhiều Nhất */}
        <div className="p-5 bg-white rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-between hover:shadow-md transition-shadow">
          <div className="flex items-start justify-between">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                PHÂN TÍCH TẢI AI
              </span>
              <h3 className="text-xs font-medium text-slate-600 mt-0.5">
                Tính Năng Chiếm Tỷ Trọng Lớn Nhất
              </h3>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="text-xl font-extrabold text-slate-900">
                  {overview?.ai_token_usage?.top_consuming_feature || "Chưa có lượt gọi"}
                </span>
              </div>
            </div>
            <div className="w-11 h-11 rounded-xl flex items-center justify-center bg-purple-50 text-purple-700">
              <BookOpen className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 pt-3 flex items-center justify-between text-[11px] text-slate-500 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-100">
            <span>Mô hình chuẩn</span>
            <span className="font-bold text-purple-700">gemini-3.8-flash</span>
          </div>
        </div>
      </section>

      {/* ================= BẢNG DANH SÁCH NHẬT KÝ THẬT TỪ CƠ SỞ DỮ LIỆU (AI QUOTA AUDIT LOGS) ================= */}
      <section className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden flex flex-col">
        {/* Header của bảng */}
        <div className="p-6 pb-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-indigo-50 text-indigo-700">
                <Activity className="w-4 h-4" />
              </span>
              <h2 className="text-base font-bold text-slate-900">
                Nhật Ký Sử Dụng AI & Đánh Giá Gần Nhất (Audit Trail)
              </h2>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Dữ liệu được nạp trực tiếp 100% từ bảng <code>ai_quota_logs</code> qua API <code>GET /admin/reports/ai-usage</code>
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold px-3 py-1 rounded-full bg-slate-100 text-slate-600">
              Tổng số: <strong>{pagination.total_items}</strong> bản ghi
            </span>
          </div>
        </div>

        {/* Data Table */}
        <div className="overflow-x-auto w-full">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50/80 text-slate-500 uppercase text-[10px] font-bold tracking-wider border-y border-slate-100">
              <tr>
                <th className="px-6 py-3">MÃ LOG / ID</th>
                <th className="px-6 py-3">GIẢNG VIÊN THỰC HIỆN</th>
                <th className="px-6 py-3">TÍNH NĂNG (FEATURE TYPE)</th>
                <th className="px-6 py-3">MÔ HÌNH AI</th>
                <th className="px-6 py-3">PROMPT TOKENS</th>
                <th className="px-6 py-3">COMPLETION TOKENS</th>
                <th className="px-6 py-3">TỔNG TOKENS</th>
                <th className="px-6 py-3 text-right">THỜI GIAN GỌI</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {loading ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-slate-400">
                    <div className="flex items-center justify-center gap-2">
                      <Loader2 className="w-5 h-5 animate-spin text-[#F26F21]" />
                      <span>Đang tải nhật ký từ cơ sở dữ liệu Neon...</span>
                    </div>
                  </td>
                </tr>
              ) : usageItems.length > 0 ? (
                usageItems.map((item) => (
                  <tr
                    key={item.id}
                    className="hover:bg-slate-50/80 transition-colors"
                  >
                    <td className="px-6 py-3.5 font-mono text-slate-500 text-[11px]">
                      {item.id.slice(0, 8)}...
                    </td>
                    <td className="px-6 py-3.5 font-bold text-slate-800">
                      <div>{item.full_name || item.username}</div>
                      <div className="text-[10px] text-slate-400 font-normal">
                        @{item.username}
                      </div>
                    </td>
                    <td className="px-6 py-3.5">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md font-bold text-[11px] bg-purple-50 text-purple-700 border border-purple-100">
                        {item.feature_type}
                      </span>
                    </td>
                    <td className="px-6 py-3.5 text-slate-600 font-mono text-[11px]">
                      {item.model_name}
                    </td>
                    <td className="px-6 py-3.5 text-slate-600">
                      {item.prompt_tokens.toLocaleString()}
                    </td>
                    <td className="px-6 py-3.5 text-slate-600">
                      {item.completion_tokens.toLocaleString()}
                    </td>
                    <td className="px-6 py-3.5 font-extrabold text-[#F26F21]">
                      {item.total_tokens.toLocaleString()}
                    </td>
                    <td className="px-6 py-3.5 text-right text-slate-400 text-[11px]">
                      <div className="flex items-center justify-end gap-1">
                        <Clock className="w-3 h-3" />
                        <span>{new Date(item.created_at).toLocaleString("vi-VN")}</span>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="px-6 py-16 text-center text-slate-400">
                    <div className="flex flex-col items-center justify-center gap-2">
                      <Layers className="w-8 h-8 text-slate-300" />
                      <span className="font-semibold text-slate-600">
                        Chưa có nhật ký sử dụng AI nào trong cơ sở dữ liệu
                      </span>
                      <p className="text-xs text-slate-400 max-w-md">
                        Khi có giảng viên thực hiện sinh Testcase, review code hoặc chấm bài tự động, bản ghi kiểm toán sẽ xuất hiện ngay tại đây theo thời gian thực.
                      </p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Phân trang thật từ Backend */}
        <div className="px-6 py-3.5 bg-white flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-slate-100 text-xs text-slate-500">
          <div>
            Hiển thị <strong>{usageItems.length}</strong> / <strong>{pagination.total_items}</strong> bản ghi
            {pagination.total_pages > 0 && ` (Trang ${pagination.page} / ${pagination.total_pages})`}
          </div>

          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage <= 1 || loading}
              className="p-1.5 rounded-lg bg-slate-100 text-slate-500 hover:bg-slate-200 disabled:opacity-40 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="px-3 py-1 font-bold text-slate-700 bg-slate-100 rounded-lg">
              {currentPage}
            </span>
            <button
              onClick={() => setCurrentPage((p) => Math.min(Math.max(1, pagination.total_pages), p + 1))}
              disabled={currentPage >= pagination.total_pages || loading || pagination.total_pages === 0}
              className="p-1.5 rounded-lg bg-slate-100 text-slate-500 hover:bg-slate-200 disabled:opacity-40 transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
