import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image

# 1. [디자인 박제] 화이트/연하늘 비즈니스 스타일
st.set_page_config(page_title="청호방재 업무일지", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; background-color: #FFFFFF !important; color: #000000 !important; }import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. [디자인 박제] 화이트/블랙/연하늘 비즈니스 스타일 (다크모드 완벽 차단)
st.set_page_config(page_title="청호방재 업무일지", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; background-color: #FFFFFF !important; color: #000000 !important; }
    
    /* 사이드바 커스텀 디자인 (노션 스타일 트리 구조) */
    [data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #E3F2FD !important; }
    [data-testid="stSidebar"] .stButton button {
        text-align: left !important; padding: 5px 10px !important;
        background-color: transparent !important; border: none !important; font-size: 14px !important;
        color: #333333 !important;
    }
    [data-testid="stSidebar"] .stButton button:hover { background-color: #E3F2FD !important; color: #0D47A1 !important; }
    
    /* 메인 대시보드 요약 카드 */
    .metric-card {
        background: #E3F2FD; border-radius: 15px; padding: 20px;
        text-align: center; border: 1px solid #BBDEFB; box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .metric-label { font-size: 15px; color: #546E7A; font-weight: bold; margin-bottom: 5px; }
    .metric-value { font-size: 28px; font-weight: 800; color: #0D47A1; }

    /* 구글 스타일 검색창 */
    .stTextInput > div > div > input {
        border-radius: 25px !important; padding: 12px 20px !important;
        border: 1px solid #dfe1e5 !important; box-shadow: 0 1px 4px rgba(32,33,36,0.15) !important;
    }

    /* 바로가기 아이콘 그리드 */
    .shortcut-box {
        width: 80px; height: 80px; background: #FFFFFF; border-radius: 18px;
        border: 1px solid #EEEEEE; display: flex; flex-direction: column;
        align-items: center; justify-content: center; transition: 0.2s; cursor: pointer;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
    }
    .shortcut-box:hover { background: #E3F2FD; border-color: #BBDEFB; transform: translateY(-2px); }
    </style>
    """, unsafe_allow_html=True)

# 2. [데이터 관리 로직: 모든 파일 자동 생성 및 로드]
def load_all_master_data():
    # 현장 데이터
    if not os.path.exists("data.xlsx"):
        pd.DataFrame(columns=['ID', '관리번호', '진행상태', '현장명', '사업장주소', '계약금액']).to_excel("data.xlsx", index=False)
    site_df = pd.read_excel("data.xlsx")
    site_df['ID'] = range(1, len(site_df) + 1)
    
    # 목표 데이터 (5개 항목 초기화)
    if not os.path.exists("goals.csv"):
        pd.DataFrame({'목표': ['신규 수주 5건', '미수금 제로화', '현장 안전 무사고', '장비 현대화', '고객 만족도 향상'], '완료': [False]*5}).to_csv("goals.csv", index=False)
    goal_df = pd.read_csv("goals.csv")

    # 바로가기 데이터
    if not os.path.exists("shortcuts.csv"):
        pd.DataFrame([{"이름": "구글", "URL": "https://google.com"}, {"이름": "네이버", "URL": "https://naver.com"}]).to_csv("shortcuts.csv", index=False)
    short_df = pd.read_csv("shortcuts.csv")
    
    return site_df, goal_df, short_df

site_df, goal_df, short_df = load_all_master_data()

# 세션 상태 관리
if 'page' not in st.session_state: st.session_state.page = 'dashboard'
if 'selected_site' not in st.session_state: st.session_state.selected_site = None

# --- [사이드바: 사장님이 요청하신 아이콘 트리 구조 복구] ---
with st.sidebar:
    st.markdown("### 🏢 청호방재 관리")
    if st.button("🏠 메인 대시보드"): 
        st.session_state.page = 'dashboard'; st.session_state.selected_site = None; st.rerun()
    st.divider()

    # [1] 견적중 트리 (최신 3개 + 추가)
    with st.sidebar.expander("🍀 견적중 현장", expanded=True):
        ests = site_df[site_df['진행상태'].str.contains('견적', na=False)].tail(3)
        for _, r in ests.iterrows():
            if st.button(f"🏛️ {r['현장명']}", key=f"s_est_{r['ID']}"):
                st.session_state.selected_site = r['현장명']; st.session_state.page = 'detail'; st.rerun()
        if st.button("➕ 견적 신규 등록", key="add_est"): st.info("데이터 관리 페이지로 이동합니다.")

    # [2] 진행중 트리 (최신 3개 + 추가)
    with st.sidebar.expander("🔄 진행중 현장", expanded=True):
        ings = site_df[site_df['진행상태'].str.contains('진행|공사', na=False)].tail(3)
        for _, r in ings.iterrows():
            if st.button(f"🏢 {r['현장명']}", key=f"s_ing_{r['ID']}"):
                st.session_state.selected_site = r['현장명']; st.session_state.page = 'detail'; st.rerun()
        if st.button("➕ 현장 신규 등록", key="add_ing"): st.info("데이터 관리 페이지로 이동합니다.")

    # [3] 완공현장 (사장님 요청 아이콘 적용)
    with st.sidebar.expander("📂 완공 현장 (카테고리)", expanded=False):
        done_cats = [
            ("🦋", "제조소_취급소"), ("🔋", "옥외탱크"), ("🔋", "지하탱크_자가주유"), 
            ("🔋", "옥내탱크"), ("🎃", "옥내저장소"), ("🎃", "옥외저장소"), 
            ("🛂", "군부대"), ("⛑️", "도료류"), ("👨‍🏫", "컨설팅")
        ]
        for icon, name in done_cats:
            if st.button(f"{icon} {name}", key=f"cat_{name}"):
                st.session_state.page = 'archive'; st.session_state.cat = name; st.rerun()

# --- [메인 대시보드: 구글 스타일 + 로고] ---
if st.session_state.page == 'dashboard' and st.session_state.selected_site is None:
    # 상단 로고 및 타이틀
    head_l, head_r = st.columns([1, 4])
    with head_l:
        if os.path.exists("square-mobile-800-800.png"):
            st.image("square-mobile-800-800.png", width=110)
    with head_r:
        st.markdown("<h1 style='margin-top:20px;'>위험물 전문기업 청호방재</h1>", unsafe_allow_html=True)

    # 1. 3단 요약 바 (견적, 진행, 목표)
    st.write("")
    m1, m2, m3 = st.columns(3)
    with m1:
        c_est = len(site_df[site_df['진행상태'].str.contains('견적', na=False)])
        st.markdown(f'<div class="metric-card"><div class="metric-label">🟡 견적 대기</div><div class="metric-value">{c_est}건</div></div>', unsafe_allow_html=True)
    with m2:
        c_ing = len(site_df[site_df['진행상태'].str.contains('진행|공사', na=False)])
        st.markdown(f'<div class="metric-card"><div class="metric-label">🔵 공사 진행중</div><div class="metric-value">{c_ing}건</div></div>', unsafe_allow_html=True)
    with m3:
        d_goal = goal_df['완료'].sum()
        st.markdown(f'<div class="metric-card"><div class="metric-label">🏆 목표 달성률</div><div class="metric-value">{d_goal}/{len(goal_df)}</div></div>', unsafe_allow_html=True)

    # 2. 구글형 검색창
    st.write("")
    search_q = st.text_input("", placeholder="Google 검색 또는 URL 입력", key="main_search", label_visibility="collapsed")
    if search_q:
        st.markdown(f'<meta http-equiv="refresh" content="0;url=https://www.google.com/search?q={search_q}">', unsafe_allow_html=True)

    # 3. 바로가기 그리드 (최대 30개)
    st.write("#### 🔗 바로가기")
    s_cols = st.columns(10) # 한 줄에 10개씩 배치
    for i, row in short_df.iterrows():
        with s_cols[i % 10]:
            st.markdown(f"""
                <a href="{row['URL']}" target="_blank" style="text-decoration:none;">
                    <div class="shortcut-box">
                        <div style="font-size:24px;">🌐</div>
                        <div style="font-size:11px; color:#333; margin-top:5px; text-align:center;">{row['이름']}</div>
                    </div>
                </a>
            """, unsafe_allow_html=True)
    
    with st.expander("➕ 바로가기 추가 및 삭제"):
        add_name = st.text_input("사이트 이름")
        add_url = st.text_input("사이트 주소(URL)")
        if st.button("추가하기"):
            new_shortcuts = pd.concat([short_df, pd.DataFrame([{"이름": add_name, "URL": add_url}])], ignore_index=True)
            new_shortcuts.to_csv("shortcuts.csv", index=False); st.rerun()

    st.divider()

    # 4. 청호방재 목표 & 캘린더
    col_l, col_r = st.columns([1, 2])
    with col_l:
        st.markdown("#### ✅ 청호방재의 목표")
        edited_goal = st.data_editor(goal_df, use_container_width=True, hide_index=True)
        if st.button("💾 목표 저장"):
            edited_goal.to_csv("goals.csv", index=False); st.success("저장되었습니다!"); st.rerun()
    with col_r:
        st.markdown("#### 🗓️ 일정 현황")
        cal_url = f"https://calendar.google.com/calendar/embed?src=t16705466@gmail.com&ctz=Asia/Seoul"
        st.components.v1.iframe(cal_url, height=500)

# --- [상세 페이지: 6종 업무분류 탑재] ---
elif st.session_state.page == 'detail':
    site_name = st.session_state.selected_site
    st.markdown(f"### 🏢 {site_name} 상세 업무일지")
    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.page = 'dashboard'; st.session_state.selected_site = None; st.rerun()
    
    st.divider()
    work_cat = st.selectbox("업무 분류", ["📞 통화", "🚗 방문", "📧 E-메일", "🏗️ 공사", "📄 서류작업", "💰 발행-입금"])
    log_temp = f"[업무일지 - {datetime.now().strftime('%Y-%m-%d')}]\n분류: {work_cat}\n내용: "
    st.text_area("현장 업무 내용 기록", value=log_temp, height=400)
    if st.button("💾 일지 저장"): st.success("기록이 저장되었습니다.")
    
    /* 사이드바 디자인 */
    [data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #E3F2FD !important; }
    [data-testid="stSidebar"] .stButton button {
        text-align: left !important; padding: 5px 10px !important;
        background-color: transparent !important; border: none !important; font-size: 14px !important;
    }
    
    /* 원노트 스타일 기록 카드 */
    .onenote-log {
        border-left: 6px solid #BBDEFB; background-color: #F8F9FA;
        padding: 20px; border-radius: 0 12px 12px 0; margin-bottom: 25px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
    }
    .log-header { display: flex; align-items: center; margin-bottom: 10px; }
    .log-date { font-weight: bold; color: #0D47A1; font-size: 15px; }
    .log-cat { background-color: #E3F2FD; padding: 2px 12px; border-radius: 15px; font-size: 13px; margin-left: 10px; font-weight: bold; }

    /* 대시보드 요약 카드 */
    .metric-card {
        background: #E3F2FD; border-radius: 15px; padding: 20px;
        text-align: center; border: 1px solid #BBDEFB; box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. [데이터 로드 로직]
def load_all_data():
    if not os.path.exists("data.xlsx"):
        pd.DataFrame(columns=['ID', '관리번호', '진행상태', '현장명', '사업장주소', '계약금액']).to_excel("data.xlsx", index=False)
    site_df = pd.read_excel("data.xlsx")
    site_df['ID'] = range(1, len(site_df) + 1)
    
    if not os.path.exists("goals.csv"):
        pd.DataFrame({'목표': ['신규 수주 5건', '안전 점검'], '완료': [False]*2}).to_csv("goals.csv", index=False)
    goal_df = pd.read_csv("goals.csv")

    if not os.path.exists("shortcuts.csv"):
        pd.DataFrame([{"이름": "구글", "URL": "https://google.com"}]).to_csv("shortcuts.csv", index=False)
    short_df = pd.read_csv("shortcuts.csv")
    
    return site_df, goal_df, short_df

# 상세 일지 파일 로드/저장
def get_site_log_file(site_name):
    filename = f"log_{site_name.replace(' ', '_')}.csv"
    if os.path.exists(filename): return pd.read_csv(filename)
    else: return pd.DataFrame(columns=['날짜', '분류', '내용', '이미지'])

site_df, goal_df, short_df = load_all_data()

# 페이지 세션 설정
if 'page' not in st.session_state: st.session_state.page = 'dashboard'
if 'selected_site' not in st.session_state: st.session_state.selected_site = None

# --- [사이드바 복구: 트리 구조 및 완공 카테고리] ---
with st.sidebar:
    st.markdown("### 🏢 청호방재 관리")
    if st.button("🏠 메인 대시보드"):
        st.session_state.page = 'dashboard'; st.session_state.selected_site = None; st.rerun()
    st.divider()

    with st.expander("🍀 견격중 현장", expanded=True):
        ests = site_df[site_df['진행상태'].str.contains('견적', na=False)].tail(3)
        for _, r in ests.iterrows():
            if st.button(f"🏛️ {r['현장명']}", key=f"side_est_{r['ID']}"):
                st.session_state.selected_site = r['현장명']; st.session_state.page = 'detail'; st.rerun()

    with st.expander("🔄 진행중 현장", expanded=True):
        ings = site_df[site_df['진행상태'].str.contains('진행|공사', na=False)].tail(3)
        for _, r in ings.iterrows():
            if st.button(f"🏢 {r['현장명']}", key=f"side_ing_{r['ID']}"):
                st.session_state.selected_site = r['현장명']; st.session_state.page = 'detail'; st.rerun()

    with st.expander("📂 완공 아카이브", expanded=False):
        done_cats = [("🦋", "제조소"), ("🔋", "탱크류"), ("🎃", "저장소"), ("🛂", "군부대"), ("⛑️", "도료류"), ("👨‍🏫", "컨설팅")]
        for icon, name in done_cats:
            if st.button(f"{icon} {name}", key=f"cat_{name}"):
                st.session_state.page = 'archive'; st.session_state.cat = name; st.rerun()

# --- [메인 화면 1: 대시보드 복구] ---
if st.session_state.page == 'dashboard':
    # 헤더
    h_l, h_r = st.columns([1, 5])
    with h_l:
        if os.path.exists("square-mobile-800-800.png"): st.image("square-mobile-800-800.png", width=100)
    with h_r: st.markdown("<h1 style='margin-top:20px;'>위험물 전문기업 청호방재</h1>", unsafe_allow_html=True)

    # 요약 바
    st.write("")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<div class="metric-card">🟡 견적중<br><b>{len(site_df[site_df["진행상태"].str.contains("견적", na=False)])}건</b></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card">🔵 진행중<br><b>{len(site_df[site_df["진행상태"].str.contains("진행|공사", na=False)])}건</b></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-card">🏆 목표<br><b>{goal_df["완료"].sum()}/{len(goal_df)}</b></div>', unsafe_allow_html=True)

    # 검색창
    st.write("")
    sq = st.text_input("", placeholder="Google 검색", label_visibility="collapsed")
    if sq: st.markdown(f'<meta http-equiv="refresh" content="0;url=https://www.google.com/search?q={sq}">', unsafe_allow_html=True)

    # 바로가기
    st.write("#### 🔗 바로가기")
    s_cols = st.columns(10)
    for i, row in short_df.iterrows():
        with s_cols[i % 10]:
            st.markdown(f'<a href="{row["URL"]}" target="_blank" style="text-decoration:none;"><div style="text-align:center; padding:10px; background:#F8F9FA; border-radius:10px; border:1px solid #EEE;">🌐<br><small>{row["이름"]}</small></div></a>', unsafe_allow_html=True)
    
    st.divider()
    
    # 목표 & 캘린더
    b_l, b_r = st.columns([1, 2])
    with b_l:
        st.markdown("#### ✅ 청호방재 목표")
        st.data_editor(goal_df, use_container_width=True, hide_index=True)
    with b_r:
        st.markdown("#### 🗓️ 일정 현황")
        st.components.v1.iframe(f"https://calendar.google.com/calendar/embed?src=t16705466@gmail.com&ctz=Asia/Seoul", height=450)

# --- [메인 화면 2: 상세 일지 - 원노트 복사/붙여넣기 최적화] ---
elif st.session_state.page == 'detail':
    site_name = st.session_state.selected_site
    st.markdown(f"### 🏢 {site_name} 상세 업무일지")
    if st.button("⬅️ 대시보드로 돌아가기"): st.session_state.page = 'dashboard'; st.rerun()

    # 입력 섹션
    with st.expander("➕ 새 상담/업무 내용 입력 (원노트 복사-붙여넣기 가능)", expanded=True):
        in_l, in_r = st.columns([1, 1])
        with in_l: in_date = st.date_input("🗓️ 상담일", value=datetime.now().date())
        with in_r: in_cat = st.selectbox("🗂️ 분류", ["📞 통화", "🚗 방문", "📧 메일", "🏗️ 공사", "📄 서류", "💰 입금"])
        
        # 원노트 글 붙여넣기 공간
        in_content = st.text_area("✍️ 원노트 내용을 여기에 붙여넣으세요 (자동 높이 조절)", height=200)
        in_img = st.file_uploader("📸 사진 첨부", type=['jpg', 'png', 'jpeg'])

        if st.button("💾 이 내용을 일지에 추가"):
            if in_content:
                img_path = ""
                if in_img:
                    img_path = f"img_{site_name}_{datetime.now().strftime('%H%M%S')}.png"
                    with Image.open(in_img).save(img_path)
                
                # 저장 로직
                new_data = pd.DataFrame([[in_date, in_cat, in_content, img_path]], columns=['날짜', '분류', '내용', '이미지'])
                log_df = get_site_log_file(site_name)
                pd.concat([log_df, new_data], ignore_index=True).to_csv(f"log_{site_name.replace(' ', '_')}.csv", index=False)
                st.success("새로운 상담 행이 추가되었습니다!"); st.rerun()

    st.divider()

    # 히스토리 (원노트 스타일 출력)
    history = get_site_log_file(site_name)
    if not history.empty:
        for i, row in history.iloc[::-1].iterrows():
            st.markdown(f"""
                <div class="onenote-log">
                    <div class="log-header">
                        <span class="log-date">🗓️ {row['날짜']}</span>
                        <span class="log-cat">{row['분류']}</span>
                    </div>
                    <div style="white-space: pre-wrap; line-height:1.6;">{row['내용']}</div>
                </div>
            """, unsafe_allow_html=True)
            if row['이미지'] and os.path.exists(str(row['이미지'])):
                st.image(row['이미지'], use_container_width=True)

