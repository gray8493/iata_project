const DEFAULT_DEV_API_URL = "http://localhost:3000/api/v1";

export const API_URL = (
  process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === "development" ? DEFAULT_DEV_API_URL : "")
).replace(/\/+$/, "");

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("aita_access_token");
}

export function clearSession(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem("aita_access_token");
  localStorage.removeItem("aita_user");
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
