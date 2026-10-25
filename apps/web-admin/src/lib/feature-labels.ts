export const FEATURE_META: Record<string, { label: string; badgeClass: string }> = {
  TESTCASE_GEN: {
    label: "Sinh testcase tự động",
    badgeClass: "bg-primary-bg text-primary",
  },
  CODE_REVIEW: {
    label: "Đánh giá & review code",
    badgeClass: "bg-emerald-50 text-emerald-700",
  },
  PLAGIARISM: {
    label: "Kiểm tra đạo văn",
    badgeClass: "bg-amber-50 text-amber-700",
  },
  UI_EVALUATION: {
    label: "Đánh giá giao diện web",
    badgeClass: "bg-sky-50 text-sky-700",
  },
  PE_CODE_EVAL: {
    label: "Đánh giá chất lượng mã nguồn",
    badgeClass: "bg-violet-50 text-violet-700",
  },
};

export function featureLabel(feature: string | null | undefined): string {
  return (feature && FEATURE_META[feature]?.label) || feature || "Chưa có dữ liệu";
}

export function featureBadgeClass(feature: string | null | undefined): string {
  return (feature && FEATURE_META[feature]?.badgeClass) || "bg-slate-100 text-slate-700";
}
