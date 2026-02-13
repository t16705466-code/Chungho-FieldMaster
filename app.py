import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. [디자인 박제] 고품격 비즈니스 대시보드 스타일
st.set_page_config(page_title="청호방재 업무일지", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
    html, body, [class*="css"]  { font-family: 'Noto Sans KR', sans-serif; background-color: #FFFFFF !important; color: #000000 !important; }
    
    /* 헤더 디자인 */
    .main-header { display: flex; align-items: center; justify-content: center; padding: 20px 0; border-bottom: 2px solid #E3F2FD; margin-bottom: 30px; }
    .main-header img { margin-right: 20px; border-radius: 10px; }
    .main-header h1 { font-size: 32px; font-weight: 700; color: #0D47A1; margin: 0; }

    /* 카드 디자인 (멋있게!) */
    .metric-card {
        background: #E3F2FD; border-radius: 15px; padding: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #BBDEFB;
        text-align: center; transition: transform 0.3s;
    }
    .metric-card:hover { transform: translateY(-5px); }
    .metric-label { font-size: 18px; color: #546E7A; margin-bottom: 10px; font-weight: bold; }
    .metric-value { font-size: 36px; font-weight: 800; color: #0D47A1; }

    /* 구글형 검색창 */
    .search-container { max-width: 800px; margin: 0 auto 40px; }
    .stTextInput > div > div > input {
        border-radius: 30px !important; padding: 15px 25px !important;
        border: 1px solid #dfe1e5 !important; box-shadow: 0 1px 6px rgba(32,33,36,0.28) !important;
    }

    /* 바로가기 아이콘 */
    .shortcut-btn {
        display: inline-block; width: 90px; height: 90px; margin: 10px;
        background: #F8F9FA; border-radius: 12px; border: 1px solid #EEEEEE;
        text-align: center; vertical-align: top; text-decoration: none; transition: 0.3s;
    }
    .shortcut-btn:hover { background: #E3F2FD; border-color: #BBDEFB; }
    .shortcut-icon { font-size: 30px; padding-top: 15px; }
    .shortcut-name { font-size: 12px; color: #37474F; padding: 5px; overflow: hidden; }

    /* 체크리스트 스타일 */
    .todo-item { background: #FFFFFF; border: 1px solid #E3F2FD; padding: 10px; border-radius: 8px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. [데이터 관리 로직]
def load_all_data():
    # 현장 데이터
    if not os.path.exists("data.xlsx"):
        df = pd.DataFrame(columns=['ID', '관리번호', '진행상태', '현장명', '사업장주소', '계약금액'])
        df.to_excel("data.xlsx", index=False)
    site_df = pd.read_excel("data.xlsx")
    
    # 목표(To-Do) 데이터
    if not os.path.exists("goals.csv"):
        goal_df = pd.DataFrame({'목표': ['신규 현장 수주', '미수금 정산', '안전 점검 실시', '장비 점검', '보고서 작성'], '완료': [False]*5})
        goal_df.to_csv("goals.csv", index=False)
    goal_df = pd.read_csv("goals.csv")

    # 바로가기 데이터 (초기값)
    if not os.path.exists("shortcuts.csv"):
        short_df = pd.DataFrame([
            {"이름": "캘린더", "URL": "https://calendar.google.com", "아이콘": "📅"},
            {"이름": "주소록", "URL": "https://contacts.google.com", "아이콘": "👤"},
            {"이름": "지메일", "URL": "https://mail.google.com", "icon": "✉️"},
            {"이름": "구글광고", "URL": "https://ads.google.com", "icon": "📈"},
            {"이름": "네이버", "URL": "https://www.naver.com", "icon": "N"}
        ])
        short_df.to_csv("shortcuts.csv", index=False)
    short_df = pd.read_csv("shortcuts.csv")
    
    return site_df, goal_df, short_df

site_df, goal_df, short_df = load_all_data()

# --- [상단 헤더: 로고 + 타이틀] ---
# square-mobile-800-800.png 파일이 깃허브 같은 폴더에 있어야 합니다.
col_logo, col_title = st.columns([1, 4])
with col_title:
    st.markdown(f"""
        <div class="main-header">
            <h1 style='color: #000000;'>위험물 전문기업 청호방재</h1>
        </div>
    """, unsafe_allow_html=True)
with col_logo:
    if os.path.exists("square-mobile-800-800.png"):
        st.image("square-mobile-800-800.png", width=120)

# --- [1단계: 3단 요약 바 (오류 수정 및 목표 연동)] ---
st.write("")
m1, m2, m3 = st.columns(3)
with m1:
    # 견적중 필터링 (6자리 숫자 혹은 '견적' 포함)
    c_est = len(site_df[site_df['진행상태'].str.contains('견적', na=False, case=False)])
    st.markdown(f'<div class="metric-card"><div class="metric-label">🟡 견적 대기</div><div class="metric-value">{c_est}건</div></div>', unsafe_allow_html=True)
with m2:
    # 진행중 필터링 (하이픈 포함 혹은 '진행/공사' 포함)
    c_ing = len(site_df[site_df['진행상태'].str.contains('진행|공사', na=False, case=False)])
    st.markdown(f'<div class="metric-card"><div class="metric-label">🔵 공사 진행중</div><div class="metric-value">{c_ing}건</div></div>', unsafe_allow_html=True)
with m3:
    # 목표 달성률 계산
    done_count = goal_df['완료'].sum()
    st.markdown(f'<div class="metric-card"><div class="metric-label">🏆 청호방재 목표</div><div class="metric-value">{done_count}/{len(goal_df)}</div></div>', unsafe_allow_html=True)

# --- [2단계: 검색창] ---
st.write("")
with st.container():
    search_q = st.text_input("", placeholder="Google 검색 또는 URL 입력", key="main_search", label_visibility="collapsed")
    if search_q:
        st.markdown(f'<meta http-equiv="refresh" content="0;url=https://www.google.com/search?q={search_q}">', unsafe_allow_html=True)

# --- [3단계: 바로가기 및 추가 버튼] ---
st.write("#### 🔗 바로가기")
short_cols = st.columns(10)
for i, row in short_df.iterrows():
    with short_cols[i % 10]:
        st.markdown(f"""
            <a href="{row['URL']}" target="_blank" class="shortcut-btn">
                <div class="shortcut-icon">🌐</div>
                <div class="shortcut-name">{row['이름']}</div>
            </a>
        """, unsafe_allow_html=True)

# 바로가기 추가 기능 (Expander로 깔끔하게 처리)
with st.expander("➕ 바로가기 추가 및 관리"):
    new_name = st.text_input("사이트 이름")
    new_url = st.text_input("URL 주소 (https:// 포함)")
    if st.button("추가하기"):
        new_row = pd.DataFrame([{"이름": new_name, "URL": new_url}])
        short_df = pd.concat([short_df, new_row], ignore_index=True)
        short_df.to_csv("shortcuts.csv", index=False)
        st.success("추가되었습니다!"); st.rerun()

st.divider()

# --- [4단계: 하단 2단 구성 (목표 관리 vs 캘린더)] ---
col_todo, col_cal = st.columns([1, 2])

with col_todo:
    st.markdown("#### ✅ 청호방재의 목표")
    # 목표 수정 및 체크 기능
    edited_goals = st.data_editor(goal_df, use_container_width=True, hide_index=True)
    if st.button("💾 목표 상태 저장"):
        edited_goals.to_csv("goals.csv", index=False)
        st.success("목표가 업데이트되었습니다!"); st.rerun()

with col_cal:
    st.markdown("#### 🗓️ 실시간 일정 현황")
    cal_id = "t16705466@gmail.com"
    cal_url = f"https://calendar.google.com/calendar/embed?src={cal_id}&ctz=Asia/Seoul"
    st.components.v1.iframe(cal_url, height=500)

# --- [사이드바: 사라진 기능 복구 및 상세 페이지 이동용] ---
with st.sidebar:
    st.title("📂 현장 상세 관리")
    st.info("메인 대시보드에서 숫자를 클릭하거나 아래 목록을 선택하세요.")
    selected = st.selectbox("관리할 현장을 선택하세요", site_df['현장명'].tolist())
    if st.button("📝 선택 현장 상세일지 보기"):
        st.session_state.selected_site = selected
        st.session_state.page = 'detail'; st.rerun()
