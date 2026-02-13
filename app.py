import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="청호방재 필드마스터", layout="wide")
st.title("🚀 청호방재 현장관리 시스템")

# [보너스] 현재 창고(폴더)에 무슨 파일이 있는지 확인하는 기능
files = os.listdir('.')
st.sidebar.write("📁 현재 서버 파일 목록:", files)

@st.cache_data
def load_and_clean_data():
    try:
        # 파일 이름을 유연하게 찾습니다 (대소문자 구분 없이)
        site_file = next((f for f in files if f.lower() == 'data.xlsx'), None)
        contact_file = next((f for f in files if f.lower() == 'contacts.csv'), None)

        if not site_file or not contact_file:
            st.error(f"❌ 파일을 찾을 수 없습니다. (찾는 파일: data.xlsx, contacts.csv)")
            return None, None

        # 1. 현장 장부 읽기
        site_df = pd.read_excel(site_file)
        
        # 2. 연락처 읽기 및 비어있는 칸 삭제
        contact_df = pd.read_csv(contact_file)
        contact_df = contact_df.dropna(axis=1, how='all') # 데이터 없는 칸 삭제
        contact_df = contact_df.loc[:, ~contact_df.columns.str.contains('^Unnamed')] # 쓰레기 칸 삭제
        
        return site_df, contact_df
    except Exception as e:
        st.error(f"⚠️ 읽기 오류 발생: {e}")
        return None, None

site_df, contact_df = load_and_clean_data()

if site_df is not None and contact_df is not None:
    st.success("✅ 장부와 연락처를 성공적으로 연결했습니다!")
    
    # 관리번호가 있는 칸 찾기 (현장 시트에서 '관리번호'라는 이름의 컬럼이 있는지 확인)
    col_name = '관리번호' if '관리번호' in site_df.columns else site_df.columns[0]
    
    selected_site = st.selectbox("조회할 현장명을 선택하세요", site_df['현장명'].unique())
    site_no = site_df[site_df['현장명'] == selected_site][col_name].iloc[0]
    
    st.write(f"🔢 해당 현장 관리번호: **{site_no}**")
    
    # 연락처에서 관리번호 매칭 (메모나 커스텀 필드 검색)
    def find_match(row):
        return str(site_no) in " ".join(row.astype(str))

    matched = contact_df[contact_df.apply(find_match, axis=1)]
    
    if not matched.empty:
        st.subheader(f"👥 관련 담당자 ({len(matched)}명)")
        st.dataframe(matched, use_container_width=True)
    else:
        st.warning("이 관리번호와 매칭되는 연락처가 주소록에 없습니다.")
else:
    st.warning("창고에 파일이 없거나 이름이 틀립니다. 왼쪽 사이드바의 파일 목록을 확인해 주세요.")
