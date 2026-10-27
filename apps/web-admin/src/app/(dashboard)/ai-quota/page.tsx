"use client";

import React, { useState, useEffect, useCallback, useMemo } from "react";
import Link from "next/link";
import useSWR from "swr";
import { swrFetcher, apiGet, API_URL, getAccessToken } from "@/lib/api";
import { Loader2, Inbox } from "lucide-react";
import { featureLabel, featureBadgeClass } from "@/lib/feature-labels";
import Alert from "@/components/ui/alert";
import Modal from "@/components/ui/modal";

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

interface ProviderAccountStatus {
  account: string;
  key_hint: string;
  state: "READY" | "COOLDOWN";
  cooldown_remaining_seconds: number;
}

interface ProviderStatus {
  provider: string;
  model: string;
  accounts_configured: number;
  structured_outputs_supported: boolean;
  accounts: ProviderAccountStatus[];
}

const REQUEST_TIMEOUT_MS = 12000;

export default function AiQuotaPage() {
  const [activeTab, setActiveTab] = useState<"INSTRUCTORS" | "LOGS">("INSTRUCTORS");
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [quotaError, setQuotaError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const { data: overview, mutate: mutateOverview } = useSWR<OverviewData>(
    "/admin/reports/overview",
    swrFetcher,
    { revalidateOnFocus: false, shouldRetryOnError: false, dedupingInterval: 30000 }
  );
  const [instructors, setInstructors] = useState<InstructorQuotaItem[]>([]);
  const [usageLogs, setUsageLogs] = useState<AiUsageLogItem[]>([]);
  const [hub, setHub] = useState<ProviderStatus | null>(null);
  const [hubLoading, setHubLoading] = useState(true);
  const [hubError, setHubError] = useState(false);

  const fetchHub = useCallback(async () => {
    setHubLoading(true);
    setHubError(false);
    try {
      setHub(await apiGet<ProviderStatus>("/ai/provider-status"));
    } catch {
      setHubError(true);
    } finally {
      setHubLoading(false);
    }
  }, []);
  const [logsPagination, setLogsPagination] = useState<PaginationData>({
    page: 1,
    page_size: 10,
    total_items: 0,
    total_pages: 1,
  });

  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [editingInstructor, setEditingInstructor] = useState<InstructorQuotaItem | null>(null);
  const [newQuotaValue, setNewQuotaValue] = useState<string>("");

  useEffect(() => {
    const handler = setTimeout(() => setDebouncedSearch(searchQuery.trim()), 350);
    return () => clearTimeout(handler);
  }, [searchQuery]);

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

  useEffect(() => {
    fetchHub();
  }, [fetchHub]);

  const getApiConfig = () => {
    const token = getAccessToken();
    return { token, apiUrl: API_URL };
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
    setQuotaError("");

    // Giới hạn thời gian phản hồi để tránh tab kẹt trạng thái "Đang tải"
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    try {
      const headers = {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      };

      const [resInstructors, resLogs] = await Promise.all([
        fetch(`${apiUrl}/admin/users?role=INSTRUCTOR&page=1&page_size=50`, {
          headers,
          signal: controller.signal,
        }),
        fetch(`${apiUrl}/admin/reports/ai-usage?page=${logPage}&page_size=${logsPagination.page_size}`, {
          headers,
          signal: controller.signal,
        }),
      ]);

      if (resInstructors.status === 401 || resLogs.status === 401) {
        setErrorMessage("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.");
        if (typeof window !== "undefined") {
          localStorage.removeItem("aita_access_token");
        }
        setLoading(false);
        return;
      }

      if (resInstructors.ok) {
        const json = await resInstructors.json();
        if (json.success && json.data?.items) setInstructors(json.data.items);
      } else {
        setQuotaError("Không tải được dữ liệu hạn ngạch.");
      }

      if (resLogs.ok) {
        const json = await resLogs.json();
        if (json.success && json.data) {
          setUsageLogs(json.data.items || []);
          if (json.data.pagination) setLogsPagination(json.data.pagination);
        }
      }
    } catch (err) {
      if ((err as any)?.name === "AbortError") {
        setQuotaError("Không tải được dữ liệu hạn ngạch (máy chủ phản hồi quá lâu).");
      } else {
        setErrorMessage("Lỗi kết nối tới máy chủ.");
        setQuotaError("Không tải được dữ liệu hạn ngạch.");
      }
    } finally {
      clearTimeout(timeoutId);
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
        mutateOverview();
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

  const filteredInstructors = useMemo(() => {
    const q = debouncedSearch.toLowerCase();
    if (!q) return instructors;
    return instructors.filter(
      (ins) =>
        ins.full_name.toLowerCase().includes(q) ||
        ins.username.toLowerCase().includes(q) ||
        ins.email.toLowerCase().includes(q)
    );
  }, [instructors, debouncedSearch]);

  const totalConsumed = overview?.ai_token_usage?.total_tokens_consumed_month ?? 0;
  const totalBudget = overview?.ai_token_usage?.total_budget_limit ?? 1;
  const usagePercentage = Math.min(100, Math.round((totalConsumed / totalBudget) * 100));

  // Số giảng viên dùng chung cho thẻ "Giảng viên có hạn ngạch" và tab — luôn khớp nhau
  const instructorCount = overview?.total_instructors ?? instructors.length;

  const handleExportInstructorsCsv = () => {
    if (instructors.length === 0) return;
    const headers = ["ID", "Giảng viên", "Username", "Email", "Hạn ngạch ngày (Tokens)", "Đã dùng hôm nay", "Còn lại", "Trạng thái"];
    const rows = instructors.map((ins) => [
      ins.id,
      `"${ins.full_name}"`,
      ins.username,
      ins.email,
      ins.daily_token_quota ?? 50000,
      ins.used_tokens_today ?? 0,
      Math.max(0, (ins.daily_token_quota ?? 50000) - (ins.used_tokens_today ?? 0)),
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
      `"${featureLabel(log.feature_type)}"`,
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
  const topFeatureDisplay = topFeatureRaw ? featureLabel(topFeatureRaw) : null;

  return (
    <div className="flex flex-col w-full gap-6">
      {/* Thông báo lỗi */}
      {errorMessage && (
        <Alert variant="error" onClose={() => setErrorMessage("")}>
          {errorMessage}
        </Alert>
      )}

      {/* Thông báo thành công */}
      {successMessage && (
        <Alert variant="success" onClose={() => setSuccessMessage("")}>
          {successMessage}
        </Alert>
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
          <p className="text-[13px] text-slate-500 mt-1">
            Quản lý lưu lượng token và phân bổ hạn ngạch cho giảng viên
          </p>
        </div>

        <button
          type="button"
          onClick={() => {
            fetchData();
            mutateOverview();
            fetchHub();
          }}
          disabled={loading}
          className="flex items-center gap-2 px-3.5 h-10 rounded-lg bg-white border border-slate-200 text-slate-700 font-medium text-sm hover:bg-slate-50 transition-colors disabled:opacity-50 disabled:text-slate-400 disabled:cursor-not-allowed min-h-[40px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
          aria-label="Làm mới dữ liệu"
        >
          <span>{loading ? "Đang tải..." : "Làm mới"}</span>
        </button>
      </section>

      {/* ================= 4 THẺ KPI ================= */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Thẻ 1: Ngân sách tháng */}
        <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <span className="text-sm text-slate-500 font-normal">
            Định mức tháng
          </span>
          <div className="mt-3">
            <div className="text-3xl font-semibold text-slate-900 tracking-tight">
              {(overview?.ai_token_usage?.total_budget_limit ?? 0).toLocaleString()}
            </div>
            <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden my-2">
              <div
                className="bg-primary h-full rounded-full transition-all duration-500"
                style={{ width: `${usagePercentage}%` }}
              />
            </div>
            <div className="text-[13px] text-slate-500">
              Tổng ngân sách toàn hệ thống
            </div>
          </div>
        </div>

        {/* Thẻ 2: Đã tiêu thụ */}
        <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <span className="text-sm text-slate-500 font-normal">
            Token đã sử dụng
          </span>
          <div className="mt-3">
            <div className="text-3xl font-semibold text-slate-900 tracking-tight">
              {(overview?.ai_token_usage?.total_tokens_consumed_month ?? 0).toLocaleString()}
            </div>
            <div className="text-[13px] text-slate-500 mt-1">
              Đạt {usagePercentage}% định mức tháng
            </div>
          </div>
        </div>

        {/* Thẻ 3: Top tính năng */}
        <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <span className="text-sm text-slate-500 font-normal">
            Tính năng dùng nhiều nhất
          </span>
          <div className="mt-3">
            {topFeatureDisplay ? (
              <div className="text-lg font-semibold text-slate-900 tracking-tight truncate" title={topFeatureDisplay}>
                {topFeatureDisplay}
              </div>
            ) : (
              <div className="text-lg font-medium text-slate-500">
                Chưa có dữ liệu
              </div>
            )}
            <div className="text-[13px] text-slate-500 mt-1">
              {topFeatureDisplay ? "Chiếm tỷ trọng cao nhất" : "Chưa có lượt gọi AI nào"}
            </div>
          </div>
        </div>

        {/* Thẻ 4: Tổng giảng viên */}
        <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <span className="text-sm text-slate-500 font-normal">
            Giảng viên có hạn ngạch
          </span>
          <div className="mt-3">
            <div className="text-3xl font-semibold text-slate-900 tracking-tight">
              {instructorCount}
            </div>
            <div className="text-[13px] text-slate-500 mt-1">
              Giảng viên đang hoạt động
            </div>
          </div>
        </div>
      </section>

      {/* ================= AI HUB (OPENROUTER) — TRẠNG THÁI POOL ================= */}
      <section className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h2 className="text-base font-semibold text-slate-900">AI Hub — OpenRouter</h2>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-[13px] bg-indigo-50 text-indigo-700 font-medium font-mono">
                {hub ? hub.model : "..."}
              </span>
              {hub && (
                <span
                  className={`inline-flex items-center px-2 py-0.5 rounded text-[13px] font-medium ${
                    hub.structured_outputs_supported
                      ? "bg-emerald-50 text-emerald-700"
                      : "bg-amber-50 text-amber-700"
                  }`}
                >
                  {hub.structured_outputs_supported ? "JSON Schema sẵn sàng" : "JSON Schema fallback"}
                </span>
              )}
            </div>
            <p className="text-[13px] text-slate-500 mt-0.5">
              Bể API key xoay vòng tự động — khi một tài khoản hết hạn mức, request tự chuyển sang tài khoản kế tiếp
            </p>
          </div>
          <button
            type="button"
            onClick={fetchHub}
            disabled={hubLoading}
            className="flex-shrink-0 px-3 h-9 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 font-medium text-[13px] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label="Làm mới trạng thái AI Hub"
          >
            Làm mới
          </button>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-2">
          {hubLoading && (
            <span className="text-[13px] text-slate-500 flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-primary" />
              <span>Đang tải trạng thái pool...</span>
            </span>
          )}
          {!hubLoading && hubError && (
            <span className="text-[13px] text-rose-600">
              Không tải được trạng thái AI Hub (yêu cầu quyền ADMIN hoặc máy chủ chưa cấu hình OPENROUTER_API_KEYS).
            </span>
          )}
          {!hubLoading && !hubError && hub && (
            <>
              <span className="text-[13px] text-slate-500 mr-1">
                {hub.accounts_configured} tài khoản trong bể:
              </span>
              {hub.accounts.map((account) => (
                <span
                  key={account.account}
                  title={account.key_hint}
                  className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[13px] font-medium border ${
                    account.state === "READY"
                      ? "border-emerald-200 bg-emerald-50 text-emerald-700"
                      : "border-amber-200 bg-amber-50 text-amber-700"
                  }`}
                >
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${
                      account.state === "READY" ? "bg-emerald-500" : "bg-amber-500"
                    }`}
                  />
                  <span>
                    {account.account} —{" "}
                    {account.state === "READY" ? "Sẵn sàng" : `Nghỉ ${account.cooldown_remaining_seconds}s`}
                  </span>
                </span>
              ))}
            </>
          )}
        </div>
      </section>

      {/* Thông báo lỗi tải hạn ngạch + nút Thử lại */}
      {quotaError && (
        <Alert variant="error" onClose={() => setQuotaError("")}>
          <span>{quotaError}</span>
          <button
            type="button"
            onClick={() => fetchData()}
            disabled={loading}
            className="px-3 h-8 rounded-lg border border-rose-300 text-rose-700 hover:bg-rose-100 font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Thử lại
          </button>
        </Alert>
      )}

      {/* ================= TAB CONTROLS ================= */}
      <div className="flex items-center gap-6 border-b border-slate-200 text-sm">
        <button
          type="button"
          onClick={() => setActiveTab("INSTRUCTORS")}
          className={`pb-3 font-medium transition-colors relative ${
            activeTab === "INSTRUCTORS"
              ? "text-primary font-semibold"
              : "text-slate-500 hover:text-slate-800"
          }`}
        >
          <span>Hạn ngạch giảng viên ({instructorCount})</span>
          {activeTab === "INSTRUCTORS" && (
            <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary rounded-full" />
          )}
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("LOGS")}
          className={`pb-3 font-medium transition-colors relative ${
            activeTab === "LOGS"
              ? "text-primary font-semibold"
              : "text-slate-500 hover:text-slate-800"
          }`}
        >
          <span>Nhật ký sử dụng AI ({logsPagination.total_items})</span>
          {activeTab === "LOGS" && (
            <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary rounded-full" />
          )}
        </button>
      </div>

      {/* ================= TAB 1: DANH SÁCH HẠN NGẠCH GIẢNG VIÊN ================= */}
      {activeTab === "INSTRUCTORS" && (
        <section className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
          {/* Header & Bộ lọc */}
          <div className="p-4 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div className="relative w-full max-w-sm">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Tìm giảng viên theo tên, email..."
                className="w-full px-3 h-10 rounded-lg text-[13px] bg-slate-50 border border-slate-200 placeholder:text-slate-500 focus:outline-none focus:bg-white focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
              />
            </div>

            <button
              type="button"
              onClick={handleExportInstructorsCsv}
              disabled={instructors.length === 0}
              className="flex items-center gap-2 px-3.5 h-10 rounded-lg bg-white border border-slate-200 text-slate-700 font-medium text-[13px] hover:bg-slate-50 transition-colors disabled:opacity-50 disabled:text-slate-400 disabled:cursor-not-allowed min-h-[40px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
              aria-label="Xuất file CSV hạn ngạch"
            >
              <span>Xuất CSV</span>
            </button>
          </div>

          {/* Table */}
          <div className="overflow-x-auto w-full">
            <table className="w-full text-left text-[13px]">
              <thead className="bg-slate-50/50 text-slate-500 font-medium border-b border-slate-200">
                <tr>
                  <th scope="col" className="py-3 px-4 font-medium">Giảng viên</th>
                  <th scope="col" className="py-3 px-4 font-medium">Email</th>
                  <th scope="col" className="py-3 px-4 text-right font-medium">Hạn ngạch ngày</th>
                  <th scope="col" className="py-3 px-4 text-right font-medium">Đã dùng hôm nay</th>
                  <th scope="col" className="py-3 px-4 text-right font-medium">Còn lại</th>
                  <th scope="col" className="py-3 px-4 text-center font-medium">Trạng thái</th>
                  <th scope="col" className="py-3 px-4 text-right font-medium">Thao tác</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-normal">
                {loading ? (
                  <tr>
                    <td colSpan={7} className="py-12 text-center text-slate-500">
                      <Loader2 className="w-5 h-5 mx-auto animate-spin text-primary mb-1.5" />
                      <span>Đang tải dữ liệu hạn ngạch...</span>
                    </td>
                  </tr>
                ) : quotaError && instructors.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-12 text-center">
                      <div className="flex flex-col items-center justify-center gap-2">
                        <span className="text-sm font-medium text-slate-600">Không tải được dữ liệu hạn ngạch</span>
                        <button
                          type="button"
                          onClick={() => fetchData()}
                          className="px-3.5 h-9 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 text-[13px] font-medium transition-colors min-h-[36px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
                        >
                          Thử lại
                        </button>
                      </div>
                    </td>
                  </tr>
                ) : filteredInstructors.length > 0 ? (
                  filteredInstructors.map((ins) => {
                    const quota = ins.daily_token_quota ?? 50000;
                    const used = ins.used_tokens_today ?? 0;
                    const remaining = Math.max(0, quota - used);
                    const percent = Math.min(100, Math.round((used / quota) * 100));

                    return (
                      <tr key={ins.id} className="hover:bg-slate-50 transition-colors">
                        <td className="py-3 px-4 whitespace-nowrap">
                          <div className="font-medium text-slate-900">{ins.full_name}</div>
                          <div className="text-[13px] text-slate-500">@{ins.username}</div>
                        </td>
                        <td className="py-3 px-4 text-[13px] text-slate-500 whitespace-nowrap">
                          {ins.email}
                        </td>
                        <td className="py-3 px-4 text-right font-medium text-slate-900 whitespace-nowrap">
                          {quota.toLocaleString()}
                        </td>
                        <td className="py-3 px-4 text-right text-slate-600 whitespace-nowrap">
                          {used.toLocaleString()} ({percent}%)
                        </td>
                        <td className="py-3 px-4 text-right font-medium text-primary whitespace-nowrap">
                          {remaining.toLocaleString()}
                        </td>
                        <td className="py-3 px-4 text-center whitespace-nowrap">
                          {ins.is_active ? (
                            <span className="inline-flex items-center gap-1.5 text-[13px] text-emerald-700 font-medium">
                              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                              Hoạt động
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1.5 text-[13px] text-slate-500 font-medium">
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
                              setNewQuotaValue(String(ins.daily_token_quota ?? 50000));
                            }}
                            className="inline-flex items-center px-2.5 py-1.5 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 text-[13px] font-medium transition-colors"
                          >
                            Điều chỉnh
                          </button>
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan={7} className="py-12 text-center">
                      <div className="flex flex-col items-center justify-center gap-1.5">
                        <Inbox className="w-8 h-8 text-slate-300 mb-1" aria-hidden="true" />
                        <span className="text-sm font-medium text-slate-600">Chưa có dữ liệu</span>
                        <p className="text-[13px] text-slate-500">Không có giảng viên nào phù hợp với bộ lọc hiện tại.</p>
                      </div>
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
              <p className="text-[13px] text-slate-500 mt-0.5">
                Các bản ghi gọi API xử lý bài nộp và sinh testcase
              </p>
            </div>

            <button
              type="button"
              onClick={handleExportLogsCsv}
              disabled={usageLogs.length === 0}
              className="flex items-center gap-2 px-3.5 h-10 rounded-lg bg-white border border-slate-200 text-slate-700 font-medium text-[13px] hover:bg-slate-50 transition-colors disabled:opacity-50 disabled:text-slate-400 disabled:cursor-not-allowed min-h-[40px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
              aria-label="Xuất file CSV nhật ký"
            >
              <span>Xuất CSV</span>
            </button>
          </div>

          <div className="overflow-x-auto w-full">
            <table className="w-full text-left text-[13px]">
              <thead className="bg-slate-50/50 text-slate-500 font-medium border-b border-slate-200">
                <tr>
                  <th scope="col" className="py-3 px-4 font-medium">Mã log</th>
                  <th scope="col" className="py-3 px-4 font-medium">Giảng viên</th>
                  <th scope="col" className="py-3 px-4 font-medium">Tác vụ AI</th>
                  <th scope="col" className="py-3 px-4 font-medium">Mô hình</th>
                  <th scope="col" className="py-3 px-4 text-right font-medium">Prompt</th>
                  <th scope="col" className="py-3 px-4 text-right font-medium">Completion</th>
                  <th scope="col" className="py-3 px-4 text-right font-medium">Tổng token</th>
                  <th scope="col" className="py-3 px-4 text-right font-medium">Thời gian</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-normal">
                {loading ? (
                  <tr>
                    <td colSpan={8} className="py-12 text-center text-slate-500">
                      <Loader2 className="w-5 h-5 mx-auto animate-spin text-primary mb-1.5" />
                      <span>Đang tải nhật ký...</span>
                    </td>
                  </tr>
                ) : usageLogs.length > 0 ? (
                  usageLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-3 px-4 font-mono text-slate-500 text-[13px] whitespace-nowrap">
                        {log.id.slice(0, 8)}...
                      </td>
                      <td className="py-3 px-4 text-slate-900 font-medium whitespace-nowrap">
                        <div>{log.full_name}</div>
                        <div className="text-[13px] text-slate-500 font-normal">@{log.username}</div>
                      </td>
                      <td className="py-3 px-4 text-slate-700 whitespace-nowrap">
                        <span className={`inline-block px-2 py-0.5 rounded text-[13px] ${featureBadgeClass(log.feature_type)}`}>
                          {featureLabel(log.feature_type)}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-[13px] text-slate-600 whitespace-nowrap">
                        {log.model_name}
                      </td>
                      <td className="py-3 px-4 text-right text-slate-600 whitespace-nowrap">
                        {log.prompt_tokens.toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-right text-slate-600 whitespace-nowrap">
                        {log.completion_tokens.toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-right font-medium text-slate-900 whitespace-nowrap">
                        {log.total_tokens.toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-right text-slate-500 text-[13px] whitespace-nowrap">
                        {new Date(log.created_at).toLocaleString("vi-VN")}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={8} className="py-12 text-center">
                      <div className="flex flex-col items-center justify-center gap-1.5">
                        <Inbox className="w-8 h-8 text-slate-300 mb-1" aria-hidden="true" />
                        <span className="text-sm font-medium text-slate-600">Chưa có dữ liệu</span>
                        <p className="text-[13px] text-slate-500">Chưa có bản ghi nhật ký nào.</p>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="p-4 border-t border-slate-200 flex items-center justify-between text-sm text-slate-500">
            <span>{logsPagination.total_items > 0 ? `${logsPagination.total_items} bản ghi` : "Chưa có dữ liệu"}</span>

            {logsPagination.total_items > logsPagination.page_size && (
              <div className="flex items-center gap-1.5">
                <button
                  type="button"
                  onClick={() => fetchData(Math.max(1, logsPagination.page - 1))}
                  disabled={logsPagination.page <= 1 || loading}
                  className="px-3 h-9 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors min-h-[36px] flex items-center justify-center text-[13px] font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
                  aria-label="Trang trước"
                >
                  Trước
                </button>
                <span className="px-2.5 py-1 text-[13px] font-medium text-slate-700 bg-slate-100 rounded-md">
                  {logsPagination.page} / {logsPagination.total_pages}
                </span>
                <button
                  type="button"
                  onClick={() => fetchData(Math.min(logsPagination.total_pages, logsPagination.page + 1))}
                  disabled={logsPagination.page >= logsPagination.total_pages || loading}
                  className="px-3 h-9 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors min-h-[36px] flex items-center justify-center text-[13px] font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
                  aria-label="Trang sau"
                >
                  Sau
                </button>
              </div>
            )}
          </div>
        </section>
      )}

      {/* ================= MODAL ĐIỀU CHỈNH HẠN NGẠCH ================= */}
      <Modal
        open={!!editingInstructor}
        onClose={() => setEditingInstructor(null)}
        title="Điều chỉnh hạn ngạch AI"
        description={
          editingInstructor
            ? `${editingInstructor.full_name} (@${editingInstructor.username})`
            : undefined
        }
        maxWidthClass="max-w-md"
      >
        {editingInstructor && (
          <form onSubmit={handleUpdateQuota} className="space-y-4 text-[13px]">
            {errorMessage && (
              <Alert variant="error" onClose={() => setErrorMessage("")}>
                {errorMessage}
              </Alert>
            )}

            <div>
              <label htmlFor="quota-value" className="block font-medium text-slate-700 mb-1">
                Định mức tokens mỗi ngày
              </label>
              <input
                id="quota-value"
                type="number"
                min="0"
                required
                value={newQuotaValue}
                onChange={(e) => setNewQuotaValue(e.target.value)}
                className="w-full px-3 h-10 rounded-lg bg-slate-50 border border-slate-200 focus:outline-none focus:border-primary focus:bg-white transition-colors"
              />
              <p className="text-[13px] text-slate-500 mt-1">
                Mặc định: 50,000 tokens/ngày. Đã dùng hôm nay: {(editingInstructor.used_tokens_today ?? 0).toLocaleString()} tokens.
              </p>
            </div>

            <div className="flex items-center justify-end gap-2.5 pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setEditingInstructor(null)}
                className="px-4 h-10 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 font-medium text-[13px] transition-colors"
              >
                Hủy bỏ
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="px-4 h-10 rounded-lg bg-primary hover:bg-primary-hover text-white font-medium text-[13px] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
                <span>Lưu thay đổi</span>
              </button>
            </div>
          </form>
        )}
      </Modal>
    </div>
  );
}
