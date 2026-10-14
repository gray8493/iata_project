"use client";

import React, { useState, useMemo, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  Home,
  RefreshCw,
  FileDown,
  ChevronDown,
  Users,
  Cpu,
  CheckCircle2,
  BookOpen,
  Laptop,
  Info,
  ArrowRight,
  Search,
  SlidersHorizontal,
  Clock,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

interface BatchItem {
  id: string;
  course: string;
  courseColor: string;
  className: string;
  instructorName: string;
  instructorEmail: string;
  instructorAvatar: string;
  submissionsCount: number;
  syncTime: string;
  status: string;
}

interface OverviewReportData {
  totalInstructors: number;
  usedTokens: number;
  limitTokens: number;
  totalBatches: number;
  topFeature: string;
}

export default function DashboardOverviewPage() {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastSyncText, setLastSyncText] = useState("2 phút trước");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCourse, setSelectedCourse] = useState("ALL");
  const [currentPage, setCurrentPage] = useState(1);

  // Dynamic Metrics connected to Backend
  const [metrics, setMetrics] = useState<OverviewReportData>({
    totalInstructors: 24,
    usedTokens: 12450,
    limitTokens: 50000,
    totalBatches: 18,
    topFeature: "TESTCASE_GEN",
  });

  // Fetch overview data from Backend API
  const fetchOverviewData = useCallback(async () => {
    try {
      const token = localStorage.getItem("aita_access_token");
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000";

      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      const res = await fetch(`${apiUrl}/admin/reports/overview`, {
        method: "GET",
        headers,
      });

      if (res.ok) {
        const json = await res.json();
        if (json.success && json.data) {
          const d = json.data;
          setMetrics((prev) => ({
            ...prev,
            totalInstructors: d.total_instructors ?? prev.totalInstructors,
            usedTokens:
              d.ai_token_usage?.total_tokens_consumed_month ?? prev.usedTokens,
            limitTokens:
              d.ai_token_usage?.total_budget_limit ?? prev.limitTokens,
            topFeature:
              d.ai_token_usage?.top_consuming_feature ?? prev.topFeature,
          }));
        }
      }
    } catch {
      // Backend offline fallback - dữ liệu mock tiếp tục hoạt động trơn tru
    }
  }, []);

  useEffect(() => {
    fetchOverviewData();
  }, [fetchOverviewData]);

  // Dữ liệu đợt chấm đồng bộ từ Desktop Client
  const initialBatches: BatchItem[] = [
    {
      id: "1",
      course: "PRF192",
      courseColor: "bg-[#0054A6]/10 text-[#0054A6]",
      className: "SE1801",
      instructorName: "ThS. Trần Minh Đức",
      instructorEmail: "ductm@fe.edu.vn",
      instructorAvatar: "Đ",
      submissionsCount: 35,
      syncTime: "10:45 AM Hôm nay",
      status: "Đã lưu CSDL",
    },
    {
      id: "2",
      course: "PRO192",
      courseColor: "bg-[#F26F21]/10 text-[#F26F21]",
      className: "IA1802",
      instructorName: "TS. Lê Hoàng Nam",
      instructorEmail: "namlh@fe.edu.vn",
      instructorAvatar: "N",
      submissionsCount: 40,
      syncTime: "09:20 AM Hôm nay",
      status: "Đã lưu CSDL",
    },
    {
      id: "3",
      course: "CSD201",
      courseColor: "bg-purple-500/10 text-purple-700",
      className: "SE1704",
      instructorName: "ThS. Nguyễn Thị Mai",
      instructorEmail: "maint@fe.edu.vn",
      instructorAvatar: "M",
      submissionsCount: 28,
      syncTime: "Hôm qua 16:30",
      status: "Đã lưu CSDL",
    },
    {
      id: "4",
      course: "MAS291",
      courseColor: "bg-[#10B981]/10 text-[#10B981]",
      className: "DS1801",
      instructorName: "ThS. Vũ Quốc Tuấn",
      instructorEmail: "tuanvq@fe.edu.vn",
      instructorAvatar: "T",
      submissionsCount: 32,
      syncTime: "Hôm qua 14:15",
      status: "Đã lưu CSDL",
    },
    {
      id: "5",
      course: "PRF192",
      courseColor: "bg-[#0054A6]/10 text-[#0054A6]",
      className: "SE1803",
      instructorName: "ThS. Hoàng Văn Bình",
      instructorEmail: "binhhv@fe.edu.vn",
      instructorAvatar: "B",
      submissionsCount: 30,
      syncTime: "2 ngày trước",
      status: "Đã lưu CSDL",
    },
  ];

  // Lọc dữ liệu theo Search và Môn học
  const filteredBatches = useMemo(() => {
    return initialBatches.filter((item) => {
      const matchSearch =
        item.course.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.className.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.instructorName.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.instructorEmail.toLowerCase().includes(searchQuery.toLowerCase());
      const matchCourse =
        selectedCourse === "ALL" || item.course === selectedCourse;
      return matchSearch && matchCourse;
    });
  }, [searchQuery, selectedCourse]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await fetchOverviewData();
    setTimeout(() => {
      setIsRefreshing(false);
      setLastSyncText("Vừa xong");
    }, 600);
  };

  const tokenUsagePercentage = useMemo(() => {
    if (!metrics.limitTokens || metrics.limitTokens <= 0) return 24.9;
    const pct = (metrics.usedTokens / metrics.limitTokens) * 100;
    return Math.min(Math.round(pct * 10) / 10, 100);
  }, [metrics.usedTokens, metrics.limitTokens]);

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
              <span>Đồng bộ thời gian thực: {lastSyncText}</span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-3 self-start lg:self-auto">
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
            <span>Làm mới dữ liệu</span>
          </button>

          <button
            onClick={() =>
              alert("Đang chuẩn bị xuất báo cáo PDF & Excel từ dữ liệu tổng hợp...")
            }
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#3B2D6D] hover:bg-[#31255C] text-white font-semibold text-xs shadow-md shadow-indigo-900/10 active:scale-95 transition-all"
          >
            <FileDown className="w-3.5 h-3.5" />
            <span>Xuất báo cáo PDF/Excel</span>
            <ChevronDown className="w-3.5 h-3.5 ml-1 opacity-70" />
          </button>
        </div>
      </section>

      {/* ================= 4 METRIC STAT CARDS ================= */}
      <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5">
        {/* Card 1: Tổng Giảng Viên */}
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
                <span className="text-3xl font-extrabold text-slate-900">
                  {metrics.totalInstructors}
                </span>
                <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                  +2 mới tuần này
                </span>
              </div>
            </div>
            <div className="w-11 h-11 rounded-xl flex items-center justify-center bg-blue-50 text-[#0054A6]">
              <Users className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 pt-3 flex items-center justify-between text-[11px] text-slate-500 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-100">
            <span>Tỷ lệ tích cực</span>
            <span className="font-bold text-slate-800">
              91.6% truy cập 48h qua
            </span>
          </div>
        </div>

        {/* Card 2: Hạn Ngạch AI */}
        <div className="p-5 bg-white rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-between hover:shadow-md transition-shadow">
          <div className="flex items-start justify-between">
            <div className="w-full mr-2">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                GOOGLE GEMINI 1.5 PRO
              </span>
              <h3 className="text-xs font-medium text-slate-600 mt-0.5">
                Hạn Ngạch AI Hôm Nay
              </h3>
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-2xl font-black text-slate-900 tracking-tight">
                  {metrics.usedTokens.toLocaleString()}
                </span>
                <span className="text-xs font-semibold text-slate-400">
                  / {metrics.limitTokens.toLocaleString()} Tokens
                </span>
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
                style={{ width: `${tokenUsagePercentage}%` }}
              />
            </div>
            <div className="flex items-center justify-between text-[11px]">
              <span className="text-emerald-700 font-semibold flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-600" />
                Mức tiêu thụ ổn định
              </span>
              <span className="font-bold text-slate-800">
                {tokenUsagePercentage}%
              </span>
            </div>
          </div>
        </div>

        {/* Card 3: Đợt Chấm Đã Đồng Bộ */}
        <div className="p-5 bg-white rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-between hover:shadow-md transition-shadow">
          <div className="flex items-start justify-between">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                DỮ LIỆU ĐÁNH GIÁ
              </span>
              <h3 className="text-xs font-medium text-slate-600 mt-0.5">
                Tổng Đợt Chấm Đã Đồng Bộ
              </h3>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="text-3xl font-extrabold text-slate-900">
                  {metrics.totalBatches}
                </span>
                <span className="text-xs font-bold text-slate-500">
                  Đợt chấm thi
                </span>
              </div>
            </div>
            <div className="w-11 h-11 rounded-xl flex items-center justify-center bg-emerald-50 text-emerald-600">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 pt-3 flex items-center justify-between text-[11px] text-slate-500 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-100">
            <span>Nguồn gốc</span>
            <span className="font-bold text-emerald-700 flex items-center gap-1">
              <Laptop className="w-3.5 h-3.5" />
              Từ Desktop Client
            </span>
          </div>
        </div>

        {/* Card 4: Môn Học Đang Quản Trị */}
        <div className="p-5 bg-white rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-between hover:shadow-md transition-shadow">
          <div className="flex items-start justify-between">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                CHƯƠNG TRÌNH ĐÀO TẠO
              </span>
              <h3 className="text-xs font-medium text-slate-600 mt-0.5">
                Môn Học Đang Quản Trị
              </h3>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="text-3xl font-extrabold text-slate-900">4</span>
                <span className="text-xs font-bold text-slate-500">
                  Môn nòng cốt
                </span>
              </div>
            </div>
            <div className="w-11 h-11 rounded-xl flex items-center justify-center bg-purple-50 text-purple-700">
              <BookOpen className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex flex-wrap gap-1.5 pt-1">
            <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-[#0054A6]/10 text-[#0054A6]">
              PRF192
            </span>
            <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-[#F26F21]/10 text-[#F26F21]">
              PRO192
            </span>
            <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-purple-100 text-purple-700">
              CSD201
            </span>
            <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-emerald-100 text-emerald-800">
              MAS291
            </span>
          </div>
        </div>
      </section>

      {/* ================= BIỂU ĐỒ & ĐỒ THỊ TRỰC QUAN ================= */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Cột 1: Bar Chart Tiêu Thụ Token Gemini AI 7 ngày gần nhất */}
        <div className="lg:col-span-7 bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-between">
          <div>
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-3 gap-2">
              <div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#F26F21]" />
                  <h2 className="text-sm font-bold text-slate-900">
                    Mức Tiêu Thụ Token Gemini AI 7 Ngày Gần Nhất
                  </h2>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  Thống kê API calls phục vụ sinh phản hồi và đối chiếu tiêu chí
                </p>
              </div>
              <div className="flex items-center gap-2 bg-slate-50 px-3 py-1 rounded-full border border-slate-100 self-start">
                <span className="text-[11px] font-semibold text-slate-400">
                  Trung bình:
                </span>
                <span className="text-xs font-bold text-[#F26F21]">
                  14,200 tokens/ngày
                </span>
              </div>
            </div>

            {/* Bar Chart Visualization */}
            <div className="py-4">
              <div className="h-48 w-full flex items-end justify-between gap-3 px-2 pt-6">
                {/* T2 */}
                <div className="flex-1 flex flex-col items-center gap-2 h-full justify-end group">
                  <span className="text-[10px] font-semibold text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity">
                    11.2k
                  </span>
                  <div
                    className="w-full max-w-[36px] bg-slate-100 hover:bg-[#F26F21]/80 rounded-t-lg transition-all"
                    style={{ height: "48%" }}
                  />
                  <span className="text-xs font-medium text-slate-500">T2</span>
                </div>
                {/* T3 */}
                <div className="flex-1 flex flex-col items-center gap-2 h-full justify-end group">
                  <span className="text-[10px] font-semibold text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity">
                    14.8k
                  </span>
                  <div
                    className="w-full max-w-[36px] bg-slate-100 hover:bg-[#F26F21]/80 rounded-t-lg transition-all"
                    style={{ height: "64%" }}
                  />
                  <span className="text-xs font-medium text-slate-500">T3</span>
                </div>
                {/* T4 */}
                <div className="flex-1 flex flex-col items-center gap-2 h-full justify-end group">
                  <span className="text-[10px] font-semibold text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity">
                    18.4k
                  </span>
                  <div
                    className="w-full max-w-[36px] bg-slate-100 hover:bg-[#F26F21]/80 rounded-t-lg transition-all"
                    style={{ height: "78%" }}
                  />
                  <span className="text-xs font-medium text-slate-500">T4</span>
                </div>
                {/* T5 (Đỉnh điểm) */}
                <div className="flex-1 flex flex-col items-center gap-2 h-full justify-end group">
                  <span className="text-[10px] font-bold text-[#F26F21] bg-orange-50 px-1 rounded border border-orange-200">
                    21.5k (Đỉnh)
                  </span>
                  <div
                    className="w-full max-w-[36px] bg-[#F26F21] rounded-t-lg shadow-sm"
                    style={{ height: "92%" }}
                  />
                  <span className="text-xs font-bold text-[#F26F21]">T5</span>
                </div>
                {/* T6 */}
                <div className="flex-1 flex flex-col items-center gap-2 h-full justify-end group">
                  <span className="text-[10px] font-semibold text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity">
                    16.3k
                  </span>
                  <div
                    className="w-full max-w-[36px] bg-slate-100 hover:bg-[#F26F21]/80 rounded-t-lg transition-all"
                    style={{ height: "70%" }}
                  />
                  <span className="text-xs font-medium text-slate-500">T6</span>
                </div>
                {/* T7 */}
                <div className="flex-1 flex flex-col items-center gap-2 h-full justify-end group">
                  <span className="text-[10px] font-semibold text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity">
                    12.4k
                  </span>
                  <div
                    className="w-full max-w-[36px] bg-slate-100 hover:bg-[#F26F21]/80 rounded-t-lg transition-all"
                    style={{ height: "54%" }}
                  />
                  <span className="text-xs font-medium text-slate-500">T7</span>
                </div>
                {/* CN */}
                <div className="flex-1 flex flex-col items-center gap-2 h-full justify-end group">
                  <span className="text-[10px] font-semibold text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity">
                    8.6k
                  </span>
                  <div
                    className="w-full max-w-[36px] bg-slate-100 hover:bg-[#F26F21]/80 rounded-t-lg transition-all"
                    style={{ height: "36%" }}
                  />
                  <span className="text-xs font-medium text-slate-500">CN</span>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-3 flex items-center justify-between text-xs text-slate-500 bg-slate-50 px-4 py-2.5 rounded-xl border border-slate-100">
            <span className="flex items-center gap-1.5 text-[11px]">
              <Info className="w-3.5 h-3.5 text-slate-400" />
              Hạn ngạch cấp ngày: 50,000 Tokens (Rate limit 15 RPM)
            </span>
            <Link
              href="/ai-quotas"
              className="text-[#F26F21] font-semibold hover:underline flex items-center gap-0.5 text-xs"
            >
              Cấu hình quota
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {/* Cột 2: Donut Chart Tỷ Lệ Bài Thi Theo Ngôn Ngữ */}
        <div className="lg:col-span-5 bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-1">
              <h2 className="text-sm font-bold text-slate-900">
                Tỷ Lệ Phân Bổ Bài Thi
              </h2>
              <span className="text-[10px] font-bold px-2 py-0.5 bg-slate-100 text-slate-600 rounded-full">
                Tổng: 1,420 bài
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Theo cấu trúc ngôn ngữ lập trình của các đợt nộp
            </p>

            {/* Donut SVG Display */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-6 py-5">
              <div className="relative w-36 h-36 flex items-center justify-center">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                  {/* Background circle */}
                  <circle
                    cx="50"
                    cy="50"
                    fill="none"
                    r="38"
                    stroke="#F1F5F9"
                    strokeWidth="14"
                  />
                  {/* Segment 1: C (42%) */}
                  <circle
                    cx="50"
                    cy="50"
                    fill="none"
                    r="38"
                    stroke="#0054A6"
                    strokeDasharray="100.28 238.76"
                    strokeDashoffset="0"
                    strokeWidth="14"
                  />
                  {/* Segment 2: Java (38%) */}
                  <circle
                    cx="50"
                    cy="50"
                    fill="none"
                    r="38"
                    stroke="#F26F21"
                    strokeDasharray="90.73 238.76"
                    strokeDashoffset="-100.28"
                    strokeWidth="14"
                  />
                  {/* Segment 3: Python (20%) */}
                  <circle
                    cx="50"
                    cy="50"
                    fill="none"
                    r="38"
                    stroke="#10B981"
                    strokeDasharray="47.75 238.76"
                    strokeDashoffset="-191.01"
                    strokeWidth="14"
                  />
                </svg>
                <div className="absolute flex flex-col items-center justify-center text-center">
                  <span className="text-lg font-black text-slate-900 leading-none">
                    1,420
                  </span>
                  <span className="text-[9px] font-bold text-slate-400 uppercase mt-0.5">
                    BÀI ĐÃ NỘP
                  </span>
                </div>
              </div>

              {/* Legend Items */}
              <div className="flex flex-col gap-2 w-full sm:w-auto">
                {/* Item C */}
                <div className="flex items-center justify-between gap-4 p-2 rounded-lg bg-slate-50 hover:bg-slate-100 transition-colors">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#0054A6]" />
                    <span className="text-xs font-semibold text-slate-700">
                      Ngôn ngữ C
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-extrabold text-[#0054A6]">
                      42%
                    </span>
                    <span className="text-[10px] text-slate-400 ml-1">
                      (596 bài)
                    </span>
                  </div>
                </div>

                {/* Item Java */}
                <div className="flex items-center justify-between gap-4 p-2 rounded-lg bg-slate-50 hover:bg-slate-100 transition-colors">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#F26F21]" />
                    <span className="text-xs font-semibold text-slate-700">
                      Java Core
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-extrabold text-[#F26F21]">
                      38%
                    </span>
                    <span className="text-[10px] text-slate-400 ml-1">
                      (540 bài)
                    </span>
                  </div>
                </div>

                {/* Item Python */}
                <div className="flex items-center justify-between gap-4 p-2 rounded-lg bg-slate-50 hover:bg-slate-100 transition-colors">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#10B981]" />
                    <span className="text-xs font-semibold text-slate-700">
                      Python / MAS
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-extrabold text-[#10B981]">
                      20%
                    </span>
                    <span className="text-[10px] text-slate-400 ml-1">
                      (284 bài)
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-2 text-[10px] text-center text-slate-400 bg-slate-50 rounded-lg py-1.5 border border-slate-100">
            Hệ thống hỗ trợ parse tự động file nén ZIP / RAR từ Desktop Client
          </div>
        </div>
      </section>

      {/* ================= BẢNG DANH SÁCH CÁC ĐỢT CHẤM VỪA ĐỒNG BỘ ================= */}
      <section className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden flex flex-col">
        {/* Header của bảng */}
        <div className="p-6 pb-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="p-1 rounded-md bg-purple-50 text-purple-700">
                <CheckCircle2 className="w-4 h-4" />
              </span>
              <h2 className="text-base font-bold text-slate-900">
                Các Đợt Chấm Vừa Đồng Bộ Từ Desktop Client
              </h2>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Danh sách các bài thi đã được giảng viên upload và hoàn tất ghi
              nhận vào CSDL trung tâm
            </p>
          </div>

          {/* Controls: Tìm kiếm & Bộ lọc môn */}
          <div className="flex items-center gap-3 flex-wrap">
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Tìm mã môn, lớp, giảng viên..."
                className="pl-8 pr-3 py-1.5 rounded-lg text-xs bg-slate-50 text-slate-800 border border-slate-200 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-[#F26F21] w-48 sm:w-56"
              />
            </div>

            <select
              value={selectedCourse}
              onChange={(e) => setSelectedCourse(e.target.value)}
              className="px-3 py-1.5 rounded-lg text-xs bg-slate-50 text-slate-800 border border-slate-200 font-medium focus:outline-none focus:ring-1 focus:ring-[#F26F21]"
            >
              <option value="ALL">Tất cả môn học</option>
              <option value="PRF192">PRF192 - C</option>
              <option value="PRO192">PRO192 - Java</option>
              <option value="CSD201">CSD201 - Data Structures</option>
              <option value="MAS291">MAS291 - Statistics</option>
            </select>

            <button
              onClick={() => alert("Bộ lọc nâng cao theo thời gian và phòng thi")}
              className="p-1.5 rounded-lg bg-slate-50 hover:bg-slate-100 text-slate-600 border border-slate-200 transition-colors"
              title="Bộ lọc nâng cao"
            >
              <SlidersHorizontal className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Data Table */}
        <div className="overflow-x-auto w-full">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50/80 text-slate-500 uppercase text-[10px] font-bold tracking-wider border-y border-slate-100">
              <tr>
                <th className="px-6 py-3">MÃ MÔN HỌC</th>
                <th className="px-6 py-3">LỚP HỌC</th>
                <th className="px-6 py-3">GIẢNG VIÊN CHẤM</th>
                <th className="px-6 py-3">SỐ LƯỢNG BÀI</th>
                <th className="px-6 py-3">THỜI GIAN ĐỒNG BỘ</th>
                <th className="px-6 py-3">TRẠNG THÁI</th>
                <th className="px-6 py-3 text-right">THAO TÁC</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {filteredBatches.length > 0 ? (
                filteredBatches.map((batch) => (
                  <tr
                    key={batch.id}
                    className="hover:bg-slate-50/80 transition-colors"
                  >
                    <td className="px-6 py-3.5">
                      <span
                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md font-bold text-[11px] ${batch.courseColor}`}
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-current" />
                        {batch.course}
                      </span>
                    </td>
                    <td className="px-6 py-3.5 font-bold text-slate-800">
                      {batch.className}
                    </td>
                    <td className="px-6 py-3.5">
                      <div className="flex items-center gap-2.5">
                        <div className="w-7 h-7 rounded-full bg-slate-100 flex items-center justify-center text-xs font-bold text-slate-600">
                          {batch.instructorAvatar}
                        </div>
                        <div>
                          <span className="text-slate-800 font-semibold block leading-tight text-xs">
                            {batch.instructorName}
                          </span>
                          <span className="text-[10px] text-slate-400">
                            {batch.instructorEmail}
                          </span>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-3.5">
                      <span className="font-extrabold text-slate-900">
                        {batch.submissionsCount}
                      </span>{" "}
                      <span className="text-slate-400 text-[11px]">bài</span>
                    </td>
                    <td className="px-6 py-3.5 text-slate-500">
                      <div className="flex items-center gap-1.5 text-[11px]">
                        <Clock className="w-3.5 h-3.5 text-slate-400" />
                        <span>{batch.syncTime}</span>
                      </div>
                    </td>
                    <td className="px-6 py-3.5">
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-[10px] font-bold border border-emerald-200">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                        {batch.status}
                      </span>
                    </td>
                    <td className="px-6 py-3.5 text-right">
                      <button
                        onClick={() =>
                          alert(
                            `Xem chi tiết đợt chấm: ${batch.course} - ${batch.className}`
                          )
                        }
                        className="px-3 py-1.5 rounded-lg bg-purple-50 hover:bg-purple-100 text-purple-700 font-semibold text-xs transition-colors"
                      >
                        Xem chi tiết
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-400">
                    Không tìm thấy đợt chấm nào phù hợp với bộ lọc hiện tại.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Phân trang & Footer bảng */}
        <div className="px-6 py-3.5 bg-white flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-slate-100 text-xs text-slate-500">
          <div className="flex items-center gap-1 text-[11px]">
            <span>Hiển thị</span>
            <span className="font-bold text-slate-800">
              1 - {filteredBatches.length}
            </span>
            <span>trong tổng số</span>
            <span className="font-bold text-slate-800">18</span>
            <span>đợt chấm</span>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="p-1 rounded-md bg-slate-100 text-slate-500 hover:bg-slate-200 disabled:opacity-40 transition-colors"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            {[1, 2, 3, 4].map((page) => (
              <button
                key={page}
                onClick={() => setCurrentPage(page)}
                className={`w-6 h-6 rounded-md text-xs font-bold transition-colors ${
                  currentPage === page
                    ? "bg-[#3B2D6D] text-white"
                    : "hover:bg-slate-100 text-slate-600 font-medium"
                }`}
              >
                {page}
              </button>
            ))}
            <button
              onClick={() => setCurrentPage((p) => Math.min(4, p + 1))}
              disabled={currentPage === 4}
              className="p-1 rounded-md bg-slate-100 text-slate-500 hover:bg-slate-200 transition-colors"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
