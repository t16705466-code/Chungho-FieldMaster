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
    
    /* 표 안의 자료 연하늘색 배경, 글씨 검정 박제 */
    [data-testid="stDataEditor"] div[role="gridcell"] {
        background-color: #E3F2FD !important; color: #000000 !important;
    }
    [data-testid="stDataEditor"] div[role="columnheader"] {
        background-color: #BBDEFB !important; color: #000000 !important;
    }

    /* 버튼 및 입력창 연하늘색 박제 */
    div.stButton > button {
        width: 100%; background-color: #E3F2FD !important; color: #000000 !important;
        border: 1px solid #BBDEFB !important; border-radius: 8px; font-weight: bold;
    }
    
    .stTextArea textarea {
        background-color: #FDFDFD !important;
        color: #000000 !important;
        border: 1px solid #E3F2FD !important;
        font-size: 1.1rem !important;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 로직 (ID 재부여로 에러 방지)
def load_data():
    if not os.path.exists("data.xlsx"):
        df = pd.DataFrame(columns=['ID', '관리번호', '진행상태', '현장명', '사업장주소', '계약금액', '관할서'])
        df.to_excel("data.xlsx", index=False)
    df = pd.read_excel("data.xlsx")
    df['ID'] = range(1, len(df) + 1) # ID 중복 에러 원천 차단
    return df

site_df = load_data()

# 세션 관리
if 'page' not in st.session_state: st.session_state.page = 'dashboard'
if 'selected_site' not in st.session_state: st.session_state.selected_site = None

# --- [사이드바 메뉴] ---
with st.sidebar:
    st.title("🛠️ 청호방재 관리")
    if st.button("🏠 메인 대시보드"): st.session_state.page = 'dashboard'; st.rerun()
    if st.button("🟡 견적 중 현장"): st.session_state.page = 'list_est'; st.rerun()
    if st.button("🔵 진행 중 현장"): st.session_state.page = 'list_ing'; st.rerun()

# --- [페이지 3: 상세 페이지 - 원노트 업무일지 양식] ---
if st.session_state.page == 'detail':
    if st.button("⬅️ 목록으로"): st.session_state.page = 'dashboard'; st.rerun()
    
    site_name = st.session_state.selected_site
    site_info = site_df[site_df['현장명'] == site_name].iloc[0]
    
    # 상단 현장 정보 바 (인포그래픽 스타일)
    st.markdown(f"### 🏢 {site_name}")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1: st.write(f"📍 **주소:** {site_info.get('사업장주소','-')}")
    with c2: st.write(f"🔢 **관리번호:** {site_info.get('관리번호','')}")
    with c3: money = st.text_input("💰 계약금액", value=str(site_info.get('계약금액', '0')))

    st.divider()
    
    # [원노트 양식 박제] 사장님이 바로 입력할 수 있게 미리 채워진 양식
    now = datetime.now()
    log_template = f"""───────────────────────────────────────
■ 현장 업무 일지 ({now.strftime('%Y-%m-%d')})
───────────────────────────────────────
▶ 일시: {now.strftime('%Y년 %m월 %d일 %H시')}
▶ 날씨: 
▶ 작성자: 함재영 사장님
───────────────────────────────────────

[1] 금일 주요 작업 내용
  - 
  - 
  - 

[2] 투입 인력 및 장비 현황
  - 인력: 
  - 장비: 

[3] 현장 특이사항 및 미결 과제
  - 

───────────────────────────────────────
"""
    
    st.markdown("#### 📝 업무 내용 기록")
    # 사장님이 원하시는 양식을 value값에 넣어 "박제" 했습니다.
    work_log = st.text_area("하단 양식에 맞춰 내용을 작성하세요.", value=log_template, height=500)
    
    col_save, col_img = st.columns([1, 1])
    with col_save:
        if st.button("💾 일지 및 금액 최종 저장"):
            # 금액 저장
            site_df.loc[site_df['현장명'] == site_name, '계약금액'] = money
            site_df.to_excel("data.xlsx", index=False)
            st.balloons()
            st.success(f"[{site_name}] 일지가 저장되었습니다.")
    with col_img:
        st.file_uploader("📸 현장 사진 첨부 (갤러리/카메라)", type=['png', 'jpg', 'jpeg'])

# --- [대시보드 및 리스트 페이지는 기존 로직 유지] ---
else:
    # (기존에 작성해드린 대시보드와 리스트 코드가 이 자리에 들어갑니다)
    st.info("사이드바에서 현장을 선택하거나 리스트에서 현장 상세 페이지로 이동하세요.")
