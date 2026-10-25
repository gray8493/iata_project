import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center px-4 py-12 text-center font-sans">
      <p className="text-6xl font-bold text-primary tracking-tight">404</p>
      <h1 className="mt-4 text-xl font-semibold text-slate-900">
        Không tìm thấy trang
      </h1>
      <p className="mt-2 text-sm text-slate-500 max-w-sm">
        Trang bạn đang tìm kiếm không tồn tại hoặc đã bị di chuyển đến địa chỉ khác.
      </p>
      <Link
        href="/dashboard"
        className="mt-6 px-4 h-10 inline-flex items-center rounded-lg bg-primary hover:bg-primary-hover text-white font-medium text-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-1"
      >
        Quay về bảng điều khiển
      </Link>
    </div>
  );
}
