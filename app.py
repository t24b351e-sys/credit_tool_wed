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
            name = sel.split("（
