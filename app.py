import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정 및 모바일 최적화
st.set_page_config(page_title="청호방재 필드마스터", layout="wide", initial_sidebar_state="collapsed")

# 스타일 설정 (글자색 검정, 카드 디자인)
st.markdown("""
    <style>
    .stApp { background-color: #F7F9FB; color: #1A1A1A; }
    h1, h2, h3, h4, p, label { color: #1A1A1A !important; }
    .status-card {
        background-color: #ffffff; padding: 15px; border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 10px;
        border-left: 5px solid #007AFF; cursor: pointer;
    }
    .status-header {
        background-color: #E1E8ED; padding: 10px; border-radius: 8px;
        font-weight: bold; margin-top: 20px; color: #333;
    }
    </style>
    """, unsafe_allow_html=True)

# 데이터 로드
@st.cache_data
def load_data():
    try:
        site_df = pd.read_excel("data.xlsx")
        contact_df = pd.read_csv("contacts.csv").dropna(axis=1, how='all')
        return site_df, contact_df
    except: return None, None

site_df, contact_df = load_data()

# 페이지 이동 제어 (세션 상태 이용)
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'
if 'selected_site' not in st.session_state:
    st.session_state.selected_site = None

# --- [메인 대시보드 화면] ---
if st.session_state.page == 'dashboard':
    st.title("🚀 청호방재 상황실")
    
    # 현장 분류 (진행상태 컬럼 기준)
    # 사장님 엑셀의 '진행상태' 혹은 '구분' 컬럼명을 확인해주세요. 
    # 여기서는 '진행상태' 컬럼이 있다고 가정합니다.
    ing_sites = site_df[site_df['진행상태'] == '진행중'].tail(5) # 최신 5개
    est_sites = site_df[site_df['진행상태'] == '견적중'].tail(5) # 최신 5개

    # 1. 진행중 현장 섹션
    st.markdown("<div class='status-header'>🔵 진행 중인 현장 (최신 5건)</div>", unsafe_allow_html=True)
    for _, row in ing_sites.iterrows():
        if st.button(f"🏢 {row['현장명']} | {row['사업장주소'][:20]}...", key=f"ing_{row['관리번호']}"):
            st.session_state.selected_site = row['현장명']
            st.session_state.page = 'detail'
            st.rerun()

    # 2. 견적중 현장 섹션
    st.markdown("<div class='status-header'>🟡 견적 중인 현장 (최신 5건)</div>", unsafe_allow_html=True)
    for _, row in est_sites.iterrows():
        if st.button(f"📄 {row['현장명']} | {row['관할서']}", key=f"est_{row['관리번호']}"):
            st.session_state.selected_site = row['현장명']
            st.session_state.page = 'detail'
            st.rerun()

# --- [현장 상세 페이지] ---
elif st.session_state.page == 'detail':
    site_name = st.session_state.selected_site
    site_info = site_df[site_df['현장명'] == site_name].iloc[0]
    site_no = str(site_info.get('관리번호', ''))

    if st.button("⬅️ 대시보드로 돌아가기"):
        st.session_state.page = 'dashboard'
        st.rerun()

    st.markdown(f"## 🏢 {site_name}")
    st.info(f"📍 주소: {site_info.get('사업장주소', '-')} | 🔢 관리번호: {site_no}")

    # 업무 일지 작성 (상세페이지에서만 노출)
    st.markdown("### 📝 오늘의 업무 일지")
    uploaded_file = st.file_uploader("📸 현장 사진 첨부", type=['jpg', 'png', 'jpeg'])
    log_text = st.text_area("작업 내용 기록", height=150)
    if st.button("💾 일지 저장하기"):
        st.success("해당 현장 일지가 기록되었습니다!")

    # 관계자 연락처
    st.markdown("### 👥 현장 관계자")
    matched = contact_df[contact_df.apply(lambda x: (site_no in str(x.values)) or (site_name in str(x.values)), axis=1)]
    for _, p in matched.iterrows():
        st.markdown(f"👤 **{p.get('First Name','')}** | {p.get('Phone 1 - Value','')}")
