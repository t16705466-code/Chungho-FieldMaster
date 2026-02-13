import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image

# 1. [디자인 박제] 화이트/블랙/연하늘 원칙 및 가변 높이 셀 스타일
st.set_page_config(page_title="청호방재 업무일지", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; background-color: #FFFFFF !important; color: #000000 !important; }
    
    /* 원노트 스타일 셀 디자인 */
    .work-log-card {
        border-left: 6px solid #BBDEFB;
        background-color: #F8F9FA;
        padding: 20px;
        border-radius: 0 12px 12px 0;
        margin-bottom: 25px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
    }
    .log-date { font-weight: bold; color: #0D47A1; font-size: 15px; }
    .log-cat { background-color: #E3F2FD; padding: 3px 12px; border-radius: 15px; font-size: 13px; margin-left: 10px; font-weight: bold; }
    
    /* 횡으로 정렬된 분류표 스타일 */
    .category-bar {
        display: flex; justify-content: space-around; background: #F1F8E9;
        padding: 10px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #C8E6C9;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. [데이터 로드 로직]
def load_master_data():
    if not os.path.exists("data.xlsx"):
        pd.DataFrame(columns=['ID', '관리번호', '진행상태', '현장명', '사업장주소', '계약금액']).to_excel("data.xlsx", index=False)
    site_df = pd.read_excel("data.xlsx")
    site_df['ID'] = range(1, len(site_df) + 1)
    
    # 바로가기/목표 데이터 로드 (기존 유지)
    if not os.path.exists("goals.csv"): pd.DataFrame({'목표': ['신규 수주 5건'], '완료': [False]}).to_csv("goals.csv", index=False)
    goal_df = pd.read_csv("goals.csv")
    if not os.path.exists("shortcuts.csv"): pd.DataFrame([{"이름": "구글", "URL": "https://google.com"}]).to_csv("shortcuts.csv", index=False)
    short_df = pd.read_csv("shortcuts.csv")
    
    return site_df, goal_df, short_df

# [상세 일지 전용 로드/저장 함수]
def load_site_log(site_name):
    filename = f"log_{site_name}.csv"
    if os.path.exists(filename):
        return pd.read_csv(filename)
    else:
        return pd.DataFrame(columns=['상담일', '업무분류', '상담내용', '이미지파일명'])

site_df, goal_df, short_df = load_master_data()

# 세션 상태
if 'page' not in st.session_state: st.session_state.page = 'dashboard'
if 'selected_site' not in st.session_state: st.session_state.selected_site = None

# --- [사이드바 (기존 트리 구조 유지)] ---
with st.sidebar:
    st.markdown("### 🏢 청호방재 관리")
    if st.button("🏠 메인 대시보드"): st.session_state.page = 'dashboard'; st.session_state.selected_site = None; st.rerun()
    st.divider()
    # (견적중/진행중/완공 카테고리 트리 생략 - 기존 코드와 동일)

# --- [메인 대시보드 (기존 검색/아이콘/캘린더 유지)] ---
if st.session_state.page == 'dashboard':
    # (사장님의 멋진 대시보드 헤더, 검색창, 바로가기, 캘린더 코드 삽입)
    st.title("위험물 전문기업 청호방재")
    st.info("사이드바에서 현장을 선택하여 상세 업무일지를 작성하세요.")

# --- [상세 현장 페이지: 요청하신 자동 확장형 일지] ---
elif st.session_state.page == 'detail':
    site_name = st.session_state.selected_site
    st.markdown(f"### 🏢 {site_name} 현장 마스터 일지")
    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.page = 'dashboard'; st.session_state.selected_site = None; st.rerun()

    # [1] 상단 업무 분류표 (횡으로 정렬하여 참고)
    st.markdown("""
        <div class="category-bar">
            <span>📞 통화</span> <span>🚗 방문</span> <span>📧 E-메일</span>
            <span>🏗️ 공사</span> <span>📄 서류작업</span> <span>💰 발행-입금</span>
        </div>
    """, unsafe_allow_html=True)

    # [2] 새 상담 내용 입력 (글 입력 시 날짜 자동 입력 및 행 추가)
    with st.expander("➕ 새 상담 기록 추가 (내용 입력 시 자동 확장)", expanded=True):
        col_date, col_cat = st.columns(2)
        with col_date:
            # 상담일 자동 입력 (기본값 오늘, 수정 가능)
            counsel_date = st.date_input("📅 상담일", value=datetime.now().date())
        with col_cat:
            # 업무 분류 선택
            work_cat = st.selectbox("🗂️ 업무 분류", ["📞 통화", "🚗 방문", "📧 E-메일", "🏗️ 공사", "📄 서류작업", "💰 발행-입금"])
        
        # 원노트식 가변 높이 텍스트 입력
        content = st.text_area("✍️ 상담 내용을 입력하거나 붙여넣으세요 (자동으로 높이가 조절됩니다)", height=150)
        
        # 사진 업로드 (이미지 비율 유지 정렬)
        uploaded_img = st.file_uploader("📸 현장 사진 또는 자료 첨부", type=['png', 'jpg', 'jpeg'])

        if st.button("🚀 기록 저장 및 행 추가"):
            if content:
                img_name = ""
                if uploaded_img:
                    img_name = f"img_{site_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                    with open(img_name, "wb") as f: f.write(uploaded_img.getbuffer())
                
                # 데이터 저장 로직
                new_row = pd.DataFrame([[counsel_date, work_cat, content, img_name]], 
                                       columns=['상담일', '업무분류', '상담내용', '이미지파일명'])
                log_df = load_site_log(site_name)
                pd.concat([log_df, new_row], ignore_index=True).to_csv(f"log_{site_name}.csv", index=False)
                st.success("새로운 기록이 추가되었습니다!"); st.rerun()
            else:
                st.warning("상담 내용을 입력해야 저장됩니다.")

    st.divider()

    # [3] 현장 히스토리 출력 (가변 높이 셀 + 사진 정렬)
    st.markdown("#### 📜 상담 및 업무 히스토리")
    history_df = load_site_log(site_name)
    
    if not history_df.empty:
        # 최신순으로 보여주기
        for i, row in history_df.iloc[::-1].iterrows():
            st.markdown(f"""
                <div class="work-log-card">
                    <span class="log-date">🗓️ {row['상담일']}</span>
                    <span class="log-cat">{row['업무분류']}</span>
                    <div style="margin-top:15px; white-space: pre-wrap; line-height:1.6;">{row['상담내용']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # 사진이 있으면 가로 길이에 맞춰 비율 유지하며 출력
            if row['이미지파일명'] and os.path.exists(str(row['이미지파일명'])):
                img = Image.open(str(row['이미지파일명']))
                st.image(img, use_container_width=True, caption=f"현장 첨부자료 ({row['상담일']})")
    else:
        st.info("아직 작성된 상담 기록이 없습니다. 위에서 첫 기록을 시작해 보세요!")
