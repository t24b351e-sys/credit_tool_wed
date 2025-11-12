# ==============================
# 単位管理ツール（進級／卒業選択対応版）
# ==============================

import os

def read_requirements(filename):
    """必要単位をファイルから読み込む"""
    requirements = {}
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                category, credits = parts
                requirements[category] = int(credits)
    return requirements


def read_courses(filename="courses.txt"):
    """講義リストを区分ごとに読み込む"""
    courses = {}
    current_cat = None
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("[") and line.endswith("]"):
                current_cat = line[1:-1]
                courses[current_cat] = []
            else:
                try:
                    name, credit = line.rsplit(" ", 1)
                    courses[current_cat].append((name, int(credit)))
                except ValueError:
                    continue
    return courses


def read_user_data(student_id):
    """保存済みデータを読み取る"""
    filename = f"taken_{student_id}.txt"
    earned_courses = {}
    if not os.path.exists(filename):
        return None

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 3:
                cat, name, credit = parts
                if cat not in earned_courses:
                    earned_courses[cat] = []
                earned_courses[cat].append((name, int(credit)))
    return earned_courses


def select_courses(courses):
    earned_courses = {cat: [] for cat in courses}

    print("\n=== 取得済み講義を選択してください ===")
    print("複数選ぶときは空白区切りで番号を入力。何も取っていない場合はEnter。")

    for cat, subject_list in courses.items():
        print(f"\n[{cat}区分]")
        for i, (name, credit) in enumerate(subject_list, 1):
            print(f"{i}. {name}（{credit}単位）")

        nums = input("取得済み講義の番号 → ").split()
        for n in nums:
            try:
                idx = int(n) - 1
                if 0 <= idx < len(subject_list):
                    earned_courses[cat].append(subject_list[idx])
            except ValueError:
                continue

    return earned_courses


def calculate_credits(earned_courses):
    earned = {}
    for cat, subjects in earned_courses.items():
        earned[cat] = sum(credit for _, credit in subjects)
    return earned


def show_remaining(required, earned, courses, earned_courses):
    print("\n=== 結果 ===")
    for cat in required:
        need = required[cat]
        got = earned.get(cat, 0)
        remain = max(0, need - got)
        print(f"{cat}区分: 必要{need} / 取得{got} / 残り{remain}")

        if cat in courses:
            taken_names = {name for name, _ in earned_courses.get(cat, [])}
            remaining_subjects = [
                name for name, _ in courses[cat] if name not in taken_names
            ]
            if remaining_subjects:
                print("→ まだ取っていない講義：")
                for name in remaining_subjects:
                    print(f"   - {name}")
        print()


def save_user_data(student_id, earned_courses):
    filename = f"taken_{student_id}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        for cat, subjects in earned_courses.items():
            for name, credit in subjects:
                f.write(f"{cat} {name} {credit}\n")


def main():
    print("=== 単位管理ツール（進級／卒業選択対応版） ===")

    # ✅ 進級要件 or 卒業要件の選択
    mode = ""
    while mode not in ["p", "g"]:
        mode = input("進級要件(p)か卒業要件(g)かを選んでください： ").strip().lower()

    if mode == "p":
        req_file = "requirements2.txt"
        print("\n→ 進級要件を使用します。")
    else:
        req_file = "requirements1.txt"
        print("\n→ 卒業要件を使用します。")

    # 学籍番号
    student_id = input("\n学籍番号を入力してください： ").strip()

    # ファイル読み込み
    required = read_requirements(req_file)
    courses = read_courses()

    print("\n--- 選択された要件ファイル ---")
    for k, v in required.items():
        print(f"{k}: {v}単位")

    # 前回データチェック
    old_data = read_user_data(student_id)
    if old_data:
        print(f"\n前回のデータ（taken_{student_id}.txt）が見つかりました。")
        choice = input("上書きしますか？(y/n)： ").lower()
        if choice == "n":
            print("\n前回のデータを読み込みます。")
            earned = calculate_credits(old_data)
            show_remaining(required, earned, courses, old_data)
            print("\n※変更なしで終了します。")
            return
        else:
            print("\n新しいデータを入力します（前回の記録は上書きされます）。")

    # 新しいデータ入力
    earned_courses = select_courses(courses)
    earned = calculate_credits(earned_courses)

    # 出力・保存
    show_remaining(required, earned, courses, earned_courses)
    save_user_data(student_id, earned_courses)
    print(f"\nデータを保存しました。（taken_{student_id}.txt）")


if __name__ == "__main__":
    main()
