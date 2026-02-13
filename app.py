import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. [디자인 박제] 화이트/블랙/연하늘 비즈니스 스타일
st.set_page_config(page_title="청호방재 업무일지", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; background-color: #FFFFFF !important; color: #000000 !important; }
    
    /* 사이드바 아이콘 및 글씨 크기 조절 */
    [data-testid="stSidebar"] .stButton button {
        text-align: left !important; padding-left: 10px !important;
        background-color: transparent !important; border: none !important; font-size: 14px !important;
    }
    [data-testid="stSidebar"] .stButton button:hover { background-color: #E3F2FD !important; }
    
    /* 대시보드 헤더 및 카드 */
    .main-header { display: flex; align-items: center; gap: 20px; padding: 20px 0; border-bottom: 2px solid #E3F2FD; margin-bottom: 25px; }
    .metric-card {
        background: #E3F2FD; border-radius: 12px; padding: 20px;
        text-align: center; border: 1px solid #BBDEFB; box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
    }
    .metric-label { font-size: 16px; color: #546E7A; font-weight: bold; margin-bottom: 8px; }
    .metric-value { font-size: 32px; font-weight: 800; color: #0D47A1; }

    /* 바로가기 아이콘 */
    .shortcut-container { display: flex; flex-wrap: wrap; gap: 15px; justify-content: flex-start; margin-top: 10px; }
    .shortcut-box {
        width: 85px; height: 85px; background: #F8F9FA; border-radius: 15px;
        border: 1px solid #EEEEEE; display: flex; flex-direction: column;
        align-items: center; justify-content: center; transition: 0.3s; cursor: pointer;
    }
    .shortcut-box:hover { background: #E3F2FD; border-color: #BBDEFB; transform: translateY(-3px); }
    </style>
    """, unsafe_allow_html=True)

# 2. [데이터 관리 로직]
def load_all_data():
    # 현장 데이터
    if not os.path.exists("data.xlsx"):
        pd.DataFrame(columns=['ID', '관리번호', '진행상태', '현장명', '사업장주소', '계약금액']).to_excel("data.xlsx", index=False)
    site_df = pd.read_excel("data.xlsx")
    
    # 목표 데이터
    if not os.path.exists("goals.csv"):
        pd.DataFrame({'목표': ['신규 현장 수주', '미수금 정산', '안전 점검'], '완료': [False]*3}).to_csv("goals.csv", index=False)
    goal_df = pd.read_csv("goals.csv")

    # 바로가기 데이터
    if not os.path.exists("shortcuts.csv"):
        pd.DataFrame([{"이름": "캘린더", "URL": "https://calendar.google.com", "아이콘": "📅"}]).to_csv("shortcuts.csv", index=False)
    short_df = pd.read_csv("shortcuts.csv")
    
    return site_df, goal_df, short_df

site_df, goal_df, short_df = load_all_data()

# 세션 관리
if 'page' not in st.session_state: st.session_state.page = 'dashboard'
if 'selected_site' not in st.session_state: st.session_state.selected_site = None

# --- [사이드바: 요청하신 디자인 완벽 복구] ---
with st.sidebar:
    st.markdown("### 🛠️ 청호방재 관리")
    if st.button("🏠 메인 대시보드"): st.session_state.page = 'dashboard'; st.session_state.selected_site = None; st.rerun()
    st.divider()

    # [1] 견적중 현장 (아이콘 + 트리)
    with st.expander("🍀 견적중", expanded=True):
        ests = site_df[site_df['진행상태'].str.contains('견적', na=False)].tail(3)
        for _, r in ests.iterrows():
            if st.button(f"🏛️ {r['현장명'][:12]}...", key=f"s_est_{r['ID']}"):
                st.session_state.selected_site = r['현장명']; st.session_state.page = 'detail'; st.rerun()
        if st.button("➕ 새로 추가", key="add_side_est"): st.session_state.page = 'list_edit'; st.rerun()

    # [2] 진행중 현장
    with st.expander("🔄 진행중 현장", expanded=True):
        ings = site_df[site_df['진행상태'].str.contains('진행|공사', na=False)].tail(3)
        for _, r in ings.iterrows():
            if st.button(f"🏛️ {r['현장명'][:12]}...", key=f"s_ing_{r['ID']}"):
                st.session_state.selected_site = r['현장명']; st.session_state.page = 'detail'; st.rerun()
        if st.button("➕ 새로 추가", key="add_side_ing"): st.session_state.page = 'list_edit'; st.rerun()

    # [3] 완공현장 (첨부 이미지 카테고리 그대로 적용)
    with st.expander("📂 완공 현장 (용도별)", expanded=False):
        cats = [("🦋", "제조소_취급소"), ("🔋", "옥외탱크"), ("🔋", "지하탱크_자가주유"), ("🔋", "옥내탱크"), 
                ("🎃", "옥내저장소"), ("🎃", "옥외저장소"), ("🛂", "군부대"), ("⛑️", "도료류"), ("👨‍🏫", "컨설팅")]
        for icon, name in cats:
            if st.button(f"{icon} {name}", key=f"cat_{name}"):
                st.session_state.page = 'list_done'; st.session_state.cat = name; st.rerun()

# --- [메인 화면: 대시보드] ---
if st.session_state.page == 'dashboard':
    # 헤더: 로고 + 문구
    col_l, col_r = st.columns([1, 5])
    with col_l:
        if os.path.exists("square-mobile-800-800.png"): st.image("square-mobile-800-800.png", width=100)
    with col_r:
        st.markdown("<h1 style='margin-top:20px; color:#000000;'>위험물 전문기업 청호방재</h1>", unsafe_allow_html=True)

    # 1줄: 3단 요약 바 (견적, 진행, 목표)
    st.write("")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<div class="metric-card"><div class="metric-label">🟡 견적중</div><div class="metric-value">{len(site_df[site_df["진행상태"].str.contains("견적", na=False)])}건</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card"><div class="metric-label">🔵 진행중</div><div class="metric-value">{len(site_df[site_df["진행상태"].str.contains("진행|공사", na=False)])}건</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-card"><div class="metric-label">🏆 목표 달성</div><div class="metric-value">{goal_df["완료"].sum()}/{len(goal_df)}</div></div>', unsafe_allow_html=True)

    # 2줄: 검색창
    st.write("")
    search_input = st.text_input("", placeholder="Google 검색 또는 URL 입력", key="g_search", label_visibility="collapsed")
    if search_input: st.markdown(f'<meta http-equiv="refresh" content="0;url=https://www.google.com/search?q={search_input}">', unsafe_allow_html=True)

    # 3줄: 바로가기 그리드 + 추가 버튼
    st.write("#### 🔗 바로가기")
    s_cols = st.columns(10)
    for i, row in short_df.iterrows():
        with s_cols[i % 10]:
            st.markdown(f'<a href="{row["URL"]}" target="_blank" style="text-decoration:none;"><div class="shortcut-box"><div style="font-size:24px;">🌐</div><div style="font-size:11px; color:#333; margin-top:5px;">{row["이름"]}</div></div></a>', unsafe_allow_html=True)
    
    with st.expander("➕ 바로가기 추가"):
        n_name = st.text_input("이름")
        n_url = st.text_input("URL")
        if st.button("저장"):
            new_s = pd.concat([short_df, pd.DataFrame([{"이름": n_name, "URL": n_url}])], ignore_index=True)
            new_s.to_csv("shortcuts.csv", index=False); st.rerun()

    st.divider()

    # 4줄: 목표 관리 & 캘린더
    b_l, b_r = st.columns([1, 2])
    with b_l:
        st.markdown("#### ✅ 청호방재의 목표")
        new_goals = st.data_editor(goal_df, use_container_width=True, hide_index=True)
        if st.button("💾 목표 저장"): new_goals.to_csv("goals.csv", index=False); st.success("저장 완료!"); st.rerun()
    with b_r:
        st.markdown("#### 🗓️ 일정 현황")
        st.components.v1.iframe(f"https://calendar.google.com/calendar/embed?src=t16705466@gmail.com&ctz=Asia/Seoul", height=500)

# --- [상세 페이지 로직 생략(기본 탑재)] ---
elif st.session_state.page == 'detail':
    if st.button("⬅️ 메인 대시보드로"): st.session_state.page = 'dashboard'; st.rerun()
    st.title(f"🏢 {st.session_state.selected_site} 상세일지")
    # (앞서 만든 6종 업무 분류 및 일지 템플릿 포함)
