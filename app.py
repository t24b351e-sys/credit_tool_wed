import streamlit as st
import pandas as pd
import os
import re
from tool import read_requirements, read_courses, calculate_credits

# ==============================
# 単位管理ツール Web版（保存 & 復元つき）
# ==============================

st.set_page_config(page_title="単位管理ツール", layout="wide")
st.title("🎓 単位管理ツール（進級／卒業対応版・保存機能つき）")

# === モード選択 ===
mode = st.radio("要件を選択してください", ["進級要件", "卒業要件"])
req_file = "requirements2.txt" if mode == "進級要件" else "requirements1.txt"
required = read_requirements(req_file)

# === 学籍番号入力 ===
student_id = st.text_input("学籍番号を入力してください", placeholder="例: 1234567")

# === 講義データ読み込み ===
courses = read_courses("courses.txt")

# --------------------------
#  🔄 学籍番号入力時に保存ファイルを読み込み
# --------------------------
loaded_taken = {}  # {カテゴリ: [科目名,…]}

if student_id:
    filename = f"taken_{student_id}.txt"
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                cat, name, credit = line.strip().split(" ")
                loaded_taken.setdefault(cat, []).append(name)
        st.success("📂 保存されたデータを読み込みました！")
    else:
        st.info("ℹ 保存データはありません（初回利用と思われます）。")


# ==========================
# UI：科目選択（保存内容を復元）
# ==========================
st.subheader("取得済み講義を選択してください")

earned_courses = {}

for cat, subject_list in courses.items():
    st.markdown(f"### [{cat}]区分")

    # 選択肢（例: "線形代数（2単位）"）
    options = [f"{name}（{credit}単位）" for name, credit in subject_list]

    # 保存データがあれば、それを multiselect の初期値にする
    default_selected = []
    if cat in loaded_taken:
        for name, credit in subject_list:
            if name in loaded_taken[cat]:
                default_selected.append(f"{name}（{credit}単位）")

    selected = st.multiselect(
        f"{cat}区分で取得した講義を選択",
        options,
        default=default_selected,  # ← 復元機能
        key=f"sel_{cat}"
    )

    # 選択結果を解析（安全な正規表現）
    earned_courses[cat] = []
    for sel in selected:
        name = sel.split("（")[0]
        m = re.search(r"(\d+)", sel)
        credit = int(m.group(1)) if m else 0
        earned_courses[cat].append((name, credit))


# ==========================
# 📊 結果表示 & 保存
# ==========================
if st.button("結果を表示"):
    earned = calculate_credits(earned_courses)

    # --- 集計表 ---
    st.subheader("📊 結果")
    rows = []
    for cat in required:
        need = required[cat]
        got = earned.get(cat, 0)
        remain = max(0, need - got)
        rows.append({"区分": cat, "必要": need, "取得": got, "残り": remain})
    st.table(pd.DataFrame(rows))

    # --- 詳細 ---
    st.subheader("📚 詳細")
    for cat in courses:
        taken_names = {name for name, _ in earned_courses.get(cat, [])}
        remaining = [name for name, _ in courses[cat] if name not in taken_names]
        st.markdown(f"#### [{cat}]区分")
        st.write(f"取得済み: {', '.join(taken_names) if taken_names else 'なし'}")
        st.write(f"未取得: {', '.join(remaining) if remaining else 'すべて取得済み'}")

    # --- 保存機能 ---
    if student_id:
        filename = f"taken_{student_id}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            for cat, subs in earned_courses.items():
                for name, credit in subs:
                    f.write(f"{cat} {name} {credit}\n")
        st.success(f"💾 データを保存しました！（{filename}）")
    else:
        st.warning("⚠ 学籍番号を入力するとデータを保存できます。")
