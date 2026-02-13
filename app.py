import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정 (모바일 최적화)
st.set_page_config(page_title="청호방재 필드마스터", layout="wide", initial_sidebar_state="collapsed")

# 2. [박제 1] 디자인 통일 (배경 흰색, 글씨 검정색 고정)
st.markdown("""
    <style>
    /* 전체 배경 흰색 및 기본 글자색 검정 강제 설정 */
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    h1, h2, h3, h4, p, label, span, div { color: #000000 !important; }
    
    /* 버튼 스타일: 호버 시에도 글씨가 안 보이지 않게 확실히 고정 */
    div.stButton > button {
        width: 100%;
        background-color: #F8F9FA !important; /* 아주 연한 회색 배경 */
        color: #000000 !important;           /* 무조건 검정 글씨 */
        border: 1px solid #CCCCCC !important;
        border-radius: 10px;
        padding: 15px;
        text-align: left;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* 버튼 호버/클릭 시 디자인 */
    div.stButton > button:hover, div.stButton > button:active, div.stButton > button:focus {
        border-color: #007AFF !important;
        color: #007AFF !important;           /* 강조색만 파란색으로 변경 */
        background-color: #F0F7FF !important;
    }

    /* 입력창 및 에디터 가시성 확보 */
    .stTextArea textarea, .stTextInput input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #CCCCCC !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. [박제 2] 불변의 관리번호 분류 규칙
def apply_strict_logic(df):
    """
    - '24-01' 등 하이픈(-) 포함 -> 진행중
    - '123456' 등 6자리 숫자 -> 견적중
    - 기타 -> 견적중
    """
    for i in range(len(df)):
        val = str(df.loc[i, '관리번호']).strip()
        if '-' in val:
            df.loc[i, '진행상태'] = '진행중'
        elif (val.isdigit() and len(val) >= 6) or val == "" or val == 'nan':
            df.loc[i, '진행상태'] = '견적중'
        else:
            df.loc[i, '진행상태'] = '견적중'
    return df

# 데이터 로드 및 저장 함수
def load_data():
    if not os.path.exists("data.xlsx"):
        df = pd.DataFrame(columns=['ID', '관리번호', '진행상태', '현장명', '사업장주소', '계약금액'])
        df.to_excel("data.xlsx", index=False)
    df = pd.read_excel("data.xlsx")
    if 'ID' not in df.columns: df.insert(0, 'ID', range(1, len(df) + 1))
    df = apply_strict_logic(df) # 규칙 강제 적용
    try: c_df = pd.read_csv("contacts.csv").dropna(axis=1, how='all')
    except: c_df = pd.DataFrame()
    return df, c_df

site_df, contact_df = load_data()

# 세션 관리
if 'page' not in st.session_state: st.session_state.page = 'dashboard'
if 'selected_site' not in st.session_state: st.session_state.selected_site = None

# --- [메인 화면] ---
if st.session_state.page == 'dashboard':
    st.markdown("## 🚀 청호방재 실시간 현황")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🔵 진행 중")
        ing_sites = site_df[site_df['진행상태'] == '진행중'].iloc[::-1]
        for _, row in ing_sites.head(5).iterrows():
            if st.button(f"🏢 {row['현장명']}\n({row['관리번호']})", key=f"ing_{row['ID']}"):
                st.session_state.selected_site = row['현장명']; st.session_state.page = 'detail'; st.rerun()

    with col2:
        st.markdown("#### 🟡 견적 중")
        est_sites = site_df[site_df['진행상태'] == '견적중'].iloc[::-1]
        for _, row in est_sites.head(5).iterrows():
            if st.button(f"📄 {row['현장명']}\n({row['관리번호']})", key=f"est_{row['ID']}"):
                st.session_state.selected_site = row['현장명']; st.session_state.page = 'detail'; st.rerun()

    st.divider()
    # 구글 캘린더 (사장님 공개 URL로 나중에 교체)
    st.markdown("#### 🗓️ 업무 일정")
    calendar_url = "https://calendar.google.com/calendar/embed?src=ko.south_korea%23holiday%40group.v.calendar.google.com"
    st.components.v1.iframe(calendar_url, height=500)

# --- [상세 페이지] ---
elif st.session_state.page == 'detail':
    if st.button("⬅️ 메인으로 돌아가기"): st.session_state.page = 'dashboard'; st.rerun()
    
    site_name = st.session_state.selected_site
    site_info = site_df[site_df['현장명'] == site_name].iloc[0]
    
    st.markdown(f"### 🏢 {site_name}")
    st.write(f"📍 주소: {site_info.get('사업장주소','-')} | 🔢 번호: {site_info.get
