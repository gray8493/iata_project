# -*- coding: utf-8 -*-
"""
AITA Desktop Client - Seeding đợt chấm PE môn CSD (Cấu trúc dữ liệu & giải thuật):

    submissions/CSD_Demo/SE180001..SE180015/Q1..Q5.java  (mỗi SV 1 thư mục con)
    submissions/CSD_Demo/testcases_csd_demo.json         (5 câu x 5 testcase)

15 sinh viên, 5 câu hỏi. 11 SV làm đủ 5 câu; 4 SV "làm ít hơn"
(SE180006: 3 câu, SE180007: 2 câu, SE180008: 4 câu, SE180009: 3 câu)
-> kết quả trả về đầy đủ cho cả 15 SV: SV thiếu câu bị CE ở câu đó và điểm bị trừ tương ứng.

Script tự: (1) sinh file bài làm, (2) ghi spec JSON, (3) purge đợt DEMO_CSD_* cũ,
(4) nạp đợt chấm + testcase + danh sách nộp vào SQLite, (5) CHẤM THẬT cả lớp
bằng GradingService (javac/JVM trong toolchains/) rồi in bảng kết quả.

Cách chạy (từ thư mục gốc repo):
    python apps/desktop-client/scripts/seed_csd_demo.py
"""

import json
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from database.db_manager import DatabaseManager  # noqa: E402
from services.grading_service import GradingService  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
DEMO_DIR = REPO_ROOT / "submissions" / "CSD_Demo"
PURGE_PREFIX = "DEMO_CSD_"

WEIGHT = 2.0  # mỗi testcase 2.0 điểm trọng số; tổng 50 -> quy về thang 10

