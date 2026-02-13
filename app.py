import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정
st.set_page_config(page_title="청호방재 필드마스터", layout="wide", initial_sidebar_state="collapsed")

# 디자인 설정 (검정 글씨 & 깔끔한 표)
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; color: #1A1A1A; }
    h1, h2, h3, h4, p, label { color: #1A1A1A !important; }
    /* 데이터프레임 에디터 높이 조절 */
    [data-testid="stDataEditor"] { border: 1px solid #ddd; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 헬퍼 함수: 데이터 로드 및 자동 로직 ---
def load_and_sync_data():
    if not os.path.exists("data.xlsx"):
        df = pd.DataFrame(columns=['ID', '관리번호', '진행상태', '현장명', '사업장주소', '관할서', '계약금액'])
        df.to_excel("data.xlsx", index=False)
    
    df = pd.read_excel("data.xlsx")
    
    # [자동 로직 1] ID가 비어있으면 자동 부여 (최대값 + 1)
    if 'ID' not in df.columns: df.insert(0, 'ID', range(1, len(df) + 1))
    for i in range(len(df)):
        if pd.isna(df.loc[i, 'ID']):
            df.loc[i, 'ID'] = df['ID'].max() + 1 if not df['ID'].empty else 1
            
    # [자동 로직 2] 관리번호가 입력되면 진행상태를 '진행중'으로 자동 변경
    # 관리번호가 있고, 상태가 '견적중'이거나 비어있을 때만 변경
    if '관리번호' in df.columns and '진행상태' in df.columns:
        mask = df['관리번호'].notna() & (df['관리번호'].astype(str).str.strip() != "")
        df.loc[mask, '진행상태'] = '진행중'
        df.loc[~mask, '진행상태'] = '견적중' # 관리번호 없으면 다시 견적중으로

    return df

def save_data(df):
    df.to_excel("data.xlsx", index=False)

# 데이터 불러오기
site_df = load_and_sync_data()
try:
    contact_df = pd.read_csv("contacts.csv").dropna(axis=1, how='all')
except:
    contact_df = pd.DataFrame()

# 세션 상태 제어
if 'page' not in st.session_state: st.session_state.page = 'dashboard'
if 'selected_site' not in st.session_state: st.session_state.selected_site = None

# --- [1. 메인 대시보드] ---
if st.session_state.page == 'dashboard':
    st.title("🚀 청호방재 통합 관리실")
    
    # 상단 요약 지표
    col_a, col_b = st.columns(2)
    col_a.metric("🔵 진행 중 현장", len(site_df[site_df['진행상태'] == '진행중']))
    col_b.metric("🟡 견적 중 현장", len(site_df[site_df['진행상태'] == '견적중']))

    st.divider()

    # 현장 리스트 (최신 5건씩)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🔵 진행 리스트")
        if st.button("진행 현장 전체관리 ⚙️"): st.session_state.page = 'list_ing'; st.rerun()
        for _, row in site_df[site_df['진행상태'] == '진행중'].tail(5).iloc[::-1].iterrows():
            if st.button(f"🏢 {row['현장명']}", key=f"d_ing_{row['ID']}"):
                st.session_state.selected_site = row['현장명']; st.session_state.page = 'detail'; st.rerun()

    with c2:
        st.subheader("🟡 견적 리스트")
        if st.button("견적 현장 전체관리 ⚙️"): st.session_state.page = 'list_est'; st.rerun()
        for _, row in site_df[site_df['진행상태'] == '견적중'].tail(5).iloc[::-1].iterrows():
            if st.button(f"📄 {row['현장명']}", key=f"d_est_{row['ID']}"):
                st.session_state.selected_site = row['현장명']; st.session_state.page = 'detail'; st.rerun()

# --- [2. 현장 편집 페이지 (Master_DB 표 스타일)] ---
elif st.session_state.page in ['list_ing', 'list_est']:
    status = '진행중' if st.session_state.page == 'list_ing' else '견적중'
    st.title(f"📂 {status} 데이터베이스 관리")
    
    if st.button("⬅️ 메인 대시보드로"): st.session_state.page = 'dashboard'; st.rerun()
    
    st.write("💡 표에서 내용을 직접 수정하거나 맨 아래 행에 새 데이터를 입력하세요. (관리번호 입력 시 진행중으로 자동 이동)")
    
    # 해당 상태의 데이터만 필터링해서 보여주되, 수정 가능하게 함
    target_df = site_df[site_df['진행상태'] == status].copy()
    
    # [핵심] Streamlit Data Editor 사용 (엑셀처럼 수정 가능)
    edited_df = st.data_editor(
        site_df, 
        num_rows="dynamic", # 행 추가/삭제 가능
        use_container_width=True,
        key="data_editor",
        hide_index=True
    )
    
    if st.button("💾 변경사항 저장하기"):
        save_data(edited_df)
        st.success("Master_DB가 업데이트되었습니다!"); st.rerun()

# --- [3. 현장 상세 페이지] ---
elif st.session_state.page == 'detail':
    site_name = st.session_state.selected_site
    site_info = site_df[site_df['현장명'] == site_name].iloc[0]
    
    if st.button("⬅️ 뒤로가기"): st.session_state.page = 'dashboard'; st.rerun()
    
    st.header(f"🏢 {site_name}")
    st.markdown(f"**📍 주소:** {site_info.get('사업장주소','-')} | **🔢 관리번호:** {site_info.get('관리번호','')}")
    
    # 업무 일지 및 연락처 로직 (기존과 동일)
    st.text_area("📝 현장 일지 기록", height=200)
    st.button("일지 저장")
