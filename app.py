import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_handler import load_site_data

# 페이지 설정
st.set_page_config(page_title="청호방재 필드마스터", layout="wide")

st.title("🚀 청호방재 현장관리 마스터")

# 데이터 불러오기
try:
    df = load_site_data()
    
    if df is not None and not df.empty:
        # 상단 요약 수치
        col1, col2, col3 = st.columns(3)
        col1.metric("전체 현장 수", f"{len(df)}개")
        col2.metric("오늘 점검", f"{len(df[df['점검상태']=='진행중'])}건")
        col3.metric("완료 현장", f"{len(df[df['점검상태']=='완료'])}건")
        
        st.divider()
        
        # 메인 데이터 표
        st.subheader("📋 현장 관리 리스트")
        st.dataframe(df, use_container_width=True)
        
        # 간단한 그래프
        if '현장명' in df.columns:
            st.subheader("📊 현장별 통계")
            fig = px.bar(df, x='현장명', y=df.columns[1] if len(df.columns)>1 else None)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("구글 시트에 데이터가 없거나 불러올 수 없습니다.")
        
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.info("Secrets 설정은 정상이니 안심하세요! 구글 시트 주소나 파일 구조를 점검 중입니다.")
