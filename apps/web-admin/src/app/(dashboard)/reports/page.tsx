"use client";

import React, { useState, useEffect, useCallback, useMemo } from "react";
import {
  FileText,
  Search,
  RotateCw,
  Download,
  FileSpreadsheet,
  Filter,
  Eye,
  ChevronLeft,
  ChevronRight,
  X,
  AlertCircle,
  CheckCircle2,
  Cpu,
  Users,
  Layers,
  Calendar,
  Sparkles,
  BarChart3,
  Clock,
  ShieldCheck,
  Hash,
} from "lucide-react";

// ==========================================
// ĐỊNH NGHĨA DỮ LIỆU CHUẨN TỪ CENTRAL BACKEND
// ==========================================

export interface AiUsageLogItem {
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

export interface PaginationMeta {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
}

export interface OverviewMetrics {
  total_instructors: number;
  ai_token_usage: {
    total_tokens_consumed_month: number;
    total_budget_limit: number;
    top_consuming_feature: string | null;
  };
}

export interface InstructorOption {
  id: string;
  username: string;
  full_name: string;
}

// Bảng ánh xạ tên tiếng Việt cho các tính năng AI
const FEATURE_MAP: Record<string, { label: string; color: string; bg: string }> = {
  GENERATE_TESTCASES: {
    label: "Sinh Testcase Tự Động",
    color: "text-blue-700",
    bg: "bg-blue-50 border-blue-200",
  },
  REVIEW_CODE: {
    label: "Đánh Giá & Review Code",
    color: "text-emerald-700",
    bg: "bg-emerald-50 border-emerald-200",
  },
  VERIFY_PLAGIARISM: {
    label: "Kiểm Tra Đạo Văn Code",
    color: "text-purple-700",
    bg: "bg-purple-50 border-purple-200",
  },
  EVALUATE_WEB_UI: {
    label: "Đánh Giá Giao Diện Web",
    color: "text-amber-700",
    bg: "bg-amber-50 border-amber-200",
  },
};

export default function ReportsPage() {
  // ==========================================
  // STATE MANAGEMENT
  // ==========================================
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  // Dữ liệu từ Backend NestJS
  const [overview, setOverview] = useState<OverviewMetrics | null>(null);
  const [logs, setLogs] = useState<AiUsageLogItem[]>([]);
  const [pagination, setPagination] = useState<PaginationMeta>({
    page: 1,
    page_size: 15,
    total_items: 0,
    total_pages: 1,
  });
  const [instructors, setInstructors] = useState<InstructorOption[]>([]);

  // Bộ lọc kết nối API
  const [selectedUserId, setSelectedUserId] = useState<string>("ALL");
  const [selectedFeature, setSelectedFeature] = useState<string>("ALL");
  const [fromDate, setFromDate] = useState<string>("");
  const [toDate, setToDate] = useState<string>("");
  const [searchKeyword, setSearchKeyword] = useState<string>("");

  // Modals & Chi tiết
  const [selectedLog, setSelectedLog] = useState<AiUsageLogItem | null>(null);
  const [showExportModal, setShowExportModal] = useState(false);

  // Helper lấy cấu hình API
  const getApiConfig = () => {
    const token = typeof window !== "undefined" ? localStorage.getItem("aita_access_token") : null;
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000/api/v1";
    return { token, apiUrl };
  };

  // Tự tắt thông báo sau vài giây
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

  // ==========================================
  // FETCH DANH SÁCH GIẢNG VIÊN (ĐỂ LỌC USER_ID)
  // ==========================================
  const fetchInstructors = useCallback(async () => {
    const { token, apiUrl } = getApiConfig();
    if (!token) return;

    try {
      const res = await fetch(`${apiUrl}/admin/users?role=INSTRUCTOR&page_size=100`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const json = await res.json();
        if (json.success && json.data?.items) {
          setInstructors(
            json.data.items.map((u: any) => ({
              id: u.id,
              username: u.username,
              full_name: u.full_name,
            }))
          );
        }
      }
    } catch {
      // Bỏ qua lỗi phụ khi tải danh sách lọc
    }
  }, []);

  // ==========================================
  // FETCH DỮ LIỆU CHÍNH TỪ CENTRAL BACKEND
  // ==========================================
  const fetchReportsData = useCallback(
    async (targetPage = pagination.page) => {
      const { token, apiUrl } = getApiConfig();
      if (!token) {
        setErrorMessage("Chưa tìm thấy phiên đăng nhập. Vui lòng đăng nhập lại!");
        setLoading(false);
        return;
      }

      setLoading(true);
      setErrorMessage("");

      try {
        // 1. Gọi GET /admin/reports/overview
        const overviewPromise = fetch(`${apiUrl}/admin/reports/overview`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        // 2. Xây dựng Query Params cho GET /admin/reports/ai-usage
        const queryParams = new URLSearchParams();
        queryParams.set("page", String(targetPage));
        queryParams.set("page_size", String(pagination.page_size));

        if (selectedUserId && selectedUserId !== "ALL") {
          queryParams.set("user_id", selectedUserId);
        }
        if (fromDate) {
          queryParams.set("from", new Date(fromDate).toISOString());
        }
        if (toDate) {
          // Đến cuối ngày đã chọn
          const endOfDay = new Date(toDate);
          endOfDay.setHours(23, 59, 59, 999);
          queryParams.set("to", endOfDay.toISOString());
        }

        const logsPromise = fetch(`${apiUrl}/admin/reports/ai-usage?${queryParams.toString()}`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        const [resOverview, resLogs] = await Promise.all([overviewPromise, logsPromise]);

        if (resOverview.ok) {
          const overviewJson = await resOverview.json();
          if (overviewJson.success && overviewJson.data) {
            setOverview(overviewJson.data);
          }
        }

        if (resLogs.ok) {
          const logsJson = await resLogs.json();
          if (logsJson.success && logsJson.data) {
            setLogs(logsJson.data.items || []);
            if (logsJson.data.pagination) {
              setPagination(logsJson.data.pagination);
            }
          }
        } else {
          const errJson = await resLogs.json().catch(() => ({}));
          setErrorMessage(errJson.message || "Không thể tải nhật ký báo cáo từ Backend.");
        }
      } catch {
        setErrorMessage("Lỗi kết nối tới máy chủ Central Backend.");
      } finally {
        setLoading(false);
      }
    },
    [pagination.page, pagination.page_size, selectedUserId, fromDate, toDate]
  );

  // Khởi tạo dữ liệu
  useEffect(() => {
    fetchInstructors();
  }, [fetchInstructors]);

  useEffect(() => {
    fetchReportsData(1);
  }, [fetchReportsData]);

  // ==========================================
  // LỌC CLIENT-SIDE THEO TÍNH NĂNG VÀ TỪ KHÓA
  // ==========================================
  const displayedLogs = useMemo(() => {
    return logs.filter((log) => {
      // Lọc theo tính năng
      if (selectedFeature !== "ALL" && log.feature_type !== selectedFeature) {
        return false;
      }
      // Lọc theo từ khóa tìm kiếm
      if (searchKeyword.trim() !== "") {
        const kw = searchKeyword.toLowerCase();
        const matchName = log.full_name?.toLowerCase().includes(kw);
        const matchUsername = log.username?.toLowerCase().includes(kw);
        const matchFeature = log.feature_type?.toLowerCase().includes(kw);
        const matchModel = log.model_name?.toLowerCase().includes(kw);
        const matchId = log.id?.toLowerCase().includes(kw);
        return matchName || matchUsername || matchFeature || matchModel || matchId;
      }
      return true;
    });
  }, [logs, selectedFeature, searchKeyword]);

  // Tính toán thống kê tỷ trọng từ danh sách logs thực tế
  const featureDistribution = useMemo(() => {
    if (!logs || logs.length === 0) return [];
    const counts: Record<string, { count: number; tokens: number }> = {};
    let totalTokens = 0;

    logs.forEach((item) => {
      const feat = item.feature_type || "UNKNOWN";
      if (!counts[feat]) counts[feat] = { count: 0, tokens: 0 };
      counts[feat].count += 1;
      counts[feat].tokens += item.total_tokens || 0;
      totalTokens += item.total_tokens || 0;
    });

    return Object.entries(counts).map(([feat, data]) => ({
      feature: feat,
      label: FEATURE_MAP[feat]?.label || feat,
      count: data.count,
      tokens: data.tokens,
      percentage: totalTokens > 0 ? Math.round((data.tokens / totalTokens) * 100) : 0,
    }));
  }, [logs]);

  // Reset bộ lọc
  const handleResetFilters = () => {
    setSelectedUserId("ALL");
    setSelectedFeature("ALL");
    setFromDate("");
    setToDate("");
    setSearchKeyword("");
    fetchReportsData(1);
    setSuccessMessage("Đã đặt lại bộ lọc tìm kiếm.");
  };

  // ==========================================
  // XUẤT FILE THỰC TẾ (JSON / CSV)
  // ==========================================
  const handleDownloadJson = () => {
    const exportData = {
      report_title: "AITA - Báo Cáo Nhật Ký Sử Dụng AI & Kiểm Toán",
      exported_at: new Date().toISOString(),
      overview_metrics: overview,
      total_exported_records: displayedLogs.length,
      logs: displayedLogs,
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `aita_ai_usage_reports_${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    setSuccessMessage("Đã tải tệp JSON báo cáo thành công!");
  };

  const handleExportCsv = () => {
    const headers = [
      "Mã Nhật Ký (ID)",
      "Thời Gian",
      "Giảng Viên (Họ Tên)",
      "Tên Đăng Nhập",
      "Mã Giảng Viên (User ID)",
      "Tính Năng AI",
      "Mô Hình (Model)",
      "Prompt Tokens",
      "Completion Tokens",
      "Tổng Tokens Tiêu Thụ",
    ];

    const rows = displayedLogs.map((log) => [
      `"${log.id}"`,
      `"${new Date(log.created_at).toLocaleString("vi-VN")}"`,
      `"${log.full_name || ""}"`,
      `"${log.username || ""}"`,
      `"${log.user_id}"`,
      `"${FEATURE_MAP[log.feature_type]?.label || log.feature_type}"`,
      `"${log.model_name}"`,
      log.prompt_tokens,
      log.completion_tokens,
      log.total_tokens,
    ]);

    const csvContent = "\uFEFF" + [headers.join(","), ...rows.map((e) => e.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `aita_ai_usage_reports_${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    setShowExportModal(false);
    setSuccessMessage("Đã xuất báo cáo CSV thành công!");
  };

  // Tính tỷ lệ ngân sách tiêu thụ
  const totalTokensConsumed = overview?.ai_token_usage?.total_tokens_consumed_month ?? 0;
  const totalBudgetLimit = overview?.ai_token_usage?.total_budget_limit ?? 1;
  const budgetPercentage = Math.min(100, Math.round((totalTokensConsumed / totalBudgetLimit) * 100));

  return (
    <div className="space-y-6 pb-12">
      {/* Toast thông báo */}
      {successMessage && (
        <div className="flex items-center gap-2 p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs font-medium animate-in fade-in">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{successMessage}</span>
        </div>
      )}

      {errorMessage && (
        <div className="flex items-center gap-2 p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg text-xs font-medium animate-in fade-in">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* ==========================================
          HEADER TRANG & CÁC NÚT THAO TÁC
      ========================================== */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="text-xs text-slate-500 font-medium mb-1 flex items-center gap-1.5">
            <span>Trang chủ</span>
            <span>/</span>
            <span className="text-slate-800 font-semibold">Báo cáo & Kiểm toán sử dụng AI</span>
          </div>

          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              Báo Cáo & Nhật Ký Kiểm Toán (Audit Trail)
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-blue-50 text-blue-700 border border-blue-200 flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-blue-600" />
              Dữ liệu thời gian thực
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Theo dõi toàn bộ lịch sử gọi API Gemini, kiểm toán lượng token tiêu thụ và thống kê hạn ngạch giảng viên từ Central Backend.
          </p>
        </div>

        {/* Nút thao tác */}
        <div className="flex items-center gap-2.5 shrink-0">
          <button
            onClick={() => fetchReportsData(pagination.page)}
            disabled={loading}
            title="Làm mới dữ liệu từ máy chủ"
            className="p-2 bg-white hover:bg-slate-50 border border-slate-200 rounded-lg text-slate-600 hover:text-slate-900 transition shadow-sm active:scale-95 disabled:opacity-50"
          >
            <RotateCw className={`w-4 h-4 ${loading ? "animate-spin text-orange-500" : ""}`} />
          </button>

          <button
            onClick={handleDownloadJson}
            className="flex items-center gap-2 px-3 py-2 bg-white hover:bg-slate-50 border border-slate-200 rounded-lg text-xs font-semibold text-slate-700 hover:text-slate-900 transition shadow-sm"
          >
            <Download className="w-4 h-4 text-slate-500" />
            <span>Tải Dữ Liệu (JSON)</span>
          </button>

          <button
            onClick={() => setShowExportModal(true)}
            className="flex items-center gap-2 px-3.5 py-2 bg-gradient-to-r from-orange-500 to-amber-600 hover:from-orange-600 hover:to-amber-700 text-white rounded-lg text-xs font-bold transition shadow-sm shadow-orange-500/20 active:scale-95"
          >
            <FileSpreadsheet className="w-4 h-4" />
            <span>Xuất Báo Cáo (Excel / In)</span>
          </button>
        </div>
      </div>

      {/* ==========================================
          4 THẺ KPI TÍNH TOÁN TRỰC TIẾP TỪ BACKEND
      ========================================== */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1: Tổng bản ghi nhật ký */}
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
              TỔNG BẢN GHI NHẬT KÝ
            </span>
            <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
              <FileText className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-slate-900 tracking-tight">
            {pagination.total_items.toLocaleString()}
          </div>
          <div className="mt-2 text-xs text-slate-500">
            Trang {pagination.page} / {pagination.total_pages || 1}
          </div>
        </div>

        {/* KPI 2: Tổng token tiêu thụ trong tháng */}
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
              TOKEN ĐÃ DÙNG (THÁNG NÀY)
            </span>
            <div className="w-8 h-8 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center">
              <Cpu className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-purple-700 tracking-tight">
            {totalTokensConsumed.toLocaleString()}
          </div>
          <div className="mt-2 text-xs text-slate-500 flex items-center justify-between">
            <span>Chiếm {budgetPercentage}% định mức tháng</span>
          </div>
        </div>

        {/* KPI 3: Tổng ngân sách định mức tháng */}
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
              TỔNG ĐỊNH MỨC THÁNG
            </span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <Sparkles className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-slate-900 tracking-tight">
            {(overview?.ai_token_usage?.total_budget_limit || 0).toLocaleString()}
          </div>
          <div className="mt-2 text-xs text-emerald-600 font-semibold">
            Áp dụng cho toàn bộ giảng viên
          </div>
        </div>

        {/* KPI 4: Tổng số giảng viên */}
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
              TỔNG GIẢNG VIÊN HỆ THỐNG
            </span>
            <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-slate-900 tracking-tight">
            {overview?.total_instructors ?? instructors.length}
          </div>
          <div className="mt-2 text-xs text-slate-500">
            Top tính năng:{" "}
            <span className="font-semibold text-slate-700">
              {FEATURE_MAP[overview?.ai_token_usage?.top_consuming_feature || ""]?.label ||
                overview?.ai_token_usage?.top_consuming_feature ||
                "Chưa có"}
            </span>
          </div>
        </div>
      </div>

      {/* ==========================================
          2 KHỐI THỐNG KÊ PHÂN TÍCH TỪ BACKEND
      ========================================== */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Khối Trái: Tiến độ ngân sách Token trong tháng */}
        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-orange-50 text-orange-600 flex items-center justify-center">
                  <BarChart3 className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900">
                    Tình Hình Tiêu Thụ Hạn Ngạch Token Tháng Này
                  </h3>
                  <p className="text-[11px] text-slate-500">
                    Dữ liệu tổng hợp từ bảng ai_quota_logs và ai_quota_configs
                  </p>
                </div>
              </div>
            </div>

            <div className="p-4 bg-slate-50 rounded-xl border border-slate-100 space-y-3 mt-3">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-700">Tỷ lệ tiêu thụ định mức:</span>
                <span className="font-bold text-purple-700">{budgetPercentage}%</span>
              </div>
              <div className="w-full h-3 bg-slate-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-purple-500 to-indigo-600 rounded-full transition-all duration-500"
                  style={{ width: `${budgetPercentage}%` }}
                />
              </div>
              <div className="flex items-center justify-between text-[11px] text-slate-500">
                <span>Đã dùng: {totalTokensConsumed.toLocaleString()} tokens</span>
                <span>Định mức: {(overview?.ai_token_usage?.total_budget_limit || 0).toLocaleString()} tokens</span>
              </div>
            </div>
          </div>

          <div className="mt-4 p-3 rounded-lg bg-blue-50 border border-blue-200/80 text-[11px] text-blue-900 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-blue-600 shrink-0" />
            <span>
              Mỗi tác vụ gọi Google Gemini đều được hệ thống tự động kiểm tra Quota và lưu trữ nhật ký đối soát chi tiết.
            </span>
          </div>
        </div>

        {/* Khối Phải: Phân bổ tỷ trọng các tính năng AI */}
        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
                  <Layers className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900">Phân Loại Tính Năng AI Tiêu Thụ</h3>
                  <p className="text-[11px] text-slate-500">
                    Phân bổ tỷ trọng token thực tế của các bản ghi hiện tại
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-2.5 mt-2">
              {featureDistribution.length === 0 ? (
                <div className="py-6 text-center text-slate-400 text-xs">
                  Chưa có dữ liệu gọi API AI trong khoảng thời gian này.
                </div>
              ) : (
                featureDistribution.map((item) => (
                  <div
                    key={item.feature}
                    className="flex items-center justify-between text-xs py-2 border-b border-slate-100 last:border-b-0"
                  >
                    <div className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-blue-600 shrink-0" />
                      <span className="font-medium text-slate-700">{item.label}</span>
                    </div>
                    <div className="text-right">
                      <span className="font-bold text-slate-900">{item.percentage}%</span>{" "}
                      <span className="text-slate-400 text-[11px]">
                        ({item.tokens.toLocaleString()} tokens - {item.count} lượt)
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="mt-4 text-[11px] text-slate-400 text-right">
            Tính năng tiêu tốn nhất:{" "}
            <span className="font-semibold text-slate-600">
              {FEATURE_MAP[overview?.ai_token_usage?.top_consuming_feature || ""]?.label ||
                overview?.ai_token_usage?.top_consuming_feature ||
                "N/A"}
            </span>
          </div>
        </div>
      </div>

      {/* ==========================================
          BỘ LỌC TÌM KIẾM NHẬT KÝ THỰC TẾ
      ========================================== */}
      <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-700 uppercase tracking-wider">
            <Filter className="w-4 h-4 text-slate-500" />
            <span>BỘ LỌC TÌM KIẾM BÁO CÁO & KIỂM TOÁN</span>
          </div>
          <button
            onClick={handleResetFilters}
            className="text-xs text-slate-500 hover:text-slate-800 font-semibold transition"
          >
            Đặt lại bộ lọc
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {/* Ô tìm kiếm từ khóa */}
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchKeyword}
              onChange={(e) => setSearchKeyword(e.target.value)}
              placeholder="Tìm theo tên GV, model, ID..."
              className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
            />
          </div>

          {/* Lọc theo Giảng viên (user_id) */}
          <div>
            <select
              value={selectedUserId}
              onChange={(e) => setSelectedUserId(e.target.value)}
              className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
            >
              <option value="ALL">Giảng viên: Tất cả</option>
              {instructors.map((ins) => (
                <option key={ins.id} value={ins.id}>
                  {ins.full_name} (@{ins.username})
                </option>
              ))}
            </select>
          </div>

          {/* Lọc theo Tính năng AI */}
          <div>
            <select
              value={selectedFeature}
              onChange={(e) => setSelectedFeature(e.target.value)}
              className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
            >
              <option value="ALL">Tính năng AI: Tất cả</option>
              <option value="GENERATE_TESTCASES">Sinh Testcase Tự Động</option>
              <option value="REVIEW_CODE">Đánh Giá & Review Code</option>
              <option value="VERIFY_PLAGIARISM">Kiểm Tra Đạo Văn Code</option>
              <option value="EVALUATE_WEB_UI">Đánh Giá Giao Diện Web</option>
            </select>
          </div>

          {/* Lọc từ ngày (from) */}
          <div className="relative">
            <input
              type="date"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              title="Từ ngày"
              className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
            />
          </div>

          {/* Lọc đến ngày (to) */}
          <div className="relative">
            <input
              type="date"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              title="Đến ngày"
              className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
            />
          </div>
        </div>
      </div>

      {/* ==========================================
          BẢNG NHẬT KÝ SỰ KIỆN THẬT TỪ DATABASE
      ========================================== */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-50/50">
          <div className="flex items-center gap-2.5">
            <h2 className="text-sm font-bold text-slate-900">
              Nhật Ký Sử Dụng AI & Kiểm Toán Hệ Thống
            </h2>
            <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-slate-200/80 text-slate-700">
              {pagination.total_items.toLocaleString()} bản ghi từ CSDL
            </span>
          </div>

          <div className="text-xs text-slate-500 flex items-center gap-2">
            <span>Hiển thị trang</span>
            <span className="font-bold text-slate-800">{pagination.page}</span>
            <span>/</span>
            <span>{pagination.total_pages || 1}</span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50/70 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                <th className="py-3 px-4">MÃ BẢN GHI</th>
                <th className="py-3 px-4">THỜI GIAN</th>
                <th className="py-3 px-4">GIẢNG VIÊN (ACTOR)</th>
                <th className="py-3 px-4">TÍNH NĂNG AI</th>
                <th className="py-3 px-4">MÔ HÌNH</th>
                <th className="py-3 px-4 text-right">PROMPT / COMPLETION</th>
                <th className="py-3 px-4 text-right">TỔNG TOKENS</th>
                <th className="py-3 px-4 text-center">CHI TIẾT</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    <RotateCw className="w-6 h-6 mx-auto animate-spin text-orange-500 mb-2" />
                    <span>Đang tải nhật ký kiểm toán từ máy chủ...</span>
                  </td>
                </tr>
              ) : displayedLogs.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    <AlertCircle className="w-8 h-8 mx-auto text-slate-300 mb-2" />
                    <span>Không có bản ghi nhật ký nào phù hợp với bộ lọc.</span>
                  </td>
                </tr>
              ) : (
                displayedLogs.map((log) => {
                  const featureInfo = FEATURE_MAP[log.feature_type] || {
                    label: log.feature_type,
                    color: "text-slate-700",
                    bg: "bg-slate-100 border-slate-200",
                  };

                  return (
                    <tr
                      key={log.id}
                      className="hover:bg-slate-50/80 transition-colors cursor-pointer"
                      onClick={() => setSelectedLog(log)}
                    >
                      {/* Mã log rút gọn */}
                      <td className="py-3 px-4 font-mono font-semibold text-blue-600 text-xs">
                        #{log.id.slice(0, 8)}...
                      </td>

                      {/* Thời gian */}
                      <td className="py-3 px-4 whitespace-nowrap text-slate-600">
                        {new Date(log.created_at).toLocaleString("vi-VN")}
                      </td>

                      {/* Giảng viên */}
                      <td className="py-3 px-4 whitespace-nowrap">
                        <div className="font-semibold text-slate-900">{log.full_name || "Chưa đặt tên"}</div>
                        <div className="text-[11px] text-slate-400 font-mono">@{log.username}</div>
                      </td>

                      {/* Tính năng AI */}
                      <td className="py-3 px-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-0.5 rounded text-[11px] font-semibold border ${featureInfo.bg} ${featureInfo.color}`}
                        >
                          {featureInfo.label}
                        </span>
                      </td>

                      {/* Mô hình */}
                      <td className="py-3 px-4 font-mono text-[11px] text-slate-600 whitespace-nowrap">
                        {log.model_name}
                      </td>

                      {/* Prompt / Completion */}
                      <td className="py-3 px-4 text-right font-mono text-slate-600 whitespace-nowrap">
                        {log.prompt_tokens.toLocaleString()} / {log.completion_tokens.toLocaleString()}
                      </td>

                      {/* Tổng tokens */}
                      <td className="py-3 px-4 text-right font-mono font-bold text-slate-900 whitespace-nowrap">
                        {log.total_tokens.toLocaleString()}
                      </td>

                      {/* Nút xem chi tiết */}
                      <td className="py-3 px-4 text-center whitespace-nowrap">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedLog(log);
                          }}
                          className="p-1.5 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition"
                          title="Xem chi tiết"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Phân trang */}
        <div className="p-4 border-t border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-slate-500 bg-white">
          <div>
            Hiển thị{" "}
            <span className="font-bold text-slate-800">
              {displayedLogs.length > 0 ? (pagination.page - 1) * pagination.page_size + 1 : 0}
            </span>{" "}
            -{" "}
            <span className="font-bold text-slate-800">
              {Math.min(pagination.page * pagination.page_size, pagination.total_items)}
            </span>{" "}
            trong tổng số <span className="font-bold text-slate-800">{pagination.total_items}</span> bản ghi
          </div>

          <div className="flex items-center gap-1.5 self-center">
            <button
              onClick={() => fetchReportsData(pagination.page - 1)}
              disabled={pagination.page <= 1 || loading}
              className="p-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>

            <span className="px-3 py-1 font-semibold text-slate-700 bg-slate-100 rounded-lg">
              Trang {pagination.page} / {pagination.total_pages || 1}
            </span>

            <button
              onClick={() => fetchReportsData(pagination.page + 1)}
              disabled={pagination.page >= pagination.total_pages || loading}
              className="p-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* ==========================================
          MODAL CHI TIẾT BẢN GHI (LOG DETAIL MODAL)
      ========================================== */}
      {selectedLog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white w-full max-w-xl rounded-2xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]">
            <div className="p-4 px-6 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center font-mono font-bold text-xs">
                  LOG
                </div>
                <div>
                  <h3 className="font-bold text-slate-900 text-sm">Chi Tiết Nhật Ký Sử Dụng AI</h3>
                  <p className="text-[11px] text-slate-500 font-mono">{selectedLog.id}</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedLog(null)}
                className="p-1 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-200/50 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto space-y-4 text-xs text-slate-700">
              <div className="grid grid-cols-2 gap-3 p-3.5 bg-slate-50 rounded-xl border border-slate-200/70">
                <div>
                  <span className="text-[10px] text-slate-400 font-bold uppercase">Thời gian gọi:</span>
                  <div className="font-semibold text-slate-900 mt-0.5">
                    {new Date(selectedLog.created_at).toLocaleString("vi-VN")}
                  </div>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 font-bold uppercase">Mô hình AI:</span>
                  <div className="font-mono text-slate-900 mt-0.5 font-semibold">
                    {selectedLog.model_name}
                  </div>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 font-bold uppercase">Giảng viên (Actor):</span>
                  <div className="font-semibold text-slate-900 mt-0.5">{selectedLog.full_name}</div>
                  <div className="text-[11px] text-slate-500 font-mono">@{selectedLog.username}</div>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 font-bold uppercase">Mã User ID:</span>
                  <div className="font-mono text-[11px] text-slate-600 truncate mt-0.5">
                    {selectedLog.user_id}
                  </div>
                </div>
              </div>

              <div>
                <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-1">
                  Tính năng thực thi:
                </label>
                <div className="p-3 bg-white border border-slate-200 rounded-lg font-semibold text-slate-800">
                  {FEATURE_MAP[selectedLog.feature_type]?.label || selectedLog.feature_type}
                </div>
              </div>

              <div>
                <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-1">
                  Chi tiết phân bổ Tokens:
                </label>
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="p-2.5 bg-blue-50 border border-blue-200 rounded-lg">
                    <span className="text-[10px] text-blue-600 font-bold uppercase block">Prompt</span>
                    <span className="font-mono font-bold text-blue-900 text-sm">
                      {selectedLog.prompt_tokens.toLocaleString()}
                    </span>
                  </div>
                  <div className="p-2.5 bg-emerald-50 border border-emerald-200 rounded-lg">
                    <span className="text-[10px] text-emerald-600 font-bold uppercase block">Completion</span>
                    <span className="font-mono font-bold text-emerald-900 text-sm">
                      {selectedLog.completion_tokens.toLocaleString()}
                    </span>
                  </div>
                  <div className="p-2.5 bg-purple-50 border border-purple-200 rounded-lg">
                    <span className="text-[10px] text-purple-600 font-bold uppercase block">Tổng cộng</span>
                    <span className="font-mono font-bold text-purple-900 text-sm">
                      {selectedLog.total_tokens.toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div className="p-4 border-t border-slate-200 bg-slate-50 flex justify-end">
              <button
                onClick={() => setSelectedLog(null)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white font-semibold rounded-lg text-xs transition"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ==========================================
          MODAL XUẤT BÁO CÁO (EXCEL / IN)
      ========================================== */}
      {showExportModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white w-full max-w-md rounded-2xl shadow-2xl border border-slate-200 overflow-hidden">
            <div className="p-4 px-6 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <div className="flex items-center gap-2">
                <FileSpreadsheet className="w-4 h-4 text-orange-600" />
                <h3 className="font-bold text-slate-900 text-sm">Xuất Báo Cáo Kiểm Toán</h3>
              </div>
              <button
                onClick={() => setShowExportModal(false)}
                className="p-1 text-slate-400 hover:text-slate-700 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-4 text-xs text-slate-600">
              <p>
                Chọn định dạng xuất dữ liệu cho <b>{displayedLogs.length}</b> bản ghi nhật ký hiện đang hiển thị:
              </p>

              <div className="space-y-3">
                <button
                  onClick={handleExportCsv}
                  className="w-full p-3.5 border border-slate-200 hover:border-emerald-500 hover:bg-emerald-50/50 rounded-xl flex items-center justify-between text-left transition group"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
                      CSV
                    </div>
                    <div>
                      <div className="font-bold text-slate-900 group-hover:text-emerald-800">
                        Bảng Tính Excel (.CSV UTF-8)
                      </div>
                      <div className="text-[11px] text-slate-400">
                        Mở trực tiếp trên Microsoft Excel, Google Sheets không lỗi font
                      </div>
                    </div>
                  </div>
                  <Download className="w-4 h-4 text-slate-400 group-hover:text-emerald-600" />
                </button>

                <button
                  onClick={() => {
                    setShowExportModal(false);
                    window.print();
                  }}
                  className="w-full p-3.5 border border-slate-200 hover:border-orange-500 hover:bg-orange-50/50 rounded-xl flex items-center justify-between text-left transition group"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-orange-100 text-orange-700 flex items-center justify-center font-bold">
                      IN
                    </div>
                    <div>
                      <div className="font-bold text-slate-900 group-hover:text-orange-800">
                        In Báo Cáo Khảo Thí (Print PDF)
                      </div>
                      <div className="text-[11px] text-slate-400">
                        In trực tiếp ra giấy hoặc lưu định dạng PDF
                      </div>
                    </div>
                  </div>
                  <FileText className="w-4 h-4 text-slate-400 group-hover:text-orange-600" />
                </button>
              </div>
            </div>

            <div className="p-4 border-t border-slate-200 bg-slate-50 flex justify-end">
              <button
                onClick={() => setShowExportModal(false)}
                className="px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 font-semibold rounded-lg text-xs"
              >
                Hủy bỏ
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
