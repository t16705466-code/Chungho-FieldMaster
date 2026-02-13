import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. [디자인 박제] 화이트/블랙/연하늘 원칙
st.set_page_config(page_title="청호방재 업무일지", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, h4, p, label, span, div, .stMarkdown { color: #000000 !important; }
    [data-testid="stMetric"] {
        background-color: #E3F2FD !important;
        border: 1px solid #BBDEFB !important;
        padding: 20px; border-radius: 12px;
    }
    div.stButton > button { width: 100%; background-color: #E3F2FD !important; color: #000000 !important; border: 1px solid #BBDEFB !important; border-radius: 8px; font-weight: bold; }
    [data-testid="stDataEditor"] div[role="gridcell"] { background-color: #E3F2FD !important; color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. [데이터 로딩]
def load_data():
    if not os.path.exists("data.xlsx"):
        df = pd.DataFrame(columns=['ID', '관리번호', '진행상태', '현장명', '사업장주소', '계약금액', '완공분류'])
        df.to_excel("data.xlsx", index=False)
    df = pd.read_excel("data.xlsx")
    df['ID'] = range(1, len(df) + 1)
    if os.path.exists("contacts.csv"):
        try:
            c_df = pd.read_csv("contacts.csv")
            c_df.columns = [c.strip() for c in c_df.columns]
        except: c_df = pd.DataFrame()
    else: c_df = pd.DataFrame()
    return df, c_df

site_df, contact_df = load_data()

if 'page' not in st.session_state: st.session_state.page = 'dashboard'
if 'selected_site' not in st.session_state: st.session_state.selected_site = None

# --- [사이드바] ---
with st.sidebar:
    st.title("🏢 청호방재")
    if st.button("🏠 메인 대시보드"): st.session_state.page = 'dashboard'; st.session_state.selected_site = None; st.rerun()
    st.divider()
    if st.button("🟡 견적 데이터 관리"): st.session_state.page = 'list_est'; st.rerun()
    if st.button("🔵 진행 데이터 관리"): st.session_state.page = 'list_ing'; st.rerun()

# --- [메인 대시보드] ---
if st.session_state.page == 'dashboard' and st.session_state.selected_site is None:
    st.markdown("## 🚀 청호방재 통합 현황")
    
    # 상단 요약 3단 바
    m1, m2, m3 = st.columns(3)
    with m1:
        count_est = len(site_df[site_df['진행상태'].str.contains('견적', na=False, case=False)])
        st.metric("🟡 견적 대기", f"{count_est} 건")
    with m2:
        count_ing = len(site_df[site_df['진행상태'].str.contains('진행|공사', na=False, case=False)])
        st.metric("🔵 공사 진행중", f"{count_ing} 건")
    with m3:
        st.metric("📅 오늘 일정", "캘린더 확인")

    st.divider()

    # 구글 캘린더 연동 (사장님 ID 적용)
    st.markdown("#### 🗓️ 청호방재 업무 일정")
    cal_id = "t16705466@gmail.com"
    calendar_url = f"https://calendar.google.com/calendar/embed?src={cal_id}&ctz=Asia%2FSeoul"
    st.components.v1.iframe(calendar_url, height=600)

# --- [상세 페이지] ---
elif st.session_state.page == 'detail':
    site_name = st.session_state.selected_site
    st.markdown(f"### 🏢 {site_name} 업무일지")
    if st.button("⬅️ 메인으로"): st.session_state.page = 'dashboard'; st.rerun()
    
    # 6종 업무 분류 선택
    work_cat = st.selectbox("업무 분류", ["📞 통화", "🚗 방문", "📧 E-메일", "🏗️ 공사", "📄 서류작업", "💰 발행-입금"])
    log_temp = f"[업무일지 - {datetime.now().strftime('%Y-%m-%d')}]\n분류: {work_cat}\n내용: "
    st.text_area("기록", value=log_temp, height=300)
    st.button("💾 저장")
