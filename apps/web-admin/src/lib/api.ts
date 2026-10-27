const DEFAULT_DEV_API_URL = "http://localhost:3000/api/v1";

export const API_URL = (
  process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === "development" ? DEFAULT_DEV_API_URL : "")
).replace(/\/+$/, "");

const ACCESS_TOKEN_KEY = "aita_access_token";
const USER_KEY = "aita_user";
const LOGIN_NOTICE_KEY = "aita_login_notice";

const ADMIN_ONLY_NOTICE =
  "Tài khoản Giảng viên không có quyền truy cập trang quản trị. Giảng viên vui lòng sử dụng ứng dụng AITA trên máy tính.";

/** Rút thông báo tạm đặt trước khi chuyển hướng (ví dụ bị đá vì không đủ quyền). */
export function consumeLoginNotice(): string | null {
  if (typeof window === "undefined") return null;
  const notice = window.sessionStorage.getItem(LOGIN_NOTICE_KEY);
  if (notice) window.sessionStorage.removeItem(LOGIN_NOTICE_KEY);
  return notice;
}

/** Đặt thông báo sẽ hiển thị trên trang đăng nhập sau khi chuyển hướng. */
export function setLoginNotice(message: string): void {
  if (typeof window === "undefined") return;
  window.sessionStorage.setItem(LOGIN_NOTICE_KEY, message);
}

export const ADMIN_ONLY_LOGIN_NOTICE = ADMIN_ONLY_NOTICE;

function readStorage(key: string): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(key) ?? window.sessionStorage.getItem(key);
}

export function getAccessToken(): string | null {
  return readStorage(ACCESS_TOKEN_KEY);
}

export function getStoredUser<T = unknown>(): T | null {
  if (typeof window === "undefined") return null;
  const raw = readStorage(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

export function storeSession(token: string, user: unknown, remember: boolean): void {
  if (typeof window === "undefined") return;
  const target = remember ? window.localStorage : window.sessionStorage;
  const other = remember ? window.sessionStorage : window.localStorage;
  target.setItem(ACCESS_TOKEN_KEY, token);
  target.setItem(USER_KEY, JSON.stringify(user));
  other.removeItem(ACCESS_TOKEN_KEY);
  other.removeItem(USER_KEY);
}

export function updateStoredUser(user: unknown): void {
  if (typeof window === "undefined") return;
  const target = window.localStorage.getItem(ACCESS_TOKEN_KEY)
    ? window.localStorage
    : window.sessionStorage;
  target.setItem(USER_KEY, JSON.stringify(user));
}

export function clearSession(): void {
  if (typeof window === "undefined") return;
  [window.localStorage, window.sessionStorage].forEach((storage) => {
    storage.removeItem(ACCESS_TOKEN_KEY);
    storage.removeItem(USER_KEY);
  });
}

export class ApiError extends Error {
  readonly status: number;
  readonly payload: unknown;

  constructor(status: number, message: string, payload: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

interface Envelope<T> {
  success?: boolean;
  message?: string;
  data?: T;
  details?: unknown;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  if (!API_URL) {
    throw new ApiError(
      0,
      "Chưa cấu hình địa chỉ máy chủ (NEXT_PUBLIC_API_URL). Vui lòng liên hệ quản trị viên.",
      null
    );
  }
  const token = getAccessToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string> | undefined),
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API_URL}${path}`, { ...init, headers });
  const json = (await res.json().catch(() => null)) as Envelope<T> | null;

  if (res.status === 401) {
    clearSession();
    throw new ApiError(401, json?.message || "Phiên đăng nhập đã hết hạn.", json);
  }
  if (!res.ok || json?.success === false) {
    const detail = Array.isArray(json?.details) ? json.details.join(", ") : null;
    throw new ApiError(res.status, detail || json?.message || "Yêu cầu thất bại.", json);
  }
  return (json?.data ?? null) as T;
}

export const apiGet = <T>(path: string) => request<T>(path);

export const apiSend = <T>(path: string, method: string, body?: unknown) =>
  request<T>(path, {
    method,
    body: body === undefined ? undefined : JSON.stringify(body),
  });

export const swrFetcher = <T>(path: string) => apiGet<T>(path);
