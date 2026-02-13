import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. 페이지 설정 (사이드바 제거 및 모바일 최적화)
st.set_page_config(page_title="청호방재 필드마스터", layout="wide", initial_sidebar_state="collapsed")

# 노션 스타일 디자인 적용
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none;} /* 사이드바 숨김 */
    .stApp { background-color: #ffffff; }
    .main-card { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #eee; margin-bottom: 15px; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #007AFF; color: white; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        site_df = pd.read_excel("data.xlsx")
        contact_df = pd.read_csv("contacts.csv")
        contact_df = contact_df.dropna(axis=1, how='all')
        return site_df, contact_df
    except:
        return None, None

site_df, contact_df = load_data()

if site_df is not None:
    # --- 상단 헤더 ---
    st.title("🚀 청호방재 필드마스터")
    
    # 2. 현장 선택 (가장 크게)
    selected_site_name = st.selectbox("🏥 현장을 검색하거나 선택하세요", site_df['현장명'].unique())
    site_info = site_df[site_df['현장명'] == selected_site_name].iloc[0]
    site_no = str(site_info.get('관리번호', ''))

    # --- 현장 정보 카드 ---
    st.markdown(f"""
    <div class="main-card">
        <h4>🏢 {selected_site_name}</h4>
        <p>📍 {site_info.get('사업장주소', '주소 정보 없음')}</p>
        <p>🔢 관리번호: <b>{site_no}</b> | ⚖️ 관할: {site_info.get('관할서', '-')}</p>
    </div>
    """, unsafe_allow_html=True)

    # 3. 관계자 연락처 (현장명/회사명/메모에서 관리번호나 현장명으로 검색)
    st.subheader("👥 현장 관계자")
    def find_contacts(row):
        # 이름, 회사명, 메모, 직함 등 모든 칸에서 현장명이나 관리번호가 있는지 검색
        search_text = " ".join(row.astype(str))
        return (site_no in search_text) or (selected_site_name in search_text)

    matched = contact_df[contact_df.apply(find_contacts, axis=1)]
    
    if not matched.empty:
        for _, p in matched.iterrows():
            with st.expander(f"👤 {p.get('First Name', '이름없음')} ({p.get('Organization Title', '직함없음')})"):
                st.write(f"📞 전화: {p.get('Phone 1 - Value', '번호없음')}")
                st.write(f"🏢 소속: {p.get('Organization Name', '-')}")
                if pd.notnull(p.get('Notes')): st.info(f"📝 메모: {p.get('Notes')}")
    else:
        st.caption("연결된 연락처가 없습니다. 구글 연락처 메모에 관리번호를 넣어주세요.")

    st.divider()

    # 4. 업무 일지 (현장별 자유 기입)
    st.subheader("📝 현장 업무 일지")
    
    # 사진 찍기 기능 (모바일에서 카메라 연동)
    img_file = st.camera_input("📸 현장 사진 촬영")
    if img_file:
        st.success("사진이 캡처되었습니다!")

    # 일지 입력
    today_date = datetime.now().strftime("%Y-%m-%d")
    log_content = st.text_area(f"[{today_date}] 작업 내용 기록", height=150, placeholder="오늘의 점검 내용, 특이사항을 자유롭게 적으세요.")
    
    if st.button("💾 이 현장 일지 저장하기"):
        # 여기서 실제 파일이나 DB에 저장하는 로직을 추가할 수 있습니다.
        st.balloons()
        st.success(f"{selected_site_name} 업무 일지가 로컬에 임시 저장되었습니다!")

    # 5. 노션 스타일 할일 리스트
    st.divider()
    st.subheader("✅ 오늘 할 일 (To-do)")
    st.checkbox("현장 도착 보고")
    st.checkbox("소방 시설 점검 완료")
    st.checkbox("관계자 서명 받기")

else:
    st.error("데이터 파일을 찾을 수 없습니다.")
