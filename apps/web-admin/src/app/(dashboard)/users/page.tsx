"use client";

import React, { useState, useMemo, useEffect, useCallback } from "react";
import {
  Search,
  Download,
  UserPlus,
  Eye,
  Key,
  GraduationCap,
  Coins,
  ChevronLeft,
  ChevronRight,
  X,
  Check,
  AlertCircle,
  ShieldAlert,
} from "lucide-react";

interface UserItem {
  id: string;
  code: string;
  name: string;
  email: string;
  courses: string[];
  role: "INSTRUCTOR" | "ADMIN";
  usedTokens: number;
  limitTokens: number; // -1 for unlimited
  warningText?: string;
  isActive: boolean;
}

export default function UsersManagementPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Form State cho Cấp Tài Khoản Mới
  const [newCode, setNewCode] = useState("GV006");
  const [newName, setNewName] = useState("");
  const [newEmail, setNewEmail] = useState("");
  const [newRole, setNewRole] = useState<"INSTRUCTOR" | "ADMIN">("INSTRUCTOR");
  const [newCourses, setNewCourses] = useState("PRF192");
  const [newQuota, setNewQuota] = useState(5000);

  // Danh sách tài khoản
  const [users, setUsers] = useState<UserItem[]>([
    {
      id: "1",
      code: "GV001",
      name: "ThS. Trần Minh Đức",
      email: "ductm@fe.edu.vn",
      courses: ["PRF192", "PRO192"],
      role: "INSTRUCTOR",
      usedTokens: 2400,
      limitTokens: 5000,
      isActive: true,
    },
    {
      id: "2",
      code: "GV002",
      name: "TS. Lê Hoàng Nam",
      email: "namlh@fe.edu.vn",
      courses: ["PRO192", "CSD201"],
      role: "INSTRUCTOR",
      usedTokens: 4850,
      limitTokens: 5000,
      warningText: "(Cảnh báo)",
      isActive: true,
    },
    {
      id: "3",
      code: "GV003",
      name: "ThS. Nguyễn Thị Mai",
      email: "maint@fe.edu.vn",
      courses: ["CSD201"],
      role: "INSTRUCTOR",
      usedTokens: 1200,
      limitTokens: 4000,
      isActive: true,
    },
    {
      id: "4",
      code: "GV004",
      name: "ThS. Vũ Quốc Tuấn",
      email: "tuanvq@fe.edu.vn",
      courses: ["MAS291"],
      role: "INSTRUCTOR",
      usedTokens: 0,
      limitTokens: 3000,
      isActive: false,
    },
    {
      id: "5",
      code: "AD001",
      name: "Nguyễn Hoàng Đức",
      email: "admin@fe.edu.vn",
      courses: ["Hệ thống"],
      role: "ADMIN",
      usedTokens: 0,
      limitTokens: -1, // Không giới hạn
      isActive: true,
    },
    {
      id: "6",
      code: "GV005",
      name: "ThS. Hoàng Văn Bình",
      email: "binhhv@fe.edu.vn",
      courses: ["PRF192"],
      role: "INSTRUCTOR",
      usedTokens: 3100,
      limitTokens: 5000,
      isActive: true,
    },
  ]);

  // Fetch users from backend if available
  const fetchUsers = useCallback(async () => {
    try {
      const token = localStorage.getItem("aita_access_token");
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000";

      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      const res = await fetch(`${apiUrl}/users`, { headers });
      if (res.ok) {
        const json = await res.json();
        if (json.success && Array.isArray(json.data) && json.data.length > 0) {
          // Map backend users with quota
          const mapped: UserItem[] = json.data.map((u: any, idx: number) => ({
            id: u.id || String(idx + 1),
            code: u.role === "ADMIN" ? `AD00${idx + 1}` : `GV00${idx + 1}`,
            name: u.fullName || u.username,
            email: u.email || `${u.username}@fe.edu.vn`,
            courses: u.role === "ADMIN" ? ["Hệ thống"] : ["PRF192", "PRO192"],
            role: u.role === "ADMIN" ? "ADMIN" : "INSTRUCTOR",
            usedTokens: u.quotaConfig?.usedTokensToday || 0,
            limitTokens:
              u.role === "ADMIN" ? -1 : u.quotaConfig?.dailyTokenLimit || 5000,
            isActive: u.isActive !== false,
          }));
          setUsers(mapped);
        }
      }
    } catch {
      // Backend offline fallback - giữ nguyên mock
    }
  }, []);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  // Bộ lọc
  const filteredUsers = useMemo(() => {
    return users.filter((u) => {
      const matchSearch =
        u.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        u.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
        u.email.toLowerCase().includes(searchQuery.toLowerCase());
      const matchRole = roleFilter === "ALL" || u.role === roleFilter;
      const matchStatus =
        statusFilter === "ALL" ||
        (statusFilter === "ACTIVE" && u.isActive) ||
        (statusFilter === "LOCKED" && !u.isActive);
      return matchSearch && matchRole && matchStatus;
    });
  }, [users, searchQuery, roleFilter, statusFilter]);

  // Checkbox handlers
  const handleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.checked) {
      setSelectedIds(filteredUsers.map((u) => u.id));
    } else {
      setSelectedIds([]);
    }
  };

  const handleSelectOne = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  // Toggle user active status
  const handleToggleStatus = (id: string) => {
    setUsers((prev) =>
      prev.map((u) => (u.id === id ? { ...u, isActive: !u.isActive } : u))
    );
  };

  // Tạo tài khoản mới
  const handleCreateUser = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim() || !newEmail.trim()) {
      alert("Vui lòng nhập đầy đủ họ tên và email FPT!");
      return;
    }

    const newUser: UserItem = {
      id: String(Date.now()),
      code: newCode,
      name: newName.trim(),
      email: newEmail.trim(),
      courses: newCourses.split(",").map((c) => c.trim()),
      role: newRole,
      usedTokens: 0,
      limitTokens: newRole === "ADMIN" ? -1 : newQuota,
      isActive: true,
    };

    setUsers((prev) => [newUser, ...prev]);
    setShowCreateModal(false);
    setNewName("");
    setNewEmail("");
    alert("Đã cấp phát tài khoản giảng viên mới thành công!");
  };

  return (
    <div className="flex flex-col w-full gap-5">
      {/* ================= BREADCRUMB & HEADER ================= */}
      <section className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
        <div className="flex flex-col gap-1.5">
          {/* Breadcrumb */}
          <nav className="flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-400">
            <span>Trang chủ</span>
            <span>/</span>
            <span className="text-[#F26F21]">Quản lý Giảng viên</span>
          </nav>

          {/* Heading */}
          <div className="flex items-center gap-2.5 flex-wrap mt-0.5">
            <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">
              Danh Sách Tài Khoản Giảng Viên
            </h1>
            <span className="px-2.5 py-0.5 rounded-full bg-purple-50 text-purple-700 font-extrabold text-xs border border-purple-200">
              • 24 Nhân sự
            </span>
          </div>

          <p className="text-xs text-slate-400 mt-0.5">
            Cấp phát tài khoản, phân bổ môn giảng dạy, cấu hình hạn ngạch sử dụng
            Gemini AI và quản lý trạng thái tài khoản.
          </p>
        </div>

        {/* 2 Metric Stat Cards bên phải */}
        <div className="flex items-center gap-3 self-start lg:self-auto">
          {/* Card 1: Đang hoạt động */}
          <div className="flex items-center gap-3 px-4 py-2.5 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
            <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center flex-shrink-0">
              <GraduationCap className="w-5 h-5" />
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                ĐANG HOẠT ĐỘNG
              </span>
              <div className="flex items-baseline gap-1">
                <span className="text-base font-extrabold text-slate-900">
                  22 / 24
                </span>
                <span className="text-[10px] font-bold text-emerald-600">
                  (91.6%)
                </span>
              </div>
            </div>
          </div>

          {/* Card 2: Tiêu thụ hôm nay */}
          <div className="flex items-center gap-3 px-4 py-2.5 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
            <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center flex-shrink-0">
              <Coins className="w-5 h-5" />
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                TIÊU THỤ HÔM NAY
              </span>
              <div className="flex items-baseline gap-1">
                <span className="text-base font-extrabold text-slate-900">
                  16,550
                </span>
                <span className="text-[10px] text-slate-400">tokens</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ================= FILTER TOOLBAR ================= */}
      <section className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3 bg-white p-4 rounded-2xl shadow-sm border border-slate-100">
        <div className="flex flex-wrap items-center gap-3 flex-1">
          {/* Search Input */}
          <div className="relative min-w-[260px] flex-1 max-w-sm">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Tìm kiếm theo Tên, Mã số họ..."
              className="w-full pl-9 pr-3.5 py-2 rounded-xl text-xs bg-slate-50 border border-slate-200 placeholder:text-slate-400 focus:outline-none focus:border-[#F26F21] focus:bg-white transition-all"
            />
          </div>

          {/* Role Filter */}
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="px-3.5 py-2 rounded-xl text-xs bg-slate-50 border border-slate-200 text-slate-700 font-medium focus:outline-none focus:border-[#F26F21]"
          >
            <option value="ALL">Vai trò: Tất cả</option>
            <option value="INSTRUCTOR">Giảng viên (INSTRUCTOR)</option>
            <option value="ADMIN">Quản trị viên (ADMIN)</option>
          </select>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3.5 py-2 rounded-xl text-xs bg-slate-50 border border-slate-200 text-slate-700 font-medium focus:outline-none focus:border-[#F26F21]"
          >
            <option value="ALL">Trạng thái: Tất cả</option>
            <option value="ACTIVE">Đang hoạt động</option>
            <option value="LOCKED">Tạm khóa</option>
          </select>
        </div>

        {/* Buttons */}
        <div className="flex items-center gap-2.5 self-end lg:self-auto">
          <button
            onClick={() => alert("Đang xuất danh sách tài khoản ra file Excel...")}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 font-semibold text-xs transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-emerald-600" />
            <span>Xuất Excel</span>
          </button>

          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#F26F21] hover:bg-[#D95A0E] text-white font-bold text-xs shadow-md shadow-orange-500/20 active:scale-95 transition-all"
          >
            <UserPlus className="w-4 h-4" />
            <span>+ Cấp Tài Khoản Mới</span>
          </button>
        </div>
      </section>

      {/* ================= USERS DATA TABLE ================= */}
      <section className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden flex flex-col">
        <div className="overflow-x-auto w-full">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50/80 text-slate-500 uppercase text-[10px] font-bold tracking-wider border-y border-slate-100">
              <tr>
                <th className="px-5 py-3.5 w-10">
                  <input
                    type="checkbox"
                    checked={
                      selectedIds.length === filteredUsers.length &&
                      filteredUsers.length > 0
                    }
                    onChange={handleSelectAll}
                    className="w-4 h-4 rounded border-slate-300 text-[#F26F21] focus:ring-[#F26F21]"
                  />
                </th>
                <th className="px-4 py-3.5">MÃ GV</th>
                <th className="px-4 py-3.5">HỌ & TÊN</th>
                <th className="px-4 py-3.5">EMAIL FPT</th>
                <th className="px-4 py-3.5">BỘ MÔN PHÂN CÔNG</th>
                <th className="px-4 py-3.5">VAI TRÒ</th>
                <th className="px-4 py-3.5">HẠN NGẠCH GEMINI AI (NGÀY)</th>
                <th className="px-4 py-3.5 text-center">TRẠNG THÁI</th>
                <th className="px-4 py-3.5 text-right">THAO TÁC</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {filteredUsers.length > 0 ? (
                filteredUsers.map((u) => {
                  const isUnlimited = u.limitTokens === -1;
                  const pct = isUnlimited
                    ? 0
                    : Math.round((u.usedTokens / u.limitTokens) * 100);

                  return (
                    <tr
                      key={u.id}
                      className="hover:bg-slate-50/80 transition-colors"
                    >
                      {/* Checkbox */}
                      <td className="px-5 py-4">
                        <input
                          type="checkbox"
                          checked={selectedIds.includes(u.id)}
                          onChange={() => handleSelectOne(u.id)}
                          className="w-4 h-4 rounded border-slate-300 text-[#F26F21] focus:ring-[#F26F21]"
                        />
                      </td>

                      {/* Mã GV */}
                      <td className="px-4 py-4">
                        <span
                          className={`font-mono text-xs font-bold ${
                            u.role === "ADMIN"
                              ? "text-[#F26F21]"
                              : "text-slate-600"
                          }`}
                        >
                          {u.code}
                        </span>
                      </td>

                      {/* Họ & Tên */}
                      <td className="px-4 py-4 font-bold text-slate-900">
                        {u.name}
                      </td>

                      {/* Email FPT */}
                      <td className="px-4 py-4 font-mono text-[11px] text-slate-500">
                        {u.email}
                      </td>

                      {/* Bộ Môn Phân Công */}
                      <td className="px-4 py-4">
                        <div className="flex flex-wrap gap-1.5">
                          {u.courses.map((course, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-purple-50 text-purple-700 border border-purple-100"
                            >
                              {course}
                            </span>
                          ))}
                        </div>
                      </td>

                      {/* Vai Trò */}
                      <td className="px-4 py-4">
                        {u.role === "ADMIN" ? (
                          <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-800 text-[10px] font-extrabold uppercase tracking-wide">
                            ADMIN
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded bg-blue-50 text-[#0054A6] text-[10px] font-extrabold uppercase tracking-wide">
                            INSTRUCTOR
                          </span>
                        )}
                      </td>

                      {/* Hạn Ngạch Gemini AI */}
                      <td className="px-4 py-4 min-w-[200px]">
                        {isUnlimited ? (
                          <div className="flex items-center gap-1.5 text-xs text-slate-500">
                            <span className="text-base font-bold text-slate-700">
                              ∞
                            </span>
                            <span>Không giới hạn</span>
                          </div>
                        ) : (
                          <div>
                            <div className="flex items-center justify-between text-[11px] mb-1">
                              <span className="text-slate-700 font-semibold">
                                {u.usedTokens.toLocaleString()} /{" "}
                                {u.limitTokens.toLocaleString()}
                                {u.warningText && (
                                  <span className="text-amber-600 font-bold ml-1">
                                    {u.warningText}
                                  </span>
                                )}
                              </span>
                              <span
                                className={`font-extrabold text-[10px] ${
                                  pct >= 90
                                    ? "text-red-600"
                                    : pct >= 60
                                    ? "text-amber-600"
                                    : "text-slate-500"
                                }`}
                              >
                                {pct}%
                              </span>
                            </div>
                            <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                              <div
                                className={`h-full rounded-full transition-all duration-500 ${
                                  pct >= 90
                                    ? "bg-[#C2410C]"
                                    : pct >= 60
                                    ? "bg-[#F26F21]"
                                    : "bg-[#4338CA]"
                                }`}
                                style={{ width: `${Math.min(pct, 100)}%` }}
                              />
                            </div>
                          </div>
                        )}
                      </td>

                      {/* Trạng Thái */}
                      <td className="px-4 py-4 text-center">
                        {u.isActive ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-[10px] font-bold border border-emerald-200">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                            Hoạt động
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[10px] font-bold border border-slate-200">
                            <span className="w-1.5 h-1.5 rounded-full bg-slate-400" />
                            Tạm khóa
                          </span>
                        )}
                      </td>

                      {/* Thao Tác */}
                      <td className="px-4 py-4 text-right">
                        <div className="inline-flex items-center gap-3">
                          {/* Nút Xem Chi Tiết */}
                          <button
                            onClick={() =>
                              alert(`Xem hồ sơ chi tiết của: ${u.name}`)
                            }
                            className="text-slate-400 hover:text-slate-700 transition-colors"
                            title="Xem chi tiết"
                          >
                            <Eye className="w-4 h-4" />
                          </button>

                          {/* Nút Đặt lại Mật Khẩu */}
                          <button
                            onClick={() =>
                              alert(
                                `Gửi email đặt lại mật khẩu cho tài khoản ${u.email}?`
                              )
                            }
                            className="text-slate-400 hover:text-amber-600 transition-colors"
                            title="Đặt lại mật khẩu"
                          >
                            <Key className="w-4 h-4" />
                          </button>

                          {/* Switch Khóa / Kích Hoạt */}
                          <button
                            onClick={() => handleToggleStatus(u.id)}
                            className={`w-9 h-5 rounded-full p-0.5 transition-colors relative flex items-center ${
                              u.isActive ? "bg-emerald-500" : "bg-slate-300"
                            }`}
                            title={
                              u.isActive
                                ? "Tài khoản đang hoạt động (Bấm để khóa)"
                                : "Tài khoản đang tạm khóa (Bấm để mở)"
                            }
                          >
                            <div
                              className={`w-4 h-4 rounded-full bg-white shadow-sm transform transition-transform ${
                                u.isActive ? "translate-x-4" : "translate-x-0"
                              }`}
                            />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td
                    colSpan={9}
                    className="px-6 py-12 text-center text-slate-400"
                  >
                    Không tìm thấy tài khoản giảng viên nào phù hợp.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Phân trang */}
        <div className="px-6 py-3.5 bg-white flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-slate-100 text-xs text-slate-500">
          <div>
            Hiển thị <strong>1 - {filteredUsers.length}</strong> của{" "}
            <strong>24</strong> giảng viên
          </div>

          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-slate-500 hover:bg-slate-100 disabled:opacity-40 transition-colors"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
              <span>Trước</span>
            </button>

            {[1, 2, 3].map((page) => (
              <button
                key={page}
                onClick={() => setCurrentPage(page)}
                className={`w-7 h-7 rounded-lg font-bold text-xs transition-colors ${
                  currentPage === page
                    ? "bg-[#3B2D6D] text-white"
                    : "hover:bg-slate-100 text-slate-700 font-medium"
                }`}
              >
                {page}
              </button>
            ))}
            <span className="px-1 text-slate-400">...</span>
            <button
              onClick={() => setCurrentPage(4)}
              className="w-7 h-7 rounded-lg hover:bg-slate-100 text-slate-700 font-medium text-xs transition-colors"
            >
              4
            </button>

            <button
              onClick={() => setCurrentPage((p) => Math.min(4, p + 1))}
              disabled={currentPage === 4}
              className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-slate-500 hover:bg-slate-100 disabled:opacity-40 transition-colors"
            >
              <span>Sau</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </section>

      {/* ================= MODAL CẤP TÀI KHOẢN MỚI ================= */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6 border border-slate-200 animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-xl bg-orange-50 text-[#F26F21]">
                  <UserPlus className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-extrabold text-slate-900 text-base">
                    Cấp Phát Tài Khoản Giảng Viên Mới
                  </h3>
                  <p className="text-xs text-slate-400">
                    Thêm giảng viên vào hệ thống khảo thí AITA
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowCreateModal(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateUser} className="space-y-4 mt-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-bold text-slate-700 uppercase mb-1">
                    Mã Giảng Viên
                  </label>
                  <input
                    type="text"
                    required
                    value={newCode}
                    onChange={(e) => setNewCode(e.target.value)}
                    placeholder="GV006"
                    className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 border border-slate-200 focus:outline-none focus:border-[#F26F21]"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-slate-700 uppercase mb-1">
                    Vai Trò
                  </label>
                  <select
                    value={newRole}
                    onChange={(e) =>
                      setNewRole(e.target.value as "INSTRUCTOR" | "ADMIN")
                    }
                    className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 border border-slate-200 focus:outline-none focus:border-[#F26F21]"
                  >
                    <option value="INSTRUCTOR">Giảng viên (INSTRUCTOR)</option>
                    <option value="ADMIN">Quản trị viên (ADMIN)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-700 uppercase mb-1">
                  Họ và Tên Giảng Viên
                </label>
                <input
                  type="text"
                  required
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="ThS. Nguyễn Văn A"
                  className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 border border-slate-200 focus:outline-none focus:border-[#F26F21]"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-700 uppercase mb-1">
                  Email FPT (@fe.edu.vn)
                </label>
                <input
                  type="email"
                  required
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  placeholder="anv@fe.edu.vn"
                  className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 border border-slate-200 focus:outline-none focus:border-[#F26F21]"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-bold text-slate-700 uppercase mb-1">
                    Môn Giảng Dạy (Cách nhau dấu phẩy)
                  </label>
                  <input
                    type="text"
                    value={newCourses}
                    onChange={(e) => setNewCourses(e.target.value)}
                    placeholder="PRF192, PRO192"
                    className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 border border-slate-200 focus:outline-none focus:border-[#F26F21]"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-slate-700 uppercase mb-1">
                    Hạn Ngạch AI (Tokens/Ngày)
                  </label>
                  <input
                    type="number"
                    value={newQuota}
                    onChange={(e) => setNewQuota(Number(e.target.value))}
                    min={1000}
                    step={1000}
                    className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 border border-slate-200 focus:outline-none focus:border-[#F26F21]"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-2.5 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs transition-colors"
                >
                  Hủy bỏ
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-[#F26F21] hover:bg-[#D95A0E] text-white font-bold text-xs shadow-md shadow-orange-500/20 transition-all"
                >
                  Xác Nhận Cấp Tài Khoản
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
