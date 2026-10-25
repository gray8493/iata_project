"use client";

import React from "react";

const VARIANT_STYLES = {
  error: {
    box: "bg-rose-50 border-rose-200 text-rose-700",
    closeHover: "hover:text-rose-900",
    role: "alert",
  },
  success: {
    box: "bg-emerald-50 border-emerald-200 text-emerald-800",
    closeHover: "hover:text-emerald-950",
    role: "status",
  },
  info: {
    box: "bg-sky-50 border-sky-200 text-sky-800",
    closeHover: "hover:text-sky-950",
    role: "status",
  },
} as const;

interface AlertProps {
  variant?: keyof typeof VARIANT_STYLES;
  onClose?: () => void;
  className?: string;
  children: React.ReactNode;
}

export default function Alert({
  variant = "error",
  onClose,
  className = "",
  children,
}: AlertProps) {
  const style = VARIANT_STYLES[variant];
  return (
    <div
      role={style.role}
      className={`flex items-center justify-between gap-3 p-3.5 border rounded-lg text-[13px] font-medium animate-in fade-in ${style.box} ${className}`}
    >
      <span className="min-w-0 flex items-center gap-3 flex-wrap">{children}</span>
      {onClose && (
        <button
          type="button"
          onClick={onClose}
          className={`font-medium ${style.closeHover} shrink-0 min-h-[24px]`}
          aria-label="Đóng thông báo"
        >
          Đóng
        </button>
      )}
    </div>
  );
}
