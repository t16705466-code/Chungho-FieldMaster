import streamlit as st
import pandas as pd

st.set_page_config(page_title="청호방재 필드마스터", layout="wide")
st.title("🚀 청호방재 현장관리 시스템 (클린 버전)")

@st.cache_data
def load_and_clean_data():
    try:
        # 1. 현장 장부 읽기
        site_df = pd.read_excel("data.xlsx")
        
        # 2. 연락처 읽기 및 청소
        contact_df = pd.read_csv("contacts.csv")
        
        # [핵심] 데이터가 하나도 없는(모두 NaN인) 열은 삭제
        contact_df = contact_df.dropna(axis=1, how='all')
        
        # [핵심] 'Unnamed'로 시작하는 쓰레기 열도 삭제
        contact_df = contact_df.loc[:, ~contact_df.columns.str.contains('^Unnamed')]
        
        return site_df, contact_df
    except Exception as e:
        st.error(f"⚠️ 파일을 읽는 중 오류 발생: {e}")
        return None, None

site_df, contact_df = load_and_clean_data()

if site_df is not None and contact_df is not None:
    menu = st.sidebar.radio("메뉴 선택", ["현장별 연락처 조회", "전체 주소록(청소됨)"])

    if menu == "현장별 연락처 조회":
        st.subheader("🔍 현장 담당자 찾기")
        selected_site = st.selectbox("현장을 선택하세요", site_df['현장명'].unique())
        
        # 현장의 관리번호 가져오기
        site_no = site_df[site_df['현장명'] == selected_site]['관리번호'].iloc[0]
        st.write(f"📌 선택된 현장 관리번호: **{site_no}**")

        # 연락처의 'Notes'나 'Custom Field' 등에서 관리번호가 포함된 사람만 필터링
        # (비어있지 않은 칸 중에서 관리번호를 찾습니다)
        def find_match(row):
            text_data = " ".join(row.astype(str))
            return str(site_no) in text_data

        matched = contact_df[contact_df.apply(find_match, axis=1)]
        
        if not matched.empty:
            st.success(f"✅ 연동된 담당자 {len(matched)}명을 찾았습니다.")
            st.dataframe(matched, use_container_width=True)
        else:
            st.warning("이 관리번호와 일치하는 연락처가 없습니다.")

    else:
        st.subheader("📇 전체 주소록 (비어있는 칸 삭제 완료)")
        st.write(f"총 {len(contact_df.columns)}개의 유효한 정보 칸이 남았습니다.")
        st.dataframe(contact_df, use_container_width=True)

else:
    st.info("깃허브에 'data.xlsx'와 'contacts.csv'를 올려주세요.")
