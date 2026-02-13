import streamlit as st
import pandas as pd
import plotly.express as px
from google.oauth2 import service_account
import gspread

# 1. 페이지 설정
st.set_page_config(page_title="청호방재 필드마스터", layout="wide")
st.title("🚀 청호방재 현장관리 시스템 (직접 연결 모드)")

# 2. 구글 시트 직접 연결 함수
def load_data():
    try:
        # 이미 설정하신 Secrets를 사용합니다 (로그인은 되어 있는 상태!)
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
        st.error(f"데이터 연결 중 오류: {e}")
        return None

# 3. 화면 표시
df = load_data()

if df is not None and not df.empty:
    st.success("✅ 직접 연결에 성공했습니다!")
    st.dataframe(df, use_container_width=True)
else:
    st.info("데이터를 불러오는 중입니다... (Secrets 설정을 확인해주세요)")
