"use client";

import React, { useEffect, useId, useRef } from "react";

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  maxWidthClass?: string;
  cardClassName?: string;
  contentClassName?: string;
}

export default function Modal({
  open,
  onClose,
  title,
  description,
  children,
  footer,
  maxWidthClass = "max-w-lg",
  cardClassName = "",
  contentClassName = "mt-4",
}: ModalProps) {
  const titleId = useId();
  const descriptionId = useId();
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleKeyDown);
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    dialogRef.current?.focus();

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = previousOverflow;
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-200"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        ref={dialogRef}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={description ? descriptionId : undefined}
        className={`bg-white rounded-xl shadow-xl w-full ${maxWidthClass} p-6 border border-slate-200 outline-none animate-in fade-in zoom-in-95 duration-150 ${cardClassName}`}
      >
        <div className="flex items-center justify-between gap-3 pb-4 border-b border-slate-100">
          <div className="min-w-0">
            <h3 id={titleId} className="font-semibold text-slate-900 text-base">
              {title}
            </h3>
            {description && (
              <p id={descriptionId} className="text-[13px] text-slate-500 mt-0.5 truncate">
                {description}
              </p>
            )}
          </div>
          <button
            type="button"
            onClick={onClose}
            className="px-2.5 py-1.5 text-[13px] font-medium text-slate-600 hover:text-slate-900 rounded-lg transition-colors min-h-[36px] shrink-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
            aria-label="Đóng"
          >
            Đóng
          </button>
        </div>

        <div className={contentClassName}>{children}</div>

        {footer && (
          <div className="p-4 border-t border-slate-200 bg-slate-50 flex justify-end shrink-0">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}
