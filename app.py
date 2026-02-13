import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정 및 디자인 박제
st.set_page_config(page_title="청호방재 필드마스터", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* 전체 배경 흰색 및 기본 글자색 검정 */
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, h4, p, label, span, div { color: #000000 !important; }
    
    /* [박제] 엑셀 데이터가 보이는 표 영역 전체 설정 */
    /* 1. 데이터 셀 배경색: 연한 하늘색, 글씨: 검정 */
    [data-testid="stDataEditor"] div[role="gridcell"] {
        background-color: #E3F2FD !important; 
        color: #000000 !important;
        border-bottom: 1px solid #BBDEFB !important;
    }
    
    /* 2. 표 헤더(제목단) 배경색 및 글자색 */
    [data-testid="stDataEditor"] div[role="columnheader"] {
        background-color: #BBDEFB !important;
        color: #000000 !important;
        font-weight: bold !important;
    }

    /* [박제] 버튼 스타일 통일: 연한 하늘색 */
    div.stButton > button {
        width: 100%; 
        background-color: #E3F2FD !important; 
        color: #000000 !important;
        border: 1px solid #BBDEFB !important; 
        border-radius: 8px;
        padding: 10px; 
        font-weight: bold;
    }
    
    div.stButton > button:hover {
        background-color: #BBDEFB !important;
        border-color: #007AFF !important;
    }

    /* 사이드바 스타일 */
    [data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #EEEEEE !important; }
    
    /* 입력창 디자인 */
    .stTextArea textarea { background-color: #FFFFFF !important; color: #000000 !important; border: 1px solid #E3F2FD !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 로직: 관리번호 및 데이터 관리
def apply_business_logic(df):
    for i in range(len(df)):
        if str(df.loc[i, '진행상태']) not in ['진행중', '견적중', '미정', 'nan']: continue
        val = str(df.loc[i, '관리번호']).strip()
        if '-' in val: df.loc[i, '진행상태'] = '진행중'
        elif (val.isdigit() and len(val) >= 6) or val in ["", "nan"]: df.loc[i, '진행상태'] = '견적중'
    return df

def load_data():
    if not os.path.exists("data.xlsx"):
        df = pd.DataFrame(columns=['ID', '관리번호', '진행상태', '현장명', '사업장주소', '계약금액', '관할서'])
        df.to_excel("data.xlsx", index=False)
    df = pd.read_excel("data.xlsx")
    # ID 자동 부여 (에러 방지용)
    df['ID'] = range(1, len(df) + 1)
    df = apply_business_logic(df)
    try: c_df = pd.read_csv("contacts.csv").dropna(axis=1, how='all')
    except: c_df = pd.DataFrame()
    return df, c_df

site_df, contact_df = load_data()

# 세션 관리
if 'page' not in st.session_state: st.session_state.page = 'dashboard'
if 'selected_site' not in st.session_state: st.session_state.selected_site = None

# --- 사이드바 ---
with st.sidebar:
    st.title("🛠️ 관리 메뉴")
    if st.button("🏠 메인 대시보드"): st.session_state.page = 'dashboard'; st.rerun()
    if st.button("🟡 견적 중 현장"): st.session_state.page = 'list_est'; st.rerun()
    if st.button("🔵 진행 중 현장"): st.session_state.page = 'list_ing'; st.rerun()

# --- [페이지 1: 대시보드] ---
if st.session_state.page == 'dashboard':
    st.markdown("## 🚀 청호방재 실시간 현황")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🔵 진행 중")
        ing_sites = site_df[site_df['진행상태'] == '진행중'].tail(5).iloc[::-1]
        for _, row in ing_sites.iterrows():
            if st.button(f"🏢 {row['현장명']} ({row['관리번호']})", key=f"m_ing_{row['ID']}"):
                st.session_state.selected_site = row['현장명']; st.session_state.page = 'detail'; st.rerun()
    with col2:
        st.markdown("#### 🟡 견적 중")
        est_sites = site_df[site_df['진행상태'] == '견적중'].tail(5).iloc[::-1]
        for _, row in est_sites.iterrows():
            if st.button(f"📄 {row['현장명']} ({row['관리번호']})", key=f"m_est_{row['ID']}"):
                st.session_state.selected_site = row['현장명']; st.session_state.page = 'detail'; st.rerun()
    st.divider()
    calendar_url = "https://calendar.google.com/calendar/embed?src=ko.south_korea%23holiday%40group.v.calendar.google.com"
    st.components.v1.iframe(calendar_url, height=400)

# --- [페이지 2: 리스트 관리 (하늘색 표 적용)] ---
elif st.session_state.page in ['list_ing', 'list_est']:
    title = "진행중" if st.session_state.page == 'list_ing' else "견적중"
    st.markdown(f"### 📂 {title} 데이터베이스")
    
    # 하늘색 배경의 데이터 에디터
    edited_df = st.data_editor(
        site_df.drop(columns=['계약금액']), 
        num_rows="dynamic", use_container_width=True, hide_index=True, key="master_editor"
    )

    if st.button("💾 변경사항 저장"):
        for col in edited_df.columns: site_df[col] = edited_df[col]
        site_df.to_excel("data.xlsx", index=False)
        st.success("저장 완료!"); st.rerun()
    
    target = st.selectbox("📝 이동할 현장 선택", edited_df['현장명'].unique())
    if st.button(f"🚀 {target} 일지 페이지로 이동"):
        st.session_state.selected_site = target; st.session_state.page = 'detail'; st.rerun()

# --- [페이지 3: 상세 페이지] ---
elif st.session_state.page == 'detail':
    if st.button("⬅️ 메인으로"): st.session_state.page = 'dashboard'; st.rerun()
    site_name = st.session_state.selected_site
    site_info = site_df[site_df['현장명'] == site_name].iloc[0]
    st.markdown(f"### 🏢 {site_name}")
    st.write(f"📍 주소: {site_info.get('사업장주소','-')} | 🔢 관리번호: {site_info.get('관리번호','')}")
    st.divider()
    money = st.text_input("금액 수정", value=str(site_info.get('계약금액', '0')))
    st.text_area("📝 업무 일지 기록", height=300)
    if st.button("💾 저장"):
        site_df.loc[site_df['현장명'] == site_name, '계약금액'] = money
        site_df.to_excel("data.xlsx", index=False)
        st.success("저장되었습니다.")
