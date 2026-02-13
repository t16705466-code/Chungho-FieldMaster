import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. [디자인 박제] 화이트/블랙/연하늘 + 전문가용 UI (React 감성 이식)
st.set_page_config(page_title="청호방재 업무일지", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; background-color: #FFFFFF !important; color: #000000 !important; }
    
    /* 섹션 헤더 스타일 */
    .section-header {
        font-size: 20px; font-weight: 900; color: #0D47A1; 
        display: flex; align-items: center; gap: 10px; margin-bottom: 15px; margin-top: 25px;
    }
    
    /* 계산 박스 스타일 */
    .display-box {
        background-color: #F8F9FA; border: 1px solid #E3F2FD; padding: 10px 15px; border-radius: 8px;
    }
    .display-label { font-size: 12px; font-weight: 900; color: #90A4AE; text-transform: uppercase; }
    .display-value { font-size: 16px; font-weight: 900; color: #37474F; }

    /* 메인 버튼 스타일 */
    .stButton > button {
        border-radius: 8px !important; font-weight: 900 !important; transition: all 0.3s;
    }
    
    /* 사이드바 디자인 유지 */
    [data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #E3F2FD !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. [데이터 로직: React 필드에 맞춰 확장]
def load_all_master_data():
    cols = ['ID', '관리번호', '진행상태', '관할서', '현장명', '사업장주소', '현장주소', '메모', '계약금액', '선수금', '중도금']
    if not os.path.exists("data.xlsx"):
        pd.DataFrame(columns=cols).to_excel("data.xlsx", index=False)
    site_df = pd.read_excel("data.xlsx")
    # 누락된 컬럼 자동 생성
    for col in cols:
        if col not in site_df.columns: site_df[col] = ""
    return site_df

def save_data(df):
    df.to_excel("data.xlsx", index=False)

site_df = load_all_master_data()

# 세션 상태 관리
if 'page' not in st.session_state: st.session_state.page = 'dashboard'
if 'selected_site' not in st.session_state: st.session_state.selected_site = None

# --- [사이드바] ---
with st.sidebar:
    st.markdown("### 🏢 청호방재 관리")
    if st.button("🏠 메인 대시보드", key="nav_dash"): 
        st.session_state.page = 'dashboard'; st.session_state.selected_site = None; st.rerun()
    st.divider()

    with st.sidebar.expander("🍀 견적중 현장", expanded=True):
        ests = site_df[site_df['진행상태'].str.contains('견적', na=False)]
        for _, r in ests.tail(5).iterrows():
            if st.button(f"🏛️ {r['현장명']}", key=f"s_est_{r['ID']}"):
                st.session_state.selected_site = r['관리번호']; st.session_state.page = 'detail'; st.rerun()
        # [신규 추가 버튼]
        if st.button("➕ 견적 신규 등록", key="add_est_nav"):
            st.session_state.page = 'create_site'; st.rerun()

    with st.sidebar.expander("🔄 진행중 현장", expanded=True):
        ings = site_df[site_df['진행상태'].str.contains('진행|공사', na=False)]
        for _, r in ings.tail(5).iterrows():
            if st.button(f"🏢 {r['현장명']}", key=f"s_ing_{r['ID']}"):
                st.session_state.selected_site = r['관리번호']; st.session_state.page = 'detail'; st.rerun()

# --- [페이지 1: 신규 현장 등록 (React 코드 이식)] ---
if st.session_state.page == 'create_site':
    st.markdown("## 🆕 새 업무일지 작성")
    if st.button("⬅️ 메인으로 돌아가기"): st.session_state.page = 'dashboard'; st.rerun()
    
    st.markdown('<div class="section-header">📄 현장 개요</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1: 
        m_no = st.text_input("관리번호", placeholder="예: 25-01 / 260102")
        # 진행상태 자동 계산 로직
        clean_no = m_no.replace("-", "")
        status = "견적중" if len(clean_no) >= 6 else "진행중" if m_no else "-"
    with c2: 
        st.write(f"**진행상태(자동)**")
        color = "#1565C0" if status == "진행중" else "#E64A19"
        st.markdown(f"<span style='color:{color}; font-weight:900;'>{status}</span>", unsafe_allow_html=True)
    with c3: 
        juris = st.text_input("관할서")

    site_name = st.text_input("현장명")
    biz_addr = st.text_input("사업장주소")
    site_addr = st.text_input("현장주소")
    memo = st.text_area("메모", placeholder="복사 붙여넣기도 가능합니다.")

    st.markdown('<div class="section-header">💰 금액 정보</div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1: 
        c_amt = st.number_input("계약금액 (원)", min_value=0, step=10000, value=0)
        vat = int(c_amt * 0.1)
        total = c_amt + vat
    with f2: st.info(f"부가세(10%): {vat:,} 원")
    with f3: st.success(f"총 계약금액: {total:,} 원")

    p1, p2, p3 = st.columns(3)
    with p1: adv_pay = st.number_input("선수금 (원)", min_value=0, step=10000, value=0)
    with p2: inter_pay = st.number_input("중도금 (원)", min_value=0, step=10000, value=0)
    with p3: 
        bal = total - adv_pay - inter_pay
        st.warning(f"잔금: {bal:,} 원")

    if st.button("💾 최종 일지 저장", use_container_width=True):
        if not m_no or not site_name:
            st.error("관리번호와 현장명은 필수 입력입니다.")
        elif m_no in site_df['관리번호'].astype(str).values:
            st.error(f"❌ 오류: 관리번호 [{m_no}]는 이미 존재합니다. 확인 후 다시 입력해주세요.")
        else:
            new_id = len(site_df) + 1
            new_row = {
                'ID': new_id, '관리번호': m_no, '진행상태': status, '관할서': juris,
                '현장명': site_name, '사업장주소': biz_addr, '현장주소': site_addr,
                '메모': memo, '계약금액': c_amt, '선수금': adv_pay, '중도금': inter_pay
            }
            updated_df = pd.concat([site_df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(updated_df)
            st.success(f"✅ [{site_name}] 현장이 성공적으로 등록되었습니다!"); st.balloons()
            st.session_state.page = 'dashboard'; st.rerun()

# --- [페이지 2: 상세 일지 (React 테이블 스타일)] ---
elif st.session_state.page == 'detail':
    m_no = st.session_state.selected_site
    site_info = site_df[site_df['관리번호'] == m_no].iloc[0]
    
    st.markdown(f"## 🏢 [{m_no}] {site_info['현장명']}")
    if st.button("⬅️ 메인으로"): st.session_state.page = 'dashboard'; st.rerun()

    st.markdown('<div class="section-header">📋 상세 기록 및 사진</div>', unsafe_allow_html=True)
    
    # 상담 기록 (React 스타일의 테이블 형태 에디터)
    log_file = f"log_{m_no}.csv"
    if os.path.exists(log_file): log_df = pd.read_csv(log_file)
    else: log_df = pd.DataFrame(columns=['상담일', '업무형태', '상담내용', '첨부자료'])

    edited_log = st.data_editor(log_df, num_rows="dynamic", use_container_width=True, hide_index=True)
    
    if st.button("💾 기록 업데이트"):
        edited_log.to_csv(log_file, index=False)
        st.success("상세 기록이 저장되었습니다.")

# --- [페이지 3: 대시보드] ---
else:
    st.markdown("# 🚀 청호방재 통합 대시보드")
    # 기존 대시보드 로고 및 3단 요약 로직 유지
    st.write("사이드바를 이용해 신규 등록하거나 현장을 선택하세요.")
