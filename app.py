import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="청호방재 필드마스터", layout="wide", initial_sidebar_state="collapsed")

# 2. 디자인 고도화 (글자색 검정 고정 & 입력창 개선)
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    h1, h2, h3, h4, p, label { color: #1A1A1A !important; }
    .stTextArea textarea, .stTextInput input {
        background-color: #ffffff !important;
        color: #1A1A1A !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 8px !important;
    }
    div.stButton > button {
        width: 100%; background-color: #ffffff !important;
        color: #1A1A1A !important; border: 1px solid #D1D5DB !important;
        border-radius: 8px; padding: 10px; font-weight: 500;
    }
    .main-title { font-size: 1.5rem; font-weight: bold; color: #007AFF !important; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 데이터 로드 (실시간 반영)
def load_data():
    if not os.path.exists("data.xlsx"):
        df = pd.DataFrame(columns=['현장명', '진행상태', '사업장주소', '관리번호', '관할서'])
        df.to_excel("data.xlsx", index=False)
    
    df = pd.read_excel("data.xlsx")
    df['진행상태'] = df['진행상태'].fillna('미정').astype(str).str.strip()
    c_df = pd.read_csv("contacts.csv").dropna(axis=1, how='all')
    return df, c_df

# 데이터 저장 함수
def save_data(df):
    df.to_excel("data.xlsx", index=False)

site_df, contact_df = load_data()

# 세션 상태 초기화
if 'page' not in st.session_state: st.session_state.page = 'dashboard'
if 'selected_site' not in st.session_state: st.session_state.selected_site = None

# --- [1. 메인 대시보드] ---
if st.session_state.page == 'dashboard':
    st.markdown("<div class='main-title'>🚀 청호방재 필드 마스터</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔵 진행 중인 현장 전체보기"):
            st.session_state.page = 'list_ing'
            st.rerun()
        st.caption("최신순 5건")
        ing_list = site_df[site_df['진행상태'].str.contains('진행', na=False)].tail(5).iloc[::-1]
        for _, row in ing_list.iterrows():
            if st.button(f"🏢 {row['현장명']}", key=f"d_ing_{row['현장명']}"):
                st.session_state.selected_site = row['현장명']; st.session_state.page = 'detail'; st.rerun()

    with col2:
        if st.button("🟡 견적 중인 현장 전체보기"):
            st.session_state.page = 'list_est'
            st.rerun()
        st.caption("최신순 5건")
        est_list = site_df[site_df['진행상태'].str.contains('견적', na=False)].tail(5).iloc[::-1]
        for _, row in est_list.iterrows():
            if st.button(f"📄 {row['현장명']}", key=f"d_est_{row['현장명']}"):
                st.session_state.selected_site = row['현장명']; st.session_state.page = 'detail'; st.rerun()

    st.divider()
    st.markdown("### 🗓️ 업무 일정")
    calendar_url = "https://calendar.google.com/calendar/embed?src=ko.south_korea%23holiday%40group.v.calendar.google.com" 
    st.components.v1.iframe(calendar_url, height=450)

# --- [2. 현장 리스트 및 추가 페이지] ---
elif st.session_state.page in ['list_ing', 'list_est']:
    status_filter = '진행' if st.session_state.page == 'list_ing' else '견적'
    st.markdown(f"### 📋 {status_filter} 중인 현장 목록")
    
    if st.button("⬅️ 메인으로"): st.session_state.page = 'dashboard'; st.rerun()

    # 현장 추가 기능
    with st.expander(f"➕ 새 {status_filter} 현장 등록하기"):
        new_name = st.text_input("현장명")
        new_addr = st.text_input("사업장 주소")
        new_manager = st.text_input("관리번호 (숫자)")
        if st.button("현장 추가 저장"):
            new_row = {'현장명': new_name, '진행상태': f"{status_filter}중", '사업장주소': new_addr, '관리번호': new_manager}
            site_df = pd.concat([site_df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(site_df)
            st.success("새 현장이 등록되었습니다!"); st.rerun()

    st.divider()
    filtered_df = site_df[site_df['진행상태'].str.contains(status_filter, na=False)]
    for _, row in filtered_df.iloc[::-1].iterrows():
        if st.button(f"📍 {row['현장명']} | {row.get('사업장주소','')[:20]}...", key=f"list_{row['현장명']}"):
            st.session_state.selected_site = row['현장명']; st.session_state.page = 'detail'; st.rerun()

# --- [3. 상세 페이지] ---
elif st.session_state.page == 'detail':
    site_name = st.session_state.selected_site
    site_info = site_df[site_df['현장명'] == site_name].iloc[0]
    
    if st.button("⬅️ 뒤로가기"): st.session_state.page = 'dashboard'; st.rerun()
    
    st.markdown(f"## 🏢 {site_name}")
    st.info(f"📍 주소: {site_info.get('사업장주소','-')} | 🔢 관리번호: {site_info.get('관리번호','')}")

    st.markdown("#### 📝 업무 일지 기입")
    st.file_uploader("📸 현장 사진 첨부", type=['jpg', 'jpeg', 'png'])
    st.text_area("작업 내용 및 메모", height=250, placeholder="원노트처럼 자유롭게 기록하세요.")
    if st.button("💾 일지 저장"):
        st.success("저장되었습니다.")
    
    st.divider()
    st.markdown("#### 👥 관련 연락처")
    # 연락처 검색 (현장명이나 관리번호로 검색)
    matched = contact_df[contact_df.apply(lambda x: (str(site_info.get('관리번호','')) in str(x.values)) or (site_name in str(x.values)), axis=1)]
    if not matched.empty:
        for _, p in matched.iterrows():
            st.write(f"👤 **{p.get('First Name','')}** : {p.get('Phone 1 - Value','')}")
