import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정 (모바일 최적화 & 사이드바 제거)
st.set_page_config(page_title="청호방재 필드마스터", layout="wide", initial_sidebar_state="collapsed")

# 2. 고급스러운 노션 스타일 CSS (글자색 검정 고정)
st.markdown("""
    <style>
    /* 전체 배경 및 글자색 설정 */
    .stApp { background-color: #F7F9FB; color: #1A1A1A; }
    h1, h2, h3, h4, p, span, label { color: #1A1A1A !important; }
    
    /* 사이드바 숨김 */
    [data-testid="stSidebarNav"] {display: none;}
    
    /* 카드 스타일 (인포그래픽 느낌) */
    .info-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #007AFF;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .contact-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #E0E0E0;
        margin-bottom: 10px;
    }
    
    /* 버튼 스타일 */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: #007AFF;
        color: white !important;
        font-weight: bold;
        height: 3.5em;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# 데이터 불러오기
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
    st.markdown("### 🏢 청호방재 현장관리 시스템")
    
    # 3. 현장 선택
    selected_site = st.selectbox("조회할 현장을 선택하세요", site_df['현장명'].unique())
    site_info = site_df[site_df['현장명'] == selected_site].iloc[0]
    site_no = str(site_info.get('관리번호', ''))

    # --- 현장 상세 인포그래픽 ---
    st.markdown(f"""
    <div class="info-card">
        <span style="color: #666; font-size: 0.9em;">현장 상세 정보</span>
        <h2 style="margin: 5px 0;">{selected_site}</h2>
        <p style="margin: 0;">📍 <b>주소:</b> {site_info.get('사업장주소', '-')}</p>
        <p style="margin: 0;">🔢 <b>관리번호:</b> {site_no} | ⚖️ <b>관할:</b> {site_info.get('관할서', '-')}</p>
    </div>
    """, unsafe_allow_html=True)

    # 4. 업무 일지 섹션 (매번 기입)
    st.markdown("### 📝 오늘의 업무 일지")
    with st.container():
        # 사진 업로드 (웹캠 대신 파일 선택)
        uploaded_file = st.file_uploader("📸 현장 사진 첨부 (갤러리/파일)", type=['jpg', 'png', 'jpeg'])
        if uploaded_file:
            st.image(uploaded_file, caption="업로드된 사진", use_container_width=True)
        
        # 자유 기입 노트
        log_text = st.text_area("작업 내용 및 특이사항", height=150, placeholder="여기에 오늘 작업한 내용을 자유롭게 적으세요...")
        
        if st.button("💾 업무 일지 저장하기"):
            st.balloons()
            st.success(f"[{selected_site}] 일지가 정상적으로 기록되었습니다.")

    st.divider()

    # 5. 관계자 연락처 (매칭 로직)
    st.markdown("### 👥 현장 관계자 연락처")
    def find_matches(row):
        combined = " ".join(row.astype(str))
        return (site_no in combined) or (selected_site in combined)

    matched = contact_df[contact_df.apply(find_matches, axis=1)]
    
    if not matched.empty:
        for _, p in matched.iterrows():
            st.markdown(f"""
            <div class="contact-card">
                <b>👤 {p.get('First Name', '이름없음')}</b> | {p.get('Organization Title', '직함없음')}<br>
                📞 <a href="tel:{p.get('Phone 1 - Value', '')}" style="color: #007AFF; text-decoration: none;">{p.get('Phone 1 - Value', '번호없음')}</a><br>
                <small style="color: #666;">🏢 {p.get('Organization Name', '-')}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("매칭된 연락처가 없습니다.")

    st.divider()

    # 6. 할 일 리스트 & 캘린더 느낌의 섹션
    st.markdown("### ✅ 오늘 할 일")
    col1, col2 = st.columns(2)
    with col1:
        st.checkbox("현장 안전 점검")
        st.checkbox("점검 결과 보고서 작성")
    with col2:
        st.checkbox("소방시설 작동 확인")
        st.checkbox("관계자 서명 날인")

    # 간단 캘린더 보기 (오늘 날짜 강조)
    st.markdown(f"🗓️ **오늘의 일정:** {datetime.now().strftime('%Y년 %m월 %d일')}")

else:
    st.error("장부 파일(data.xlsx)을 찾을 수 없습니다.")
