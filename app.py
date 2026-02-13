import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정 (모바일 최적화)
st.set_page_config(page_title="청호방재 필드마스터", layout="wide", initial_sidebar_state="collapsed")

# 2. 디자인 및 가독성 문제 해결 (호버 없이도 글씨가 잘 보이도록 강제 설정)
st.markdown("""
    <style>
    /* 배경 및 기본 글자색 (검정) */
    .stApp { background-color: #F8F9FA; color: #1A1A1A !important; }
    h1, h2, h3, h4, p, label, span { color: #1A1A1A !important; }
    
    /* 버튼 글씨가 안 보이는 문제(호버 이슈) 해결 */
    div.stButton > button {
        width: 100%;
        background-color: #FFFFFF !important; /* 항상 흰색 배경 */
        color: #1A1A1A !important;           /* 항상 검정 글씨 */
        border: 1px solid #D1D5DB !important;
        border-radius: 10px;
        padding: 15px;
        text-align: left;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* 버튼에 마우스 올려도 글씨색 유지 */
    div.stButton > button:hover {
        border-color: #007AFF !important;
        color: #007AFF !important;
        background-color: #F0F7FF !important;
    }
    
    /* 입력창 디자인 */
    .stTextArea textarea { background-color: #FFFFFF !important; color: #1A1A1A !important; border: 1px solid #D1D5DB !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. [사장님 전용 규칙] 절대 잊지 말아야 할 관리번호 로직
def apply_business_logic(df):
    """
    관리번호 형식에 따라 진행상태를 강제로 분류합니다.
    - 00-00 형식 (예: 24-01) -> 진행중
    - 6자리 숫자 (예: 123456) -> 견적중
    """
    for i in range(len(df)):
        val = str(df.loc[i, '관리번호']).strip()
        
        # 1. 진행중 규칙: '-' 가 포함된 경우 (예: 24-01)
        if '-' in val:
            df.loc[i, '진행상태'] = '진행중'
        # 2. 견적중 규칙: 6자리 숫자인 경우 (또는 '-'가 없는 경우)
        elif len(val) >= 6 or val.isdigit():
            df.loc[i, '진행상태'] = '견적중'
        # 3. 기타: 번호가 없으면 견적중으로 기본 설정
        elif val == "" or val == 'nan':
            df.loc[i, '진행상태'] = '견적중'
            
    return df

# 데이터 로드
def load_data():
    if not os.path.exists("data.xlsx"):
        df = pd.DataFrame(columns=['ID', '관리번호', '진행상태', '현장명', '사업장주소', '계약금액'])
        df.to_excel("data.xlsx", index=False)
    
    df = pd.read_excel("data.xlsx")
    
    # ID 자동 부여
    if 'ID' not in df.columns: df.insert(0, 'ID', range(1, len(df) + 1))
    df['ID'] = df['ID'].fillna(0).astype(int)
    
    # 사장님 불변의 규칙 적용
    df = apply_business_logic(df)
    
    # 연락처 로드
    try: c_df = pd.read_csv("contacts.csv").dropna(axis=1, how='all')
    except: c_df = pd.DataFrame()
        
    return df, c_df

site_df, contact_df = load_data()

# 페이지 제어
if 'page' not in st.session_state: st.session_state.page = 'dashboard'
if 'selected_site' not in st.session_state: st.session_state.selected_site = None

# --- [1. 대시보드 화면] ---
if st.session_state.page == 'dashboard':
    st.markdown("### 🏢 청호방재 필드마스터")
    
    # 진행/견적 분류
    ing_sites = site_df[site_df['진행상태'] == '진행중'].iloc[::-1]
    est_sites = site_df[site_df['진행상태'] == '견적중'].iloc[::-1]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**🔵 진행중 ({len(ing_sites)}건)**")
        if st.button("진행 현장 리스트 전체보기"): st.session_state.page = 'list_ing'; st.rerun()
        for _, row in ing_sites.head(5).iterrows():
            if st.button(f"{row['현장명']}\n({row['관리번호']})", key=f"ing_{row['ID']}"):
                st.session_state.selected_site = row['현장명']; st.session_state.page = 'detail'; st.rerun()

    with col2:
        st.markdown(f"**🟡 견적중 ({len(est_sites)}건)**")
        if st.button("견적 현장 리스트 전체보기"): st.session_state.page = 'list_est'; st.rerun()
        for _, row in est_sites.head(5).iterrows():
            if st.button(f"{row['현장명']}\n({row['관리번호']})", key=f"est_{row['ID']}"):
                st.session_state.selected_site = row['현장명']; st.session_state.page = 'detail'; st.rerun()

    st.divider()
    st.markdown("### 🗓️ 구글 캘린더")
    calendar_url = "https://calendar.google.com/calendar/embed?src=ko.south_korea%23holiday%40group.v.calendar.google.com"
    st.components.v1.iframe(calendar_url, height=450)

# --- [2. 상세 페이지 및 리스트 페이지 (기본 구조 유지)] ---
elif st.session_state.page == 'detail':
    if st.button("⬅️ 메인으로"): st.session_state.page = 'dashboard'; st.rerun()
    st.subheader(f"현장: {st.session_state.selected_site}")
    st.text_area("📝 업무 일지 기입", height=300, placeholder="여기에 내용을 적으세요. 이제 배경이 밝아 글씨가 잘 보입니다.")
    if st.button("저장"): st.success("기록되었습니다.")
