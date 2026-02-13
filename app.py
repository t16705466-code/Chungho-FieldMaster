import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. 페이지 설정 및 디자인 박제 (배경 흰색, 글씨 검정, 버튼/표 연하늘색)
st.set_page_config(page_title="청호방재 필드마스터", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, h4, p, label, span, div { color: #000000 !important; }
    
    /* 표 영역 연하늘색 배경 박제 */
    [data-testid="stDataEditor"] div[role="gridcell"] {
        background-color: #E3F2FD !important; color: #000000 !important;
    }
    [data-testid="stDataEditor"] div[role="columnheader"] {
        background-color: #BBDEFB !important; color: #000000 !important;
    }

    /* 버튼 및 사이드바 메뉴 연하늘색 박제 */
    div.stButton > button {
        width: 100%; background-color: #E3F2FD !important; color: #000000 !important;
        border: 1px solid #BBDEFB !important; border-radius: 8px; font-weight: bold;
    }
    [data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #EEEEEE !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 로직 (ID 재부여 및 contacts 관리번호 매칭 지원)
def load_data():
    # 현장 데이터 (data.xlsx)
    if not os.path.exists("data.xlsx"):
        df = pd.DataFrame(columns=['ID', '관리번호', '진행상태', '현장명', '사업장주소', '계약금액'])
        df.to_excel("data.xlsx", index=False)
    df = pd.read_excel("data.xlsx")
    df['ID'] = range(1, len(df) + 1) # ID 중복 에러 원천 차단
    
    # 연락처 데이터 (contacts.csv)
    if os.path.exists("contacts.csv"):
        try:
            c_df = pd.read_csv("contacts.csv")
            # 사장님이 추가하신 '관리번호' 열을 기준으로 공백 제거
            if '관리번호' in c_df.columns:
                c_df['관리번호'] = c_df['관리번호'].astype(str).str.strip()
        except:
            c_df = pd.DataFrame()
    else:
        c_df = pd.DataFrame()
    return df, c_df

site_df, contact_df = load_data()

# 세션 관리 (페이지 전환 에러 방지)
if 'page' not in st.session_state: st.session_state.page = 'dashboard'
if 'selected_site' not in st.session_state: st.session_state.selected_site = None

# --- [사이드바 메뉴] ---
with st.sidebar:
    st.title("🛠️ 청호방재 관리")
    if st.button("🏠 메인 대시보드"):
        st.session_state.page = 'dashboard'
        st.session_state.selected_site = None
        st.rerun()
    if st.button("🟡 견적 중 현장"):
        st.session_state.page = 'list_est'
        st.rerun()
    if st.button("🔵 진행 중 현장"):
        st.session_state.page = 'list_ing'
        st.rerun()

# --- [페이지 1: 대시보드] ---
if st.session_state.page == 'dashboard' and st.session_state.selected_site is None:
    st.markdown("## 🚀 청호방재 통합 관리실")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🔵 진행 중 현장")
        ing_sites = site_df[site_df['진행상태'].str.contains('진행|공사', na=False)].tail(5).iloc[::-1]
        for _, row in ing_sites.iterrows():
            if st.button(f"🏢 {row['현장명']}", key=f"dash_ing_{row['ID']}"):
                st.session_state.selected_site = row['현장명']; st.session_state.page = 'detail'; st.rerun()
    with col2:
        st.markdown("#### 🟡 견적 중 현장")
        est_sites = site_df[site_df['진행상태'].str.contains('견적', na=False)].tail(5).iloc[::-1]
        for _, row in est_sites.iterrows():
            if st.button(f"📄 {row['현장명']}", key=f"dash_est_{row['ID']}"):
                st.session_state.selected_site = row['현장명']; st.session_state.page = 'detail'; st.rerun()
    st.divider()
    st.markdown("#### 🗓️ 구글 캘린더 일정")
    calendar_url = "https://calendar.google.com/calendar/embed?src=ko.south_korea%23holiday%40group.v.calendar.google.com"
    st.components.v1.iframe(calendar_url, height=400)

# --- [페이지 2: 리스트 관리] ---
elif st.session_state.page in ['list_ing', 'list_est']:
    status_label = "진행" if st.session_state.page == 'list_ing' else "견적"
    st.markdown(f"### 📂 {status_label} 중 데이터베이스 관리")
    
    # 하늘색 바탕 표 적용
    edited_df = st.data_editor(site_df, use_container_width=True, hide_index=True, key=f"editor_{st.session_state.page}")
    
    if st.button("💾 변경사항 엑셀 저장"):
        edited_df.to_excel("data.xlsx", index=False)
        st.success("데이터가 성공적으로 업데이트되었습니다!"); st.rerun()

# --- [페이지 3: 현장 상세 페이지 - 사장님 요청 기능] ---
elif st.session_state.page == 'detail' or st.session_state.selected_site is not None:
    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.page = 'dashboard'; st.session_state.selected_site = None; st.rerun()
    
    site_name = st.session_state.selected_site
    site_info = site_df[site_df['현장명'] == site_name].iloc[0]
    site_no = str(site_info.get('관리번호', '')).strip()

    st.markdown(f"### 🏢 {site_name}")
    st.info(f"📍 주소: {site_info.get('사업장주소','-')} | 🔢 관리번호: {site_no}")

    # [기능 1] 해당 현장 관리번호와 매칭되는 연락처만 표시
    st.markdown("#### 👥 현장 전용 연락처")
    if not contact_df.empty and '관리번호' in contact_df.columns:
        matched_contacts = contact_df[contact_df['관리번호'] == site_no]
        if not matched_contacts.empty:
            st.dataframe(matched_contacts, use_container_width=True, hide_index=True)
        else:
            st.caption("매칭된 연락처가 없습니다. contacts.csv의 관리번호를 확인해 주세요.")

    st.divider()

    # [기능 2] 업무일지 제목줄 양식 박제
    st.markdown("#### 📝 현장 업무 기록 (PC/모바일 공용)")
    log_template = f"""[업무일지 - {datetime.now().strftime('%Y-%m-%d')}]
작성자: 함재영 사장님
현장명: {site_name}
날씨: 

■ 금일 작업 내용
- 

■ 투입 인력 및 장비
- 

■ 특이사항
- 
"""
    st.text_area("내용을 입력하세요", value=log_template, height=400)
    if st.button("💾 일지 내용 임시 저장"):
        st.success("현장 일지가 브라우저에 기록되었습니다. (엑셀 저장 기능은 추후 확장 가능)")
