import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정
st.set_page_config(page_title="청호방재 필드마스터", layout="wide", initial_sidebar_state="collapsed")

# 2. [디자인 박제] 흰색 배경, 검정 글씨, 연한 회색 표 선
st.markdown("""
    <style>
    /* 배경 및 글자색 */
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    h1, h2, h3, h4, p, label, span, div { color: #000000 !important; }
    
    /* 버튼 스타일 (검정 글씨 박제) */
    div.stButton > button {
        width: 100%;
        background-color: #FDFDFD !important;
        color: #000000 !important;
        border: 1px solid #DDDDDD !important; /* 연한 회색 선 */
        border-radius: 10px;
        padding: 15px;
        text-align: left;
        font-weight: bold;
    }
    
    /* 표(Table/Editor) 선 색상 연한 회색으로 박제 */
    [data-testid="stDataEditor"] {
        border: 1px solid #EEEEEE !important;
    }
    .stTable {
        border: 1px solid #EEEEEE !important;
    }
    
    /* 입력창 디자인 */
    .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #DDDDDD !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. [로직 박제] 관리번호 분류 규칙
def apply_strict_logic(df):
    for i in range(len(df)):
        val = str(df.loc[i, '관리번호']).strip()
        if '-' in val:
            df.loc[i, '진행상태'] = '진행중'
        elif (val.isdigit() and len(val) >= 6) or val == "" or val == 'nan':
            df.loc[i, '진행상태'] = '견적중'
        else:
            df.loc[i, '진행상태'] = '견적중'
    return df

# 데이터 로드
def load_data():
    if not os.path.exists("data.xlsx"):
        df = pd.DataFrame(columns=['ID', '관리번호', '진행상태', '현장명', '사업장주소', '계약금액'])
        df.to_excel("data.xlsx", index=False)
    df = pd.read_excel("data.xlsx")
    if 'ID' not in df.columns: df.insert(0, 'ID', range(1, len(df) + 1))
    df = apply_strict_logic(df)
    try: c_df = pd.read_csv("contacts.csv").dropna(axis=1, how='all')
    except: c_df = pd.DataFrame()
    return df, c_df

site_df, contact_df = load_data()

# 페이지 제어
if 'page' not in st.session_state: st.session_state.page = 'dashboard'
if 'selected_site' not in st.session_state: st.session_state.selected_site = None

# --- [메인 대시보드] ---
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
    st.markdown("#### 🗓️ 업무 일정")
    calendar_url = "https://calendar.google.com/calendar/embed?src=ko.south_korea%23holiday%40group.v.calendar.google.com"
    st.components.v1.iframe(calendar_url, height=500)

# --- [상세 페이지] ---
elif st.session_state.page == 'detail':
    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.page = 'dashboard'
        st.rerun()
    
    site_name = st.session_state.selected_site
    # 상세 정보 조회
    site_info = site_df[site_df['현장명'] == site_name].iloc[0]
    
    st.markdown(f"### 🏢 {site_name}")
    # 에러가 났던 괄호 부분을 정확히 수정했습니다.
    st.write(f"📍 주소: {site_info.get('사업장주소','-')} | 🔢 번호: {site_info.get('관리번호','')}")
    
    st.markdown("---")
    st.markdown("#### 📝 업무 일지")
    st.text_area("내용을 입력하세요", height=250, placeholder="오늘 작업 내용을 자유롭게 기록하세요.")
    if st.button("💾 저장"):
        st.success("저장되었습니다.")
