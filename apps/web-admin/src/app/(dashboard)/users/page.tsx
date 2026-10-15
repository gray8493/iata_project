"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  Search,
  Download,
  UserPlus,
  RefreshCw,
  Edit3,
  Trash2,
  X,
  AlertCircle,
  CheckCircle2,
  GraduationCap,
  ChevronLeft,
  ChevronRight,
  Loader2,
  KeyRound,
  Shield,
} from "lucide-react";

interface UserItem {
  id: string;
  username: string;
  full_name: string;
  email: string;
  role: "ADMIN" | "INSTRUCTOR";
  is_active: boolean;
  created_at: string;
  daily_token_quota?: number | null;
}

interface PaginationData {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
}

export default function UsersManagementPage() {
  // Dữ liệu người dùng nhận từ Backend NestJS
  const [users, setUsers] = useState<UserItem[]>([]);
  const [pagination, setPagination] = useState<PaginationData>({
    page: 1,
    page_size: 10,
    total_items: 0,
    total_pages: 1,
  });

  // Bộ lọc đúng chuẩn ListUsersDto của Backend
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState<"ALL" | "ADMIN" | "INSTRUCTOR">("ALL");

  // State trạng thái tải & thông báo
  const [loading, setLoading] = useState(true);
  const [isActionLoading, setIsActionLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  // Modal Cấp Tài Khoản Mới (CreateUserDto)
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newUsername, setNewUsername] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newFullName, setNewFullName] = useState("");
  const [newEmail, setNewEmail] = useState("");
  const [newRole, setNewRole] = useState<"INSTRUCTOR" | "ADMIN">("INSTRUCTOR");
  const [newQuota, setNewQuota] = useState<string>("");

  // Modal Chỉnh Sửa Tài Khoản (UpdateUserDto)
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingUser, setEditingUser] = useState<UserItem | null>(null);
  const [editFullName, setEditFullName] = useState("");
  const [editEmail, setEditEmail] = useState("");
  const [editRole, setEditRole] = useState<"INSTRUCTOR" | "ADMIN">("INSTRUCTOR");
  const [editQuota, setEditQuota] = useState<string>("");
  const [editNewPassword, setEditNewPassword] = useState("");

  // Modal Xác Nhận Xóa
  const [deletingUser, setDeletingUser] = useState<UserItem | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Debounce tìm kiếm 350ms
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(searchQuery.trim());
      setPagination((prev) => ({ ...prev, page: 1 }));
    }, 350);
    return () => clearTimeout(handler);
  }, [searchQuery]);

  // Tự ẩn thông báo
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(""), 5000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  useEffect(() => {
    if (errorMessage) {
      const timer = setTimeout(() => setErrorMessage(""), 7000);
      return () => clearTimeout(timer);
    }
  }, [errorMessage]);

  const getApiConfig = () => {
    const token = typeof window !== "undefined" ? localStorage.getItem("aita_access_token") : null;
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000/api/v1";
    return { token, apiUrl };
  };

  // Lấy danh sách từ API Backend (GET /api/v1/admin/users)
  const fetchUsers = useCallback(
    async (pageTarget = pagination.page) => {
      const { token, apiUrl } = getApiConfig();
      if (!token) {
        setErrorMessage("Chưa tìm thấy phiên đăng nhập. Vui lòng đăng nhập lại!");
        setLoading(false);
        return;
      }

      setLoading(true);
      try {
        const queryParams = new URLSearchParams();
        queryParams.set("page", String(pageTarget));
        queryParams.set("page_size", String(pagination.page_size));
        if (roleFilter !== "ALL") {
          queryParams.set("role", roleFilter);
        }
        if (debouncedSearch) {
          queryParams.set("search", debouncedSearch);
        }

        const res = await fetch(`${apiUrl}/admin/users?${queryParams.toString()}`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        });

        if (res.status === 401) {
          setErrorMessage("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại!");
          if (typeof window !== "undefined") {
            localStorage.removeItem("aita_access_token");
          }
          setLoading(false);
          return;
        }

        const result = await res.json();
        if (res.ok && result.success && result.data) {
          setUsers(result.data.items || []);
          if (result.data.pagination) {
            setPagination(result.data.pagination);
          }
        } else {
          setErrorMessage(result.message || "Không thể tải danh sách tài khoản từ máy chủ.");
        }
      } catch {
        setErrorMessage("Không thể kết nối đến máy chủ backend.");
      } finally {
        setLoading(false);
      }
    },
    [pagination.page, pagination.page_size, roleFilter, debouncedSearch]
  );

  useEffect(() => {
    fetchUsers(pagination.page);
  }, [fetchUsers, pagination.page]);

  // Cập nhật trạng thái kích hoạt / khóa (PUT /api/v1/admin/users/:id)
  const handleToggleStatus = async (user: UserItem) => {
    const { token, apiUrl } = getApiConfig();
    if (!token) return;

    try {
      const res = await fetch(`${apiUrl}/admin/users/${user.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ is_active: !user.is_active }),
      });

      const json = await res.json();
      if (res.ok && json.success) {
        setSuccessMessage(
          `Đã ${!user.is_active ? "kích hoạt" : "tạm khóa"} tài khoản "${user.username}" thành công!`
        );
        setUsers((prev) =>
          prev.map((u) => (u.id === user.id ? { ...u, is_active: !u.is_active } : u))
        );
      } else {
        const detailMsg = Array.isArray(json.details)
          ? json.details.join(", ")
          : (json.message || "Không thể thay đổi trạng thái tài khoản này.");
        setErrorMessage(detailMsg);
      }
    } catch {
      setErrorMessage("Lỗi kết nối khi cập nhật trạng thái tài khoản.");
    }
  };

  // Cấp tài khoản mới (POST /api/v1/admin/users)
  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    const { token, apiUrl } = getApiConfig();
    if (!token) return;

    const trimmedUsername = newUsername.trim().toLowerCase();
    const trimmedFullName = newFullName.trim();
    const trimmedEmail = newEmail.trim().toLowerCase();

    // Client-side validation kiểm tra tính hợp lệ trước khi gửi
    if (!/^[a-z0-9_]{3,30}$/.test(trimmedUsername)) {
      setErrorMessage("Tên đăng nhập phải từ 3 đến 30 ký tự, chỉ gồm chữ thường (a-z), chữ số (0-9) và dấu gạch dưới (_).");
      return;
    }

    if (!/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/.test(newPassword)) {
      setErrorMessage("Mật khẩu phải tối thiểu 8 ký tự, gồm ít nhất 1 chữ hoa, 1 chữ thường và 1 chữ số (ví dụ: User@123456).");
      return;
    }

    if (trimmedFullName.length < 2) {
      setErrorMessage("Họ và tên phải có ít nhất 2 ký tự.");
      return;
    }

    setIsActionLoading(true);
    setErrorMessage("");

    try {
      const body: Record<string, any> = {
        username: trimmedUsername,
        password: newPassword,
        full_name: trimmedFullName,
        email: trimmedEmail,
        role: newRole,
      };

      // Hạn ngạch không bắt buộc, nếu nhập bao nhiêu cũng được
      if (newQuota !== "" && !isNaN(Number(newQuota))) {
        body.daily_token_quota = Math.max(0, Math.floor(Number(newQuota)));
      }

      const res = await fetch(`${apiUrl}/admin/users`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
      });

      const json = await res.json();
      if (res.ok && json.success) {
        setSuccessMessage(`Đã cấp tài khoản "${body.username}" thành công!`);
        setShowCreateModal(false);
        setNewUsername("");
        setNewPassword("");
        setNewFullName("");
        setNewEmail("");
        setNewRole("INSTRUCTOR");
        setNewQuota("");
        fetchUsers(1);
      } else {
        const detailMsg = Array.isArray(json.details)
          ? json.details.join(", ")
          : (json.message || "Không thể tạo tài khoản người dùng.");
        setErrorMessage(detailMsg);
      }
    } catch {
      setErrorMessage("Lỗi kết nối khi gửi yêu cầu tạo tài khoản.");
    } finally {
      setIsActionLoading(false);
    }
  };

  // Mở modal chỉnh sửa & tải hạn ngạch chi tiết (GET /api/v1/admin/users/:id)
  const handleOpenEditModal = async (user: UserItem) => {
    setEditingUser(user);
    setEditFullName(user.full_name);
    setEditEmail(user.email);
    setEditRole(user.role);
    setEditNewPassword("");
    setEditQuota("");

    const { token, apiUrl } = getApiConfig();
    if (token) {
      try {
        const res = await fetch(`${apiUrl}/admin/users/${user.id}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const json = await res.json();
          if (json.data?.daily_token_quota !== undefined && json.data?.daily_token_quota !== null) {
            setEditQuota(String(json.data.daily_token_quota));
          }
        }
      } catch {
        // Tiếp tục với hạn ngạch rỗng nếu không tải được
      }
    }

    setShowEditModal(true);
  };

  // Cập nhật tài khoản (PUT /api/v1/admin/users/:id)
  const handleUpdateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingUser) return;
    const { token, apiUrl } = getApiConfig();
    if (!token) return;

    if (editNewPassword.trim() && !/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/.test(editNewPassword.trim())) {
      setErrorMessage("Mật khẩu mới phải tối thiểu 8 ký tự, gồm ít nhất 1 chữ hoa, 1 chữ thường và 1 chữ số.");
      return;
    }

    setIsActionLoading(true);
    setErrorMessage("");

    try {
      const payload: Record<string, any> = {
        full_name: editFullName.trim(),
        email: editEmail.trim().toLowerCase(),
        role: editRole,
      };

      // Nhập hạn ngạch bao nhiêu cũng được, không bắt buộc
      if (editQuota !== "" && !isNaN(Number(editQuota))) {
        payload.daily_token_quota = Math.max(0, Math.floor(Number(editQuota)));
      }

      if (editNewPassword.trim()) {
        payload.password = editNewPassword.trim();
      }

      const res = await fetch(`${apiUrl}/admin/users/${editingUser.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      const json = await res.json();
      if (res.ok && json.success) {
        setSuccessMessage(`Đã cập nhật tài khoản "${editingUser.username}" thành công!`);
        setShowEditModal(false);
        setEditingUser(null);
        fetchUsers(pagination.page);
      } else {
        const detailMsg = Array.isArray(json.details)
          ? json.details.join(", ")
          : (json.message || "Không thể cập nhật tài khoản.");
        setErrorMessage(detailMsg);
      }
    } catch {
      setErrorMessage("Lỗi kết nối khi cập nhật tài khoản.");
    } finally {
      setIsActionLoading(false);
    }
  };

  // Xóa mềm tài khoản (DELETE /api/v1/admin/users/:id)
  const handleDeleteUser = async () => {
    if (!deletingUser) return;
    const { token, apiUrl } = getApiConfig();
    if (!token) return;

    setIsActionLoading(true);
    setErrorMessage("");

    try {
      const res = await fetch(`${apiUrl}/admin/users/${deletingUser.id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const json = await res.json();
      if (res.ok && json.success) {
        setSuccessMessage(`Đã xóa tài khoản "${deletingUser.username}" thành công!`);
        setShowDeleteConfirm(false);
        setDeletingUser(null);
        fetchUsers(1);
      } else {
        const detailMsg = Array.isArray(json.details)
          ? json.details.join(", ")
          : (json.message || "Không thể xóa tài khoản này.");
        setErrorMessage(detailMsg);
      }
    } catch {
      setErrorMessage("Lỗi kết nối khi gửi yêu cầu xóa tài khoản.");
    } finally {
      setIsActionLoading(false);
    }
  };

  // Xuất file CSV từ dữ liệu thực tế
  const handleExportCsv = () => {
    if (users.length === 0) return;

    const headers = ["ID", "Tên đăng nhập", "Họ và tên", "Email", "Vai trò", "Trạng thái", "Ngày tạo"];
    const rows = users.map((u) => [
      u.id,
      u.username,
      `"${u.full_name}"`,
      u.email,
      u.role,
      u.is_active ? "Hoạt động" : "Tạm khóa",
      new Date(u.created_at).toLocaleString("vi-VN"),
    ]);

    const csvContent = "\uFEFF" + [headers.join(","), ...rows.map((e) => e.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `danh_sach_tai_khoan_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="flex flex-col w-full gap-5">
      {/* Thông báo lỗi */}
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

      {/* Thông báo thành công */}
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

      {/* ================= TIÊU ĐỀ TRANG ================= */}
      <section className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
        <div className="flex flex-col gap-1.5">
          <nav className="flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-400">
            <span>Trang chủ</span>
            <span>/</span>
            <span className="text-[#F26F21]">Quản lý Tài khoản</span>
          </nav>

          <div className="flex items-center gap-2.5 flex-wrap mt-0.5">
            <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">
              Danh Sách Tài Khoản Người Dùng
            </h1>
            <span className="px-2.5 py-0.5 rounded-full bg-purple-50 text-purple-700 font-extrabold text-xs border border-purple-200">
              • {pagination.total_items} Tài khoản
            </span>
          </div>

          <p className="text-xs text-slate-400 mt-0.5">
            Quản lý tài khoản Giảng viên và Quản trị viên kết nối trực tiếp với Backend NestJS.
          </p>
        </div>

        {/* Nút hành động chính */}
        <div className="flex items-center gap-2.5 self-start sm:self-auto">
          <button
            onClick={handleExportCsv}
            disabled={users.length === 0}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 font-semibold text-xs transition-colors disabled:opacity-40"
          >
            <Download className="w-3.5 h-3.5 text-emerald-600" />
            <span>Xuất CSV</span>
          </button>

          <button
            onClick={() => {
              setErrorMessage("");
              setShowCreateModal(true);
            }}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#F26F21] hover:bg-[#D95A0E] text-white font-bold text-xs shadow-md shadow-orange-500/20 active:scale-95 transition-all"
          >
            <UserPlus className="w-4 h-4" />
            <span>+ Cấp Tài Khoản Mới</span>
          </button>
        </div>
      </section>

      {/* ================= BỘ LỌC (ROLE & SEARCH CHUẨN BACKEND) ================= */}
      <section className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-2xl shadow-sm border border-slate-100">
        <div className="flex flex-wrap items-center gap-3 flex-1">
          {/* Tìm kiếm */}
          <div className="relative min-w-[260px] flex-1 max-w-sm">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Tìm theo Username, Họ tên, Email..."
              className="w-full pl-9 pr-3.5 py-2 rounded-xl text-xs bg-slate-50 border border-slate-200 placeholder:text-slate-400 focus:outline-none focus:border-[#F26F21] focus:bg-white transition-all font-medium"
            />
          </div>

          {/* Lọc Vai trò */}
          <select
            value={roleFilter}
            onChange={(e) => {
              setRoleFilter(e.target.value as any);
              setPagination((prev) => ({ ...prev, page: 1 }));
            }}
            className="px-3.5 py-2 rounded-xl text-xs bg-slate-50 border border-slate-200 text-slate-700 font-semibold focus:outline-none focus:border-[#F26F21]"
          >
            <option value="ALL">Tất cả vai trò</option>
            <option value="INSTRUCTOR">Giảng viên (INSTRUCTOR)</option>
            <option value="ADMIN">Quản trị viên (ADMIN)</option>
          </select>

          {/* Nút Làm mới */}
          <button
            onClick={() => fetchUsers(pagination.page)}
            disabled={loading}
            title="Tải lại dữ liệu"
            className="p-2 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-600 border border-slate-200 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-[#F26F21]" : ""}`} />
          </button>
        </div>
      </section>

      {/* ================= BẢNG DỮ LIỆU TÀI KHOẢN ================= */}
      <section className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden flex flex-col">
        <div className="overflow-x-auto w-full">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50/80 text-slate-500 uppercase text-[10px] font-bold tracking-wider border-y border-slate-100">
              <tr>
                <th className="px-5 py-3.5">TÊN ĐĂNG NHẬP</th>
                <th className="px-4 py-3.5">HỌ & TÊN</th>
                <th className="px-4 py-3.5">EMAIL</th>
                <th className="px-4 py-3.5">VAI TRÒ</th>
                <th className="px-4 py-3.5 text-center">TRẠNG THÁI</th>
                <th className="px-4 py-3.5">NGÀY TẠO</th>
                <th className="px-5 py-3.5 text-right">THAO TÁC</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-14 text-center">
                    <div className="flex flex-col items-center justify-center gap-2">
                      <Loader2 className="w-6 h-6 text-[#F26F21] animate-spin" />
                      <span className="text-xs text-slate-400">Đang tải dữ liệu từ máy chủ Backend...</span>
                    </div>
                  </td>
                </tr>
              ) : users.length > 0 ? (
                users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-50/80 transition-colors">
                    {/* Tên đăng nhập */}
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-2.5">
                        <div
                          className={`w-7 h-7 rounded-lg flex items-center justify-center font-bold text-xs ${
                            u.role === "ADMIN"
                              ? "bg-amber-100 text-amber-800"
                              : "bg-blue-100 text-blue-800"
                          }`}
                        >
                          {u.username.charAt(0).toUpperCase()}
                        </div>
                        <span className="font-mono text-xs font-bold text-slate-800">
                          {u.username}
                        </span>
                      </div>
                    </td>

                    {/* Họ & Tên */}
                    <td className="px-4 py-4 font-bold text-slate-900">
                      {u.full_name}
                    </td>

                    {/* Email */}
                    <td className="px-4 py-4 font-mono text-[11px] text-slate-500">
                      {u.email}
                    </td>

                    {/* Vai Trò */}
                    <td className="px-4 py-4">
                      {u.role === "ADMIN" ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-amber-50 text-amber-800 text-[10px] font-extrabold uppercase tracking-wide border border-amber-200">
                          <Shield className="w-3 h-3 text-amber-600" />
                          ADMIN
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-blue-50 text-[#0054A6] text-[10px] font-extrabold uppercase tracking-wide border border-blue-200">
                          <GraduationCap className="w-3 h-3 text-[#0054A6]" />
                          INSTRUCTOR
                        </span>
                      )}
                    </td>

                    {/* Trạng Thái */}
                    <td className="px-4 py-4 text-center">
                      {u.is_active ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-[10px] font-bold border border-emerald-200">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                          Hoạt động
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-500 text-[10px] font-bold border border-slate-200">
                          <span className="w-1.5 h-1.5 rounded-full bg-slate-400" />
                          Đã khóa
                        </span>
                      )}
                    </td>

                    {/* Ngày tạo */}
                    <td className="px-4 py-4 text-slate-400 text-[11px]">
                      {new Date(u.created_at).toLocaleDateString("vi-VN", {
                        year: "numeric",
                        month: "2-digit",
                        day: "2-digit",
                      })}
                    </td>

                    {/* Thao Tác */}
                    <td className="px-5 py-4 text-right">
                      <div className="inline-flex items-center gap-2.5">
                        {/* Switch Khóa / Mở Khóa */}
                        <button
                          onClick={() => handleToggleStatus(u)}
                          className={`w-9 h-5 rounded-full p-0.5 transition-colors relative flex items-center ${
                            u.is_active ? "bg-emerald-500" : "bg-slate-300"
                          }`}
                          title={
                            u.is_active
                              ? "Tài khoản đang hoạt động (Bấm để khóa)"
                              : "Tài khoản đang khóa (Bấm để mở)"
                          }
                        >
                          <div
                            className={`w-4 h-4 rounded-full bg-white shadow-sm transform transition-transform ${
                              u.is_active ? "translate-x-4" : "translate-x-0"
                            }`}
                          />
                        </button>

                        {/* Nút Sửa */}
                        <button
                          onClick={() => handleOpenEditModal(u)}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
                          title="Chỉnh sửa thông tin"
                        >
                          <Edit3 className="w-4 h-4" />
                        </button>

                        {/* Nút Xóa */}
                        <button
                          onClick={() => {
                            setDeletingUser(u);
                            setShowDeleteConfirm(true);
                          }}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                          title="Xóa tài khoản"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-400">
                    Không tìm thấy tài khoản nào phù hợp với điều kiện tìm kiếm.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Phân trang Backend */}
        <div className="px-6 py-3.5 bg-white flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-slate-100 text-xs text-slate-500">
          <div>
            Trang <strong>{pagination.page}</strong> / <strong>{pagination.total_pages || 1}</strong>{" "}
            (Tổng cộng <strong>{pagination.total_items}</strong> tài khoản)
          </div>

          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setPagination((prev) => ({ ...prev, page: Math.max(1, prev.page - 1) }))}
              disabled={pagination.page <= 1 || loading}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-slate-600 bg-slate-50 hover:bg-slate-100 border border-slate-200 disabled:opacity-40 transition-colors font-medium"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
              <span>Trước</span>
            </button>

            {Array.from({ length: pagination.total_pages || 1 }, (_, i) => i + 1).map((pageNum) => (
              <button
                key={pageNum}
                onClick={() => setPagination((prev) => ({ ...prev, page: pageNum }))}
                disabled={loading}
                className={`w-7 h-7 rounded-lg font-bold text-xs transition-colors ${
                  pagination.page === pageNum
                    ? "bg-[#3B2D6D] text-white"
                    : "hover:bg-slate-100 text-slate-700 font-medium"
                }`}
              >
                {pageNum}
              </button>
            ))}

            <button
              onClick={() =>
                setPagination((prev) => ({
                  ...prev,
                  page: Math.min(prev.total_pages, prev.page + 1),
                }))
              }
              disabled={pagination.page >= (pagination.total_pages || 1) || loading}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-slate-600 bg-slate-50 hover:bg-slate-100 border border-slate-200 disabled:opacity-40 transition-colors font-medium"
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
                    Cấp Phát Tài Khoản Mới
                  </h3>
                  <p className="text-xs text-slate-400">
                    Lưu trữ trực tiếp vào cơ sở dữ liệu AITA Backend
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

            <form onSubmit={handleCreateUser} className="space-y-3.5 mt-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-bold text-slate-700 uppercase mb-1">
                    Tên Đăng Nhập <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={newUsername}
                    onChange={(e) => setNewUsername(e.target.value.toLowerCase())}
                    placeholder="vd: teacher_nam"
                    className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 border border-slate-200 focus:outline-none focus:border-[#F26F21]"
                  />
                  <p className="text-[10px] text-slate-400 mt-0.5">Chữ thường, số, dấu _ (3-30 ký tự)</p>
                </div>

                <div>
                  <label className="block text-[11px] font-bold text-slate-700 uppercase mb-1">
                    Vai Trò <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={newRole}
                    onChange={(e) => setNewRole(e.target.value as "INSTRUCTOR" | "ADMIN")}
                    className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 border border-slate-200 focus:outline-none focus:border-[#F26F21]"
                  >
                    <option value="INSTRUCTOR">Giảng viên (INSTRUCTOR)</option>
                    <option value="ADMIN">Quản trị viên (ADMIN)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-700 uppercase mb-1">
                  Mật Khẩu Khởi Tạo <span className="text-red-500">*</span>
                </label>
                <input
                  type="password"
                  required
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="vd: User@123456"
                  className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 border border-slate-200 focus:outline-none focus:border-[#F26F21]"
                />
                <p className="text-[10px] text-slate-400 mt-0.5">Tối thiểu 8 ký tự, gồm ít nhất 1 chữ hoa, 1 chữ thường và 1 chữ số</p>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-700 uppercase mb-1">
                  Họ và Tên Đầy Đủ <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={newFullName}
                  onChange={(e) => setNewFullName(e.target.value)}
                  placeholder="vd: ThS. Nguyễn Văn A"
                  className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 border border-slate-200 focus:outline-none focus:border-[#F26F21]"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-700 uppercase mb-1">
                  Địa Chỉ Email <span className="text-red-500">*</span>
                </label>
                <input
                  type="email"
                  required
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  placeholder="vd: nguyenvana@aita.edu.vn"
                  className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 border border-slate-200 focus:outline-none focus:border-[#F26F21]"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="block text-[11px] font-bold text-slate-700 uppercase">
                    Hạn Ngạch AI Hằng Ngày (Tokens)
                  </label>
                  <span className="text-[10px] font-semibold text-slate-400">(Không bắt buộc)</span>
                </div>
                <input
                  type="number"
                  value={newQuota}
                  onChange={(e) => setNewQuota(e.target.value)}
                  placeholder="Nhập số token tùy ý (để trống sẽ mặc định 50,000)"
                  className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 border border-slate-200 focus:outline-none focus:border-[#F26F21]"
                />
              </div>

              <div className="flex items-center justify-end gap-2.5 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  disabled={isActionLoading}
                  className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs transition-colors"
                >
                  Hủy bỏ
                </button>
                <button
                  type="submit"
                  disabled={isActionLoading}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#F26F21] hover:bg-[#D95A0E] text-white font-bold text-xs shadow-md shadow-orange-500/20 disabled:opacity-50 transition-all"
                >
                  {isActionLoading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  <span>Xác Nhận Tạo Tài Khoản</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ================= MODAL CHỈNH SỬA TÀI KHOẢN ================= */}
      {showEditModal && editingUser && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6 border border-slate-200 animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-xl bg-blue-50 text-blue-600">
                  <Edit3 className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-extrabold text-slate-900 text-base">
                    Chỉnh Sửa Tài Khoản ({editingUser.username})
                  </h3>
                  <p className="text-xs text-slate-400">
                    Cập nhật thông tin và hạn ngạch trên hệ thống
                  </p>
                </div>
              </div>
              <button
                onClick={() => {
                  setShowEditModal(false);
                  setEditingUser(null);
                }}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUpdateUser} className="space-y-3.5 mt-4">
              <div>
                <label className="block text-[11px] font-bold text-slate-700 uppercase mb-1">
                  Họ và Tên
                </label>
                <input
                  type="text"
                  required
                  value={editFullName}
                  onChange={(e) => setEditFullName(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 border border-slate-200 focus:outline-none focus:border-[#F26F21]"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-bold text-slate-700 uppercase mb-1">
                    Email
                  </label>
                  <input
                    type="email"
                    required
                    value={editEmail}
                    onChange={(e) => setEditEmail(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 border border-slate-200 focus:outline-none focus:border-[#F26F21]"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-bold text-slate-700 uppercase mb-1">
                    Vai Trò
                  </label>
                  <select
                    value={editRole}
                    onChange={(e) => setEditRole(e.target.value as "INSTRUCTOR" | "ADMIN")}
                    className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 border border-slate-200 focus:outline-none focus:border-[#F26F21]"
                  >
                    <option value="INSTRUCTOR">Giảng viên (INSTRUCTOR)</option>
                    <option value="ADMIN">Quản trị viên (ADMIN)</option>
                  </select>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="block text-[11px] font-bold text-slate-700 uppercase">
                    Hạn Ngạch AI Hằng Ngày (Tokens)
                  </label>
                  <span className="text-[10px] font-semibold text-slate-400">(Không bắt buộc)</span>
                </div>
                <input
                  type="number"
                  value={editQuota}
                  onChange={(e) => setEditQuota(e.target.value)}
                  placeholder="Nhập số token tùy ý (để trống sẽ giữ nguyên)"
                  className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 border border-slate-200 focus:outline-none focus:border-[#F26F21]"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-700 uppercase mb-1">
                  Đặt Mật Khẩu Mới (Để trống nếu không đổi)
                </label>
                <div className="relative">
                  <KeyRound className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input
                    type="password"
                    value={editNewPassword}
                    onChange={(e) => setEditNewPassword(e.target.value)}
                    placeholder="Nhập mật khẩu mới nếu muốn đổi..."
                    className="w-full pl-9 pr-3.5 py-2 rounded-xl text-xs bg-slate-50 border border-slate-200 focus:outline-none focus:border-[#F26F21]"
                  />
                </div>
                <p className="text-[10px] text-slate-400 mt-0.5">Tối thiểu 8 ký tự, gồm chữ hoa, chữ thường và số</p>
              </div>

              <div className="flex items-center justify-end gap-2.5 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => {
                    setShowEditModal(false);
                    setEditingUser(null);
                  }}
                  disabled={isActionLoading}
                  className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs transition-colors"
                >
                  Hủy bỏ
                </button>
                <button
                  type="submit"
                  disabled={isActionLoading}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-md shadow-blue-500/20 disabled:opacity-50 transition-all"
                >
                  {isActionLoading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  <span>Lưu Thay Đổi</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ================= MODAL XÁC NHẬN XÓA ================= */}
      {showDeleteConfirm && deletingUser && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 border border-slate-200 animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-3 rounded-2xl bg-red-100 text-red-600 flex-shrink-0">
                <Trash2 className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-extrabold text-slate-900 text-base">
                  Xác Nhận Xóa Tài Khoản
                </h3>
                <p className="text-xs text-slate-400">
                  Hành động này sẽ vô hiệu hóa và xóa mềm tài khoản
                </p>
              </div>
            </div>

            <p className="text-xs text-slate-600 mb-5 leading-relaxed">
              Bạn có chắc chắn muốn xóa tài khoản{" "}
              <strong className="text-slate-900 font-bold font-mono">
                {deletingUser.username}
              </strong>{" "}
              ({deletingUser.full_name})?
            </p>

            <div className="flex items-center justify-end gap-2.5">
              <button
                type="button"
                onClick={() => {
                  setShowDeleteConfirm(false);
                  setDeletingUser(null);
                }}
                disabled={isActionLoading}
                className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs transition-colors"
              >
                Hủy bỏ
              </button>
              <button
                type="button"
                onClick={handleDeleteUser}
                disabled={isActionLoading}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white font-bold text-xs shadow-md shadow-red-500/20 disabled:opacity-50 transition-all"
              >
                {isActionLoading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                <span>Xóa Tài Khoản</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