# ---------------------------------------------------------------------------
# Đề thi CSD: 5 câu, mỗi câu kèm code mẫu (đúng 100%) + 5 testcase
# ---------------------------------------------------------------------------
QUESTIONS = [
    {
        "label": "Cau 1: Dao nguoc chuoi bang Stack (LIFO)",
        "entrypoint": "Q1",
        "code": """import java.util.Scanner;
import java.util.Stack;

public class Q1 {
    static String reverseString(String s) {
        Stack<Character> st = new Stack<>();
        for (char c : s.toCharArray()) st.push(c);
        StringBuilder sb = new StringBuilder();
        while (!st.isEmpty()) sb.append(st.pop());
        return sb.toString();
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.nextLine();
        System.out.println(reverseString(s));
    }
}
""",
        "testcases": [
            ("hello", "olleh"), ("AITA", "ATIA"), ("12345", "54321"),
            ("abc def", "fed cba"), ("a", "a"),
        ],
    },
    {
        "label": "Cau 2: Two Sum bang HashMap - O(n)",
        "entrypoint": "Q2",
        "code": """import java.util.HashMap;
import java.util.Scanner;

public class Q2 {
    static int[] twoSum(int[] nums, int target) {
        HashMap<Integer, Integer> map = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int c = target - nums[i];
            if (map.containsKey(c)) return new int[]{map.get(c), i};
            map.put(nums[i], i);
        }
        return new int[]{-1, -1};
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] nums = new int[n];
        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();
        int target = sc.nextInt();
        int[] res = twoSum(nums, target);
        System.out.println(res[0] + " " + res[1]);
    }
}
""",
        "testcases": [
            ("4\n2 7 11 15\n9", "0 1"), ("3\n3 2 4\n6", "1 2"),
            ("2\n3 3\n6", "0 1"), ("5\n1 5 3 9 7\n4", "0 2"),
            ("6\n-3 4 8 1 -5 6\n-8", "0 4"),
        ],
    },
    {
        "label": "Cau 3: Phat hien chu trinh danh sach lien ket (Floyd)",
        "entrypoint": "Q3",
        "code": """import java.util.Scanner;

public class Q3 {
    static class Node {
        int val;
        Node next;
        Node(int v) { val = v; }
    }

    static boolean hasCycle(Node head) {
        if (head == null) return false;
        Node slow = head, fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
            if (slow == fast) return true;
        }
        return false;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        if (n == 0) {
            System.out.println("KHONG CO CHU TRINH");
            return;
        }
        Node[] nodes = new Node[n];
        for (int i = 0; i < n; i++) nodes[i] = new Node(sc.nextInt());
        for (int i = 0; i + 1 < n; i++) nodes[i].next = nodes[i + 1];
        int pos = sc.nextInt();
        if (pos >= 0) nodes[n - 1].next = nodes[pos];
        System.out.println(hasCycle(nodes[0]) ? "CO CHU TRINH" : "KHONG CO CHU TRINH");
    }
}
""",
        "testcases": [
            ("4\n3 2 0 -4\n1", "CO CHU TRINH"), ("2\n1 2\n0", "CO CHU TRINH"),
            ("1\n1\n-1", "KHONG CO CHU TRINH"), ("5\n1 2 3 4 5\n-1", "KHONG CO CHU TRINH"),
            ("3\n7 8 9\n2", "CO CHU TRINH"),
        ],
    },
    {
        "label": "Cau 4: Tim kiem nhi phan (Binary Search) - O(log n)",
        "entrypoint": "Q4",
        "code": """import java.util.Scanner;

public class Q4 {
    static int binSearch(int[] a, int n, int x) {
        int l = 0, r = n - 1;
        while (l <= r) {
            int m = l + (r - l) / 2;
            if (a[m] == x) return m;
            if (a[m] < x) l = m + 1;
            else r = m - 1;
        }
        return -1;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] a = new int[n];
        for (int i = 0; i < n; i++) a[i] = sc.nextInt();
        int x = sc.nextInt();
        System.out.println(binSearch(a, n, x));
    }
}
""",
        "testcases": [
            ("5\n1 3 5 7 9\n5", "2"), ("6\n2 4 6 8 10 12\n10", "4"),
            ("5\n1 3 5 7 9\n4", "-1"), ("4\n-5 0 3 9\n-5", "0"), ("1\n7\n7", "0"),
        ],
    },
    {
        "label": "Cau 5: Duyet cay nhi phan theo tang BFS (Queue)",
        "entrypoint": "Q5",
        "code": """import java.util.LinkedList;
import java.util.Queue;
import java.util.Scanner;

public class Q5 {
    static class Node {
        int val;
        Node left, right;
        Node(int v) { val = v; }
    }

    static String levelOrder(Node root) {
        if (root == null) return "";
        StringBuilder sb = new StringBuilder();
        Queue<Node> q = new LinkedList<>();
        q.add(root);
        while (!q.isEmpty()) {
            Node cur = q.poll();
            sb.append(cur.val);
            if (cur.left != null) q.add(cur.left);
            if (cur.right != null) q.add(cur.right);
            if (!q.isEmpty()) sb.append(" ");
        }
        return sb.toString();
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        sc.nextLine();
        String[] tokens = sc.nextLine().trim().split("\\\\s+");
        Node root = new Node(Integer.parseInt(tokens[0]));
        Queue<Node> q = new LinkedList<>();
        q.add(root);
        int i = 1;
        while (i < n) {
            Node cur = q.poll();
            if (!tokens[i].equals("null")) {
                cur.left = new Node(Integer.parseInt(tokens[i]));
                q.add(cur.left);
            }
            i++;
            if (i < n && !tokens[i].equals("null")) {
                cur.right = new Node(Integer.parseInt(tokens[i]));
                q.add(cur.right);
            }
            i++;
        }
        System.out.println(levelOrder(root));
    }
}
""",
        "testcases": [
            ("5\n1 2 3 4 5", "1 2 3 4 5"), ("3\n1 null 2", "1 2"),
            ("7\n3 9 20 null null 15 7", "3 9 20 15 7"), ("4\n1 2 null 3", "1 2 3"),
            ("1\n42", "42"),
        ],
    },
]

# 15 sinh viên; `answered` = số câu SV thực sự làm (SV làm ít hơn 5 -> thiếu file câu sau)
STUDENTS = [
    ("SE180001", "Nguyen Van An", 5),
    ("SE180002", "Tran Thi Binh", 5),
    ("SE180003", "Le Minh Chau", 5),
    ("SE180004", "Pham Duc Duy", 5),
    ("SE180005", "Vu Hong Em", 5),
    ("SE180006", "Hoang Van Phuc", 3),   # làm ít hơn: chỉ Q1-Q3
    ("SE180007", "Ngo Thi Giang", 2),    # làm ít hơn: chỉ Q1-Q2
    ("SE180008", "Doan Quoc Hung", 4),   # làm ít hơn: chỉ Q1-Q4
    ("SE180009", "Dang Ngoc Ich", 3),    # làm ít hơn: chỉ Q1-Q3
    ("SE180010", "Bui Thi Kim", 5),
    ("SE180011", "Ly Thanh Long", 5),
    ("SE180012", "Nguyen Thi Mai", 5),
    ("SE180013", "Truong Van Nam", 5),
    ("SE180014", "Phan Thi Oanh", 5),
    ("SE180015", "To Quoc Phong", 5),
]


