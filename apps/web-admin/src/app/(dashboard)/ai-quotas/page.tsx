"use client";

import React, { useState, useMemo } from "react";
import {
  SlidersHorizontal,
  RefreshCw,
  AlertTriangle,
  X,
  TrendingUp,
  Clock,
  Zap,
  RotateCcw,
  Sparkles,
  Search,
  Filter,
  Sliders,
  ChevronLeft,
  ChevronRight,
  PlusCircle,
  Activity,
  CheckCircle,
} from "lucide-react";

interface InstructorQuota {
  id: string;
  name: string;
  department: string;
  avatar: string;
  avatarBg: string;
  email: string;
  usedTokens: number;
  remainingTokens: number;
  limitTokens: number;
  testcaseCount: number;
  aiReviewCount: number;
  isOverLimit?: boolean;
}

export default function AiQuotasPage() {
  const [showAlert, setShowAlert] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterOverLimitOnly, setFilterOverLimitOnly] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);

  // Danh sách giảng viên tiêu thụ hạn ngạch
  const [instructors, setInstructors] = useState<InstructorQuota[]>([
    {
      id: "1",
      name: "TS. Lê Hoàng Nam",
      department: "Bộ môn Kỹ thuật phần mềm",
      avatar: "LN",
      avatarBg: "bg-red-100 text-red-700",
      email: "namlh@fe.edu.vn",
      usedTokens: 4850,
      remainingTokens: 150,
      limitTokens: 5000,
      testcaseCount: 28,
      aiReviewCount: 14,
      isOverLimit: true,
    },
    {
      id: "2",
      name: "ThS. Hoàng Văn Bình",
      department: "Bộ môn Trí tuệ nhân tạo",
      avatar: "HB",
      avatarBg: "bg-amber-100 text-amber-800",
      email: "binhhv@fe.edu.vn",
      usedTokens: 3100,
      remainingTokens: 1900,
      limitTokens: 5000,
      testcaseCount: 18,
      aiReviewCount: 9,
    },
    {
      id: "3",
      name: "ThS. Trần Minh Đức",
      department: "Bộ môn An toàn thông tin",
      avatar: "MD",
      avatarBg: "bg-emerald-100 text-emerald-800",
      email: "ductm@fe.edu.vn",
      usedTokens: 2400,
      remainingTokens: 2600,
      limitTokens: 5000,
      testcaseCount: 12,
      aiReviewCount: 8,
    },
    {
      id: "4",
      name: "ThS. Nguyễn Thị Mai",
      department: "Bộ môn Khoa học dữ liệu",
      avatar: "NM",
      avatarBg: "bg-purple-100 text-purple-800",
      email: "maint@fe.edu.vn",
      usedTokens: 1200,
      remainingTokens: 2800,
      limitTokens: 4000,
      testcaseCount: 6,
      aiReviewCount: 4,
    },
    {
      id: "5",
      name: "ThS. Vũ Quốc Tuấn",
      department: "Bộ môn Hệ thống thông tin",
      avatar: "VT",
      avatarBg: "bg-slate-100 text-slate-700",
      email: "tuanvq@fe.edu.vn",
      usedTokens: 0,
      remainingTokens: 3000,
      limitTokens: 3000,
      testcaseCount: 0,
      aiReviewCount: 0,
    },
  ]);

  // Bộ lọc danh sách
  const filteredInstructors = useMemo(() => {
    return instructors.filter((item) => {
      const matchSearch =
        item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.department.toLowerCase().includes(searchQuery.toLowerCase());
      const matchOverLimit = filterOverLimitOnly ? item.isOverLimit : true;
      return matchSearch && matchOverLimit;
    });
  }, [instructors, searchQuery, filterOverLimitOnly]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setIsRefreshing(false);
    }, 600);
  };

  const handleAddTokens = (instructorId: string) => {
    setInstructors((prev) =>
      prev.map((ins) => {
        if (ins.id === instructorId) {
          const newLimit = ins.limitTokens + 2000;
          const newRemaining = ins.remainingTokens + 2000;
          return {
            ...ins,
            limitTokens: newLimit,
            remainingTokens: newRemaining,
            isOverLimit: false,
          };
        }
        return ins;
      })
    );
    alert("Đã cấp thêm +2,000 Tokens khẩn cấp thành công cho giảng viên!");
    setShowAlert(false);
  };

  return (
    <div className="flex flex-col w-full gap-5">
      {/* ================= BREADCRUMB & HEADER ================= */}
      <section className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
        <div className="flex flex-col gap-1.5">
          {/* Breadcrumb */}
          <nav className="flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-400">
            <span>Trang chủ</span>
            <span>&gt;</span>
            <span className="text-[#F26F21]">Giám sát Hạn ngạch AI</span>
          </nav>

          {/* Heading */}
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 mt-0.5">
            Giám Sát & Điều Phối Hạn Ngạch Google Gemini AI
          </h1>

          {/* Status Chip & Subtitle */}
          <div className="flex items-center gap-3 flex-wrap mt-0.5">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-xs font-semibold border border-emerald-200">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Gemini 1.5 Pro Connected • 240ms
            </span>
            <span className="text-xs text-slate-400">
              Phân bổ Token, kiểm soát lưu lượng gọi API và tối ưu chi phí hạ
              tầng AI hỗ trợ khảo thí.
            </span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2.5 self-start lg:self-auto">
          <button
            onClick={() =>
              alert("Mở hộp thoại Cấu hình Hạn ngạch Toàn trường...")
            }
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#B78838] hover:bg-[#A3772C] text-white font-semibold text-xs shadow-md shadow-amber-900/10 active:scale-95 transition-all"
          >
            <SlidersHorizontal className="w-3.5 h-3.5" />
            <span>Cấu hình Hạn Ngạch Toàn Trường</span>
          </button>

          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="p-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors disabled:opacity-60"
            title="Làm mới dữ liệu"
          >
            <RefreshCw
              className={`w-4 h-4 ${
                isRefreshing ? "rotate-180 animate-spin text-[#F26F21]" : ""
              }`}
            />
          </button>
        </div>
      </section>

      {/* ================= EMERGENCY QUOTA ALERT BANNER ================= */}
      {showAlert && (
        <section className="p-4 rounded-2xl bg-[#FFF6EE] border border-[#FED7AA] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 transition-all">
          <div className="flex items-start gap-3.5">
            <div className="p-2 rounded-xl bg-[#FDBA74]/30 text-[#EA580C] flex-shrink-0 mt-0.5">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs font-extrabold uppercase tracking-wider text-[#C2410C]">
                CẢNH BÁO QUOTA KHẨN CẤP
              </div>
              <p className="text-xs text-slate-700 mt-0.5 leading-relaxed">
                Giảng viên <strong className="text-slate-900">TS. Lê Hoàng Nam</strong> đã sử
                dụng <strong className="text-[#EA580C]">97%</strong> hạn ngạch
                trong ngày (4,850 / 5,000 tokens). Hệ thống đã kích hoạt cơ chế
                tiết kiệm token tự động cho module Sinh Testcase.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 self-end sm:self-auto">
            <button
              onClick={() => handleAddTokens("1")}
              className="px-3.5 py-2 rounded-xl bg-[#EA580C] hover:bg-[#C2410C] text-white font-bold text-xs tracking-wide shadow-sm transition-colors whitespace-nowrap"
            >
              +2,000 Token Ngay
            </button>
            <button
              onClick={() => setShowAlert(false)}
              className="p-2 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-orange-100/50 transition-colors"
              title="Đóng cảnh báo"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </section>
      )}

      {/* ================= MAIN QUOTA GAUGES & INFRASTRUCTURE ================= */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* ================= CỘT TRÁI (LỚN): DAILY MASTER TOKEN POOL ================= */}
        <div className="lg:col-span-8 bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-between">
          <div>
            {/* Top row */}
            <div className="flex items-start justify-between gap-4 mb-4">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  HẠN MỨC TOÀN HỆ THỐNG (DAILY MASTER TOKEN POOL)
                </span>
                <h2 className="text-sm font-bold text-slate-900 mt-0.5">
                  Gemini Token Consumption Rate
                </h2>
              </div>
              <span className="px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 text-[11px] font-bold border border-emerald-200">
                Hệ thống an toàn (&lt; 50%)
              </span>
            </div>

            {/* Big Numbers */}
            <div className="flex items-baseline gap-2.5 flex-wrap my-2">
              <span className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
                12,450
              </span>
              <span className="text-lg font-bold text-slate-400">
                / 50,000
              </span>
              <span className="text-xs font-semibold text-slate-400">
                tokens hôm nay
              </span>
              <span className="ml-auto inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-indigo-50 text-indigo-700 font-bold text-xs">
                <TrendingUp className="w-3.5 h-3.5" />
                24.9% Đã Tiêu Thụ
              </span>
            </div>

            {/* Multi-tier Progress Bar */}
            <div className="mt-4 mb-3">
              <div className="w-full bg-slate-100 h-3 rounded-full overflow-hidden flex relative">
                {/* 24.9% used */}
                <div
                  className="h-full bg-gradient-to-r from-[#0054A6] via-[#10B981] to-[#F26F21] rounded-full transition-all duration-700"
                  style={{ width: "24.9%" }}
                />
              </div>

              {/* Threshold Labels */}
              <div className="flex items-center justify-between text-[10px] text-slate-400 mt-2 font-medium px-0.5">
                <span>0%</span>
                <span className="text-slate-500 font-semibold">
                  50% (Tiêu chuẩn)
                </span>
                <span className="text-amber-600 font-semibold">
                  80% Cảnh báo
                </span>
                <span className="text-red-500 font-semibold">
                  90% Giới hạn
                </span>
                <span>100%</span>
              </div>
            </div>

            {/* 3 Feature Token Breakdown Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5 mt-6 pt-5 border-t border-slate-100">
              {/* Feature 1 */}
              <div className="p-3.5 rounded-xl bg-slate-50/80 border border-slate-100 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between text-[11px] mb-1">
                    <span className="font-semibold text-slate-700">
                      Sinh Testcase tự động
                    </span>
                    <span className="font-extrabold text-[#0054A6]">54.6%</span>
                  </div>
                  <div className="text-lg font-black text-slate-900">6,800</div>
                  <span className="text-[10px] text-slate-400">tokens</span>
                </div>
                <div className="w-full bg-slate-200 h-1.5 rounded-full mt-2.5 overflow-hidden">
                  <div className="bg-[#0054A6] h-full rounded-full w-[54.6%]" />
                </div>
              </div>

              {/* Feature 2 */}
              <div className="p-3.5 rounded-xl bg-slate-50/80 border border-slate-100 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between text-[11px] mb-1">
                    <span className="font-semibold text-slate-700">
                      Đánh giá & Review logic
                    </span>
                    <span className="font-extrabold text-[#F26F21]">39.8%</span>
                  </div>
                  <div className="text-lg font-black text-slate-900">4,950</div>
                  <span className="text-[10px] text-slate-400">tokens</span>
                </div>
                <div className="w-full bg-slate-200 h-1.5 rounded-full mt-2.5 overflow-hidden">
                  <div className="bg-[#F26F21] h-full rounded-full w-[39.8%]" />
                </div>
              </div>

              {/* Feature 3 */}
              <div className="p-3.5 rounded-xl bg-slate-50/80 border border-slate-100 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between text-[11px] mb-1">
                    <span className="font-semibold text-slate-700">
                      Phân tích cú pháp & Gợi ý
                    </span>
                    <span className="font-extrabold text-[#10B981]">5.6%</span>
                  </div>
                  <div className="text-lg font-black text-slate-900">700</div>
                  <span className="text-[10px] text-slate-400">tokens</span>
                </div>
                <div className="w-full bg-slate-200 h-1.5 rounded-full mt-2.5 overflow-hidden">
                  <div className="bg-[#10B981] h-full rounded-full w-[5.6%]" />
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Card Footer */}
          <div className="mt-6 pt-4 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500">
            <div className="flex items-center gap-1.5 text-slate-600">
              <Clock className="w-4 h-4 text-slate-400" />
              <span>
                Chu kỳ làm mới tiếp theo: <strong>00:00:00 GMT+7</strong> (còn
                6h 15p)
              </span>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() =>
                  alert("Kích hoạt chế độ Nâng mức Hạn ngạch khẩn cấp!")
                }
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-orange-50 hover:bg-orange-100 text-[#EA580C] font-semibold text-xs border border-orange-200 transition-colors"
              >
                <Zap className="w-3.5 h-3.5" />
                <span>Nâng mức khẩn cấp</span>
              </button>
              <button
                onClick={() =>
                  alert("Đã gửi tín hiệu reset bộ đếm hạn ngạch 24h.")
                }
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs transition-colors"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Reset 24h</span>
              </button>
            </div>
          </div>
        </div>

        {/* ================= CỘT PHẢI (NHỎ): LLM INFRASTRUCTURE & TIPS ================= */}
        <div className="lg:col-span-4 flex flex-col gap-4">
          {/* Card Trên: HẠ TẦNG LLM */}
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  HẠ TẦNG LLM
                </span>
                <span className="p-1.5 rounded-lg bg-purple-50 text-purple-700">
                  <Activity className="w-4 h-4" />
                </span>
              </div>

              <h2 className="text-base font-extrabold text-slate-900 mb-4">
                Google Gemini 1.5 Pro
              </h2>

              {/* Request Sparkline Display */}
              <div className="mb-4">
                <div className="flex items-baseline justify-between text-xs mb-1">
                  <span className="text-slate-500 font-medium">
                    Lưu lượng request (24h qua)
                  </span>
                  <span className="text-purple-700 font-bold">142 RPM Peak</span>
                </div>
                {/* SVG Curve Sparkline */}
                <div className="w-full h-14 bg-purple-50/50 rounded-xl p-1 flex items-center justify-center overflow-hidden">
                  <svg
                    viewBox="0 0 200 40"
                    className="w-full h-full text-purple-600 stroke-current fill-purple-100"
                  >
                    <path
                      d="M0,35 Q30,10 60,25 T120,8 T160,20 T200,12 L200,40 L0,40 Z"
                      opacity="0.4"
                    />
                    <path
                      d="M0,35 Q30,10 60,25 T120,8 T160,20 T200,12"
                      fill="none"
                      strokeWidth="2.5"
                    />
                  </svg>
                </div>
              </div>

              {/* Stats Rows */}
              <div className="space-y-2.5 text-xs">
                <div className="flex items-center justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Tỷ lệ Prompt Cache Hit:</span>
                  <span className="font-extrabold text-emerald-700">
                    81.4% <span className="text-[10px] text-emerald-600">(Tối ưu 42% token)</span>
                  </span>
                </div>

                <div className="flex items-center justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Chi phí ước tính phiên này:</span>
                  <span className="font-extrabold text-slate-800">
                    $0.87 USD <span className="text-[10px] text-slate-400">(~21,500đ)</span>
                  </span>
                </div>

                <div className="flex items-center justify-between py-1">
                  <span className="text-slate-500">Ngưỡng giới hạn/giảng viên:</span>
                  <span className="font-extrabold text-slate-900">
                    5,000 Token/Ngày
                  </span>
                </div>
              </div>
            </div>

            <button
              onClick={() => alert("Mở cấu hình Hạn mức riêng từng Giảng viên...")}
              className="w-full mt-5 py-2.5 px-3 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition-colors"
            >
              Điều chỉnh Hạn mức Giảng viên
            </button>
          </div>

          {/* Card Dưới: Gợi ý tối ưu Token */}
          <div className="p-4 rounded-2xl bg-gradient-to-br from-[#EDE9FE] to-[#F5F3FF] border border-[#DDD6FE] flex items-start gap-3 text-xs">
            <div className="p-2 rounded-xl bg-purple-600 text-white flex-shrink-0 mt-0.5">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <span className="font-extrabold text-purple-900 block mb-0.5">
                Gợi ý tối ưu Token
              </span>
              <p className="text-purple-800/90 text-[11px] leading-relaxed">
                Khuyến khích giảng viên rút ngắn tài liệu SRS đầu vào hoặc bật tính năng{" "}
                <strong>Context Truncation</strong> để giảm 35% lượng token tiêu thụ.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ================= DATA TABLE: INSTRUCTOR CONSUMPTION ================= */}
      <section className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden flex flex-col">
        {/* Table Header */}
        <div className="p-6 pb-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-extrabold text-slate-900">
                Theo Dõi Chi Tiết Tiêu Thụ Từng Giảng Viên
              </h2>
              <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[11px] font-semibold">
                5 Giảng viên ca trực
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Cập nhật theo thời gian thực mỗi khi có request sinh đề, testcase hoặc chấm bài
            </p>
          </div>

          {/* Controls: Tìm kiếm & Lọc vượt ngưỡng */}
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Tìm tên, email..."
                className="pl-8 pr-3 py-1.5 rounded-lg text-xs bg-slate-50 text-slate-800 border border-slate-200 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-[#F26F21] w-48 sm:w-56"
              />
            </div>

            <button
              onClick={() => setFilterOverLimitOnly(!filterOverLimitOnly)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                filterOverLimitOnly
                  ? "bg-red-50 text-red-700 border-red-300"
                  : "bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100"
              }`}
            >
              <Filter className="w-3.5 h-3.5" />
              <span>{filterOverLimitOnly ? "Đang lọc: Vượt ngưỡng" : "Lọc vượt ngưỡng"}</span>
            </button>
          </div>
        </div>

        {/* Data Table */}
        <div className="overflow-x-auto w-full">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50/80 text-slate-500 uppercase text-[10px] font-bold tracking-wider border-y border-slate-100">
              <tr>
                <th className="px-6 py-3">GIẢNG VIÊN</th>
                <th className="px-6 py-3">EMAIL</th>
                <th className="px-6 py-3">ĐÃ DÙNG (HÔM NAY)</th>
                <th className="px-6 py-3">CÒN LẠI</th>
                <th className="px-6 py-3">SINH TESTCASE</th>
                <th className="px-6 py-3">AI REVIEW</th>
                <th className="px-6 py-3">TỶ LỆ SỬ DỤNG</th>
                <th className="px-6 py-3 text-right">THAO TÁC</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {filteredInstructors.length > 0 ? (
                filteredInstructors.map((ins) => {
                  const percentage = Math.round(
                    (ins.usedTokens / ins.limitTokens) * 100
                  );
                  return (
                    <tr
                      key={ins.id}
                      className="hover:bg-slate-50/80 transition-colors"
                    >
                      {/* Giảng viên */}
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2.5">
                          <div
                            className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${ins.avatarBg}`}
                          >
                            {ins.avatar}
                          </div>
                          <div>
                            <div className="flex items-center gap-1.5">
                              <span className="font-bold text-slate-900">
                                {ins.name}
                              </span>
                              {ins.isOverLimit && (
                                <span className="px-1.5 py-0.2 rounded bg-red-600 text-white text-[9px] font-black uppercase">
                                  97% Vượt Ngưỡng
                                </span>
                              )}
                            </div>
                            <span className="text-[10px] text-slate-400 block">
                              {ins.department}
                            </span>
                          </div>
                        </div>
                      </td>

                      {/* Email */}
                      <td className="px-6 py-4 text-slate-500 font-mono text-[11px]">
                        {ins.email}
                      </td>

                      {/* Đã dùng */}
                      <td className="px-6 py-4">
                        <span
                          className={`font-black ${
                            percentage >= 90
                              ? "text-red-600"
                              : percentage >= 60
                              ? "text-amber-600"
                              : percentage > 0
                              ? "text-emerald-700"
                              : "text-slate-400"
                          }`}
                        >
                          {ins.usedTokens.toLocaleString()} tk
                        </span>
                      </td>

                      {/* Còn lại */}
                      <td className="px-6 py-4 text-slate-500 font-semibold">
                        {ins.remainingTokens.toLocaleString()} tk
                      </td>

                      {/* Sinh Testcase */}
                      <td className="px-6 py-4">
                        <span className="font-extrabold text-slate-800">
                          {ins.testcaseCount}
                        </span>{" "}
                        <span className="text-slate-400 text-[10px]">lượt</span>
                      </td>

                      {/* AI Review */}
                      <td className="px-6 py-4">
                        <span className="font-extrabold text-slate-800">
                          {ins.aiReviewCount}
                        </span>{" "}
                        <span className="text-slate-400 text-[10px]">lượt</span>
                      </td>

                      {/* Tỷ lệ sử dụng */}
                      <td className="px-6 py-4 min-w-[150px]">
                        <div className="flex items-center justify-between text-[10px] font-semibold mb-1">
                          <span
                            className={
                              percentage >= 90
                                ? "text-red-600"
                                : percentage >= 60
                                ? "text-amber-600"
                                : percentage > 0
                                ? "text-emerald-700"
                                : "text-slate-400"
                            }
                          >
                            {percentage > 0 ? `${percentage}%` : "0%"}
                          </span>
                          <span className="text-slate-400 font-mono">
                            {ins.usedTokens > 0
                              ? `${ins.usedTokens.toLocaleString()} / ${ins.limitTokens.toLocaleString()}`
                              : "Chưa sử dụng"}
                          </span>
                        </div>
                        <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              percentage >= 90
                                ? "bg-red-500"
                                : percentage >= 60
                                ? "bg-[#F26F21]"
                                : percentage > 0
                                ? "bg-emerald-500"
                                : "bg-transparent"
                            }`}
                            style={{ width: `${Math.min(percentage, 100)}%` }}
                          />
                        </div>
                      </td>

                      {/* Thao tác */}
                      <td className="px-6 py-4 text-right">
                        <div className="inline-flex items-center gap-1.5">
                          {ins.isOverLimit ? (
                            <button
                              onClick={() => handleAddTokens(ins.id)}
                              className="px-2.5 py-1 rounded-lg bg-[#EA580C] hover:bg-[#C2410C] text-white font-bold text-[11px] shadow-sm transition-colors"
                            >
                              +2,000 Token
                            </button>
                          ) : (
                            <button
                              onClick={() =>
                                alert(`Cấu hình hạn ngạch cho: ${ins.name}`)
                              }
                              className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-[11px] transition-colors"
                            >
                              Cấu hình
                            </button>
                          )}
                          <button
                            onClick={() =>
                              alert(`Lịch sử chi tiết gọi API của ${ins.name}`)
                            }
                            className="p-1 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
                            title="Lịch sử chi tiết"
                          >
                            <Sliders className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={8} className="px-6 py-10 text-center text-slate-400">
                    Không tìm thấy giảng viên nào phù hợp.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Table Footer & Pagination */}
        <div className="px-6 py-3.5 bg-white flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-slate-100 text-xs text-slate-500">
          <div className="text-[11px] text-slate-500">
            Hiển thị <strong>5</strong> trên tổng số <strong>18</strong> giảng viên môn
            SWD392 đã được cấp quyền AI
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="p-1 rounded-md bg-slate-100 text-slate-500 hover:bg-slate-200 disabled:opacity-40 transition-colors"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            {[1, 2, 3].map((page) => (
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
              onClick={() => setCurrentPage((p) => Math.min(3, p + 1))}
              disabled={currentPage === 3}
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
