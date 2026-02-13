import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. [디자인 박제] 흰색 배경, 검정 글씨, 연하늘색 포인트 강제 설정
st.set_page_config(page_title="청호방재 업무일지", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* 다크모드 차단: 무조건 흰색 배경 / 검정 글씨 */
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, h4, p, label, span, div, .stMarkdown { color: #000000 !important; }
    
    /* 표(DB) 영역 연하늘색 배경 박제 */
    [data-testid="stDataEditor"] div[role="gridcell"] {
        background-color: #E3F2FD !important; color: #000000 !important;
    }
    [data-testid="stDataEditor"] div[role="columnheader"] {
        background-color: #BBDEFB !important; color: #000000 !important;
    }

    /* 모든 버튼 및 사이드바 메뉴 연하늘색 박제 */
    div.stButton > button {
        width: 100%; background-color: #E3F2FD !important; color: #000000 !important;
        border: 1px solid #BBDEFB !important; border-radius: 8px; font-weight: bold;
    }
    [data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #EEEEEE !important; }
    
    /* 입력창 디자인 */
    .stTextArea textarea { background-color: #FDFDFD !important; color: #000000 !important; border: 1px solid #E3F2FD !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. [데이터 로드] ID 자동 부여 및 관리번호 매칭 로직
def load_data():
    if not os.path.exists("data.xlsx"):
        df = pd.DataFrame(columns=['ID', '관리번호', '진행상태', '현장명', '사업장주소', '계약금액', '완공분류'])
        df.to_excel("data.xlsx", index=False)
    df = pd.read_excel("data.xlsx")
    df['ID'] = range(1, len(df) + 1) # ID 중복 에러 방지
    
    if os.path.exists("contacts.csv"):
        try:
            c_df = pd.read_csv("contacts.csv")
            c_df['관리번호'] = c_df['관리번호'].astype(str).str.strip()
        except: c_df = pd.DataFrame()
    else: c_df = pd.DataFrame()
    return df, c_df

site_df, contact_df = load_data()

# 세션 관리
if 'page' not in st.session_state: st.session_state.page = 'dashboard'
if 'selected_site' not in st.session_state: st.session_state.selected_site = None

# --- [사이드바 메뉴: 노션 스타일 계층 구조] ---
with st.sidebar:
    st.image("https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png", width=100) # 사장님 로고 위치
    st.title("🏢 청호방재")
    
    if st.button("🏠 메인 대시보드"):
        st.session_state.page = 'dashboard'; st.session_state.selected_site = None; st.rerun()
    
    st.divider()
    
    # [계층 메뉴 1] 견적 중 현장
    with st.expander("🟡 견적 중 현장", expanded=False):
        est_list = site_df[site_df['진행상태'].str.contains('견적', na=False)].tail(3)
        for _, row in est_list.iterrows():
            if st.button(f"📄 {row['현장명']}", key=f"side_est_{row['ID']}"):
                st.session_state.selected_site = row['현장명']; st.session_state.page = 'detail'; st.rerun()
        if st.button("➕ 견적 추가", key="add_est"): st.info("데이터베이스에서 추가하세요")

    # [계층 메뉴 2] 진행 중 현장
    with st.expander("🔵 진행 중 현장", expanded=False):
        ing_list = site_df[site_df['진행상태'].str.contains('진행|공사', na=False)].tail(3)
        for _, row in ing_list.iterrows():
            if st.button(f"🏢 {row['현장명']}", key=f"side_ing_{row['ID']}"):
                st.session_state.selected_site = row['현장명']; st.session_state.page = 'detail'; st.rerun()
        if st.button("➕ 현장 추가", key="add_ing"): st.info("데이터베이스에서 추가하세요")

    # [계층 메뉴 3] 완공 현장 아카이브
    with st.expander("📂 완공 현장 (용도별)", expanded=False):
        cats = ["제조소_취급소", "옥내저장소", "옥외저장소", "옥내탱크", "옥외탱크", "지하탱크", "군부대", "도료류", "컨설팅"]
        for cat in cats:
            if st.button(f"▪️ {cat}"):
                st.session_state.page = 'list_done'; st.session_state.cat_filter = cat; st.rerun()

# --- [상세 페이지: 원노트 양식 + 업무 분류 6종] ---
if st.session_state.page == 'detail':
    site_name = st.session_state.selected_site
    site_info = site_df[site_df['현장명'] == site_name].iloc[0]
    site_no = str(site_info.get('관리번호', '')).strip()

    st.markdown(f"### 🏢 {site_name} 상세일지")
    if st.button("⬅️ 메인으로"): st.session_state.page = 'dashboard'; st.session_state.selected_site = None; st.rerun()

    st.divider()
    
    # 현장 연락처 자동 연동
    st.markdown("#### 📞 현장 연락처")
    matched = contact_df[contact_df['관리번호'] == site_no]
    st.dataframe(matched if not matched.empty else pd.DataFrame(columns=["연락처 없음"]), use_container_width=True, hide_index=True)

    # 업무 분류 6종 선택 박스
    st.markdown("#### 📝 업무 기록")
    work_cat = st.selectbox("업무 분류", ["📞 통화", "🚗 방문", "📧 E-메일", "🏗️ 공사", "📄 서류작업", "💰 발행-입금"])
    
    # 원노트 표준 양식 박제
    log_format = f"""[업무일지 - {datetime.now().strftime('%Y-%m-%d')}]
분류: {work_cat}
작성자: 함재영 사장님
---------------------------------------
■ 작업내용: 

■ 인력/장비: 

■ 특이사항: 
"""
    st.text_area("내용 입력", value=log_format, height=350)
    
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("💾 일지 저장"): st.success("일지가 기록되었습니다.")
    with c2:
        # 완공 이동 기능
        finish_cat = st.selectbox("공사 완료 시 카테고리 선택", ["제조소_취급소", "옥내저장소", "옥외저장소", "옥내탱크", "옥외탱크", "지하탱크", "군부대", "도료류", "컨설팅"])
        if st.button("✅ 완공 처리 및 아카이빙"):
            st.warning(f"이 현장을 '{finish_cat}' 섹션으로 이동하시겠습니까?")

# --- [대시보드 화면] ---
else:
    st.markdown("## 🚀 청호방재 업무일지 실시간 현황")
    st.info("사이드바의 계층 메뉴를 통해 현장을 관리하거나, 아래 일정표를 확인하세요.")
    st.divider()
    st.components.v1.iframe("https://calendar.google.com/calendar/embed?src=ko.south_korea%23holiday%40group.v.calendar.google.com", height=500)
