import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정 및 디자인 박제
st.set_page_config(page_title="청호방재 필드마스터", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, h4, p, label, span, div { color: #000000 !important; }
    [data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #EEEEEE !important; }
    div.stButton > button {
        width: 100%; background-color: #F1F3F5 !important; color: #000000 !important;
        border: 1px solid #DEE2E6 !important; border-radius: 8px;
        padding: 12px; text-align: left; font-weight: bold;
    }
    div.stButton > button:hover { border-color: #007AFF !important; color: #007AFF !important; }
    /* 입력창 배경 연하게 박제 */
    .stTextArea textarea { background-color: #FFFFFF !important; color: #000000 !important; border: 1px solid #DDDDDD !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 로직: 관리번호 규칙
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
    # [에러수정] ID 강제 재부여 (중복 방지)
    df['ID'] = range(1, len(df) + 1)
    df = apply_business_logic(df)
    try: c_df = pd.read_csv("contacts.csv").dropna(axis=1, how='all')
    except: c_df = pd.DataFrame()
    return df, c_df

site_df, contact_df = load_data()

# 세션 관리
if 'page' not in st.session_state: st.session_state.page = 'dashboard'
if 'selected_site' not in st.session_state: st.session_state.selected_site = None
if 'category_filter' not in st.session_state: st.session_state.category_filter = None

# 3. 사이드바 메뉴
with st.sidebar:
    st.title("🛠️ 관리 메뉴")
    if st.button("🏠 메인 대시보드"): st.session_state.page = 'dashboard'; st.rerun()
    if st.button("🟡 견적 중 현장"): st.session_state.page = 'list_est'; st.rerun()
    if st.button("🔵 진행 중 현장"): st.session_state.page = 'list_ing'; st.rerun()
    st.divider()
    st.markdown("📂 **완공 현장 (용도별)**")
    categories = ["제조소_취급소", "옥내저장소", "옥외저장소", "옥내탱크", "옥외탱크", "지하탱크", "군부대", "도료류", "컨설팅"]
    for cat in categories:
        if st.button(f"▪️ {cat}"):
            st.session_state.page = 'list_done'; st.session_state.category_filter = cat; st.rerun()

# --- [페이지 1: 대시보드] ---
if st.session_state.page == 'dashboard':
    st.markdown("## 🚀 청호방재 실시간 현황")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🔵 진행 중 (최신)")
        ing_sites = site_df[site_df['진행상태'] == '진행중'].tail(5).iloc[::-1]
        for _, row in ing_sites.iterrows():
            if st.button(f"🏢 {row['현장명']}\n({row['관리번호']})", key=f"main_ing_{row['ID']}"):
                st.session_state.selected_site = row['현장명']; st.session_state.page = 'detail'; st.rerun()
    with col2:
        st.markdown("#### 🟡 견적 중 (최신)")
        est_sites = site_df[site_df['진행상태'] == '견적중'].tail(5).iloc[::-1]
        for _, row in est_sites.iterrows():
            if st.button(f"📄 {row['현장명']}\n({row['관리번호']})", key=f"main_est_{row['ID']}"):
                st.session_state.selected_site = row['현장명']; st.session_state.page = 'detail'; st.rerun()
    st.divider()
    st.markdown("#### 🗓️ 업무 일정")
    calendar_url = "https://calendar.google.com/calendar/embed?src=ko.south_korea%23holiday%40group.v.calendar.google.com"
    st.components.v1.iframe(calendar_url, height=450)

# --- [페이지 2: 리스트/데이터베이스 관리] ---
elif st.session_state.page in ['list_ing', 'list_est', 'list_done']:
    title = "진행 중" if st.session_state.page == 'list_ing' else "견적 중" if st.session_state.page == 'list_est' else f"완공: {st.session_state.category_filter}"
    st.markdown(f"### 📂 {title} 현장 데이터베이스")
    
    # 금액 컬럼은 제외하고 보여주기 (상세페이지에서만 확인)
    display_df = site_df.drop(columns=['계약금액']) if '계약금액' in site_df.columns else site_df
    
    edited_df = st.data_editor(
        display_df, 
        num_rows="dynamic", 
        use_container_width=True, 
        hide_index=True, 
        key="master_editor",
        column_config={
            "현장명": st.column_config.TextColumn(width="medium"),
            "사업장주소": st.column_config.TextColumn(width="large"),
            "관리번호": st.column_config.TextColumn(width="small"),
        }
    )
    
    col_save, col_go = st.columns(2)
    with col_save:
        if st.button("💾 변경사항 저장"):
            # 저장 시에는 원본 site_df의 금액 정보를 유지하며 업데이트
            for col in edited_df.columns: site_df[col] = edited_df[col]
            site_df.to_excel("data.xlsx", index=False)
            st.success("저장되었습니다!"); st.rerun()
    
    with col_go:
        selected_name = st.selectbox("상세 페이지로 이동할 현장 선택", edited_df['현장명'].unique())
        if st.button("➡️ 해당 현장 일지 적으러 가기"):
            st.session_state.selected_site = selected_name; st.session_state.page = 'detail'; st.rerun()

# --- [페이지 3: 상세 페이지] ---
elif st.session_state.page == 'detail':
    if st.button("⬅️ 메인으로"): st.session_state.page = 'dashboard'; st.rerun()
    site_name = st.session_state.selected_site
    site_info = site_df[site_df['현장명'] == site_name].iloc[0]
    
    st.markdown(f"### 🏢 {site_name}")
    st.write(f"📍 주소: {site_info.get('사업장주소','-')} | 🔢 번호: {site_info.get('관리번호','')}")
    
    # [박제] 금액 정보는 여기서만 노출 및 수정
    st.markdown("---")
    st.markdown("#### 💰 계약/견적 금액 관리")
    money = st.text_input("현재 설정된 금액", value=str(site_info.get('계약금액', '0')))
    
    st.markdown("#### 📝 업무 일지 기록")
    st.text_area("내용을 입력하세요", height=300)
    if st.button("💾 일지 및 금액 저장"):
        site_df.loc[site_df['현장명'] == site_name, '계약금액'] = money
        site_df.to_excel("data.xlsx", index=False)
        st.success("저장되었습니다.")
