import streamlit as st
import pandas as pd
import plotly.express as px
from google.oauth2 import service_account
import gspread

# 페이지 설정
st.set_page_config(page_title="청호방재 필드마스터", layout="wide")

st.title("🚀 청호방재 현장관리 마스터")

# 구글 시트 연결 함수
def load_data():
    try:
        creds_info = st.secrets["gcp_service_account"]
        spreadsheet_id = st.secrets["connections"]["spreadsheet_id"]
        
        creds = service_account.Credentials.from_service_account_info(creds_info)
        scoped_creds = creds.with_scopes([
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ])
        client = gspread.authorize(scoped_creds)
        
        sh = client.open_by_key(spreadsheet_id)
        worksheet = sh.get_worksheet(0) 
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"연결 오류: {e}")
        return None

# 실행
df = load_data()

if df is not None and not df.empty:
    st.success("✅ 데이터 연동 성공!")
    
    # 상단 요약
    col1, col2 = st.columns(2)
    col1.metric("전체 등록 현장", f"{len(df)}개")
    col2.metric("시스템 상태", "정상")

    st.divider()
    
    # 데이터 표
    st.subheader("📋 실시간 현장 리스트")
    st.dataframe(df, use_container_width=True)
    
    # 그래프
    st.subheader("📊 현황 분석")
    # '점검상태' 컬럼이 있다면 그래프 생성
    status_col = '점검상태' if '점검상태' in df.columns else df.columns[-1]
    fig = px.pie(df, names=status_col, title="현장 진행 현황")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("구글 시트에서 데이터를 불러오고 있습니다...")
