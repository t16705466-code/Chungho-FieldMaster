import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. [디자인 박제] 구글 스타일 커스텀 CSS
st.set_page_config(page_title="청호방재 업무일지", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, h4, p, label, span, div { color: #000000 !important; }
    
    /* 구글 검색창 스타일 */
    .search-container {
        display: flex; justify-content: center; padding: 20px 0;
    }
    .search-box {
        width: 60%; padding: 12px 25px; border-radius: 30px;
        border: 1px solid #dfe1e5; font-size: 16px; outline: none;
        box-shadow: 0 1px 6px rgba(32,33,36,0.28);
    }
    
    /* 바로가기 아이콘 스타일 */
    .shortcut-item {
        display: flex; flex-direction: column; align-items: center;
        text-align: center; margin: 10px; cursor: pointer; text-decoration: none;
    }
    .shortcut-icon {
        width: 48px; height: 48px; border-radius: 50%;
        background-color: #F8F9FA; display: flex; align-items: center;
        justify-content: center; margin-bottom: 8px; font-size: 24px;
        border: 1px solid #EEEEEE; transition: background 0.3s;
    }
    .shortcut-icon:hover { background-color: #E3F2FD; }
    .shortcut-label { font-size: 12px; color: #3c4043; width: 80px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

    /* 기존 버튼/카드 디자인 유지 */
    [data-testid="stMetric"] { background-color: #E3F2FD !important; border: 1px solid #BBDEFB !important; border-radius: 12px; }
    div.stButton > button { width: 100%; background-color: #E3F2FD !important; color: #000000 !important; border: 1px solid #BBDEFB !important; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. [바로가기 데이터] 사장님이 자주 가시는 곳 30개 (수정 가능)
shortcuts = [
    {"name": "캘린더", "url": "https://calendar.google.com", "icon": "📅"},
    {"name": "주소록", "url": "https://contacts.google.com", "icon": "👤"},
    {"name": "지메일", "url": "https://mail.google.com", "icon": "✉️"},
    {"name": "구글광고", "url": "https://ads.google.com", "icon": "📈"},
    {"name": "네이버", "url": "https://www.naver.com", "icon": "N"},
    {"name": "제미나이", "url": "https://gemini.google.com", "icon": "✨"},
    {"name": "노트북LM", "url": "https://notebooklm.google.com", "icon": "📓"},
    {"name": "드라이브", "url": "https://drive.google.com", "icon": "📁"},
    {"name": "16705466", "url": "http://16705466.com", "icon": "🏢"},
    {"name": "노션-일지", "url": "https://www.notion.so", "icon": "📝"},
    # ... 여기에 30개까지 추가 가능 (현재는 예시로 10개)
]

# 3. [메인 대시보드 로직]
if 'page' not in st.session_state: st.session_state.page = 'dashboard'

if st.session_state.page == 'dashboard':
    st.markdown("<h2 style='text-align: center; color: #4285F4;'>Chungho Search</h2>", unsafe_allow_html=True)
    
    # [1] 구글형 검색창 (입력 후 엔터 치면 구글 검색으로 이동)
    search_query = st.text_input("", placeholder="Google 검색 또는 URL 입력", key="main_search", label_visibility="collapsed")
    if search_query:
        st.markdown(f'<meta http-equiv="refresh" content="0;url=https://www.google.com/search?q={search_query}">', unsafe_allow_html=True)

    # [2] 바로가기 아이콘 그리드 (한 줄에 8~10개씩 자동 배치)
    st.write("")
    cols = st.columns(8) # 한 줄에 보일 개수 조절
    for i, item in enumerate(shortcuts):
        with cols[i % 8]:
            st.markdown(f"""
                <a href="{item['url']}" target="_blank" style="text-decoration: none;">
                    <div class="shortcut-item">
                        <div class="shortcut-icon">{item['icon']}</div>
                        <div class="shortcut-label">{item['name']}</div>
                    </div>
                </a>
            """, unsafe_allow_html=True)

    st.divider()

    # [3] 기존 3단 요약 바 및 캘린더
    m1, m2, m3 = st.columns(3)
    # (기존 데이터 로드 로직 생략 - 실제 파일에 포함됨)
    m1.metric("🟡 견적 현황", "대기 중")
    m2.metric("🔵 진행 현황", "공사 중")
    m3.metric("📅 일정 현황", "확인 요망")

    st.markdown("#### 🗓️ 청호방재 업무 일정")
    st.components.v1.iframe(f"https://calendar.google.com/calendar/embed?src=t16705466@gmail.com&ctz=Asia/Seoul", height=600)
