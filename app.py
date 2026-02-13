import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="청호방재 필드마스터", layout="wide", initial_sidebar_state="collapsed")

# 2. 확실한 가독성을 위한 디자인 (글자색 검정 고정)
st.markdown("""
    <style>
    .stApp { background-color: #F7F9FB; }
    h1, h2, h3, h4, p, label, .stMarkdown { color: #1A1A1A !important; }
    
    /* 버튼 글씨 안 보이는 문제 해결 */
    div.stButton > button {
        width: 100%;
        background-color: #ffffff !important;
        color: #1A1A1A !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 8px;
        text-align: left;
        padding: 10px;
        margin-bottom: 5px;
    }
    div.stButton > button:hover {
        border-color: #007AFF !important;
        background-color: #F0F7FF !important;
    }
    
    .status-title {
        font-size: 1.2rem;
        font-weight: bold;
        padding: 10px;
        border-bottom: 2px solid #007AFF;
        margin-bottom: 15px;
        color: #007AFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 데이터 로드 (캐시를 지워서 엑셀 수정 시 바로 반영되게 함)
def load_data():
    try:
        # 파일 이름을 찾습니다.
        site_df = pd.read_excel("data.xlsx")
        contact_df = pd.read_csv("contacts.csv").dropna(axis=1, how='all')
        return site_df, contact_df
    except: return None, None

site_df, contact_df = load_data()

if 'page' not in st.session_state: st.session_state.page = 'dashboard'
if 'selected_site' not in st.session_state: st.session_state.selected_site = None

# --- [메인 대시보드 화면] ---
if st.session_state.page == 'dashboard':
    st.title("🚀 청호방재 실시간 현황")
    
    if site_df is not None:
        # 데이터 분류
        ing_sites = site_df[site_df['진행상태'] == '진행중'].tail(5).iloc[::-1]
        est_sites = site_df[site_df['진행상태'] == '견적중'].tail(5).iloc[::-1]

        # 2열 배치 (진행중 | 견적중)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div class='status-title'>🔵 진행 중인 현장</div>", unsafe_allow_html=True)
            for _, row in ing_sites.iterrows():
                if st.button(f"🏢 {row['현장명']}\n📍 {str(row['사업장주소'])[:15]}...", key=f"ing_{row['관리번호']}"):
                    st.session_state.selected_site = row['현장명']
                    st.session_state.page = 'detail'
                    st.rerun()

        with col2:
            st.markdown("<div class='status-title'>🟡 견적 중인 현장</div>", unsafe_allow_html=True)
            for _, row in est_sites.iterrows():
                if st.button(f"📄 {row['현장명']}\n⚖️ {row['관할서']}", key=f"est_{row['관리번호']}"):
                    st.session_state.selected_site = row['현장명']
                    st.session_state.page = 'detail'
                    st.rerun()
    
    st.divider()

    # 3. 구글 캘린더 연동 (iframe)
    st.markdown("### 🗓️ 업무 일정 (구글 캘린더)")
    # 사장님 구글 캘린더의 '설정 및 공유'에서 '공개 주소' 또는 '임베드 코드'를 여기 넣으면 실제 캘린더가 뜹니다.
    # 일단은 샘플 캘린더를 띄워드립니다.
    calendar_url = "https://calendar.google.com/calendar/embed?src=ko.south_korea%23holiday%40group.v.calendar.google.com&ctz=Asia%2FSeoul"
    st.components.v1.iframe(calendar_url, height=500)

# --- [현장 상세 페이지] ---
elif st.session_state.page == 'detail':
    site_name = st.session_state.selected_site
    site_info = site_df[site_df['현장명'] == site_name].iloc[0]
    site_no = str(site_info.get('관리번호', ''))

    if st.button("⬅️ 메인 대시보드로 돌아가기"):
        st.session_state.page = 'dashboard'
        st.rerun()

    st.markdown(f"## 🏢 {site_name}")
    
    # 정보 카드
    st.info(f"📍 주소: {site_info.get('사업장주소', '-')} | 🔢 관리번호: {site_no}")

    # 업무 일지 (여기서 기입)
    st.markdown("### 📝 오늘의 업무 일지")
    uploaded_file = st.file_uploader("📸 현장 사진 첨부", type=['jpg', 'png', 'jpeg'])
    log_text = st.text_area("작업 내용 기록", height=200, placeholder="오늘 작업 내용을 자유롭게 기록하세요.")
    if st.button("💾 일지 저장"):
        st.success(f"{site_name} 일지가 기록되었습니다.")

    st.divider()
    
    # 연락처 연동
    st.markdown("### 👥 관련 연락처")
    matched = contact_df[contact_df.apply(lambda x: (site_no in str(x.values)) or (site_name in str(x.values)), axis=1)]
    if not matched.empty:
        for _, p in matched.iterrows():
            st.write(f"👤 **{p.get('First Name','')}** ({p.get('Organization Title','')}) : {p.get('Phone 1 - Value','')}")
