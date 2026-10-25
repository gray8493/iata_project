"use client";

import React, { useState, useEffect, useCallback, useRef } from "react";
import Link from "next/link";
import useSWR from "swr";
import { swrFetcher, API_URL } from "@/lib/api";
import { Loader2, Inbox } from "lucide-react";
import { featureLabel, featureBadgeClass } from "@/lib/feature-labels";
import Alert from "@/components/ui/alert";

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
  const {
    data: overview,
    error: overviewError,
    mutate: mutateOverview,
  } = useSWR<OverviewData>("/admin/reports/overview", swrFetcher, {
    revalidateOnFocus: false,
    shouldRetryOnError: false,
    dedupingInterval: 30000,
  });
  const overviewLoading = !overview && !overviewError;
  const [usageItems, setUsageItems] = useState<AiUsageItem[]>([]);
  const [pagination, setPagination] = useState<PaginationData>({
    page: 1,
    page_size: 10,
    total_items: 0,
    total_pages: 0,
  });

  const [showExportMenu, setShowExportMenu] = useState(false);
  const exportMenuRef = useRef<HTMLDivElement>(null);

  // Đóng menu xuất báo cáo khi click ra ngoài hoặc nhấn Esc
  useEffect(() => {
    if (!showExportMenu) return;
    const handlePointerDown = (e: MouseEvent) => {
      if (exportMenuRef.current && !exportMenuRef.current.contains(e.target as Node)) {
        setShowExportMenu(false);
      }
    };
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") setShowExportMenu(false);
    };
    document.addEventListener("mousedown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [showExportMenu]);

  // Fetch real data from NestJS Backend APIs
  const fetchDashboardData = useCallback(async (pageNumber = 1) => {
    setErrorMessage("");
    const token = localStorage.getItem("aita_access_token");

    if (!token) {
      setErrorMessage("Chưa tìm thấy phiên đăng nhập. Vui lòng đăng nhập lại.");
      setLoading(false);
      return;
    }

    try {
      const headers = {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      };

      const resUsage = await fetch(
        `${API_URL}/admin/reports/ai-usage?page=${pageNumber}&page_size=10`,
        { method: "GET", headers }
      );

      if (resUsage.status === 401) {
        setErrorMessage("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.");
        localStorage.removeItem("aita_access_token");
        setLoading(false);
        return;
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
      setLastSyncText(
        `${now.getHours()}:${String(now.getMinutes()).padStart(2, "0")}:${String(now.getSeconds()).padStart(2, "0")}`
      );
    } catch {
      setErrorMessage("Không thể kết nối đến máy chủ. Vui lòng kiểm tra lại dịch vụ Backend.");
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData(currentPage);
  }, [fetchDashboardData, currentPage]);

  useEffect(() => {
    if (overviewError) {
      setErrorMessage(
        overviewError instanceof Error
          ? overviewError.message
          : "Không thể tải báo cáo tổng quan từ máy chủ."
      );
    }
  }, [overviewError]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await Promise.all([fetchDashboardData(currentPage), mutateOverview()]);
    setIsRefreshing(false);
  };

  // Tính toán tỷ lệ phần trăm hạn ngạch AI tiêu thụ thực tế
  const totalTokensUsed = overview?.ai_token_usage?.total_tokens_consumed_month ?? 0;
  const totalBudgetLimit = overview?.ai_token_usage?.total_budget_limit ?? 0;
  const usagePercentage =
    totalBudgetLimit > 0
      ? Math.min(Math.round((totalTokensUsed / totalBudgetLimit) * 1000) / 10, 100)
      : 0;

  // Xuất file CSV mở trên Excel (UTF-8 BOM tiếng Việt)
  const handleExportCsv = () => {
    setShowExportMenu(false);
    const nowStr = new Date().toLocaleString("vi-VN");
    const dateStr = new Date().toISOString().slice(0, 10);
    const fileName = `Bao_cao_AITA_tong_quan_${dateStr}.csv`;

    const totalConsumed = overview?.ai_token_usage?.total_tokens_consumed_month ?? 0;
    const totalBudget = overview?.ai_token_usage?.total_budget_limit ?? 0;
    const topFeature = featureLabel(overview?.ai_token_usage?.top_consuming_feature);

    let csv = "\uFEFF";
    csv += "BÁO CÁO TỔNG QUAN HỆ THỐNG AITA\n";
    csv += `Thời điểm xuất:,"${nowStr}"\n`;
    csv += `Cổng quản trị:,Hệ thống Khảo thí AITA - Đại học FPT\n\n`;

    csv += "--- 1. CHỈ SỐ HỆ THỐNG & HẠN NGẠCH AI ---\n";
    csv += `Tổng số giảng viên (không gồm quản trị viên):,${overview?.total_instructors ?? 0}\n`;
    csv += `Tổng token đã tiêu thụ trong tháng:,${totalConsumed}\n`;
    csv += `Ngân sách token toàn hệ thống:,${totalBudget}\n`;
    csv += `Tỷ lệ sử dụng thực tế:,${totalBudget > 0 ? ((totalConsumed / totalBudget) * 100).toFixed(2) : 0}%\n`;
    csv += `Tính năng AI chiếm tỷ trọng lớn nhất:,"${topFeature}"\n\n`;

    csv += "--- 2. NHẬT KÝ SỬ DỤNG AI GẦN NHẤT (AUDIT TRAIL) ---\n";
    csv += "Mã Log,Giảng viên,Tài khoản,Tính năng (Feature Type),Mô hình AI,Prompt Tokens,Completion Tokens,Tổng Tokens,Thời gian ghi nhận\n";

    if (usageItems && usageItems.length > 0) {
      usageItems.forEach((log) => {
        csv += `"${log.id}","${log.full_name}","${log.username}","${featureLabel(log.feature_type)}","${log.model_name}",${log.prompt_tokens},${log.completion_tokens},${log.total_tokens},"${new Date(log.created_at).toLocaleString("vi-VN")}"\n`;
      });
    } else {
      csv += "Chưa có dữ liệu\n";
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

  const topFeatureRaw = overview?.ai_token_usage?.top_consuming_feature;
  const topFeatureDisplay = topFeatureRaw ? featureLabel(topFeatureRaw) : null;

  const hasUsageRecords = pagination.total_items > 0;

  return (
    <div className="flex flex-col w-full gap-6">
      {/* ================= HEADER TRANG ================= */}
      <section className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          {/* Breadcrumb tối giản */}
          <nav className="flex items-center gap-1.5 text-sm text-slate-500 mb-1">
            <Link href="/dashboard" className="hover:text-slate-800 transition-colors">
              Trang chủ
            </Link>
            <span>/</span>
            <span className="text-slate-800 font-medium">Tổng quan</span>
          </nav>

          {/* Tiêu đề & Trạng thái đồng bộ */}
          <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">
            Bảng điều khiển tổng quan
          </h1>
          <div className="flex items-center gap-1.5 text-[13px] text-slate-500 mt-1">
            <span
              className={`w-2 h-2 rounded-full shrink-0 ${
                errorMessage ? "bg-rose-500" : "bg-emerald-500"
              }`}
            />
            <span>
              {errorMessage
                ? "Không kết nối được máy chủ"
                : `Cập nhật lúc ${lastSyncText}`}
            </span>
          </div>
        </div>

        {/* Nút thao tác: Làm mới (outline) + Xuất báo cáo (primary duy nhất) */}
        <div className="flex items-center gap-2.5 shrink-0 relative">
          <button
            type="button"
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-2 px-3.5 h-10 rounded-lg bg-white border border-slate-200 text-slate-700 font-medium text-sm hover:bg-slate-50 active:scale-[0.99] transition-colors min-h-[40px] disabled:opacity-50 disabled:text-slate-400 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
            aria-label="Làm mới dữ liệu"
          >
            <span>{isRefreshing ? "Đang cập nhật..." : "Làm mới"}</span>
          </button>

          {/* Menu Xuất Báo Cáo - Nút Primary duy nhất */}
          <div className="relative" ref={exportMenuRef}>
            <button
              type="button"
              onClick={() => setShowExportMenu(!showExportMenu)}
              aria-haspopup="menu"
              aria-expanded={showExportMenu}
              className="flex items-center gap-2 px-4 h-10 rounded-lg bg-primary hover:bg-primary-hover text-white font-medium text-sm transition-colors min-h-[40px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-1"
              aria-label="Xuất báo cáo dữ liệu"
            >
              <span>Xuất báo cáo</span>
            </button>

            {showExportMenu && (
              <div className="absolute right-0 mt-1.5 w-48 bg-white rounded-lg shadow-lg border border-slate-200 p-1 z-30 animate-in fade-in zoom-in-95 duration-100">
                <button
                  type="button"
                  onClick={handleExportCsv}
                  className="w-full px-3 py-2 rounded-md text-[13px] font-medium text-slate-700 hover:bg-slate-50 transition-colors text-left"
                >
                  Xuất file Excel (.csv)
                </button>
                <button
                  type="button"
                  onClick={handlePrintPdf}
                  className="w-full px-3 py-2 rounded-md text-[13px] font-medium text-slate-700 hover:bg-slate-50 transition-colors text-left"
                >
                  In hoặc lưu PDF
                </button>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Thông báo lỗi nếu có */}
      {errorMessage && (
        <Alert variant="error">
          <span>{errorMessage}</span>
          <Link
            href="/login"
            className="font-medium underline hover:text-rose-900 shrink-0"
          >
            Đăng nhập lại
          </Link>
        </Alert>
      )}

      {/* ================= 4 THẺ KPI ================= */}
      <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {/* Thẻ 1: Tổng Giảng Viên */}
        <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <span className="text-sm text-slate-500 font-normal">
            Tổng số giảng viên
          </span>
          <div className="mt-3">
            {overviewLoading ? (
              <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
            ) : (
              <div className="text-3xl font-semibold text-slate-900 tracking-tight">
                {overview?.total_instructors ?? 0}
              </div>
            )}
            <div className="text-[13px] text-slate-500 mt-1">
              Không gồm quản trị viên
            </div>
          </div>
        </div>

        {/* Thẻ 2: Token Đã Sử Dụng */}
        <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <span className="text-sm text-slate-500 font-normal">
            Token đã sử dụng
          </span>
          <div className="mt-3">
            {overviewLoading ? (
              <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
            ) : (
              <div className="text-3xl font-semibold text-slate-900 tracking-tight">
                {totalTokensUsed.toLocaleString()}
              </div>
            )}
            <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden my-2">
              <div
                className="bg-primary h-full rounded-full transition-all duration-500"
                style={{ width: `${Math.min(usagePercentage, 100)}%` }}
              />
            </div>
            <div className="text-[13px] text-slate-500">
              {totalTokensUsed.toLocaleString()} / {totalBudgetLimit.toLocaleString()} token ({usagePercentage}%)
            </div>
          </div>
        </div>

        {/* Thẻ 3: Lượt Sử Dụng AI */}
        <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <span className="text-sm text-slate-500 font-normal">
            Lượt yêu cầu AI
          </span>
          <div className="mt-3">
            {loading ? (
              <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
            ) : hasUsageRecords ? (
              <div className="text-3xl font-semibold text-slate-900 tracking-tight">
                {pagination.total_items.toLocaleString()}
              </div>
            ) : (
              <div className="text-lg font-medium text-slate-500">Chưa có dữ liệu</div>
            )}
            <div className="text-[13px] text-slate-500 mt-1">
              Tổng lượt ghi nhận
            </div>
          </div>
        </div>

        {/* Thẻ 4: Tính Năng Dùng Nhiều Nhất */}
        <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <span className="text-sm text-slate-500 font-normal">
            Tính năng dùng nhiều nhất
          </span>
          <div className="mt-3">
            {overviewLoading ? (
              <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
            ) : topFeatureDisplay ? (
              <div className="text-lg font-semibold text-slate-900 tracking-tight truncate" title={topFeatureDisplay}>
                {topFeatureDisplay}
              </div>
            ) : (
              <div className="text-lg font-medium text-slate-500">Chưa có dữ liệu</div>
            )}
            <div className="text-[13px] text-slate-500 mt-1">
              {topFeatureDisplay ? "Chiếm tỷ trọng cao nhất" : "Chưa có lượt gọi AI nào"}
            </div>
          </div>
        </div>
      </section>

      {/* ================= BẢNG NHẬT KÝ SỬ DỤNG AI ================= */}
      <section className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
        <div className="p-5 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <div>
            <h2 className="text-base font-semibold text-slate-900">
              Nhật ký sử dụng AI
            </h2>
            <p className="text-[13px] text-slate-500 mt-0.5">
              Lịch sử các yêu cầu xử lý AI được ghi nhận gần đây.
            </p>
          </div>
          <span className="text-[13px] text-slate-500 font-medium">
            {hasUsageRecords ? `${pagination.total_items} bản ghi` : "Chưa có dữ liệu"}
          </span>
        </div>

        {/* Table Content */}
        <div className="overflow-x-auto w-full">
          <table className="w-full text-left text-[13px]">
            <thead className="bg-slate-50/50 text-slate-500 font-medium border-b border-slate-200">
              <tr>
                <th scope="col" className="py-3 px-4 font-medium">Mã log</th>
                <th scope="col" className="py-3 px-4 font-medium">Giảng viên</th>
                <th scope="col" className="py-3 px-4 font-medium">Tính năng</th>
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
                  <td colSpan={8} className="py-10 text-center text-slate-500">
                    <Loader2 className="w-5 h-5 mx-auto animate-spin text-primary mb-1.5" />
                    <span>Đang tải nhật ký...</span>
                  </td>
                </tr>
              ) : usageItems.length > 0 ? (
                usageItems.map((item) => (
                  <tr
                    key={item.id}
                    className="hover:bg-slate-50 transition-colors"
                  >
                    <td className="py-3 px-4 font-mono text-slate-500 text-[13px] whitespace-nowrap">
                      {item.id.slice(0, 8)}...
                    </td>
                    <td className="py-3 px-4 text-slate-900 font-medium whitespace-nowrap">
                      <div>{item.full_name || item.username}</div>
                      <div className="text-[13px] text-slate-500 font-normal">
                        @{item.username}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-slate-700 whitespace-nowrap">
                      <span className={`inline-block px-2 py-0.5 rounded text-[13px] ${featureBadgeClass(item.feature_type)}`}>
                        {featureLabel(item.feature_type)}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-[13px] text-slate-600 whitespace-nowrap">
                      {item.model_name}
                    </td>
                    <td className="py-3 px-4 text-right text-slate-600 whitespace-nowrap">
                      {item.prompt_tokens.toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-right text-slate-600 whitespace-nowrap">
                      {item.completion_tokens.toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-right font-medium text-slate-900 whitespace-nowrap">
                      {item.total_tokens.toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-right text-slate-500 text-[13px] whitespace-nowrap">
                      {new Date(item.created_at).toLocaleString("vi-VN")}
                    </td>
                  </tr>
                ))
              ) : (
                /* Empty state */
                <tr>
                  <td colSpan={8} className="py-12 text-center">
                    <div className="flex flex-col items-center justify-center gap-1.5">
                      <Inbox className="w-8 h-8 text-slate-300 mb-1" aria-hidden="true" />
                      <span className="text-sm font-medium text-slate-600">
                        Chưa có dữ liệu
                      </span>
                      <p className="text-[13px] text-slate-500 max-w-sm">
                        Các hoạt động gọi AI sẽ được tự động ghi nhận và hiển thị tại đây.
                      </p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Footer bảng: Chỉ hiển thị phân trang khi tổng bản ghi > page_size */}
        <div className="p-4 border-t border-slate-200 flex items-center justify-between text-sm text-slate-500">
          <span>{hasUsageRecords ? `${pagination.total_items} bản ghi` : "Chưa có dữ liệu"}</span>

          {pagination.total_items > pagination.page_size && (
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage <= 1 || loading}
                className="px-3 h-9 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors min-h-[36px] flex items-center justify-center text-[13px] font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
                aria-label="Trang trước"
              >
                Trước
              </button>
              <span className="px-2.5 py-1 text-[13px] font-medium text-slate-700 bg-slate-100 rounded-md">
                {currentPage} / {pagination.total_pages}
              </span>
              <button
                type="button"
                onClick={() =>
                  setCurrentPage((p) =>
                    Math.min(Math.max(1, pagination.total_pages), p + 1)
                  )
                }
                disabled={
                  currentPage >= pagination.total_pages ||
                  loading ||
                  pagination.total_pages === 0
                }
                className="px-3 h-9 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors min-h-[36px] flex items-center justify-center text-[13px] font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
                aria-label="Trang sau"
              >
                Sau
              </button>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
