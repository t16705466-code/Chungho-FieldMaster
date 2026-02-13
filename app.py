import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="청호방재 필드마스터", layout="wide", initial_sidebar_state="collapsed")

# 2. 디자인 수정 (입력창 색상 연하게 + 가독성 강화)
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    h1, h2, h3, h4, p, label { color: #1A1A1A !important; }
    
    /* 입력창(Text Area) 디자인: 연한 배경에 깔끔한 테두리 */
    .stTextArea textarea {
        background-color: #ffffff !important;
        color: #1A1A1A !important;
        border: 1px solid #E0E0E0 !important;
        border-radius: 10px !important;
    }
    
    /* 버튼 스타일 */
    div.stButton > button {
        width: 100%;
        background-color: #ffffff !important;
        color: #1A1A1A !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 8px;
        padding: 12px;
        font-weight: 500;
    }
    
    .status-title {
        font-size: 1.2rem; font-weight: bold; padding: 10px;
        border-bottom: 3px solid #007AFF; margin-bottom: 15px; color: #007AFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 데이터 로드
def load_data():
    try:
        df = pd.read_excel("data.xlsx")
        df['진행상태'] = df['진행상태'].astype(str).str.strip()
        c_df = pd.read_csv("contacts.csv").dropna(axis=1, how='all')
        return df, c_df
    except: return None, None

site_df, contact_df = load_data()

if 'page' not in st.session_state: st.session_state.page = 'dashboard'
if 'selected_site' not in st.session_state: st.session_state.selected_site = None

# --- [대시보드 화면] ---
if st.session_state.page == 'dashboard':
    st.title("🚀 청호방재 상황실")
    
    if site_df is not None:
        # 데이터 분류 (진행/견적 포함된 것 모두 찾기)
        ing_sites = site_df[site_df['진행상태'].str.contains('진행', na=False)].iloc[::-1].head(5)
        est_sites = site_df[site_df['진행상태'].str.contains('견적', na=False)].iloc[::-1].head(5)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='status-title'>🔵 진행 중인 현장</div>", unsafe_allow_html=True)
            for _, row in ing_sites.iterrows():
                if st.button(f"🏢 {row['현장명']}\n📍 {str(row['사업장주소'])[:15]}...", key=f"ing_{row['관리번호']}"):
                    st.session_state.selected_site = row['현장명']
                    st.session_state.page = 'detail'; st.rerun()

        with col2:
            st.markdown("<div class='status-title'>🟡 견적 중인 현장</div>", unsafe_allow_html=True)
            for _, row in est_sites.iterrows():
                if st.button(f"📄 {row['현장명']}\n⚖️ {row['관할서']}", key=f"est_{row['관리번호']}"):
                    st.session_state.selected_site = row['현장명']
                    st.session_state.page = 'detail'; st.rerun()
    
    st.divider()
    st.markdown("### 🗓️ 업무 일정 (구글 캘린더)")
    # 사장님 캘린더 주소로 교체하세요! (비공개 주소 말고 '공개 URL'을 넣으시면 됩니다)
    calendar_url = "https://calendar.google.com/calendar/embed?src=ko.south_korea%23holiday%40group.v.calendar.google.com" 
    st.components.v1.iframe(calendar_url, height=500)

# --- [상세 페이지] ---
elif st.session_state.page == 'detail':
    site_name = st.session_state.selected_site
    site_info = site_df[site_df['현장명'] == site_name].iloc[0]
    site_no = str(site_info.get('관리번호', ''))

    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.page = 'dashboard'; st.rerun()

    st.markdown(f"### 🏢 {site_name}")
    st.markdown(f"📍 **주소:** {site_info.get('사업장주소', '-')} | 🔢 **관리번호:** {site_no}")

    # 업무 일지 (입력창 배경을 연하게 수정함)
    st.markdown("#### 📝 현장 업무 일지")
    uploaded_file = st.file_uploader("📸 현장 사진 첨부", type=['jpg', 'png', 'jpeg'])
    log_text = st.text_area("작업 내용 기록", height=200, placeholder="여기에 작업 내용을 입력하세요 (배경색이 연해졌습니다)")
    
    if st.button("💾 일지 저장"):
        st.success(f"[{site_name}] 일지가 임시 기록되었습니다.")

    st.divider()
    
    # 연락처 연동 (현장명이나 관리번호로 찾기)
    st.markdown("#### 👥 관련 연락처")
    # 연락처 매칭 로직 강화
    matched = contact_df[contact_df.apply(lambda x: (site_no in str(x.values)) or (site_name in str(x.values)), axis=1)]
    
    if not matched.empty:
        for _, p in matched.iterrows():
            st.write(f"👤 **{p.get('First Name','')}** ({p.get('Organization Title','')})")
            st.write(f"📞 {p.get('Phone 1 - Value','')}")
            st.write("---")
    else:
        st.caption("매칭된 연락처가 없습니다.")