def write_student_files() -> None:
    """Sinh thư mục + file Q<n>.java cho từng sinh viên (SV làm ít câu -> thiếu file câu sau)."""
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    for mssv, name, answered in STUDENTS:
        folder = DEMO_DIR / mssv
        folder.mkdir(exist_ok=True)
        # Dọn file của đợt seed trước (C cũ / bytecode / exe) để thư mục chỉ còn bài Java
        for stale in folder.iterdir():
            if stale.is_file() and (stale.suffix.lower() in {".c", ".exe", ".class"}):
                stale.unlink()
        for q in QUESTIONS:
            qnum = q["entrypoint"]
            if int(qnum[1]) > answered:
                continue
            code = f"// {mssv} - {name}\n// {q['label']}: sinh vien chi viet ham con (main khong sua)\n\n" + q["code"]
            (folder / f"{qnum}.java").write_text(code, encoding="utf-8")
    print(f"[files] Đã sinh {len(STUDENTS)} thư mục sinh viên trong {DEMO_DIR}")


def write_spec_json() -> None:
    spec = {
        "language": "Java",
        "class_name": "DEMO_CSD_5CAU",
        "class_label": "DEMO_CSD_5CAU",
        "students": [
            {"mssv": m, "name": n, "answered": a} for m, n, a in STUDENTS
        ],
        "questions": [
            {
                "question_label": q["label"],
                "entrypoint": q["entrypoint"],
                "testcases": [
                    {
                        "question_number": q["entrypoint"],
                        "input_data": inp,
                        "expected_output": out,
                        "score_weight": WEIGHT,
                        "time_limit_ms": 2000,
                        "memory_limit_mb": 256,
                        "matching_strategy": "EXACT_MATCH",
                    }
                    for inp, out in q["testcases"]
                ],
            }
            for q in QUESTIONS
        ],
    }
    path = DEMO_DIR / "testcases_csd_demo.json"
    path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[spec] Đã ghi {path}")


def purge_old_csd_sessions(db: DatabaseManager) -> int:
    purged = 0
    for cls in db.get_all_classes():
        if not str(cls.get("class_name", "")).startswith(PURGE_PREFIX):
            continue
        for tc_row in db.get_testcases_by_class(int(cls["id"])):
            db.delete_testcase(int(tc_row["id"]))
        db.delete_class_session(int(cls["id"]))
        purged += 1
    return purged


def seed(db: DatabaseManager) -> int:
    class_id = db.create_class_session(
        class_name="DEMO_CSD_5CAU",
        course_code="CSD",
        programming_language="Java",
        folder_path=str(DEMO_DIR),
        csv_path="",
    )
    for q in QUESTIONS:
        for inp, out in q["testcases"]:
            db.add_testcase(
                class_id=class_id,
                input_data=inp,
                expected_output=out,
                score_weight=WEIGHT,
                time_limit_ms=2000,
                memory_limit_mb=256,
                matching_strategy="EXACT_MATCH",
                question_number=q["entrypoint"],
            )
    items = [(class_id, mssv, str(DEMO_DIR / mssv)) for mssv, _, _ in STUDENTS]
    db.bulk_insert_submissions(items)
    return class_id


def grade_all(db: DatabaseManager, class_id: int) -> None:
    svc = GradingService(db)

    def progress(done: int, total: int, mssv: str) -> None:
        print(f"       Chấm {mssv} ({done}/{total})", flush=True)

    print(f"[grade] Bắt đầu chấm thật 15 bài nộp (javac + JVM + sandbox)...")
    svc.grade_class_batch(class_id, progress_callback=progress)


def print_summary(db: DatabaseManager, class_id: int) -> None:
    rows = db.get_submissions_by_class(class_id)
    print()
    print("=" * 62)
    print(f"{'MSSV':<10} {'Điểm':>6} {'Verdict':<8}  Ghi chú")
    print("-" * 62)
    partial = {m: a for m, _, a in STUDENTS if a < 5}
    for r in rows:
        mssv = r["student_mssv"]
        score = r["calculated_score"] or 0.0
        verdict = r["final_verdict"] or "PENDING"
        note = f"làm {partial[mssv]}/5 câu" if mssv in partial else ""
        print(f"{mssv:<10} {score:>6.1f} {verdict:<8}  {note}")
    print("=" * 62)
    n_partial = len(partial)
    print(f"Tổng: {len(rows)} sinh viên có đủ kết quả (11 đủ 5 câu, {n_partial} làm ít hơn).")


def main() -> None:
    db = DatabaseManager()

    write_student_files()
    write_spec_json()

    purged = purge_old_csd_sessions(db)
    if purged:
        print(f"[purge] Đã xóa {purged} đợt chấm DEMO_CSD_* cũ (kết quả cũ bị đánh dấu ẩn).")

    class_id = seed(db)
    print(f"[seed] Đợt chấm 'DEMO_CSD_5CAU' (môn CSD): 25 testcase (5 câu x 5), "
          f"15 bài nộp (class_id={class_id})")

    grade_all(db, class_id)
    print_summary(db, class_id)


if __name__ == "__main__":
    main()
