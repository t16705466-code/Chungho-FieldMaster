import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. [디자인 박제] 리액트 버전의 고품격 UI 재현 (Slate-950 테마)
st.set_page_config(page_title="청호방재 비즈니스 마스터", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
    }

    /* 메인 헤더 */
    .main-header {
        background-color: #020617;
        padding: 1.5rem 2rem;
        border-bottom: 1px solid #1e293b;
        margin: -6rem -5rem 2rem -5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* 요약 카드 디자인 */
    .metric-card {
        background: white;
        padding: 2.5rem;
        border-radius: 40px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-align: left;
        transition: transform 0.2s;
    }
    .metric-title { font-size: 0.9rem; font-weight: 900; color: #94a3b8; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.5rem; }
    .metric-value { font-size: 4rem; font-weight: 900; color: #2563eb; line-height: 1; }
    .metric-unit { font-size: 1.5rem; color: #94a3b8; margin-left: 0.5rem; }

    /* 전문가용 입력창 섹션 */
    .section-container {
        background: white;
        border-radius: 60px;
        border: 1px solid #e2e8f0;
        overflow: hidden;
        margin-bottom: 3rem;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05);
    }
    .section-header {
        background: #020617;
        color: white;
        padding: 3rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* 인풋 박스 스타일 */
    div[data-baseweb="input"] { border-radius: 15px !important; }
    
    /* 버튼 스타일 */
    .stButton>button {
        border-radius: 30px !important;
        font-weight: 900 !important;
        padding: 0.75rem 2rem !important;
        transition: all 0.2s;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. [데이터 로직]
def load_data():
    if not os.path.exists("data.xlsx"):
        df = pd.DataFrame(columns=['ID', '관리번호', '진행상태', '관할서', '현장명', '사업장주소', '현장주소', '메모', '계약금액', '선수금', '중도금'])
        df.to_excel("data.xlsx", index=False)
    df = pd.read_excel("data.xlsx")
    return df

site_df = load_data()

# 세션 관리
if 'page' not in st.session_state: st.session_state.page = 'dashboard'
if 'selected_id' not in st.session_state: st.session_state.selected_id = None

# --- [메인 대시보드 화면] ---
if st.session_state.page == 'dashboard':
    # 상단 헤더 커스텀
    st.markdown("""
        <div class="main-header">
            <div style="display: flex; align-items: center; gap: 15px;">
                <div style="background: #2563eb; padding: 10px; border-radius: 12px; color: white; font-weight: 900;">🏢</div>
                <span style="color: white; font-size: 1.5rem; font-weight: 900;">청호방재 비즈니스 마스터</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 1. 요약 메트릭
    m_col1, m_col2 = st.columns(2)
    
    # 상태 판별 로직
    def get_status(no):
        clean_no = str(no).replace('-', '')
        return "견적중" if len(clean_no) >= 6 else "진행중"

    with m_col1:
        count_ing = len(site_df[site_df['진행상태'] == '진행중'])
        st.markdown(f"""<div class="metric-card"><div class="metric-title">진행중 현장</div><div class="metric-value">{count_ing}<span class="metric-unit">건</span></div></div>""", unsafe_allow_html=True)
    with m_col2:
        count_quote = len(site_df[site_df['진행상태'] == '견적중'])
        st.markdown(f"""<div class="metric-card"><div class="metric-title">견적 및 대기</div><div class="metric-value" style="color:#ea580c;">{count_quote}<span class="metric-unit">건</span></div></div>""", unsafe_allow_html=True)

    # 2. 검색 및 리스트
    st.write("")
    search = st.text_input("🔍 현장명 또는 관리번호 검색", placeholder="검색어를 입력하세요...")
    
    filtered_df = site_df
    if search:
        filtered_df = site_df[site_df['현장명'].str.contains(search, na=False) | site_df['관리번호'].str.contains(search, na=False)]

    st.markdown("### 📑 전체 현장 마스터 리스트")
    # 금액 계산 로직 포함된 표 출력
    display_df = filtered_df.copy()
    if not display_df.empty:
        # 잔금 계산 열 추가
        display_df['총액(VAT포함)'] = (display_df['계약금액'] * 1.1).astype(int)
        display_df['미수잔금'] = (display_df['총액(VAT포함)'] - display_df['선수금'] - display_df['중도금']).astype(int)
        
        event = st.dataframe(
            display_df[['관리번호', '관할서', '현장명', '현장주소', '총액(VAT포함)', '미수잔금']],
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        # 행 선택 시 상세페이지 이동
        if event.selection.rows:
            selected_idx = event.selection.rows[0]
            st.session_state.selected_id = display_df.iloc[selected_idx]['ID']
            st.session_state.page = 'detail'
            st.rerun()
    else:
        st.info("등록된 현장이 없습니다.")

    if st.button("➕ 신규 현장 등록하기"):
        st.session_state.selected_id = None
        st.session_state.page = 'detail'
        st.rerun()

    st.divider()
    st.markdown("### 📅 구글 업무 일정표")
    st.components.v1.iframe("https://calendar.google.com/calendar/embed?src=t16705466%40gmail.com&ctz=Asia/Seoul", height=600)

# --- [상세 및 등록 화면] ---
elif st.session_state.page == 'detail':
    # 데이터 불러오기
    is_new = st.session_state.selected_id is None
    if not is_new:
        site_info = site_df[site_df['ID'] == st.session_state.selected_id].iloc[0].to_dict()
    else:
        site_info = {'관리번호': '', '관할서': '', '현장명': '', '사업장주소': '', '현장주소': '', '메모': '', '계약금액': 0, '선수금': 0, '중도금': 0}

    st.markdown(f"## {'🏢 ' + site_info['현장명'] if not is_new else '🆕 신규 현장 등록'}")
    if st.button("⬅️ 목록으로 돌아가기"):
        st.session_state.page = 'dashboard'
        st.rerun()

    # 섹션 1: 기본 정보
    st.markdown("#### 1. 현장 개요 정보")
    c1, c2, c3 = st.columns(3)
    with c1:
        m_no = st.text_input("관리번호", value=site_info['관리번호'], placeholder="YY-NN 또는 숫자")
        clean_no = m_no.replace('-', '')
        status = "견적중" if len(clean_no) >= 6 else "진행중" if m_no else "-"
    with c2:
        st.write("진행상태(자동)")
        st.info(f"**{status}**")
    with c3:
        juris = st.text_input("관할 소방서", value=site_info['관할서'])

    site_name = st.text_input("현장명 (상호명)", value=site_info['현장명'])
    biz_addr = st.text_input("사업장 주소", value=site_info['사업장주소'])
    site_addr = st.text_input("실제 공사 현장 주소", value=site_info['현장주소'])
    memo = st.text_area("현장 특이사항 및 메모", value=site_info['메모'])

    # 섹션 2: 금액 정산
    st.markdown("#### 2. 금전 및 수금 관리")
    f1, f2, f3 = st.columns(3)
    with f1:
        c_amt = st.number_input("계약금액 (공급가)", value=int(site_info['계약금액']), step=10000)
        vat = int(c_amt * 0.1)
        total = c_amt + vat
    with f2: st.write(f"부가세(10%): **{vat:,}원**")
    with f3: st.success(f"총 계약금액: **{total:,}원**")

    p1, p2, p3 = st.columns(3)
    with p1: adv = st.number_input("입금액 (선수금)", value=int(site_info['선수금']), step=10000)
    with p2: mid = st.number_input("입금액 (중도금)", value=int(site_info['중도금']), step=10000)
    with p3:
        bal = total - adv - mid
        st.error(f"최종 미수잔금: **{bal:,}원**")

    if st.button("💾 데이터 최종 저장 및 박제", use_container_width=True):
        if not m_no or not site_name:
            st.warning("관리번호와 현장명은 필수 입력 사항입니다.")
        else:
            new_data = {
                'ID': site_info.get('ID', len(site_df) + 1),
                '관리번호': m_no, '진행상태': status, '관할서': juris, '현장명': site_name,
                '사업장주소': biz_addr, '현장주소': site_addr, '메모': memo,
                '계약금액': c_amt, '선수금': adv, '중도금': mid
            }
            
            if is_new:
                site_df = pd.concat([site_df, pd.DataFrame([new_data])], ignore_index=True)
            else:
                site_df.loc[site_df['ID'] == st.session_state.selected_id] = new_data
            
            site_df.to_excel("data.xlsx", index=False)
            st.success("성공적으로 저장되었습니다!")
            st.session_state.page = 'dashboard'
            st.rerun()

    # 관계인 및 상담 일지는 Streamlit의 data_editor 기능을 활용하여 전문가용 테이블로 제공
    if not is_new:
        st.divider()
        st.markdown("#### 👥 관계인 및 상세 일지 (행 추가 가능)")
        # 관계인 테이블
        c_file = f"con_{m_no}.csv"
        c_df = pd.read_csv(c_file) if os.path.exists(c_file) else pd.DataFrame(columns=['이름', '직위', '연락처', '비고'])
        edited_c = st.data_editor(c_df, num_rows="dynamic", use_container_width=True, key="c_edit")
        if st.button("저장: 관계인 정보"): edited_c.to_csv(c_file, index=False)

        # 상세 일지 테이블
        l_file = f"log_{m_no}.csv"
        l_df = pd.read_csv(l_file) if os.path.exists(l_file) else pd.DataFrame(columns=['날짜', '분류', '업무내용'])
        edited_l = st.data_editor(l_df, num_rows="dynamic", use_container_width=True, key="l_edit")
        if st.button("저장: 상세 일지"): edited_l.to_csv(l_file, index=False)
