import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread

# 페이지 설정
st.set_page_config(page_title="청호방재 필드마스터", layout="wide")
st.title("🚀 청호방재 현장관리 시스템")

def load_data():
    try:
        # 셋팅창(Secrets)에 저장된 정보를 불러옵니다
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
        st.error(f"연결 대기 중입니다: {e}")
        return None

df = load_data()

if df is not None and not df.empty:
    st.success("✅ 실시간 데이터 연동 성공!")
    st.dataframe(df, use_container_width=True)
else:
    st.info("데이터를 불러오고 있습니다. 잠시만 기다려주세요.")
