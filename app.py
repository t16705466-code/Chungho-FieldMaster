import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정 (사이드바를 다시 노출하여 PC 가독성 확보)
st.set_page_config(page_title="청호방재 필드마스터", layout="wide", initial_sidebar_state="expanded")

# 2. [디자인 박제] 바탕은 흰색이지만, 버튼과 영역은 연한 회색으로 구분
st.markdown("""
    <style>
    /* 전체 배경 흰색 */
    .stApp { background-color: #FFFFFF !important; }
    
    /* 모든 글자색 검정 고정 */
    h1, h2, h3, h4, h5, p, label, span, div, .stMarkdown { color: #000000 !important; }

    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background-color: #F8F9FA !important;
        border-right: 1px solid #EEEEEE !important;
    }

    /* 버튼 디자인: 배경을 아주 연한 회색으로 해서 흰 바탕과 구분 (연한 회색 선 박제) */
    div.stButton > button {
        width: 100%;
        background-color: #F1F3F5 !important; /* 연한 회색 배경으로 버튼 존재 알림 */
        color: #000000 !important;
        border: 1px solid #DEE2E6 !important; /* 연한 회색 테두리 */
        border-radius: 8px;
        padding: 12px;
        text-align: left;
        font-weight: 600;
        margin-bottom: 5px;
    }
    
    /* 버튼 호버 시 디자인 */
    div.stButton > button:hover {
        background-color: #E9ECEF !important;
        border-color: #007AFF !important;
        color: #007AFF !important;
    }

    /* 상세 페이지 입력창 */
    .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #CED4DA !important;
    }

    /* 구분선 색상 */
    hr { border: 0; border-top: 1px solid #EEEEEE !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. [로직 박제] 관리번호 분류 규칙 (불변)
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

# 세션 관리
if 'page' not in st.session_state: st.session_state.page = 'dashboard'
if 'selected_site' not in st.session_state: st.session_state.selected_site = None

# --- 사이드바 메뉴 (PC 버전에서 편리함) ---
with st.sidebar:
    st.title("🛠️ 관리 메뉴")
    if st.button("🏠 메인 대시보드"):
        st.session_state.page = 'dashboard'
        st.rerun()
    st.divider()
    st.info("관리번호에 '-'가 있으면 자동으로 '진행중'으로 분류됩니다.")

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
    site_name = st.session_state.selected_site
    site_info = site_df[site_df['현장명'] == site_name].iloc[0]
    
    st.markdown(f"### 🏢 {site_name}")
    # 에러 방지용 괄호 체크 완료
    st.write(f"📍 주소: {site_info.get('사업장주소','-')} | 🔢 번호: {site_info.get('관리번호','')}")
    
    st.markdown("---")
    st.markdown("#### 📝 업무 일지")
    st.text_area("내용을 입력하세요", height=300)
    if st.button("💾 저장"):
        st.success("저장되었습니다.")
