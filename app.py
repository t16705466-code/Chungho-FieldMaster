import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. [디자인 박제] 불변의 디자인 규칙
st.set_page_config(page_title="청호방재 업무일지", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, h4, p, label, span, div, .stMarkdown { color: #000000 !important; }
    [data-testid="stDataEditor"] div[role="gridcell"] { background-color: #E3F2FD !important; color: #000000 !important; }
    [data-testid="stDataEditor"] div[role="columnheader"] { background-color: #BBDEFB !important; color: #000000 !important; }
    div.stButton > button { width: 100%; background-color: #E3F2FD !important; color: #000000 !important; border: 1px solid #BBDEFB !important; border-radius: 8px; font-weight: bold; }
    [data-testid="stMetric"] { background-color: #F8F9FA !important; border: 1px solid #E3F2FD !important; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. [데이터 로드 및 지능형 매칭 로직]
def load_data():
    # 현장 데이터 로드
    if not os.path.exists("data.xlsx"):
        df = pd.DataFrame(columns=['ID', '관리번호', '진행상태', '현장명', '사업장주소', '계약금액', '완공분류'])
        df.to_excel("data.xlsx", index=False)
    df = pd.read_excel("data.xlsx")
    df['ID'] = range(1, len(df) + 1)
    
    # 연락처 데이터 로드
    if os.path.exists("contacts.csv"):
        try:
            c_df = pd.read_csv("contacts.csv")
            c_df.columns = [c.strip() for c in c_df.columns]
        except: c_df = pd.DataFrame(columns=['관리번호', '이름', '내용'])
    else:
        c_df = pd.DataFrame(columns=['관리번호', '이름', '내용'])
    return df, c_df

# [지능형 매칭 함수] 현장명과 비슷한 연락처를 찾아 관리번호 자동 입력
def sync_contacts_logic(site_df, contact_df):
    updated_count = 0
    # 관리번호가 있는 현장들만 추출
    valid_sites = site_df[site_df['관리번호'].notna() & (site_df['관리번호'].astype(str) != '')]
    
    for _, site_row in valid_sites.iterrows():
        s_name = str(site_row['현장명']).strip()
        m_no = str(site_row['관리번호']).strip()
        
        if len(s_name) < 2: continue # 너무 짧은 이름 방지
        
        # 연락처의 모든 열을 검사하여 현장명이 포함되어 있는지 확인
        for col in contact_df.columns:
            if col == '관리번호': continue
            
            # 관리번호가 비어있는 행들 중에서 검색
            mask = (contact_df[col].astype(str).str.contains(s_name, na=False)) & \
                   (contact_df['관리번호'].isna() | (contact_df['관리번호'].astype(str).isin(['', 'nan', 'None'])))
            
            if mask.any():
                contact_df.loc[mask, '관리번호'] = m_no
                updated_count += mask.sum()
                
    return contact_df, updated_count

site_df, contact_df = load_data()

# 세션 관리
if 'page' not in st.session_state: st.session_state.page = 'dashboard'
if 'selected_site' not in st.session_state: st.session_state.selected_site = None

# --- [사이드바 메뉴] ---
with st.sidebar:
    st.title("🏢 청호방재")
    if st.button("🏠 메인 대시보드"): st.session_state.page = 'dashboard'; st.session_state.selected_site = None; st.rerun()
    st.divider()
    if st.button("🟡 견적 데이터 관리"): st.session_state.page = 'list_est'; st.rerun()
    if st.button("🔵 진행 데이터 관리"): st.session_state.page = 'list_ing'; st.rerun()
    if st.button("📞 연락처 관리/매칭"): st.session_state.page = 'manage_contacts'; st.rerun()

# --- [페이지 1: 대시보드 - 요약 정보] ---
if st.session_state.page == 'dashboard' and st.session_state.selected_site is None:
    st.markdown("## 🚀 청호방재 실시간 현황")
    
    # 사장님 요청: 3단 요약 표
    m1, m2, m3 = st.columns(3)
    with m1:
        count_est = len(site_df[site_df['진행상태'].str.contains('견적', na=False, case=False)])
        st.metric("🟡 견적 대기", f"{count_est}건")
    with m2:
        count_ing = len(site_df[site_df['진행상태'].str.contains('진행|공사', na=False, case=False)])
        st.metric("🔵 공사 진행중", f"{count_ing}건")
    with m3:
        st.metric("📅 오늘 일정", "To-Do 확인")

    st.divider()
    st.markdown("#### 🗓️ 일정 및 할 일 (Calendar)")
    st.components.v1.iframe("https://calendar.google.com/calendar/embed?src=ko.south_korea%23holiday%40group.v.calendar.google.com", height=500)

# --- [페이지 2: 연락처 관리 및 지능형 매칭] ---
elif st.session_state.page == 'manage_contacts':
    st.markdown("### 📞 연락처 지능형 관리")
    st.info("비어있는 연락처의 관리번호를 현장명 기준으로 자동으로 찾아 연결합니다.")
    
    col_sync, col_save = st.columns(2)
    with col_sync:
        if st.button("🔍 연락처-현장번호 자동 매칭 실행"):
            contact_df, count = sync_contacts_logic(site_df, contact_df)
            st.success(f"총 {count}개의 연락처에 관리번호를 새로 입력했습니다!")
            
    with col_save:
        if st.button("💾 매칭 결과 최종 저장"):
            contact_df.to_csv("contacts.csv", index=False)
            st.success("연락처 파일이 업데이트 되었습니다.")

    st.markdown("#### 연락처 목록 (하늘색 영역)")
    st.data_editor(contact_df, use_container_width=True, hide_index=True)

# --- [페이지 3: 상세 페이지] ---
elif st.session_state.page == 'detail':
    site_name = st.session_state.selected_site
    site_info = site_df[site_df['현장명'] == site_name].iloc[0]
    site_no = str(site_info.get('관리번호', '')).strip()

    st.markdown(f"### 🏢 {site_name} (상세)")
    if st.button("⬅️ 메인으로"): st.session_state.page = 'dashboard'; st.session_state.selected_site = None; st.rerun()

    st.markdown("#### 👥 연결된 현장 연락처")
    # 자동 매칭된 연락처가 여기서 보이게 됩니다.
    matched = contact_df[contact_df['관리번호'].astype(str).str.strip() == site_no]
    if not matched.empty:
        st.dataframe(matched, use_container_width=True, hide_index=True)
    else:
        st.caption("매칭된 연락처가 없습니다. '연락처 관리' 메뉴에서 매칭을 실행해 보세요.")

    st.divider()
    st.markdown("#### 📝 업무 일지")
    st.text_area("작업 내용을 입력하세요", height=300)
    st.button("💾 일지 저장")
