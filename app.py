import streamlit as st
import pandas as pd

st.set_page_config(page_title="청호방재 필드마스터", layout="wide")
st.title("🚀 청호방재 현장관리 시스템 (엑셀 모드)")

try:
    # 깃허브에 올린 data.xlsx 파일을 읽습니다
    # 첫 번째 시트(index 0)를 가져옵니다
    df = pd.read_excel("data.xlsx", engine='openpyxl')
    st.success("✅ 엑셀 데이터를 성공적으로 불러왔습니다!")
    
    st.metric("전체 등록 현장", f"{len(df)}개")
    st.divider()

    st.subheader("📋 현장 리스트")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"데이터를 불러올 수 없습니다: {e}")
    st.info("깃허브에 'data.xlsx' 파일이 잘 올라가 있는지 확인해주세요.")
