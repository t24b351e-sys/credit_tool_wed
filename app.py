import streamlit as st
import pandas as pd
from tannabi import read_requirements, read_courses, calculate_credits

# ==============================
# 単位管理ツール Web版
# ==============================

st.set_page_config(page_title="単位管理ツール", layout="wide")

st.title("🎓 単位管理ツール（進級／卒業対応版）")

# === モード選択 ===
mode = st.radio("要件を選択してください", ["進級要件", "卒業要件"])

req_file = "requirements2.txt" if mode == "進級要件" else "requirements1.txt"
required = read_requirements(req_file)

# === 学籍番号入力 ===
student_id = st.text_input("学籍番号を入力してください", placeholder="例: 1234567")

# === 講義データ読み込み ===
courses = read_courses("courses.txt")

# === 入力エリア ===
st.subheader("取得済み講義を選択してください")

earned_courses = {}

for cat, subject_list in courses.items():
    st.markdown(f"### [{cat}]区分")
    options = [f"{name}（{credit}単位）" for name, credit in subject_list]
    selected = st.multiselect(
        f"{cat}区分で取得した講義を選択", options, key=cat
    )

    earned_courses[cat] = []
    for sel in selected:
        name = sel.split("（")[0]
        credit = int(sel.split("（")[1].replace("単位）", ""))
        earned_courses[cat].append((name, credit))

# === 集計 ===
if st.button("結果を表示"):
    earned = calculate_credits(earned_courses)

    st.subheader("📊 結果")
    result_rows = []
    for cat in required:
        need = required[cat]
        got = earned.get(cat, 0)
        remain = max(0, need - got)
        result_rows.append({"区分": cat, "必要": need, "取得": got, "残り": remain})
    df = pd.DataFrame(result_rows)
    st.table(df)

    # 取得・未取得リスト表示
    st.subheader("📚 詳細")
    for cat in courses:
        taken_names = {name for name, _ in earned_courses.get(cat, [])}
        remaining = [name for name, _ in courses[cat] if name not in taken_names]
        st.markdown(f"#### [{cat}]区分")
        st.write(f"取得済み: {', '.join(taken_names) if taken_names else 'なし'}")
        st.write(f"未取得: {', '.join(remaining) if remaining else 'すべて取得済み'}")

    # === 保存機能 ===
    if student_id:
        filename = f"taken_{student_id}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            for cat, subjects in earned_courses.items():
                for name, credit in subjects:
                    f.write(f"{cat} {name} {credit}\n")
        st.success(f"✅ データを保存しました（{filename}）")
    else:
        st.warning("⚠ 学籍番号を入力するとデータを保存できます。")
