"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  RefreshCw,
  Cpu,
  Users,
  Search,
  Download,
  ChevronLeft,
  ChevronRight,
  Loader2,
  Sliders,
  X,
  AlertCircle,
  CheckCircle2,
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

interface InstructorQuotaItem {
  id: string;
  username: string;
  full_name: string;
  email: string;
  role: "ADMIN" | "INSTRUCTOR";
  is_active: boolean;
  daily_token_quota: number;
  used_tokens_today: number;
  created_at: string;
}

interface AiUsageLogItem {
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

const FEATURE_NAMES: Record<string, string> = {
  GENERATE_TESTCASES: "Sinh testcase tự động",
  REVIEW_CODE: "Đánh giá & review code",
  VERIFY_PLAGIARISM: "Kiểm tra đạo văn",
  EVALUATE_WEB_UI: "Đánh giá giao diện web",
};

export default function AiQuotaPage() {
  const [activeTab, setActiveTab] = useState<"INSTRUCTORS" | "LOGS">("INSTRUCTORS");
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [instructors, setInstructors] = useState<InstructorQuotaItem[]>([]);
  const [usageLogs, setUsageLogs] = useState<AiUsageLogItem[]>([]);
  const [logsPagination, setLogsPagination] = useState<PaginationData>({
    page: 1,
    page_size: 10,
    total_items: 0,
    total_pages: 1,
  });

  const [searchQuery, setSearchQuery] = useState("");
  const [editingInstructor, setEditingInstructor] = useState<InstructorQuotaItem | null>(null);
  const [newQuotaValue, setNewQuotaValue] = useState<string>("");

  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(""), 4000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  useEffect(() => {
    if (errorMessage) {
      const timer = setTimeout(() => setErrorMessage(""), 6000);
      return () => clearTimeout(timer);
    }
  }, [errorMessage]);

  const getApiConfig = () => {
    const token = typeof window !== "undefined" ? localStorage.getItem("aita_access_token") : null;
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000/api/v1";
    return { token, apiUrl };
  };

  const fetchData = useCallback(async (logPage = logsPagination.page) => {
    const { token, apiUrl } = getApiConfig();
    if (!token) {
      setErrorMessage("Chưa tìm thấy phiên đăng nhập. Vui lòng đăng nhập lại.");
      setLoading(false);
      return;
    }

    setLoading(true);
    setErrorMessage("");

    try {
      const headers = {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      };

      const [resOverview, resInstructors, resLogs] = await Promise.all([
        fetch(`${apiUrl}/admin/reports/overview`, { headers }),
        fetch(`${apiUrl}/admin/users?role=INSTRUCTOR&page=1&page_size=50`, { headers }),
        fetch(`${apiUrl}/admin/reports/ai-usage?page=${logPage}&page_size=${logsPagination.page_size}`, { headers }),
      ]);

      if (resOverview.status === 401 || resInstructors.status === 401 || resLogs.status === 401) {
        setErrorMessage("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.");
        if (typeof window !== "undefined") {
          localStorage.removeItem("aita_access_token");
        }
        setLoading(false);
        return;
      }

      if (resOverview.ok) {
        const json = await resOverview.json();
        if (json.success && json.data) setOverview(json.data);
      }

      if (resInstructors.ok) {
        const json = await resInstructors.json();
        if (json.success && json.data?.items) setInstructors(json.data.items);
      }

      if (resLogs.ok) {
        const json = await resLogs.json();
        if (json.success && json.data) {
          setUsageLogs(json.data.items || []);
          if (json.data.pagination) setLogsPagination(json.data.pagination);
        }
      }
    } catch {
      setErrorMessage("Lỗi kết nối tới máy chủ.");
    } finally {
      setLoading(false);
    }
  }, [logsPagination.page, logsPagination.page_size]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleUpdateQuota = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingInstructor) return;
    const { token, apiUrl } = getApiConfig();
    if (!token) return;

    const quotaNum = Number(newQuotaValue);
    if (isNaN(quotaNum) || quotaNum < 0) {
      setErrorMessage("Vui lòng nhập số hạn ngạch hợp lệ (lớn hơn hoặc bằng 0).");
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await fetch(`${apiUrl}/admin/users/${editingInstructor.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ daily_token_quota: Math.floor(quotaNum) }),
      });

      const json = await res.json();
      if (res.ok && json.success) {
        setSuccessMessage(`Đã cập nhật hạn ngạch cho "${editingInstructor.full_name}" thành ${quotaNum.toLocaleString()} tokens/ngày.`);
        setEditingInstructor(null);
        fetchData();
      } else {
        const msg = Array.isArray(json.details) ? json.details.join(", ") : (json.message || "Không thể cập nhật hạn ngạch.");
        setErrorMessage(msg);
      }
    } catch {
      setErrorMessage("Lỗi kết nối khi cập nhật hạn ngạch.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredInstructors = instructors.filter((ins) => {
    const q = searchQuery.toLowerCase();
    return (
      ins.full_name.toLowerCase().includes(q) ||
      ins.username.toLowerCase().includes(q) ||
      ins.email.toLowerCase().includes(q)
    );
  });

  const totalConsumed = overview?.ai_token_usage?.total_tokens_consumed_month ?? 0;
  const totalBudget = overview?.ai_token_usage?.total_budget_limit ?? 1;
  const usagePercentage = Math.min(100, Math.round((totalConsumed / totalBudget) * 100));

  const handleExportInstructorsCsv = () => {
    if (instructors.length === 0) return;
    const headers = ["ID", "Giảng viên", "Username", "Email", "Hạn ngạch ngày (Tokens)", "Đã dùng hôm nay", "Còn lại", "Trạng thái"];
    const rows = instructors.map((ins) => [
      ins.id,
      `"${ins.full_name}"`,
      ins.username,
      ins.email,
      ins.daily_token_quota || 50000,
      ins.used_tokens_today || 0,
      Math.max(0, (ins.daily_token_quota || 50000) - (ins.used_tokens_today || 0)),
      ins.is_active ? "Hoạt động" : "Đã khóa",
    ]);
    const csvContent = "\uFEFF" + [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `Han_ngach_giang_vien_${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleExportLogsCsv = () => {
    if (usageLogs.length === 0) return;
    const headers = ["Mã Log", "Giảng viên", "Username", "Tác vụ AI", "Mô hình", "Prompt Tokens", "Completion Tokens", "Tổng Tokens", "Thời gian ghi nhận"];
    const rows = usageLogs.map((log) => [
      log.id,
      `"${log.full_name}"`,
      log.username,
      `"${FEATURE_NAMES[log.feature_type] || log.feature_type}"`,
      log.model_name,
      log.prompt_tokens,
      log.completion_tokens,
      log.total_tokens,
      `"${new Date(log.created_at).toLocaleString("vi-VN")}"`,
    ]);
    const csvContent = "\uFEFF" + [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `Nhat_ky_su_dung_AI_${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const topFeatureRaw = overview?.ai_token_usage?.top_consuming_feature;
  const topFeatureDisplay = topFeatureRaw
    ? FEATURE_NAMES[topFeatureRaw] || topFeatureRaw
    : null;

  return (
    <div className="flex flex-col w-full gap-6">
      {/* Thông báo lỗi */}
      {errorMessage && (
        <div className="flex items-center justify-between p-3.5 bg-rose-50 border border-rose-200 text-rose-700 rounded-lg text-xs font-medium animate-in fade-in">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
            <span>{errorMessage}</span>
          </div>
          <button onClick={() => setErrorMessage("")} className="hover:text-rose-900" aria-label="Đóng thông báo">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Thông báo thành công */}
      {successMessage && (
        <div className="flex items-center justify-between p-3.5 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs font-medium animate-in fade-in">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
            <span>{successMessage}</span>
          </div>
          <button onClick={() => setSuccessMessage("")} className="hover:text-emerald-950" aria-label="Đóng thông báo">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* ================= HEADER TRANG ================= */}
      <section className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <nav className="flex items-center gap-1.5 text-sm text-slate-500 mb-1">
            <Link href="/dashboard" className="hover:text-slate-800 transition-colors">
              Trang chủ
            </Link>
            <span>/</span>
            <span className="text-slate-800 font-medium">Hạn ngạch AI</span>
          </nav>

          <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">
            Giám sát hạn ngạch AI
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Quản lý lưu lượng token và phân bổ hạn ngạch cho giảng viên
          </p>
        </div>

        <button
          type="button"
          onClick={() => fetchData()}
          disabled={loading}
          className="flex items-center gap-2 px-3.5 h-10 rounded-lg bg-white border border-slate-200 text-slate-700 font-medium text-sm hover:bg-slate-50 transition-colors disabled:opacity-50 min-h-[40px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
          aria-label="Làm mới dữ liệu"
        >
          <RefreshCw className={`w-4 h-4 text-slate-500 ${loading ? "animate-spin text-indigo-600" : ""}`} />
          <span>Làm mới</span>
        </button>
      </section>

      {/* ================= 4 THẺ KPI ĐỒNG NHẤT (INDIGO + SLATE) ================= */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Thẻ 1: Ngân sách tháng */}
        <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-start justify-between gap-2">
            <span className="text-sm text-slate-500 font-normal">
              Định mức tháng
            </span>
            <div className="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
              <Cpu className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-3xl font-semibold text-slate-900 tracking-tight">
              {(overview?.ai_token_usage?.total_budget_limit ?? 0).toLocaleString()}
            </div>
            <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden my-2">
              <div
                className="bg-indigo-600 h-full rounded-full transition-all duration-500"
                style={{ width: `${usagePercentage}%` }}
              />
            </div>
            <div className="text-xs text-slate-500">
              Tổng ngân sách toàn hệ thống
            </div>
          </div>
        </div>

        {/* Thẻ 2: Đã tiêu thụ */}
        <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-start justify-between gap-2">
            <span className="text-sm text-slate-500 font-normal">
              Token đã sử dụng
            </span>
            <div className="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
              <Activity className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-3xl font-semibold text-slate-900 tracking-tight">
              {(overview?.ai_token_usage?.total_tokens_consumed_month ?? 0).toLocaleString()}
            </div>
            <div className="text-xs text-slate-500 mt-1">
              Đạt {usagePercentage}% định mức tháng
            </div>
          </div>
        </div>

        {/* Thẻ 3: Top tính năng */}
        <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-start justify-between gap-2">
            <span className="text-sm text-slate-500 font-normal">
              Tính năng dùng nhiều nhất
            </span>
            <div className="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
              <Layers className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3">
            {topFeatureDisplay ? (
              <div className="text-lg font-semibold text-slate-900 tracking-tight truncate" title={topFeatureDisplay}>
                {topFeatureDisplay}
              </div>
            ) : (
              <div className="text-3xl font-semibold text-slate-400">
                —
              </div>
            )}
            <div className="text-xs text-slate-400 mt-1">
              {topFeatureDisplay ? "Chiếm tỷ trọng cao nhất" : "Chưa có dữ liệu"}
            </div>
          </div>
        </div>

        {/* Thẻ 4: Tổng giảng viên */}
        <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-start justify-between gap-2">
            <span className="text-sm text-slate-500 font-normal">
              Giảng viên có hạn ngạch
            </span>
            <div className="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
              <Users className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-3xl font-semibold text-slate-900 tracking-tight">
              {overview?.total_instructors ?? instructors.length}
            </div>
            <div className="text-xs text-slate-500 mt-1">
              Giảng viên đang hoạt động
            </div>
          </div>
        </div>
      </section>

      {/* ================= TAB CONTROLS (TỐI GIẢN) ================= */}
      <div className="flex items-center gap-6 border-b border-slate-200 text-sm">
        <button
          type="button"
          onClick={() => setActiveTab("INSTRUCTORS")}
          className={`pb-3 font-medium transition-colors relative ${
            activeTab === "INSTRUCTORS"
              ? "text-indigo-600 font-semibold"
              : "text-slate-500 hover:text-slate-800"
          }`}
        >
          <span>Hạn ngạch giảng viên ({instructors.length})</span>
          {activeTab === "INSTRUCTORS" && (
            <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600 rounded-full" />
          )}
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("LOGS")}
          className={`pb-3 font-medium transition-colors relative ${
            activeTab === "LOGS"
              ? "text-indigo-600 font-semibold"
              : "text-slate-500 hover:text-slate-800"
          }`}
        >
          <span>Nhật ký sử dụng AI ({logsPagination.total_items})</span>
          {activeTab === "LOGS" && (
            <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600 rounded-full" />
          )}
        </button>
      </div>

      {/* ================= TAB 1: DANH SÁCH HẠN NGẠCH GIẢNG VIÊN ================= */}
      {activeTab === "INSTRUCTORS" && (
        <section className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
          {/* Header & Bộ lọc */}
          <div className="p-4 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div className="relative w-full max-w-sm">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Tìm giảng viên theo tên, email..."
                className="w-full pl-9 pr-3 h-10 rounded-lg text-xs bg-slate-50 border border-slate-200 placeholder:text-slate-400 focus:outline-none focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
              />
            </div>

            <button
              type="button"
              onClick={handleExportInstructorsCsv}
              disabled={instructors.length === 0}
              className="flex items-center gap-2 px-3.5 h-10 rounded-lg bg-white border border-slate-200 text-slate-700 font-medium text-xs hover:bg-slate-50 transition-colors disabled:opacity-40 min-h-[40px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
              aria-label="Xuất file CSV hạn ngạch"
            >
              <Download className="w-4 h-4 text-slate-500" />
              <span>Xuất CSV</span>
            </button>
          </div>

          {/* Table */}
          <div className="overflow-x-auto w-full">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/50 text-slate-500 font-medium border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4 font-medium">Giảng viên</th>
                  <th className="py-3 px-4 font-medium">Email</th>
                  <th className="py-3 px-4 text-right font-medium">Hạn ngạch ngày</th>
                  <th className="py-3 px-4 text-right font-medium">Đã dùng hôm nay</th>
                  <th className="py-3 px-4 text-right font-medium">Còn lại</th>
                  <th className="py-3 px-4 text-center font-medium">Trạng thái</th>
                  <th className="py-3 px-4 text-right font-medium">Thao tác</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-normal">
                {loading ? (
                  <tr>
                    <td colSpan={7} className="py-12 text-center text-slate-400">
                      <Loader2 className="w-5 h-5 mx-auto animate-spin text-indigo-600 mb-1.5" />
                      <span>Đang tải dữ liệu hạn ngạch...</span>
                    </td>
                  </tr>
                ) : filteredInstructors.length > 0 ? (
                  filteredInstructors.map((ins) => {
                    const quota = ins.daily_token_quota || 50000;
                    const used = ins.used_tokens_today || 0;
                    const remaining = Math.max(0, quota - used);
                    const percent = Math.min(100, Math.round((used / quota) * 100));

                    return (
                      <tr key={ins.id} className="hover:bg-slate-50 transition-colors">
                        <td className="py-3 px-4 whitespace-nowrap">
                          <div className="font-medium text-slate-900">{ins.full_name}</div>
                          <div className="text-[11px] text-slate-400 font-mono">@{ins.username}</div>
                        </td>
                        <td className="py-3 px-4 font-mono text-[11px] text-slate-500 whitespace-nowrap">
                          {ins.email}
                        </td>
                        <td className="py-3 px-4 text-right font-mono font-medium text-slate-900 whitespace-nowrap">
                          {quota.toLocaleString()}
                        </td>
                        <td className="py-3 px-4 text-right font-mono text-slate-600 whitespace-nowrap">
                          {used.toLocaleString()} ({percent}%)
                        </td>
                        <td className="py-3 px-4 text-right font-mono font-medium text-indigo-600 whitespace-nowrap">
                          {remaining.toLocaleString()}
                        </td>
                        <td className="py-3 px-4 text-center whitespace-nowrap">
                          {ins.is_active ? (
                            <span className="inline-flex items-center gap-1.5 text-xs text-emerald-700 font-medium">
                              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                              Hoạt động
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1.5 text-xs text-slate-400 font-medium">
                              <span className="w-1.5 h-1.5 rounded-full bg-slate-400" />
                              Đã khóa
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-right whitespace-nowrap">
                          <button
                            type="button"
                            onClick={() => {
                              setEditingInstructor(ins);
                              setNewQuotaValue(String(ins.daily_token_quota || 50000));
                            }}
                            className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-medium transition-colors"
                          >
                            <Sliders className="w-3.5 h-3.5 text-slate-400" />
                            <span>Điều chỉnh</span>
                          </button>
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan={7} className="py-12 text-center text-slate-400 text-sm">
                      Không tìm thấy giảng viên nào.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="p-4 border-t border-slate-200 text-sm text-slate-500">
            {filteredInstructors.length} giảng viên
          </div>
        </section>
      )}

      {/* ================= TAB 2: NHẬT KÝ SỬ DỤNG AI ================= */}
      {activeTab === "LOGS" && (
        <section className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
          <div className="p-4 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <h2 className="text-base font-semibold text-slate-900">
                Nhật ký sử dụng AI
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Các bản ghi gọi API xử lý bài nộp và sinh testcase
              </p>
            </div>

            <button
              type="button"
              onClick={handleExportLogsCsv}
              disabled={usageLogs.length === 0}
              className="flex items-center gap-2 px-3.5 h-10 rounded-lg bg-white border border-slate-200 text-slate-700 font-medium text-xs hover:bg-slate-50 transition-colors disabled:opacity-40 min-h-[40px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
              aria-label="Xuất file CSV nhật ký"
            >
              <Download className="w-4 h-4 text-slate-500" />
              <span>Xuất CSV</span>
            </button>
          </div>

          <div className="overflow-x-auto w-full">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/50 text-slate-500 font-medium border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4 font-medium">Mã log</th>
                  <th className="py-3 px-4 font-medium">Giảng viên</th>
                  <th className="py-3 px-4 font-medium">Tác vụ AI</th>
                  <th className="py-3 px-4 font-medium">Mô hình</th>
                  <th className="py-3 px-4 text-right font-medium">Prompt</th>
                  <th className="py-3 px-4 text-right font-medium">Completion</th>
                  <th className="py-3 px-4 text-right font-medium">Tổng token</th>
                  <th className="py-3 px-4 text-right font-medium">Thời gian</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-normal">
                {loading ? (
                  <tr>
                    <td colSpan={8} className="py-12 text-center text-slate-400">
                      <Loader2 className="w-5 h-5 mx-auto animate-spin text-indigo-600 mb-1.5" />
                      <span>Đang tải nhật ký...</span>
                    </td>
                  </tr>
                ) : usageLogs.length > 0 ? (
                  usageLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-3 px-4 font-mono text-slate-500 text-[11px] whitespace-nowrap">
                        {log.id.slice(0, 8)}...
                      </td>
                      <td className="py-3 px-4 text-slate-900 font-medium whitespace-nowrap">
                        <div>{log.full_name}</div>
                        <div className="text-[11px] text-slate-400 font-mono font-normal">@{log.username}</div>
                      </td>
                      <td className="py-3 px-4 text-slate-700 whitespace-nowrap">
                        <span className="inline-block px-2 py-0.5 rounded text-xs bg-slate-100 text-slate-700">
                          {FEATURE_NAMES[log.feature_type] || log.feature_type}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-mono text-[11px] text-slate-600 whitespace-nowrap">
                        {log.model_name}
                      </td>
                      <td className="py-3 px-4 text-right font-mono text-slate-600 whitespace-nowrap">
                        {log.prompt_tokens.toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-right font-mono text-slate-600 whitespace-nowrap">
                        {log.completion_tokens.toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-right font-mono font-medium text-slate-900 whitespace-nowrap">
                        {log.total_tokens.toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-right text-slate-500 text-[11px] whitespace-nowrap">
                        {new Date(log.created_at).toLocaleString("vi-VN")}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={8} className="py-12 text-center text-slate-400 text-sm">
                      Chưa có bản ghi nhật ký nào.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="p-4 border-t border-slate-200 flex items-center justify-between text-sm text-slate-500">
            <span>{logsPagination.total_items} bản ghi</span>

            {logsPagination.total_items > logsPagination.page_size && (
              <div className="flex items-center gap-1.5">
                <button
                  type="button"
                  onClick={() => fetchData(Math.max(1, logsPagination.page - 1))}
                  disabled={logsPagination.page <= 1 || loading}
                  className="p-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40 transition-colors min-h-[36px] min-w-[36px] flex items-center justify-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                  aria-label="Trang trước"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <span className="px-2.5 py-1 text-xs font-medium text-slate-700 bg-slate-100 rounded-md">
                  {logsPagination.page} / {logsPagination.total_pages}
                </span>
                <button
                  type="button"
                  onClick={() => fetchData(Math.min(logsPagination.total_pages, logsPagination.page + 1))}
                  disabled={logsPagination.page >= logsPagination.total_pages || loading}
                  className="p-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40 transition-colors min-h-[36px] min-w-[36px] flex items-center justify-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                  aria-label="Trang sau"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        </section>
      )}

      {/* ================= MODAL ĐIỀU CHỈNH HẠN NGẠCH ================= */}
      {editingInstructor && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6 border border-slate-200 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div>
                <h3 className="font-semibold text-slate-900 text-base">
                  Điều chỉnh hạn ngạch AI
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  {editingInstructor.full_name} (@{editingInstructor.username})
                </p>
              </div>
              <button
                type="button"
                onClick={() => setEditingInstructor(null)}
                className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg transition-colors"
                aria-label="Đóng"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUpdateQuota} className="space-y-4 mt-4 text-xs">
              <div>
                <label className="block font-medium text-slate-700 mb-1">
                  Định mức tokens mỗi ngày
                </label>
                <input
                  type="number"
                  min="0"
                  required
                  value={newQuotaValue}
                  onChange={(e) => setNewQuotaValue(e.target.value)}
                  className="w-full px-3 h-10 rounded-lg bg-slate-50 border border-slate-200 focus:outline-none focus:border-indigo-500 focus:bg-white transition-colors"
                />
                <p className="text-[11px] text-slate-500 mt-1">
                  Mặc định: 50,000 tokens/ngày. Đã dùng hôm nay: {(editingInstructor.used_tokens_today || 0).toLocaleString()} tokens.
                </p>
              </div>

              <div className="flex items-center justify-end gap-2.5 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setEditingInstructor(null)}
                  className="px-4 h-10 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 font-medium text-xs transition-colors"
                >
                  Hủy bỏ
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 h-10 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-xs transition-colors disabled:opacity-50 flex items-center gap-2"
                >
                  {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
                  <span>Lưu thay đổi</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
