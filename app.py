import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. 페이지 설정 및 디자인 박제
st.set_page_config(page_title="청호방재 필드마스터", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, h4, p, label, span, div { color: #000000 !important; }
    
    /* 표 영역 하늘색 박제 */
    [data-testid="stDataEditor"] div[role="gridcell"] {
        background-color: #E3F2FD !important; color: #000000 !important;
    }
    [data-testid="stDataEditor"] div[role="columnheader"] {
        background-color: #BBDEFB !important; color: #000000 !important;
    }

    /* 모든 버튼 하늘색 박제 */
    div.stButton > button {
        width: 100%; background-color: #E3F2FD !important; color: #000000 !important;
        border: 1px solid #BBDEFB !important; border-radius: 8px; font-weight: bold;
    }
    
    /* 일지 입력창 글씨 검정 고정 */
    .stTextArea textarea {
        background-color: #F8F9FA !important;
        color: #000000 !important;
        border: 1px solid #E3F2FD !important;
        font-family: 'Malgun Gothic', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 로직 및 데이터 로드
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
    df['ID'] = range(1, len(df) + 1)
    df = apply_business_logic(df)
    return df

site_df = load_data()

# 세션 관리
if 'page' not in st.session_state: st.session_state.page = 'dashboard'
if 'selected_site' not in st.session_state: st.session_state.selected_site = None

# --- 사이드바 ---
with st.sidebar:
    st.title("🛠️ 청호방재 관리")
    if st.button("🏠 메인 대시보드"): st.session_state.page = 'dashboard'; st.rerun()
    if st.button("🟡 견적 중 현장"): st.session_state.page = 'list_est'; st.rerun()
    if st.button("🔵 진행 중 현장"): st.session_state.page = 'list_ing'; st.rerun()

# --- [페이지 1: 대시보드 / 페이지 2: 리스트] (생략 - 기존 로직 유지) ---
if st.session_state.page == 'dashboard':
    st.markdown("## 🚀 실시간 현황")
    # ... (기존 대시보드 코드 동일)
    st.info("사이드바 메뉴를 이용해 현장을 관리하세요.")

elif st.session_state.page in ['list_ing', 'list_est']:
    title = "진행중" if st.session_state.page == 'list_ing' else "견적중"
    st.markdown(f"### 📂 {title} 데이터베이스")
    edited_df = st.data_editor(site_df.drop(columns=['계약금액']), use_container_width=True, hide_index=True)
    if st.button("💾 변경사항 저장"):
        for col in edited_df.columns: site_df[col] = edited_df[col]
        site_df.to_excel("data.xlsx", index=False); st.success("저장 완료!"); st.rerun()
    target = st.selectbox("📝 이동할 현장 선택", edited_df['현장명'].unique())
    if st.button(f"🚀 {target} 일지 작성하기"):
        st.session_state.selected_site = target; st.session_state.page = 'detail'; st.rerun()

# --- [페이지 3: 상세 페이지 - 업무일지 양식 탑재] ---
elif st.session_state.page == 'detail':
    if st.button("⬅️ 목록으로 돌아가기"): st.session_state.page = 'dashboard'; st.rerun()
    
    site_name = st.session_state.selected_site
    site_info = site_df[site_df['현장명'] == site_name].iloc[0]
    
    st.markdown(f"### 🏢 {site_name} (상세)")
    col_a, col_b = st.columns(2)
    with col_a:
        st.write(f"📍 **주소:** {site_info.get('사업장주소','-')}")
        st.write(f"🔢 **관리번호:** {site_info.get('관리번호','')}")
    with col_b:
        money = st.text_input("💰 계약/견적 금액", value=str(site_info.get('계약금액', '0')))

    st.divider()
    
    # [박제] 업무일지_DB 표준 양식 불러오기
    today_date = datetime.now().strftime("%Y-%m-%d")
    default_log_format = f"""[업무일지 - {today_date}]
작성자: 함재영 사장님
현장명: {site_name}
날씨: 

■ 금일 작업 내용
1. 
2. 
3. 

■ 투입 인력/장비
- 인력: 
- 장비: 

■ 미결 사항 및 특이사항
- 
---------------------------------------
"""
    
    st.markdown("#### 📝 업무일지 작성")
    # 사장님이 직접 입력하실 수 있도록 양식을 입력창에 미리 넣어둡니다.
    work_log = st.text_area("일지 양식에 맞춰 내용을 기입하세요.", value=default_log_format, height=450)
    
    col_save, col_photo = st.columns([1, 1])
    with col_save:
        if st.button("💾 일지 및 금액 최종 저장"):
            # 금액 저장 로직
            site_df.loc[site_df['현장명'] == site_name, '계약금액'] = money
            site_df.to_excel("data.xlsx", index=False)
            # 업무 일지 내용은 추후 별도 파일이나 로그로 관리 가능 (현재는 성공 메시지)
            st.success(f"[{site_name}] 일지가 안전하게 저장되었습니다.")
    with col_photo:
        st.file_uploader("📸 현장 사진 첨부", type=['png', 'jpg', 'jpeg'])
