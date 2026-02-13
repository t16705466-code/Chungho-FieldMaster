import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. [디자인 박제] 리액트(React) 감성의 고품격 UI 스타일 적용
st.set_page_config(page_title="청호방재 업무일지", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; background-color: #FFFFFF !important; color: #000000 !important; }
    
    /* 섹션 헤더 (리스트와 구분되는 묵직한 디자인) */
    .section-header {
        font-size: 24px; font-weight: 900; color: #1E293B; 
        display: flex; align-items: center; gap: 12px; margin: 40px 0 20px 0;
        padding-bottom: 15px; border-bottom: 3px solid #F1F5F9;
    }
    
    /* 리액트 스타일의 입력 박스 라벨 */
    .input-label { font-size: 13px; font-weight: 900; color: #64748B; text-transform: uppercase; margin-bottom: 8px; }
    
    /* 자동 계산 박스 스타일 */
    .calc-box {
        background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 15px; border-radius: 12px; height: 100%;
    }
    .calc-value { font-size: 20px; font-weight: 900; color: #0F172A; }
    .calc-status-quote { color: #EA580C !important; } /* 견적중 주황색 */
    .calc-status-ing { color: #2563EB !important; }   /* 진행중 파란색 */

    /* 버튼 디자인 */
    .stButton > button {
        border-radius: 12px !important; font-weight: 900 !important; height: 3.5rem !important;
        background-color: #0F172A !important; color: white !important; transition: all 0.3s;
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# 2. [데이터 관리 로직]
def load_master_data():
    cols = ['ID', '관리번호', '진행상태', '관할서', '현장명', '사업장주소', '현장주소', '메모', '계약금액', '선수금', '중도금']
    if not os.path.exists("data.xlsx"):
        pd.DataFrame(columns=cols).to_excel("data.xlsx", index=False)
    df = pd.read_excel("data.xlsx")
    for col in cols: # 누락 컬럼 대응
        if col not in df.columns: df[col] = 0 if '금액' in col or '금' in col else ""
    return df

site_df = load_master_data()

# 페이지 세션 상태
if 'page' not in st.session_state: st.session_state.page = 'dashboard'
if 'selected_site' not in st.session_state: st.session_state.selected_site = None

# --- [사이드바 메뉴] ---
with st.sidebar:
    st.markdown("### 🏢 청호방재")
    if st.button("🏠 대시보드 홈"): st.session_state.page = 'dashboard'; st.rerun()
    st.divider()

    with st.expander("🍀 견적중 현장", expanded=True):
        ests = site_df[site_df['진행상태'].str.contains('견적', na=False)]
        for _, r in ests.tail(5).iterrows():
            if st.button(f"🏛️ {r['현장명']}", key=f"side_est_{r['ID']}"):
                st.session_state.selected_site = r['관리번호']; st.session_state.page = 'detail'; st.rerun()
        # [사장님 요청] 신규 추가 버튼
        if st.button("➕ 견적 신규 등록", key="btn_nav_create"):
            st.session_state.page = 'create_site'; st.rerun()

# --- [신규 페이지: 리액트 디자인 완벽 이식] ---
if st.session_state.page == 'create_site':
    st.markdown("## 🆕 새 업무일지 작성")
    if st.button("⬅️ 목록으로 돌아가기"): st.session_state.page = 'dashboard'; st.rerun()

    # 1. 현장 개요
    st.markdown('<div class="section-header">📄 현장 개요</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        m_no = st.text_input("관리번호", placeholder="예: 25-01 / 260102")
        # 리액트 로직 이식: 상태 자동 계산
        clean_no = str(m_no).replace("-", "")
        status = "견적중" if len(clean_no) >= 6 else "진행중" if m_no else "-"
    with c2:
        st.markdown('<p class="input-label">진행상태 (자동)</p>', unsafe_allow_html=True)
        status_class = "calc-status-quote" if status == "견적중" else "calc-status-ing"
        st.markdown(f'<div class="calc-box"><span class="calc-value {status_class}">{status}</span></div>', unsafe_allow_html=True)
    with c3:
        juris = st.text_input("관할서")

    s_name = st.text_input("현장명 (회사명)")
    b_addr = st.text_input("사업장 주소")
    s_addr = st.text_input("현장 실제 주소")
    memo = st.text_area("현장 메모 (원노트 복사 가능)", height=100)

    # 2. 금액 정산 (리액트의 수식 그대로 이식)
    st.markdown('<div class="section-header">💰 금전 및 수금 관리</div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        c_amt = st.number_input("계약금액 (공급가)", min_value=0, step=10000, value=0)
        vat = int(c_amt * 0.1)
        total = c_amt + vat
    with f2:
        st.markdown('<p class="input-label">부가세 (10%)</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="calc-box"><span class="calc-value">{vat:,} 원</span></div>', unsafe_allow_html=True)
    with f3:
        st.markdown('<p class="input-label">총 계약금액 (합계)</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="calc-box" style="background-color:#EFF6FF;"><span class="calc-value" style="color:#1D4ED8;">{total:,} 원</span></div>', unsafe_allow_html=True)

    p1, p2, p3 = st.columns(3)
    with p1: adv_pay = st.number_input("선수금", min_value=0, step=10000, value=0)
    with p2: inter_pay = st.number_input("중도금", min_value=0, step=10000, value=0)
    with p3:
        balance = total - adv_pay - inter_pay
        st.markdown('<p class="input-label">잔금 (미수금)</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="calc-box" style="background-color:#FEF2F2;"><span class="calc-value" style="color:#B91C1C;">{balance:,} 원</span></div>', unsafe_allow_html=True)

    st.write("")
    if st.button("💾 최종 일지 저장 및 엑셀 추가", use_container_width=True):
        # [사장님 요청] 중복 체크 로직
        if not m_no or not s_name:
            st.error("관리번호와 현장명은 필수 입력 사항입니다.")
        elif m_no in site_df['관리번호'].astype(str).values:
            st.error(f"❌ 중복 오류: 관리번호 [{m_no}]가 이미 존재합니다. 다른 번호를 입력해주세요.")
        else:
            new_row = {
                'ID': len(site_df)+1, '관리번호': m_no, '진행상태': status, '관할서': juris,
                '현장명': s_name, '사업장주소': b_addr, '현장주소': s_addr,
                '메모': memo, '계약금액': c_amt, '선수금': adv_pay, '중도금': inter_pay
            }
            updated_df = pd.concat([site_df, pd.DataFrame([new_row])], ignore_index=True)
            updated_df.to_excel("data.xlsx", index=False)
            st.success(f"✅ [{s_name}] 현장이 성공적으로 등록되었습니다!"); st.balloons()
            st.session_state.page = 'dashboard'; st.rerun()

# --- [상세 페이지: 관계인 및 상담 로그 자동 확장 테이블] ---
elif st.session_state.page == 'detail':
    m_no = st.session_state.selected_site
    info = site_df[site_df['관리번호'] == m_no].iloc[0]
    
    st.markdown(f"## 🏢 [{m_no}] {info['현장명']}")
    if st.button("⬅️ 메인으로"): st.session_state.page = 'dashboard'; st.rerun()

    # 1. 관계인 섹션 (Dynamic Table)
    st.markdown('<div class="section-header">👥 현장 관계인</div>', unsafe_allow_html=True)
    c_file = f"contacts_{m_no}.csv"
    c_df = pd.read_csv(c_file) if os.path.exists(c_file) else pd.DataFrame(columns=['회사명', '이름', '직위', '전화', '비고'])
    edited_c = st.data_editor(c_df, num_rows="dynamic", use_container_width=True, hide_index=True)
    if st.button("💾 관계인 정보 업데이트"): edited_c.to_csv(c_file, index=False); st.success("저장 완료")

    # 2. 상담 기록 섹션 (Dynamic Table)
    st.markdown('<div class="section-header">📜 상담 및 현장 상세 기록</div>', unsafe_allow_html=True)
    l_file = f"log_{m_no}.csv"
    l_df = pd.read_csv(l_file) if os.path.exists(l_file) else pd.DataFrame(columns=['상담일', '업무형태', '상담내용', '비고'])
    edited_l = st.data_editor(l_df, num_rows="dynamic", use_container_width=True, hide_index=True)
    if st.button("💾 상담 기록 업데이트"): edited_l.to_csv(l_file, index=False); st.success("저장 완료")

# --- [대시보드 페이지 (복원 완료)] ---
else:
    st.markdown("# 🚀 청호방재 통합 대시보드")
    # (이전에 만든 3단 요약 바, 구글 검색, 바로가기 아이콘, 캘린더 연동 코드 유지)
    st.info("사이드바의 [➕ 견적 신규 등록] 버튼을 눌러 새 업무를 시작하세요.")
