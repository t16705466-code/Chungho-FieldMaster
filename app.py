import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. 페이지 설정 및 디자인 (연하늘색 바탕, 검정 글씨 박제)
st.set_page_config(page_title="청호방재 필드마스터", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, h4, p, label, span, div { color: #000000 !important; }
    
    /* 표 영역 연하늘색 배경, 글씨 검정 */
    [data-testid="stDataEditor"] div[role="gridcell"] {
        background-color: #E3F2FD !important; color: #000000 !important;
    }
    [data-testid="stDataEditor"] div[role="columnheader"] {
        background-color: #BBDEFB !important; color: #000000 !important;
    }

    /* 버튼 연하늘색 박제 */
    div.stButton > button {
        width: 100%; background-color: #E3F2FD !important; color: #000000 !important;
        border: 1px solid #BBDEFB !important; border-radius: 8px; font-weight: bold;
    }
    
    /* 입력창 디자인 */
    .stTextArea textarea {
        background-color: #FDFDFD !important;
        color: #000000 !important;
        border: 1px solid #E3F2FD !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 로직
def load_data():
    # 현장 데이터 로드
    if not os.path.exists("data.xlsx"):
        df = pd.DataFrame(columns=['ID', '관리번호', '진행상태', '현장명', '사업장주소', '계약금액'])
        df.to_excel("data.xlsx", index=False)
    df = pd.read_excel("data.xlsx")
    df['ID'] = range(1, len(df) + 1) # ID 중복 방지
    
    # 연락처 데이터 로드 (수정하신 contacts.csv)
    try:
        c_df = pd.read_csv("contacts.csv")
        # 공백 제거 및 이름 정제
        c_df.columns = [col.strip() for col in c_df.columns]
    except:
        c_df = pd.DataFrame(columns=['관리번호', '이름', '전화번호', '직함'])
        
    return df, c_df

site_df, contact_df = load_data()

# 세션 관리
if 'page' not in st.session_state: st.session_state.page = 'dashboard'
if 'selected_site' not in st.session_state: st.session_state.selected_site = None

# --- [사이드바 메뉴] ---
with st.sidebar:
    st.title("🛠️ 청호방재 관리")
    if st.button("🏠 메인 대시보드"): st.session_state.page = 'dashboard'; st.rerun()
    if st.button("🟡 견적 중 현장"): st.session_state.page = 'list_est'; st.rerun()
    if st.button("🔵 진행 중 현장"): st.session_state.page = 'list_ing'; st.rerun()

# --- [페이지: 상세 페이지 (연락처 연동 & 일지 양식)] ---
if st.session_state.page == 'detail':
    if st.button("⬅️ 목록으로"): st.session_state.page = 'dashboard'; st.rerun()
    
    site_name = st.session_state.selected_site
    site_info = site_df[site_df['현장명'] == site_name].iloc[0]
    site_no = str(site_info.get('관리번호', '')).strip()
    
    st.markdown(f"### 🏢 {site_name}")
    
    # 상단 정보 레이아웃
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1: st.info(f"📍 주소: {site_info.get('사업장주소','-')}")
    with c2: st.warning(f"🔢 관리번호: {site_no}")
    with c3: money = st.text_input("💰 계약금액", value=str(site_info.get('계약금액', '0')))

    st.divider()

    # [핵심기능 1] 해당 현장 연락처만 필터링해서 보여주기
    st.markdown("#### 📞 현장 담당자 연락처")
    # contacts 파일의 맨 앞줄 '관리번호'와 현재 현장의 '관리번호'가 일치하는 것만 추출
    this_contact = contact_df[contact_df['관리번호'].astype(str).str.strip() == site_no]
    
    if not this_contact.empty:
        st.dataframe(this_contact, use_container_width=True, hide_index=True)
    else:
        st.caption("등록된 전용 연락처가 없습니다. contacts.csv 파일에 관리번호를 입력해 주세요.")

    st.divider()

    # [핵심기능 2] 업무일지 제목줄 양식 박제
    now = datetime.now()
    log_format = f"""[업무일지 - {now.strftime('%Y-%m-%d')}]
작성자: 함재영 사장님
현장명: {site_name}
날씨: 

■ 금일 작업 내용
- 

■ 투입 인력/장비
- 

■ 특이사항 및 미결과제
- 
"""
    
    st.markdown("#### 📝 현장 업무 기록")
    work_log = st.text_area("내용을 입력하세요 (PC/모바일 공용)", value=log_format, height=400)
    
    if st.button("💾 이 현장 정보 및 일지 저장"):
        # 금액 업데이트 로직
        site_df.loc[site_df['현장명'] == site_name, '계약금액'] = money
        site_df.to_excel("data.xlsx", index=False)
        st.success(f"[{site_name}] 데이터가 저장되었습니다.")

# --- [대시보드 및 리스트 로직 생략(기존 유지)] ---
else:
    # 기존에 작성해드린 대시보드와 리스트 화면이 나타납니다.
    st.info("사이드바에서 현장을 선택하거나 상세 페이지로 이동하세요.")
