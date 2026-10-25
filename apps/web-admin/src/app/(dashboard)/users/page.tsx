"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { Loader2, Inbox } from "lucide-react";
import { API_URL, getAccessToken, getStoredUser } from "@/lib/api";
import Alert from "@/components/ui/alert";
import Modal from "@/components/ui/modal";

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
  const [users, setUsers] = useState<UserItem[]>([]);
  const [pagination, setPagination] = useState<PaginationData>({
    page: 1,
    page_size: 10,
    total_items: 0,
    total_pages: 1,
  });

  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState<"ALL" | "ADMIN" | "INSTRUCTOR">("INSTRUCTOR");

  const [loading, setLoading] = useState(true);
  const [isActionLoading, setIsActionLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  // Tài khoản đang đăng nhập (để chặn thao tác trên chính mình)
  const [currentUser, setCurrentUser] = useState<{ id?: string; username?: string }>({});

  // Modal Cấp Tài Khoản Mới
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newUsername, setNewUsername] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newFullName, setNewFullName] = useState("");
  const [newEmail, setNewEmail] = useState("");
  const [newRole, setNewRole] = useState<"INSTRUCTOR" | "ADMIN">("INSTRUCTOR");
  const [newQuota, setNewQuota] = useState<string>("");

  // Modal Chỉnh Sửa Tài Khoản
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingUser, setEditingUser] = useState<UserItem | null>(null);
  const [editFullName, setEditFullName] = useState("");
  const [editEmail, setEditEmail] = useState("");
  const [editRole, setEditRole] = useState<"INSTRUCTOR" | "ADMIN">("INSTRUCTOR");
  const [editQuota, setEditQuota] = useState<string>("");
  const [editNewPassword, setEditNewPassword] = useState("");
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showEditPassword, setShowEditPassword] = useState(false);

  // Modal Xác Nhận Xóa
  const [deletingUser, setDeletingUser] = useState<UserItem | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const anyModalOpen = showCreateModal || showEditModal || showDeleteConfirm;

  // Nạp thông tin tài khoản đang đăng nhập từ cache phiên
  useEffect(() => {
    const parsed = getStoredUser<{ id?: string; username?: string }>();
    if (parsed) {
      setCurrentUser({ id: parsed.id, username: parsed.username });
    }
  }, []);

  const isSelf = useCallback(
    (u: UserItem) =>
      (currentUser.id && u.id === currentUser.id) ||
      (!!currentUser.username && u.username === currentUser.username),
    [currentUser]
  );

  const countLabel =
    roleFilter === "INSTRUCTOR"
      ? "giảng viên (không gồm quản trị viên)"
      : roleFilter === "ADMIN"
      ? "quản trị viên"
      : "tài khoản";

  // Debounce tìm kiếm 350ms
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(searchQuery.trim());
      setPagination((prev) => ({ ...prev, page: 1 }));
    }, 350);
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

  const getApiConfig = () => {
    const token = getAccessToken();
    return { token, apiUrl: API_URL };
  };

  // Lấy danh sách từ API Backend
  const fetchUsers = useCallback(
    async (pageTarget = pagination.page) => {
      const { token, apiUrl } = getApiConfig();
      if (!token) {
        setErrorMessage("Chưa tìm thấy phiên đăng nhập. Vui lòng đăng nhập lại.");
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
            Authorization: `Bearer ${token}`,
          },
        });

        if (res.status === 401) {
          setErrorMessage("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.");
          localStorage.removeItem("aita_access_token");
          return;
        }

        const json = await res.json();
        if (res.ok && json.success) {
          setUsers(json.data.items || []);
          if (json.data.pagination) {
            setPagination(json.data.pagination);
          }
        } else {
          setErrorMessage(json.message || "Không thể tải danh sách tài khoản từ máy chủ.");
        }
      } catch {
        setErrorMessage("Lỗi kết nối tới máy chủ.");
      } finally {
        setLoading(false);
      }
    },
    [pagination.page, pagination.page_size, roleFilter, debouncedSearch]
  );

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  // Cấp phát tài khoản mới
  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    const { token, apiUrl } = getApiConfig();
    if (!token) return;

    if (!/^[a-zA-Z0-9_]{3,30}$/.test(newUsername.trim())) {
      setErrorMessage("Tên đăng nhập phải từ 3-30 ký tự, chỉ gồm chữ cái, số và dấu gạch dưới.");
      return;
    }

    if (!/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/.test(newPassword.trim())) {
      setErrorMessage("Mật khẩu khởi tạo phải tối thiểu 8 ký tự, gồm ít nhất 1 chữ hoa, 1 chữ thường và 1 chữ số.");
      return;
    }

    setIsActionLoading(true);
    setErrorMessage("");

    try {
      const payload: Record<string, any> = {
        username: newUsername.trim().toLowerCase(),
        password: newPassword.trim(),
        full_name: newFullName.trim(),
        email: newEmail.trim().toLowerCase(),
        role: newRole,
      };

      if (newQuota !== "" && !isNaN(Number(newQuota))) {
        payload.daily_token_quota = Math.max(0, Math.floor(Number(newQuota)));
      }

      const res = await fetch(`${apiUrl}/admin/users`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      const json = await res.json();
      if (res.ok && json.success) {
        setSuccessMessage(`Đã cấp tài khoản thành công cho "${newUsername}"!`);
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
          : (json.message || "Không thể tạo tài khoản.");
        setErrorMessage(detailMsg);
      }
    } catch {
      setErrorMessage("Lỗi kết nối khi gửi yêu cầu cấp tài khoản.");
    } finally {
      setIsActionLoading(false);
    }
  };

  // Khóa / Mở khóa tài khoản
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
        setSuccessMessage(`Đã ${user.is_active ? "khóa" : "kích hoạt"} tài khoản "${user.username}".`);
        fetchUsers(pagination.page);
      } else {
        setErrorMessage(json.message || "Không thể cập nhật trạng thái tài khoản.");
        fetchUsers(pagination.page);
      }
    } catch {
      setErrorMessage("Lỗi kết nối khi thay đổi trạng thái tài khoản.");
      fetchUsers(pagination.page);
    }
  };

  const handleOpenEditModal = async (u: UserItem) => {
    setEditingUser(u);
    setEditFullName(u.full_name);
    setEditEmail(u.email);
    setEditRole(u.role);
    setEditNewPassword("");
    setEditQuota(u.daily_token_quota !== undefined && u.daily_token_quota !== null ? String(u.daily_token_quota) : "");

    const { token, apiUrl } = getApiConfig();
    if (token) {
      try {
        const res = await fetch(`${apiUrl}/admin/users/${u.id}`, {
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

  // Cập nhật tài khoản
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

  // Xóa tài khoản
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
        setSuccessMessage(`Đã xóa và vô hiệu hóa tài khoản "${deletingUser.username}" thành công.`);
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
    <div className="flex flex-col w-full gap-6">
      {/* Thông báo lỗi — ẩn khi modal đang mở (lỗi được hiển thị bên trong modal) */}
      {errorMessage && !anyModalOpen && (
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
            <span className="text-slate-800 font-medium">Quản lý giảng viên</span>
          </nav>

          <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">
            Quản lý tài khoản giảng viên
          </h1>
          <p className="text-[13px] text-slate-500 mt-1">
            {pagination.total_items} {countLabel}
          </p>
        </div>

        {/* Nút hành động chính */}
        <div className="flex items-center gap-2.5 shrink-0">
          <button
            type="button"
            onClick={handleExportCsv}
            disabled={users.length === 0}
            className="flex items-center gap-2 px-3.5 h-10 rounded-lg bg-white border border-slate-200 text-slate-700 font-medium text-sm hover:bg-slate-50 transition-colors disabled:opacity-50 disabled:text-slate-400 disabled:cursor-not-allowed min-h-[40px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
            aria-label="Xuất file CSV"
          >
            <span>Xuất CSV</span>
          </button>

          <button
            type="button"
            onClick={() => {
              setErrorMessage("");
              setShowCreateModal(true);
            }}
            className="flex items-center gap-2 px-4 h-10 rounded-lg bg-primary hover:bg-primary-hover text-white font-medium text-sm transition-colors min-h-[40px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-1"
            aria-label="Cấp tài khoản mới"
          >
            <span>Cấp tài khoản mới</span>
          </button>
        </div>
      </section>

      {/* ================= BỘ LỌC TÌM KIẾM ================= */}
      <section className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3 flex-1">
          {/* Ô tìm kiếm */}
          <div className="relative min-w-[260px] flex-1 max-w-sm">
            <input
              type="search"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Tìm theo username, họ tên, email..."
              aria-label="Tìm kiếm tài khoản"
              className="w-full px-3 pr-9 h-10 rounded-lg text-[13px] bg-slate-50 border border-slate-200 placeholder:text-slate-500 focus:outline-none focus:bg-white focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery("")}
                className="absolute right-0 top-0 h-10 px-2.5 text-slate-400 hover:text-slate-700 transition-colors"
                aria-label="Xóa nội dung tìm kiếm"
              >
                ×
              </button>
            )}
          </div>

          {/* Lọc Vai trò */}
          <select
            value={roleFilter}
            onChange={(e) => {
              setRoleFilter(e.target.value as any);
              setPagination((prev) => ({ ...prev, page: 1 }));
            }}
            className="h-10 px-3 rounded-lg text-[13px] bg-slate-50 border border-slate-200 text-slate-700 font-medium focus:outline-none focus:border-primary focus:bg-white transition-colors"
          >
            <option value="INSTRUCTOR">Giảng viên (INSTRUCTOR)</option>
            <option value="ADMIN">Quản trị viên (ADMIN)</option>
            <option value="ALL">Tất cả vai trò</option>
          </select>

          {/* Nút Làm mới */}
          <button
            type="button"
            onClick={() => fetchUsers(pagination.page)}
            disabled={loading}
            title="Làm mới danh sách"
            className="h-10 px-3.5 rounded-lg bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 flex items-center justify-center text-[13px] font-medium transition-colors disabled:opacity-50 disabled:text-slate-400 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
            aria-label="Tải lại dữ liệu"
          >
            {loading ? "Đang tải..." : "Làm mới"}
          </button>
        </div>
      </section>

      {/* ================= BẢNG DỮ LIỆU TÀI KHOẢN ================= */}
      <section className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
        <div className="overflow-x-auto w-full">
          <table className="w-full text-left text-[13px]">
            <thead className="bg-slate-50/50 text-slate-500 font-medium border-b border-slate-200">
              <tr>
                <th scope="col" className="py-3 px-4 font-medium">Tên đăng nhập</th>
                <th scope="col" className="py-3 px-4 font-medium">Họ và tên</th>
                <th scope="col" className="py-3 px-4 font-medium">Email</th>
                <th scope="col" className="py-3 px-4 font-medium">Vai trò</th>
                <th scope="col" className="py-3 px-4 text-center font-medium">Trạng thái</th>
                <th scope="col" className="py-3 px-4 font-medium">Ngày tạo</th>
                <th scope="col" className="py-3 px-4 text-right font-medium">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-normal">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-500">
                    <Loader2 className="w-5 h-5 mx-auto animate-spin text-primary mb-1.5" />
                    <span>Đang tải danh sách tài khoản...</span>
                  </td>
                </tr>
              ) : users.length > 0 ? (
                users.map((u) => {
                  const self = isSelf(u);
                  const isAdmin = u.role === "ADMIN";
                  const lockDisabled = self || isAdmin;
                  const deleteDisabled = self || isAdmin;
                  const lockTooltip = self
                    ? "Không thể khóa tài khoản đang đăng nhập"
                    : isAdmin
                    ? "Không thao tác khóa trên tài khoản quản trị viên"
                    : u.is_active
                    ? "Khóa tài khoản"
                    : "Mở khóa tài khoản";
                  const deleteTooltip = self
                    ? "Không thể xóa tài khoản đang đăng nhập"
                    : isAdmin
                    ? "Không thao tác xóa trên tài khoản quản trị viên"
                    : "Xóa tài khoản";

                  return (
                    <tr key={u.id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-3 px-4 whitespace-nowrap text-[13px] font-medium text-slate-900">
                        {u.username}
                      </td>

                      <td className="py-3 px-4 text-slate-900 font-medium whitespace-nowrap">
                        {u.full_name}
                      </td>

                      <td className="py-3 px-4 text-[13px] text-slate-500 whitespace-nowrap">
                        {u.email}
                      </td>

                      <td className="py-3 px-4 whitespace-nowrap">
                        {isAdmin ? (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-[13px] bg-slate-100 text-slate-700 font-medium">
                            Quản trị viên
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-[13px] bg-primary-bg text-primary font-medium">
                            Giảng viên
                          </span>
                        )}
                      </td>

                      <td className="py-3 px-4 text-center whitespace-nowrap">
                        {u.is_active ? (
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

                      <td className="py-3 px-4 text-slate-500 text-[13px] whitespace-nowrap">
                        {new Date(u.created_at).toLocaleDateString("vi-VN")}
                      </td>

                      <td className="py-3 px-4 text-right whitespace-nowrap">
                        <div className="inline-flex items-center gap-3">
                          {/* Nút chữ Khóa / Mở khóa */}
                          <button
                            type="button"
                            onClick={() => handleToggleStatus(u)}
                            disabled={lockDisabled}
                            className={`text-[13px] font-medium rounded-md px-2 py-1 transition-colors ${
                              lockDisabled
                                ? "text-slate-400 cursor-not-allowed"
                                : u.is_active
                                ? "text-amber-700 hover:bg-amber-50"
                                : "text-emerald-700 hover:bg-emerald-50"
                            }`}
                            title={lockTooltip}
                            aria-label={lockTooltip}
                          >
                            {u.is_active ? "Khóa" : "Mở khóa"}
                          </button>

                          {/* Nút chữ Sửa */}
                          <button
                            type="button"
                            onClick={() => handleOpenEditModal(u)}
                            className="text-[13px] font-medium rounded-md px-2 py-1 text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-colors"
                            title="Sửa tài khoản"
                            aria-label="Sửa tài khoản"
                          >
                            Sửa
                          </button>

                          {/* Nút chữ Xóa */}
                          <button
                            type="button"
                            onClick={() => {
                              setDeletingUser(u);
                              setShowDeleteConfirm(true);
                            }}
                            disabled={deleteDisabled}
                            className={`text-[13px] font-medium rounded-md px-2 py-1 transition-colors ${
                              deleteDisabled
                                ? "text-slate-400 cursor-not-allowed"
                                : "text-rose-600 hover:bg-rose-50"
                            }`}
                            title={deleteTooltip}
                            aria-label={deleteTooltip}
                          >
                            Xóa
                          </button>
                        </div>
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
                      <p className="text-[13px] text-slate-500">
                        Không có tài khoản nào phù hợp với bộ lọc hiện tại.
                      </p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Phân trang */}
        <div className="p-4 border-t border-slate-200 flex items-center justify-between text-sm text-slate-500">
          <span>{pagination.total_items} {countLabel}</span>

          {pagination.total_items > pagination.page_size && (
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={() => setPagination((prev) => ({ ...prev, page: Math.max(1, prev.page - 1) }))}
                disabled={pagination.page <= 1 || loading}
                className="px-3 h-9 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors min-h-[36px] flex items-center justify-center text-[13px] font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
                aria-label="Trang trước"
              >
                Trước
              </button>

              <span className="px-2.5 py-1 text-[13px] font-medium text-slate-700 bg-slate-100 rounded-md">
                {pagination.page} / {pagination.total_pages}
              </span>

              <button
                type="button"
                onClick={() =>
                  setPagination((prev) => ({
                    ...prev,
                    page: Math.min(prev.total_pages, prev.page + 1),
                  }))
                }
                disabled={pagination.page >= (pagination.total_pages || 1) || loading}
                className="px-3 h-9 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors min-h-[36px] flex items-center justify-center text-[13px] font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
                aria-label="Trang sau"
              >
                Sau
              </button>
            </div>
          )}
        </div>
      </section>

      {/* ================= MODAL CẤP TÀI KHOẢN MỚI ================= */}
      <Modal
        open={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Cấp tài khoản mới"
        description="Tạo tài khoản quản trị hoặc giảng viên trong hệ thống"
      >
        <form onSubmit={handleCreateUser} className="space-y-3.5 text-[13px]">
          {errorMessage && (
            <Alert variant="error" onClose={() => setErrorMessage("")}>
              {errorMessage}
            </Alert>
          )}

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="new-username" className="block font-medium text-slate-700 mb-1">
                Tên đăng nhập <span className="text-rose-500">*</span>
              </label>
              <input
                id="new-username"
                type="text"
                required
                autoComplete="off"
                value={newUsername}
                onChange={(e) => setNewUsername(e.target.value.toLowerCase())}
                placeholder="vd: teacher_nam"
                className="w-full px-3 h-10 rounded-lg bg-slate-50 border border-slate-200 focus:outline-none focus:border-primary focus:bg-white transition-colors"
              />
              <p className="text-[13px] text-slate-500 mt-0.5">Chữ thường, số, dấu _ (3-30 ký tự)</p>
            </div>

            <div>
              <label htmlFor="new-role" className="block font-medium text-slate-700 mb-1">
                Vai trò <span className="text-rose-500">*</span>
              </label>
              <select
                id="new-role"
                value={newRole}
                onChange={(e) => setNewRole(e.target.value as "INSTRUCTOR" | "ADMIN")}
                className="w-full px-3 h-10 rounded-lg bg-slate-50 border border-slate-200 focus:outline-none focus:border-primary focus:bg-white transition-colors"
              >
                <option value="INSTRUCTOR">Giảng viên (INSTRUCTOR)</option>
                <option value="ADMIN">Quản trị viên (ADMIN)</option>
              </select>
            </div>
          </div>

          <div>
            <label htmlFor="new-password" className="block font-medium text-slate-700 mb-1">
              Mật khẩu khởi tạo <span className="text-rose-500">*</span>
            </label>
            <div className="relative flex items-center">
              <input
                id="new-password"
                type={showNewPassword ? "text" : "password"}
                required
                autoComplete="new-password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-3 pr-14 h-10 rounded-lg bg-slate-50 border border-slate-200 focus:outline-none focus:border-primary focus:bg-white transition-colors"
              />
              <button
                type="button"
                onClick={() => setShowNewPassword(!showNewPassword)}
                className="absolute right-0 py-1.5 px-2.5 text-[13px] font-medium text-slate-500 hover:text-slate-700 transition"
                aria-label={showNewPassword ? "Ẩn mật khẩu" : "Hiện mật khẩu"}
              >
                {showNewPassword ? "Ẩn" : "Hiện"}
              </button>
            </div>
            <p className="text-[13px] text-slate-500 mt-0.5">Tối thiểu 8 ký tự, gồm ít nhất 1 chữ hoa, 1 chữ thường và 1 chữ số</p>
          </div>

          <div>
            <label htmlFor="new-fullname" className="block font-medium text-slate-700 mb-1">
              Họ và tên đầy đủ <span className="text-rose-500">*</span>
            </label>
            <input
              id="new-fullname"
              type="text"
              required
              value={newFullName}
              onChange={(e) => setNewFullName(e.target.value)}
              placeholder="vd: ThS. Nguyễn Văn A"
              className="w-full px-3 h-10 rounded-lg bg-slate-50 border border-slate-200 focus:outline-none focus:border-primary focus:bg-white transition-colors"
            />
          </div>

          <div>
            <label htmlFor="new-email" className="block font-medium text-slate-700 mb-1">
              Địa chỉ email <span className="text-rose-500">*</span>
            </label>
            <input
              id="new-email"
              type="email"
              required
              value={newEmail}
              onChange={(e) => setNewEmail(e.target.value)}
              placeholder="vd: nguyenvana@aita.edu.vn"
              className="w-full px-3 h-10 rounded-lg bg-slate-50 border border-slate-200 focus:outline-none focus:border-primary focus:bg-white transition-colors"
            />
          </div>

          <div>
            <label htmlFor="new-quota" className="block font-medium text-slate-700 mb-1">
              Hạn ngạch AI (Tokens/ngày)
            </label>
            <input
              id="new-quota"
              type="number"
              min="0"
              value={newQuota}
              onChange={(e) => setNewQuota(e.target.value)}
              placeholder="Mặc định: 50,000 (Không bắt buộc)"
              className="w-full px-3 h-10 rounded-lg bg-slate-50 border border-slate-200 focus:outline-none focus:border-primary focus:bg-white transition-colors"
            />
            <p className="text-[13px] text-slate-500 mt-0.5">Để trống sẽ tự động áp dụng 50,000 tokens/ngày</p>
          </div>

          <div className="flex items-center justify-end gap-2.5 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setShowCreateModal(false)}
              className="px-4 h-10 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 font-medium transition-colors"
            >
              Hủy bỏ
            </button>

            <button
              type="submit"
              disabled={isActionLoading}
              className="px-4 h-10 rounded-lg bg-primary hover:bg-primary-hover text-white font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isActionLoading && <Loader2 className="w-4 h-4 animate-spin" />}
              <span>Xác nhận tạo tài khoản</span>
            </button>
          </div>
        </form>
      </Modal>

      {/* ================= MODAL CHỈNH SỬA TÀI KHOẢN ================= */}
      <Modal
        open={showEditModal}
        onClose={() => setShowEditModal(false)}
        title="Chỉnh sửa tài khoản"
        description={editingUser ? `@${editingUser.username}` : undefined}
      >
        {editingUser && (
          <form onSubmit={handleUpdateUser} className="space-y-3.5 text-[13px]">
            {errorMessage && (
              <Alert variant="error" onClose={() => setErrorMessage("")}>
                {errorMessage}
              </Alert>
            )}

            <div>
              <label htmlFor="edit-fullname" className="block font-medium text-slate-700 mb-1">
                Họ và tên
              </label>
              <input
                id="edit-fullname"
                type="text"
                required
                value={editFullName}
                onChange={(e) => setEditFullName(e.target.value)}
                className="w-full px-3 h-10 rounded-lg bg-slate-50 border border-slate-200 focus:outline-none focus:border-primary focus:bg-white transition-colors"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="edit-email" className="block font-medium text-slate-700 mb-1">
                  Email
                </label>
                <input
                  id="edit-email"
                  type="email"
                  required
                  value={editEmail}
                  onChange={(e) => setEditEmail(e.target.value)}
                  className="w-full px-3 h-10 rounded-lg bg-slate-50 border border-slate-200 focus:outline-none focus:border-primary focus:bg-white transition-colors"
                />
              </div>

              <div>
                <label htmlFor="edit-role" className="block font-medium text-slate-700 mb-1">
                  Vai trò
                </label>
                <select
                  id="edit-role"
                  value={editRole}
                  onChange={(e) => setEditRole(e.target.value as "INSTRUCTOR" | "ADMIN")}
                  disabled={isSelf(editingUser)}
                  title={isSelf(editingUser) ? "Không thể hạ quyền tài khoản đang đăng nhập" : undefined}
                  className="w-full px-3 h-10 rounded-lg bg-slate-50 border border-slate-200 focus:outline-none focus:border-primary focus:bg-white transition-colors disabled:text-slate-400 disabled:cursor-not-allowed"
                >
                  <option value="INSTRUCTOR">Giảng viên (INSTRUCTOR)</option>
                  <option value="ADMIN">Quản trị viên (ADMIN)</option>
                </select>
                {isSelf(editingUser) && (
                  <p className="text-[13px] text-slate-500 mt-0.5">Không thể đổi vai trò của tài khoản đang đăng nhập.</p>
                )}
              </div>
            </div>

            <div>
              <label htmlFor="edit-quota" className="block font-medium text-slate-700 mb-1">
                Hạn ngạch AI (Tokens/ngày)
              </label>
              <input
                id="edit-quota"
                type="number"
                min="0"
                value={editQuota}
                onChange={(e) => setEditQuota(e.target.value)}
                placeholder="Nhập số token/ngày"
                className="w-full px-3 h-10 rounded-lg bg-slate-50 border border-slate-200 focus:outline-none focus:border-primary focus:bg-white transition-colors"
              />
            </div>

            <div>
              <label htmlFor="edit-password" className="block font-medium text-slate-700 mb-1">
                Đổi mật khẩu mới (Bỏ trống nếu không đổi)
              </label>
              <div className="relative flex items-center">
                <input
                  id="edit-password"
                  type={showEditPassword ? "text" : "password"}
                  autoComplete="new-password"
                  value={editNewPassword}
                  onChange={(e) => setEditNewPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-3 pr-14 h-10 rounded-lg bg-slate-50 border border-slate-200 focus:outline-none focus:border-primary focus:bg-white transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowEditPassword(!showEditPassword)}
                  className="absolute right-0 py-1.5 px-2.5 text-[13px] font-medium text-slate-500 hover:text-slate-700 transition"
                  aria-label={showEditPassword ? "Ẩn mật khẩu" : "Hiện mật khẩu"}
                >
                  {showEditPassword ? "Ẩn" : "Hiện"}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2.5 pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setShowEditModal(false)}
                className="px-4 h-10 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 font-medium transition-colors"
              >
                Hủy bỏ
              </button>

              <button
                type="submit"
                disabled={isActionLoading}
                className="px-4 h-10 rounded-lg bg-primary hover:bg-primary-hover text-white font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isActionLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                <span>Lưu thay đổi</span>
              </button>
            </div>
          </form>
        )}
      </Modal>

      {/* ================= MODAL XÁC NHẬN XÓA ================= */}
      <Modal
        open={showDeleteConfirm}
        onClose={() => {
          setShowDeleteConfirm(false);
          setDeletingUser(null);
        }}
        title="Xác nhận xóa tài khoản?"
        maxWidthClass="max-w-sm"
      >
        {deletingUser && (
          <>
            {errorMessage && (
              <Alert variant="error" onClose={() => setErrorMessage("")}>
                {errorMessage}
              </Alert>
            )}

            <p className="text-[13px] text-slate-500 leading-relaxed">
              Bạn có chắc chắn muốn xóa tài khoản{" "}
              <strong className="text-slate-800">@{deletingUser.username}</strong>{" "}
              ({deletingUser.full_name})? Tài khoản sẽ bị vô hiệu hóa vĩnh viễn,
              không thể đăng nhập lại và toàn bộ phiên đang hoạt động sẽ bị thu hồi.
            </p>

            <div className="flex items-center justify-end gap-2.5 pt-5 mt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => {
                  setShowDeleteConfirm(false);
                  setDeletingUser(null);
                }}
                className="px-4 h-10 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 font-medium text-[13px] transition-colors"
              >
                Hủy bỏ
              </button>

              <button
                type="button"
                onClick={handleDeleteUser}
                disabled={isActionLoading}
                className="px-4 h-10 rounded-lg bg-rose-600 hover:bg-rose-700 text-white font-medium text-[13px] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isActionLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                <span>Xác nhận xóa</span>
              </button>
            </div>
          </>
        )}
      </Modal>
    </div>
  );
}
