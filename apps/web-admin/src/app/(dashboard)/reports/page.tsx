"use client";

import React, { useState, useEffect, useCallback, useMemo } from "react";
import Link from "next/link";
import useSWR from "swr";
import { swrFetcher, API_URL } from "@/lib/api";
import { Loader2 } from "lucide-react";

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

const EMPTY_TEXT = "Chưa có dữ liệu";

// Bảng ánh xạ tên tiếng Việt cho các tính năng AI
const FEATURE_MAP: Record<string, { label: string; color: string; bg: string }> = {
  GENERATE_TESTCASES: {
    label: "Sinh testcase tự động",
    color: "text-primary",
    bg: "bg-primary-bg",
  },
  REVIEW_CODE: {
    label: "Đánh giá & review code",
    color: "text-emerald-700",
    bg: "bg-emerald-50",
  },
  VERIFY_PLAGIARISM: {
    label: "Kiểm tra đạo văn",
    color: "text-amber-700",
    bg: "bg-amber-50",
  },
  EVALUATE_WEB_UI: {
    label: "Đánh giá giao diện web",
    color: "text-sky-700",
    bg: "bg-sky-50",
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
  const { data: overview, mutate: mutateOverview } = useSWR<OverviewMetrics>(
    "/admin/reports/overview",
    swrFetcher,
    { revalidateOnFocus: false, shouldRetryOnError: false, dedupingInterval: 30000 }
  );
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
    return { token, apiUrl: API_URL };
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
          const endOfDay = new Date(toDate);
          endOfDay.setHours(23, 59, 59, 999);
          queryParams.set("to", endOfDay.toISOString());
        }

        const resLogs = await fetch(`${apiUrl}/admin/reports/ai-usage?${queryParams.toString()}`, {
          headers: { Authorization: `Bearer ${token}` },
        });

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
          setErrorMessage(errJson.message || "Không thể tải nhật ký báo cáo từ máy chủ.");
        }
      } catch {
        setErrorMessage("Lỗi kết nối tới máy chủ Central Backend.");
      } finally {
        setLoading(false);
      }
    },
    [pagination.page, pagination.page_size, selectedUserId, fromDate, toDate]
  );

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
      if (selectedFeature !== "ALL" && log.feature_type !== selectedFeature) {
        return false;
      }
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
    mutateOverview();
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
    setSuccessMessage("Đã tải tệp JSON báo cáo thành công.");
  };

  const handleExportCsv = () => {
    const headers = [
      "Mã nhật ký (ID)",
      "Thời gian",
      "Giảng viên",
      "Tên đăng nhập",
      "Mã người dùng (User ID)",
      "Tính năng AI",
      "Mô hình",
      "Prompt Tokens",
      "Completion Tokens",
      "Tổng Tokens",
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
    setSuccessMessage("Đã xuất báo cáo CSV thành công.");
  };

  // Tính tỷ lệ ngân sách tiêu thụ
  const totalTokensConsumed = overview?.ai_token_usage?.total_tokens_consumed_month ?? 0;
  const totalBudgetLimit = overview?.ai_token_usage?.total_budget_limit ?? 1;
  const budgetPercentage = Math.min(100, Math.round((totalTokensConsumed / totalBudgetLimit) * 100));

  const hasRecords = pagination.total_items > 0;

  const topFeatureLabel =
    FEATURE_MAP[overview?.ai_token_usage?.top_consuming_feature || ""]?.label ||
    overview?.ai_token_usage?.top_consuming_feature ||
    EMPTY_TEXT;

  return (
    <div className="flex flex-col w-full gap-6 pb-12">
      {/* Toast thông báo lỗi */}
      {errorMessage && (
        <div className="flex items-center justify-between p-3.5 bg-rose-50 border border-rose-200 text-rose-700 rounded-lg text-[13px] font-medium animate-in fade-in">
          <span>{errorMessage}</span>
          <button onClick={() => setErrorMessage("")} className="font-medium hover:text-rose-900" aria-label="Đóng">
            Đóng
          </button>
        </div>
      )}

      {/* Toast thông báo thành công */}
      {successMessage && (
        <div className="flex items-center justify-between p-3.5 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-[13px] font-medium animate-in fade-in">
          <span>{successMessage}</span>
          <button onClick={() => setSuccessMessage("")} className="font-medium hover:text-emerald-950" aria-label="Đóng">
            Đóng
          </button>
        </div>
      )}

      {/* ==========================================
          HEADER TRANG & CÁC NÚT THAO TÁC
      ========================================== */}
      <section className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <nav className="flex items-center gap-1.5 text-sm text-slate-500 mb-1">
            <Link href="/dashboard" className="hover:text-slate-800 transition-colors">
              Trang chủ
            </Link>
            <span>/</span>
            <span className="text-slate-800 font-medium">Báo cáo & kiểm toán</span>
          </nav>

          <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">
            Báo cáo & kiểm toán sử dụng AI
          </h1>
          <p className="text-[13px] text-slate-500 mt-1">
            Lịch sử thực thi tác vụ AI, kiểm toán token tiêu thụ và đối soát theo thời gian thực
          </p>
        </div>

        {/* Nút thao tác — tất cả dùng kiểu nút phụ (viền) */}
        <div className="flex items-center gap-2.5 shrink-0">
          <button
            onClick={() => {
              fetchReportsData(pagination.page);
              mutateOverview();
            }}
            disabled={loading}
            title="Làm mới dữ liệu"
            className="inline-flex items-center gap-2 px-3.5 py-2 bg-white hover:bg-slate-50 border border-slate-200 rounded-lg text-[13px] font-medium text-slate-700 hover:text-slate-900 transition shadow-sm disabled:opacity-50 disabled:text-slate-400 disabled:cursor-not-allowed"
            aria-label="Làm mới dữ liệu"
          >
            <span>{loading ? "Đang tải..." : "Làm mới"}</span>
          </button>

          <button
            onClick={handleDownloadJson}
            className="inline-flex items-center gap-2 px-3.5 py-2 bg-white hover:bg-slate-50 border border-slate-200 rounded-lg text-[13px] font-medium text-slate-700 hover:text-slate-900 transition shadow-sm"
          >
            <span>Tải JSON</span>
          </button>

          <button
            onClick={() => setShowExportModal(true)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-white hover:bg-slate-50 border border-slate-200 rounded-lg text-[13px] font-medium text-slate-700 hover:text-slate-900 transition shadow-sm"
          >
            <span>Xuất báo cáo</span>
          </button>
        </div>
      </section>

      {/* ==========================================
          4 THẺ KPI
      ========================================== */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1: Tổng bản ghi nhật ký */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <span className="text-[13px] font-medium text-slate-500">Tổng bản ghi nhật ký</span>
          <div className="mt-3">
            {hasRecords ? (
              <>
                <div className="text-2xl font-semibold text-slate-900 tracking-tight">
                  {pagination.total_items.toLocaleString()}
                </div>
                <p className="mt-1 text-[13px] text-slate-500">
                  Trang {pagination.page} trên tổng {pagination.total_pages || 1} trang
                </p>
              </>
            ) : (
              <div className="text-lg font-medium text-slate-500">{EMPTY_TEXT}</div>
            )}
          </div>
        </div>

        {/* KPI 2: Token đã tiêu thụ trong tháng */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <span className="text-[13px] font-medium text-slate-500">Token đã dùng tháng này</span>
          <div className="mt-3">
            <div className="text-2xl font-semibold text-slate-900 tracking-tight">
              {totalTokensConsumed.toLocaleString()}
            </div>
            <p className="mt-1 text-[13px] text-slate-500">
              Chiếm {budgetPercentage}% tổng định mức
            </p>
          </div>
        </div>

        {/* KPI 3: Tổng định mức tháng */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <span className="text-[13px] font-medium text-slate-500">Tổng định mức tháng</span>
          <div className="mt-3">
            <div className="text-2xl font-semibold text-slate-900 tracking-tight">
              {(overview?.ai_token_usage?.total_budget_limit || 0).toLocaleString()}
            </div>
            <p className="mt-1 text-[13px] text-slate-500">
              Ngân sách token toàn hệ thống
            </p>
          </div>
        </div>

        {/* KPI 4: Tổng số giảng viên */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <span className="text-[13px] font-medium text-slate-500">Giảng viên (không gồm quản trị viên)</span>
          <div className="mt-3">
            <div className="text-2xl font-semibold text-slate-900 tracking-tight">
              {overview?.total_instructors ?? instructors.length}
            </div>
            <p className="mt-1 text-[13px] text-slate-500 truncate">
              Tác vụ nhiều nhất:{" "}
              <span className="font-medium text-slate-700">
                {topFeatureLabel}
              </span>
            </p>
          </div>
        </div>
      </section>

      {/* ==========================================
          2 KHỐI THỐNG KÊ PHÂN TÍCH TỔNG QUAN
      ========================================== */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Khối Trái: Tiến độ ngân sách Token trong tháng */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <div className="mb-4">
              <h3 className="text-sm font-semibold text-slate-900">
                Tiến độ tiêu thụ hạn ngạch tháng này
              </h3>
              <p className="text-[13px] text-slate-500">
                Tỷ lệ token tiêu hao so với định mức ngân sách quy định
              </p>
            </div>

            <div className="p-4 bg-slate-50 rounded-lg border border-slate-200/80 space-y-2.5">
              <div className="flex items-center justify-between text-[13px]">
                <span className="text-slate-600 font-medium">Tỷ lệ tiêu thụ định mức:</span>
                <span className="font-semibold text-slate-900">{budgetPercentage}%</span>
              </div>
              <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary rounded-full transition-all duration-500"
                  style={{ width: `${budgetPercentage}%` }}
                />
              </div>
              <div className="flex items-center justify-between text-[13px] text-slate-500">
                <span>Đã dùng: {totalTokensConsumed.toLocaleString()}</span>
                <span>Định mức: {(overview?.ai_token_usage?.total_budget_limit || 0).toLocaleString()}</span>
              </div>
            </div>
          </div>

          <div className="mt-4 p-3 rounded-lg bg-slate-50 border border-slate-200 text-[13px] text-slate-600">
            <span>
              Mọi yêu cầu gọi mô hình AI Hub đều được kiểm tra hạn ngạch tự động và lưu trữ nhật ký đối soát.
            </span>
          </div>
        </div>

        {/* Khối Phải: Phân bổ tỷ trọng các tính năng AI */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <div className="mb-4">
              <h3 className="text-sm font-semibold text-slate-900">
                Phân bổ theo tác vụ AI
              </h3>
              <p className="text-[13px] text-slate-500">
                Tỷ trọng token thực tế theo từng nghiệp vụ khảo thí
              </p>
            </div>

            <div className="space-y-2">
              {featureDistribution.length === 0 ? (
                <div className="py-8 text-center text-slate-500 text-[13px]">
                  {EMPTY_TEXT}
                </div>
              ) : (
                featureDistribution.map((item) => (
                  <div
                    key={item.feature}
                    className="flex items-center justify-between text-[13px] py-2 border-b border-slate-100 last:border-b-0"
                  >
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-primary shrink-0" />
                      <span className="font-medium text-slate-700">{item.label}</span>
                    </div>
                    <div className="text-right">
                      <span className="font-semibold text-slate-900">{item.percentage}%</span>{" "}
                      <span className="text-slate-500 text-[13px]">
                        ({item.tokens.toLocaleString()} tokens - {item.count} lượt)
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="mt-4 text-[13px] text-slate-500 text-right">
            Tác vụ tiêu tốn nhiều nhất:{" "}
            <span className="font-medium text-slate-700">{topFeatureLabel}</span>
          </div>
        </div>
      </section>

      {/* ==========================================
          BỘ LỌC TÌM KIẾM NHẬT KÝ
      ========================================== */}
      <section className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-[13px] font-semibold text-slate-700">
            Bộ lọc tìm kiếm & đối soát
          </div>
          <button
            onClick={handleResetFilters}
            className="text-[13px] text-primary hover:text-primary-hover font-medium transition-colors"
          >
            Đặt lại bộ lọc
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {/* Ô tìm kiếm từ khóa */}
          <div className="relative">
            <input
              type="text"
              value={searchKeyword}
              onChange={(e) => setSearchKeyword(e.target.value)}
              placeholder="Tìm theo tên GV, model, ID..."
              className="w-full px-3 py-2 text-[13px] bg-white border border-slate-200 rounded-lg text-slate-800 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition"
            />
          </div>

          {/* Lọc theo Giảng viên (user_id) */}
          <div>
            <select
              value={selectedUserId}
              onChange={(e) => setSelectedUserId(e.target.value)}
              className="w-full px-3 py-2 text-[13px] bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition"
            >
              <option value="ALL">Tất cả giảng viên</option>
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
              className="w-full px-3 py-2 text-[13px] bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition"
            >
              <option value="ALL">Tất cả tác vụ AI</option>
              <option value="GENERATE_TESTCASES">Sinh testcase tự động</option>
              <option value="REVIEW_CODE">Đánh giá & review code</option>
              <option value="VERIFY_PLAGIARISM">Kiểm tra đạo văn</option>
              <option value="EVALUATE_WEB_UI">Đánh giá giao diện web</option>
            </select>
          </div>

          {/* Lọc từ ngày (from) */}
          <div className="relative">
            <input
              type="date"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              title="Từ ngày"
              className="w-full px-3 py-2 text-[13px] bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition"
            />
          </div>

          {/* Lọc đến ngày (to) */}
          <div className="relative">
            <input
              type="date"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              title="Đến ngày"
              className="w-full px-3 py-2 text-[13px] bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition"
            />
          </div>
        </div>
      </section>

      {/* ==========================================
          BẢNG NHẬT KÝ SỰ KIỆN THẬT TỪ DATABASE
      ========================================== */}
      <section className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-50/50">
          <div className="flex items-center gap-2">
            <h2 className="text-sm font-semibold text-slate-900">
              Nhật ký gọi API & kiểm toán hệ thống
            </h2>
            <span className="px-2 py-0.5 rounded text-[13px] font-medium bg-slate-100 text-slate-600">
              {hasRecords ? `${pagination.total_items.toLocaleString()} bản ghi` : EMPTY_TEXT}
            </span>
          </div>

          {hasRecords && (
            <div className="text-[13px] text-slate-500 flex items-center gap-1.5">
              <span>Trang</span>
              <span className="font-semibold text-slate-800">{pagination.page}</span>
              <span>/</span>
              <span>{pagination.total_pages || 1}</span>
            </div>
          )}
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50/75 text-[13px] font-medium text-slate-500">
                <th className="py-3 px-4">Mã bản ghi</th>
                <th className="py-3 px-4">Thời gian</th>
                <th className="py-3 px-4">Giảng viên</th>
                <th className="py-3 px-4">Tác vụ AI</th>
                <th className="py-3 px-4">Mô hình</th>
                <th className="py-3 px-4 text-right">Prompt / Completion</th>
                <th className="py-3 px-4 text-right">Tổng tokens</th>
                <th className="py-3 px-4 text-center">Chi tiết</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-[13px] text-slate-700">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-500">
                    <Loader2 className="w-6 h-6 mx-auto animate-spin text-primary mb-2" />
                    <span>Đang tải nhật ký kiểm toán từ máy chủ...</span>
                  </td>
                </tr>
              ) : displayedLogs.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center">
                    <div className="flex flex-col items-center justify-center gap-1.5">
                      <span className="text-sm font-medium text-slate-600">{EMPTY_TEXT}</span>
                      <p className="text-[13px] text-slate-500">Không có bản ghi nhật ký nào phù hợp với bộ lọc.</p>
                    </div>
                  </td>
                </tr>
              ) : (
                displayedLogs.map((log) => {
                  const featureInfo = FEATURE_MAP[log.feature_type] || {
                    label: log.feature_type,
                    color: "text-slate-700",
                    bg: "bg-slate-100",
                  };

                  return (
                    <tr
                      key={log.id}
                      className="hover:bg-slate-50/75 transition-colors cursor-pointer"
                      onClick={() => setSelectedLog(log)}
                    >
                      {/* Mã log rút gọn (giữ monospace cho cột mã) */}
                      <td className="py-3 px-4 font-mono font-medium text-slate-600 text-[13px]">
                        #{log.id.slice(0, 8)}
                      </td>

                      {/* Thời gian */}
                      <td className="py-3 px-4 whitespace-nowrap text-slate-500">
                        {new Date(log.created_at).toLocaleString("vi-VN")}
                      </td>

                      {/* Giảng viên */}
                      <td className="py-3 px-4 whitespace-nowrap">
                        <div className="font-medium text-slate-900">{log.full_name || EMPTY_TEXT}</div>
                        <div className="text-[13px] text-slate-500">@{log.username}</div>
                      </td>

                      {/* Tính năng AI */}
                      <td className="py-3 px-4 whitespace-nowrap">
                        <span
                          className={`inline-block px-2 py-0.5 rounded text-[13px] font-medium ${featureInfo.bg} ${featureInfo.color}`}
                        >
                          {featureInfo.label}
                        </span>
                      </td>

                      {/* Mô hình */}
                      <td className="py-3 px-4 text-[13px] text-slate-600 whitespace-nowrap">
                        {log.model_name}
                      </td>

                      {/* Prompt / Completion */}
                      <td className="py-3 px-4 text-right text-slate-500 whitespace-nowrap">
                        {log.prompt_tokens.toLocaleString()} / {log.completion_tokens.toLocaleString()}
                      </td>

                      {/* Tổng tokens */}
                      <td className="py-3 px-4 text-right font-semibold text-slate-900 whitespace-nowrap">
                        {log.total_tokens.toLocaleString()}
                      </td>

                      {/* Nút xem chi tiết */}
                      <td className="py-3 px-4 text-center whitespace-nowrap">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedLog(log);
                          }}
                          className="px-2.5 py-1 text-[13px] font-medium text-primary hover:bg-primary-bg rounded-lg transition"
                          title="Xem chi tiết"
                          aria-label="Xem chi tiết bản ghi"
                        >
                          Xem
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
        <div className="p-4 border-t border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-[13px] text-slate-500 bg-white">
          <div>
            {hasRecords ? (
              <>
                Hiển thị{" "}
                <span className="font-semibold text-slate-800">
                  {displayedLogs.length > 0 ? (pagination.page - 1) * pagination.page_size + 1 : 0}
                </span>{" "}
                -{" "}
                <span className="font-semibold text-slate-800">
                  {Math.min(pagination.page * pagination.page_size, pagination.total_items)}
                </span>{" "}
                trong tổng số <span className="font-semibold text-slate-800">{pagination.total_items}</span> bản ghi
              </>
            ) : (
              EMPTY_TEXT
            )}
          </div>

          {hasRecords && (
            <div className="flex items-center gap-1.5 self-center">
              <button
                onClick={() => fetchReportsData(pagination.page - 1)}
                disabled={pagination.page <= 1 || loading}
                className="px-3 h-9 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition text-[13px] font-medium"
                aria-label="Trang trước"
              >
                Trước
              </button>

              <span className="px-3 py-1 font-medium text-slate-700 bg-slate-100 rounded-lg">
                Trang {pagination.page} / {pagination.total_pages || 1}
              </span>

              <button
                onClick={() => fetchReportsData(pagination.page + 1)}
                disabled={pagination.page >= pagination.total_pages || loading}
                className="px-3 h-9 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition text-[13px] font-medium"
                aria-label="Trang sau"
              >
                Sau
              </button>
            </div>
          )}
        </div>
      </section>

      {/* ==========================================
          MODAL CHI TIẾT BẢN GHI (LOG DETAIL MODAL)
      ========================================== */}
      {selectedLog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white w-full max-w-xl rounded-xl shadow-xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]">
            <div className="p-4 px-6 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <div>
                <h3 className="font-semibold text-slate-900 text-sm">Chi tiết nhật ký sử dụng AI</h3>
                <p className="text-[13px] text-slate-500">{selectedLog.id}</p>
              </div>
              <button
                onClick={() => setSelectedLog(null)}
                className="px-2.5 py-1 text-[13px] font-medium text-slate-600 hover:text-slate-900 rounded-lg hover:bg-slate-200/50 transition"
                aria-label="Đóng"
              >
                Đóng
              </button>
            </div>

            <div className="p-6 overflow-y-auto space-y-4 text-[13px] text-slate-700">
              <div className="grid grid-cols-2 gap-3 p-3.5 bg-slate-50 rounded-lg border border-slate-200/70">
                <div>
                  <span className="text-[13px] text-slate-500 font-medium">Thời gian gọi:</span>
                  <div className="font-medium text-slate-900 mt-0.5">
                    {new Date(selectedLog.created_at).toLocaleString("vi-VN")}
                  </div>
                </div>
                <div>
                  <span className="text-[13px] text-slate-500 font-medium">Mô hình AI:</span>
                  <div className="text-slate-900 mt-0.5 font-medium">
                    {selectedLog.model_name}
                  </div>
                </div>
                <div>
                  <span className="text-[13px] text-slate-500 font-medium">Giảng viên:</span>
                  <div className="font-medium text-slate-900 mt-0.5">{selectedLog.full_name}</div>
                  <div className="text-[13px] text-slate-500">@{selectedLog.username}</div>
                </div>
                <div>
                  <span className="text-[13px] text-slate-500 font-medium">Mã User ID:</span>
                  <div className="text-[13px] text-slate-600 truncate mt-0.5">
                    {selectedLog.user_id}
                  </div>
                </div>
              </div>

              <div>
                <label className="text-[13px] font-medium text-slate-500 block mb-1">
                  Nghiệp vụ thực thi:
                </label>
                <div className="p-3 bg-white border border-slate-200 rounded-lg font-medium text-slate-800">
                  {FEATURE_MAP[selectedLog.feature_type]?.label || selectedLog.feature_type}
                </div>
              </div>

              <div>
                <label className="text-[13px] font-medium text-slate-500 block mb-1">
                  Chi tiết phân bổ Tokens:
                </label>
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
                    <span className="text-[13px] text-slate-500 font-medium block">Prompt</span>
                    <span className="font-semibold text-slate-900 text-sm mt-1 block">
                      {selectedLog.prompt_tokens.toLocaleString()}
                    </span>
                  </div>
                  <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
                    <span className="text-[13px] text-slate-500 font-medium block">Completion</span>
                    <span className="font-semibold text-slate-900 text-sm mt-1 block">
                      {selectedLog.completion_tokens.toLocaleString()}
                    </span>
                  </div>
                  <div className="p-3 bg-primary-bg border border-primary rounded-lg">
                    <span className="text-[13px] text-primary font-medium block">Tổng cộng</span>
                    <span className="font-semibold text-primary text-sm mt-1 block">
                      {selectedLog.total_tokens.toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div className="p-4 border-t border-slate-200 bg-slate-50 flex justify-end">
              <button
                onClick={() => setSelectedLog(null)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white font-medium rounded-lg text-[13px] transition"
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
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white w-full max-w-md rounded-xl shadow-xl border border-slate-200 overflow-hidden">
            <div className="p-4 px-6 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <h3 className="font-semibold text-slate-900 text-sm">Xuất báo cáo kiểm toán</h3>
              <button
                onClick={() => setShowExportModal(false)}
                className="px-2.5 py-1 text-[13px] font-medium text-slate-600 hover:text-slate-900 rounded-lg"
                aria-label="Đóng"
              >
                Đóng
              </button>
            </div>

            <div className="p-6 space-y-4 text-[13px] text-slate-600">
              <p>
                Chọn định dạng xuất dữ liệu cho <b>{displayedLogs.length}</b> bản ghi nhật ký hiện đang hiển thị:
              </p>

              <div className="space-y-3">
                <button
                  onClick={handleExportCsv}
                  className="w-full p-3.5 border border-slate-200 hover:border-primary hover:bg-primary-bg rounded-xl flex items-center justify-between text-left transition"
                >
                  <div>
                    <div className="font-semibold text-slate-900">
                      Bảng tính Excel (.CSV UTF-8)
                    </div>
                    <div className="text-[13px] text-slate-500">
                      Mở trực tiếp trên Microsoft Excel, Google Sheets không lỗi font tiếng Việt
                    </div>
                  </div>
                </button>

                <button
                  onClick={() => {
                    setShowExportModal(false);
                    window.print();
                  }}
                  className="w-full p-3.5 border border-slate-200 hover:border-primary hover:bg-primary-bg rounded-xl flex items-center justify-between text-left transition"
                >
                  <div>
                    <div className="font-semibold text-slate-900">
                      In báo cáo / Lưu PDF (Print)
                    </div>
                    <div className="text-[13px] text-slate-500">
                      In trực tiếp ra văn bản hoặc lưu định dạng PDF
                    </div>
                  </div>
                </button>
              </div>
            </div>

            <div className="p-4 border-t border-slate-200 bg-slate-50 flex justify-end">
              <button
                onClick={() => setShowExportModal(false)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded-lg text-[13px] transition"
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
