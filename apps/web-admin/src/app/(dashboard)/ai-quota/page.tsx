"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  RefreshCw,
  TrendingUp,
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
  FileCode,
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
  GENERATE_TESTCASES: "Sinh Testcase Tự Động",
  REVIEW_CODE: "Đánh Giá & Review Code",
  VERIFY_PLAGIARISM: "Kiểm Tra Đạo Văn Code",
  EVALUATE_WEB_UI: "Đánh Giá Giao Diện Web UI",
};

export default function AiQuotaPage() {
  const [activeTab, setActiveTab] = useState<"INSTRUCTORS" | "LOGS">("INSTRUCTORS");
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  // Dữ liệu từ Backend
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [instructors, setInstructors] = useState<InstructorQuotaItem[]>([]);
  const [usageLogs, setUsageLogs] = useState<AiUsageLogItem[]>([]);
  const [logsPagination, setLogsPagination] = useState<PaginationData>({
    page: 1,
    page_size: 10,
    total_items: 0,
    total_pages: 1,
  });

  // Tìm kiếm giảng viên
  const [searchQuery, setSearchQuery] = useState("");

  // Modal điều chỉnh hạn ngạch giảng viên (PUT /api/v1/admin/users/:id)
  const [editingInstructor, setEditingInstructor] = useState<InstructorQuotaItem | null>(null);
  const [newQuotaValue, setNewQuotaValue] = useState<string>("");

  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(""), 5000);
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

  // Tải dữ liệu tổng quan và danh sách giảng viên
  const fetchData = useCallback(async (logPage = logsPagination.page) => {
    const { token, apiUrl } = getApiConfig();
    if (!token) {
      setErrorMessage("Chưa tìm thấy phiên đăng nhập. Vui lòng đăng nhập lại!");
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
        setErrorMessage("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại!");
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
      setErrorMessage("Lỗi kết nối tới máy chủ Backend NestJS.");
    } finally {
      setLoading(false);
    }
  }, [logsPagination.page, logsPagination.page_size]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Cập nhật hạn ngạch giảng viên qua PUT /api/v1/admin/users/:id
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
        setSuccessMessage(`Đã cập nhật hạn ngạch cho "${editingInstructor.full_name}" thành ${quotaNum.toLocaleString()} tokens/ngày!`);
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

  // Lọc danh sách giảng viên
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

  // Xuất file CSV danh sách hạn ngạch giảng viên
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

  // Xuất file CSV nhật ký AI
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

  return (
    <div className="flex flex-col w-full gap-5">
      {/* Alert thông báo */}
      {errorMessage && (
        <div className="flex items-center justify-between p-4 bg-red-50 border border-red-200 text-red-700 rounded-2xl text-xs font-semibold shadow-sm animate-in fade-in">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-600" />
            <span>{errorMessage}</span>
          </div>
          <button onClick={() => setErrorMessage("")} className="hover:text-red-900">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {successMessage && (
        <div className="flex items-center justify-between p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-2xl text-xs font-semibold shadow-sm animate-in fade-in">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0 text-emerald-600" />
            <span>{successMessage}</span>
          </div>
          <button onClick={() => setSuccessMessage("")} className="hover:text-emerald-950">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* ================= HEADER ================= */}
      <section className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
        <div className="flex flex-col gap-1.5">
          <nav className="flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-400">
            <span>Trang chủ</span>
            <span>/</span>
            <span className="text-[#F26F21]">Hạn ngạch AI</span>
          </nav>

          <div className="flex items-center gap-2.5 flex-wrap mt-0.5">
            <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">
              Giám Sát & Điều Phối Hạn Ngạch Gemini AI
            </h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-xs font-bold border border-emerald-200">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Backend Connected
            </span>
          </div>

          <p className="text-xs text-slate-400 mt-0.5">
            Theo dõi lưu lượng tiêu thụ Google Gemini AI thực tế và phân bổ hạn ngạch cho Giảng viên.
          </p>
        </div>

        <button
          onClick={() => fetchData()}
          disabled={loading}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 text-xs font-bold transition-all disabled:opacity-50 self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-[#F26F21]" : ""}`} />
          <span>Làm mới</span>
        </button>
      </section>

      {/* ================= THỐNG KÊ TỔNG QUAN (OVERVIEW) ================= */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Hạn mức toàn trường tháng */}
        <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              NGÂN SÁCH THÁNG
            </span>
            <div className="p-2 rounded-xl bg-blue-50 text-[#0054A6]">
              <Cpu className="w-4 h-4" />
            </div>
          </div>
          <div>
            <div className="text-2xl font-black text-slate-900">
              {(overview?.ai_token_usage?.total_budget_limit ?? 0).toLocaleString()}
            </div>
            <span className="text-[11px] text-slate-400">tokens / tháng toàn hệ thống</span>
          </div>
          <div className="mt-3 w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
            <div className="bg-[#0054A6] h-full rounded-full transition-all duration-500" style={{ width: `${usagePercentage}%` }} />
          </div>
        </div>

        {/* Card 2: Tiêu thụ tháng */}
        <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              ĐÃ TIÊU THỤ THÁNG
            </span>
            <div className="p-2 rounded-xl bg-orange-50 text-[#F26F21]">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div>
            <div className="text-2xl font-black text-[#F26F21]">
              {(overview?.ai_token_usage?.total_tokens_consumed_month ?? 0).toLocaleString()}
            </div>
            <span className="text-[11px] font-semibold text-slate-500">
              {usagePercentage}% ngân sách đã dùng
            </span>
          </div>
          <div className="mt-3 w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
            <div className="bg-[#F26F21] h-full rounded-full transition-all duration-500" style={{ width: `${usagePercentage}%` }} />
          </div>
        </div>

        {/* Card 3: Top tính năng */}
        <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              TÍNH NĂNG DÙNG NHIỀU NHẤT
            </span>
            <div className="p-2 rounded-xl bg-purple-50 text-purple-700">
              <FileCode className="w-4 h-4" />
            </div>
          </div>
          <div>
            <div className="text-sm font-extrabold text-slate-900 truncate" title={overview?.ai_token_usage?.top_consuming_feature ?? "Chưa ghi nhận"}>
              {overview?.ai_token_usage?.top_consuming_feature
                ? (FEATURE_NAMES[overview.ai_token_usage.top_consuming_feature] || overview.ai_token_usage.top_consuming_feature)
                : "Chưa ghi nhận"}
            </div>
            <span className="text-[11px] text-slate-400">dựa trên nhật ký sử dụng</span>
          </div>
          <div className="mt-3 text-[10px] text-purple-700 font-bold">
            Gemini AI Hub
          </div>
        </div>

        {/* Card 4: Tổng giảng viên */}
        <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              GIẢNG VIÊN CÓ HẠN NGẠCH
            </span>
            <div className="p-2 rounded-xl bg-emerald-50 text-emerald-600">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <div>
            <div className="text-2xl font-black text-slate-900">
              {overview?.total_instructors ?? instructors.length}
            </div>
            <span className="text-[11px] text-slate-400">tài khoản giảng viên hoạt động</span>
          </div>
          <div className="mt-3 text-[10px] text-emerald-600 font-bold">
            Quản trị viên phân phối
          </div>
        </div>
      </section>

      {/* ================= TAB CONTROLS ================= */}
      <div className="flex items-center gap-2 border-b border-slate-200">
        <button
          onClick={() => setActiveTab("INSTRUCTORS")}
          className={`flex items-center gap-2 pb-3 px-3 text-xs font-bold border-b-2 transition-all ${
            activeTab === "INSTRUCTORS"
              ? "border-[#F26F21] text-[#F26F21]"
              : "border-transparent text-slate-500 hover:text-slate-800"
          }`}
        >
          <Users className="w-4 h-4" />
          <span>Hạn Ngạch Giảng Viên ({instructors.length})</span>
        </button>

        <button
          onClick={() => setActiveTab("LOGS")}
          className={`flex items-center gap-2 pb-3 px-3 text-xs font-bold border-b-2 transition-all ${
            activeTab === "LOGS"
              ? "border-[#F26F21] text-[#F26F21]"
              : "border-transparent text-slate-500 hover:text-slate-800"
          }`}
        >
          <Layers className="w-4 h-4" />
          <span>Nhật Ký Gọi AI ({logsPagination.total_items})</span>
        </button>
      </div>

      {/* ================= TAB 1: BẢNG HẠN NGẠCH GIẢNG VIÊN ================= */}
      {activeTab === "INSTRUCTORS" && (
        <section className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden flex flex-col">
          {/* Header Bảng */}
          <div className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100">
            <div className="relative min-w-[240px] max-w-sm">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Tìm giảng viên theo tên, email..."
                className="w-full pl-9 pr-3 py-1.5 rounded-xl text-xs bg-slate-50 border border-slate-200 focus:outline-none focus:border-[#F26F21]"
              />
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs text-slate-400">
                Hiển thị {filteredInstructors.length} giảng viên
              </span>
              <button
                onClick={handleExportInstructorsCsv}
                disabled={instructors.length === 0}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 text-xs font-semibold transition-all disabled:opacity-40"
              >
                <Download className="w-3.5 h-3.5 text-emerald-600" />
                <span>Xuất CSV</span>
              </button>
            </div>
          </div>

          <div className="overflow-x-auto w-full">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-bold tracking-wider border-b border-slate-100">
                <tr>
                  <th className="px-5 py-3.5">GIẢNG VIÊN</th>
                  <th className="px-4 py-3.5">EMAIL</th>
                  <th className="px-4 py-3.5">HẠN NGẠCH NGÀY</th>
                  <th className="px-4 py-3.5">ĐÃ DÙNG HÔM NAY</th>
                  <th className="px-4 py-3.5">CÒN LẠI</th>
                  <th className="px-4 py-3.5">TIẾN ĐỘ</th>
                  <th className="px-5 py-3.5 text-right">THAO TÁC</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {loading ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center text-slate-400">
                      <div className="flex items-center justify-center gap-2">
                        <Loader2 className="w-5 h-5 text-[#F26F21] animate-spin" />
                        <span>Đang tải danh sách giảng viên...</span>
                      </div>
                    </td>
                  </tr>
                ) : filteredInstructors.length > 0 ? (
                  filteredInstructors.map((ins) => {
                    const limit = ins.daily_token_quota || 50000;
                    const used = ins.used_tokens_today || 0;
                    const remaining = Math.max(0, limit - used);
                    const pct = limit > 0 ? Math.min(100, Math.round((used / limit) * 100)) : 0;

                    return (
                      <tr key={ins.id} className="hover:bg-slate-50/80 transition-colors">
                        <td className="px-5 py-4">
                          <div className="font-bold text-slate-900">{ins.full_name}</div>
                          <div className="text-[10px] font-mono text-slate-400">@{ins.username}</div>
                        </td>
                        <td className="px-4 py-4 font-mono text-[11px] text-slate-500">
                          {ins.email}
                        </td>
                        <td className="px-4 py-4 font-bold text-slate-800">
                          {limit.toLocaleString()} <span className="text-[10px] text-slate-400 font-normal">tokens</span>
                        </td>
                        <td className="px-4 py-4 font-bold text-[#F26F21]">
                          {used.toLocaleString()} <span className="text-[10px] text-slate-400 font-normal">tokens</span>
                        </td>
                        <td className="px-4 py-4 font-bold text-emerald-700">
                          {remaining.toLocaleString()} <span className="text-[10px] text-slate-400 font-normal">tokens</span>
                        </td>
                        <td className="px-4 py-4 min-w-[140px]">
                          <div className="flex items-center justify-between text-[10px] font-bold mb-1">
                            <span className={pct >= 90 ? "text-red-600" : pct >= 60 ? "text-amber-600" : "text-emerald-600"}>
                              {pct}%
                            </span>
                          </div>
                          <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                            <div
                              className={`h-full rounded-full ${pct >= 90 ? "bg-red-500" : pct >= 60 ? "bg-amber-500" : "bg-emerald-500"}`}
                              style={{ width: `${pct}%` }}
                            />
                          </div>
                        </td>
                        <td className="px-5 py-4 text-right">
                          <button
                            onClick={() => {
                              setEditingInstructor(ins);
                              setNewQuotaValue(String(limit));
                            }}
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 text-xs font-bold transition-all ml-auto"
                          >
                            <Sliders className="w-3.5 h-3.5 text-[#F26F21]" />
                            <span>Điều chỉnh Quota</span>
                          </button>
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan={7} className="px-6 py-10 text-center text-slate-400">
                      Không tìm thấy giảng viên nào.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* ================= TAB 2: BẢNG NHẬT KÝ GỌI AI ================= */}
      {activeTab === "LOGS" && (
        <section className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden flex flex-col">
          {/* Header Bảng Nhật Ký */}
          <div className="p-4 flex items-center justify-between gap-3 border-b border-slate-100">
            <span className="text-xs font-bold text-slate-700">
              Nhật ký kiểm toán gọi API Google Gemini AI (Audit Trail)
            </span>
            <button
              onClick={handleExportLogsCsv}
              disabled={usageLogs.length === 0}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 text-xs font-semibold transition-all disabled:opacity-40"
            >
              <Download className="w-3.5 h-3.5 text-emerald-600" />
              <span>Xuất CSV</span>
            </button>
          </div>

          <div className="overflow-x-auto w-full">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-bold tracking-wider border-b border-slate-100">
                <tr>
                  <th className="px-5 py-3.5">GIẢNG VIÊN</th>
                  <th className="px-4 py-3.5">TÁC VỤ AI</th>
                  <th className="px-4 py-3.5">MÔ HÌNH</th>
                  <th className="px-4 py-3.5">PROMPT TOKENS</th>
                  <th className="px-4 py-3.5">COMPLETION TOKENS</th>
                  <th className="px-4 py-3.5">TỔNG TOKENS</th>
                  <th className="px-5 py-3.5 text-right">THỜI GIAN GỌI</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {loading ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center text-slate-400">
                      <div className="flex items-center justify-center gap-2">
                        <Loader2 className="w-5 h-5 text-[#F26F21] animate-spin" />
                        <span>Đang tải nhật ký...</span>
                      </div>
                    </td>
                  </tr>
                ) : usageLogs.length > 0 ? (
                  usageLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="px-5 py-4">
                        <div className="font-bold text-slate-900">{log.full_name}</div>
                        <div className="text-[10px] font-mono text-slate-400">@{log.username}</div>
                      </td>
                      <td className="px-4 py-4">
                        <span className="px-2 py-0.5 rounded-md bg-purple-50 text-purple-700 text-[10px] font-bold border border-purple-100">
                          {FEATURE_NAMES[log.feature_type] || log.feature_type}
                        </span>
                      </td>
                      <td className="px-4 py-4 font-mono text-[11px] text-slate-600">
                        {log.model_name}
                      </td>
                      <td className="px-4 py-4 text-slate-600">
                        {log.prompt_tokens.toLocaleString()}
                      </td>
                      <td className="px-4 py-4 text-slate-600">
                        {log.completion_tokens.toLocaleString()}
                      </td>
                      <td className="px-4 py-4 font-bold text-[#F26F21]">
                        {log.total_tokens.toLocaleString()}
                      </td>
                      <td className="px-5 py-4 text-right text-slate-400 text-[11px]">
                        {new Date(log.created_at).toLocaleString("vi-VN")}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={7} className="px-6 py-10 text-center text-slate-400">
                      Chưa có nhật ký tiêu thụ AI nào được ghi nhận.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* Phân trang Logs */}
          <div className="px-6 py-3.5 bg-white flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-slate-100 text-xs text-slate-500">
            <div>
              Trang <strong>{logsPagination.page}</strong> / <strong>{logsPagination.total_pages || 1}</strong>{" "}
              (Tổng cộng <strong>{logsPagination.total_items}</strong> lượt gọi AI)
            </div>

            <div className="flex items-center gap-1.5">
              <button
                onClick={() => fetchData(Math.max(1, logsPagination.page - 1))}
                disabled={logsPagination.page <= 1 || loading}
                className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-slate-600 bg-slate-50 hover:bg-slate-100 border border-slate-200 disabled:opacity-40 transition-colors font-medium"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
                <span>Trước</span>
              </button>

              <button
                onClick={() => fetchData(Math.min(logsPagination.total_pages, logsPagination.page + 1))}
                disabled={logsPagination.page >= (logsPagination.total_pages || 1) || loading}
                className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-slate-600 bg-slate-50 hover:bg-slate-100 border border-slate-200 disabled:opacity-40 transition-colors font-medium"
              >
                <span>Sau</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </section>
      )}

      {/* ================= MODAL ĐIỀU CHỈNH QUOTA GIẢNG VIÊN ================= */}
      {editingInstructor && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 border border-slate-200 animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-xl bg-orange-50 text-[#F26F21]">
                  <Sliders className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-extrabold text-slate-900 text-base">
                    Điều Chỉnh Hạn Ngạch AI
                  </h3>
                  <p className="text-xs text-slate-400">
                    Cập nhật giới hạn token/ngày cho giảng viên
                  </p>
                </div>
              </div>
              <button
                onClick={() => setEditingInstructor(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUpdateQuota} className="space-y-4 mt-4">
              <div>
                <label className="block text-[11px] font-bold text-slate-700 uppercase mb-1">
                  Giảng Viên
                </label>
                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs">
                  <span className="font-bold text-slate-900">{editingInstructor.full_name}</span>{" "}
                  <span className="text-slate-500">({editingInstructor.email})</span>
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-700 uppercase mb-1">
                  Hạn Ngạch Mới (Tokens/Ngày) <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  required
                  min={0}
                  step="any"
                  value={newQuotaValue}
                  onChange={(e) => setNewQuotaValue(e.target.value)}
                  placeholder="Nhập số token tùy ý..."
                  className="w-full px-3.5 py-2.5 rounded-xl text-xs bg-slate-50 border border-slate-200 focus:outline-none focus:border-[#F26F21] font-mono font-bold"
                />
                <p className="text-[10px] text-slate-400 mt-1">
                  Có thể tăng thêm hoặc thiết lập lại theo nhu cầu kiểm thử AI của giảng viên.
                </p>
              </div>

              <div className="flex items-center justify-end gap-2.5 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setEditingInstructor(null)}
                  disabled={isSubmitting}
                  className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs transition-colors"
                >
                  Hủy bỏ
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#F26F21] hover:bg-[#D95A0E] text-white font-bold text-xs shadow-md shadow-orange-500/20 disabled:opacity-50 transition-all"
                >
                  {isSubmitting && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  <span>Lưu Hạn Ngạch</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
