import streamlit as st
import pandas as pd

st.set_page_config(page_title="청호방재 필드마스터", layout="wide")
st.title("🚀 청호방재 현장관리 시스템")

try:
    # 엑셀 파일을 읽어옵니다.
    df = pd.read_excel("data.xlsx")
    st.success("✅ 데이터를 성공적으로 불러왔습니다!")
    
    # 표로 보여주기
    st.dataframe(df, use_container_width=True)

except FileNotFoundError:
    st.error("❌ 'data.xlsx' 파일을 찾을 수 없습니다. 깃허브에 파일을 올리셨나요?")
except Exception as e:
    st.error(f"❌ 에러 발생: {e}")
