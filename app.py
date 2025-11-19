import streamlit as st
import pandas as pd
from tool import read_requirements, read_courses, calculate_credits

# ==============================
# 単位管理ツール Web版（タブ切り替え）
# ==============================

st.set_page_config(page_title="単位管理ツール", layout="wide")

st.title("🎓 単位管理ツール")
st.markdown("進級・卒業に必要な単位を区分ごとに管理・確認できます。")

# === モード選択 ===
mode = st.radio("要件を選択してください", ["進級要件", "卒業要件"], horizontal=True)
req_file = "requirements2.txt" if mode == "進級要件" else "requirements1.txt"
required = read_requirements(req_file)

# === 学籍番号入力 ===
student_id = st.text_input("学籍番号を入力してください", placeholder="例: 1234567")

# === 講義データ読み込み ===
courses = read_courses("courses.txt")

# === タブ作成 ===
tab_names = list(courses.keys())
tabs = st.tabs(tab_names)

earned_courses = {}

for tab, cat in zip(tabs, tab_names):
    with tab:
        st.markdown(f"### {cat}区分")
        options = [f"{name}（{credit}単位）" for name, credit in courses[cat]]
        selected = st.multiselect(
            f"{cat}区分で取得した講義を選択してください",
            options,
            key=f"select_{cat}"
        )

        earned_courses[cat] = []
        for sel in selected:
            name = sel.split("（")[0]
            credit = int(sel.split("（")[1].replace("単位）", ""))
            earned_courses[cat].append((name, credit))

# === 結果表示ボタン ===
st.divider()
if st.button("📊 結果を表示"):
    earned = calculate_credits(earned_courses)

    st.subheader("📈 区分別集計結果")
    result_rows = []
    for cat in required:
        need = required[cat]
        got = earned.get(cat, 0)
        remain = max(0, need - got)
        result_rows.append({"区分": cat, "必要": need, "取得": got, "残り": remain})
    df = pd.DataFrame(result_rows)

    col1, col2 = st.columns(2)
    with col1:
        st.table(df)
    with col2:
        st.bar_chart(df.set_index("区分")[["必要", "取得"]])

    # === 未取得科目リスト ===
    st.subheader("📚 未取得科目一覧")
    for cat in courses:
        taken_names = {name for name, _ in earned_courses.get(cat, [])}
        remaining = [name for name, _ in courses[cat] if name not in taken_names]
        if remaining:
            st.markdown(f"**{cat}区分:** {', '.join(remaining)}")
        else:
            st.markdown(f"**{cat}区分:** ✅ 全て取得済み！")

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
