import streamlit as st
import pandas as pd
import plotly.express as px
from google.oauth2 import service_account
import gspread

# 1. 화면 제목
st.set_page_config(page_title="청호방재 필드마스터", layout="wide")
st.title("🚀 청호방재 현장관리 시스템")

# 2. 구글 시트 연결 (Secrets만 믿고 갑니다)
def load_data():
    try:
        # 사장님이 설정한 Secrets 정보를 가져옴
        creds_info = st.secrets["gcp_service_account"]
        spreadsheet_id = st.secrets["connections"]["spreadsheet_id"]
        
        creds = service_account.Credentials.from_service_account_info(creds_info)
        scoped_creds = creds.with_scopes([
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ])
        client = gspread.authorize(scoped_creds)
        
        # 시트 열기
        sh = client.open_by_key(spreadsheet_id)
        worksheet = sh.get_worksheet(0)
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"연결 오류 발생: {e}")
        return None

# 3. 화면에 데이터 뿌리기
df = load_data()

if df is not None and not df.empty:
    st.success("✅ 구글 시트와 성공적으로 연결되었습니다!")
    st.dataframe(df, use_container_width=True)
    
    # 상태별 그래프 (열 이름에 맞게 자동 조정)
    status_col = '점검상태' if '점검상태' in df.columns else df.columns[-1]
    fig = px.pie(df, names=status_col, title="현장 진행 현황")
    st.plotly_chart(fig)
else:
    st.info("데이터를 불러오는 중입니다...")
