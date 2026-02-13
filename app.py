import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
import json

st.set_page_config(page_title="청호방재 필드마스터", layout="wide")
st.title("🚀 청호방재 현장관리 시스템")

def load_data():
    try:
        # 금고에서 한 줄로 된 정보를 가져와서 파싱합니다
        creds_json = st.secrets["GCP_JSON"]
        creds_info = json.loads(creds_json)
        spreadsheet_id = st.secrets["SHEET_ID"]
        
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
        st.error(f"⚠️ 설정 대기 중: {e}")
        st.info("오른쪽 Manage app -> Settings -> Secrets에 값을 넣어주세요.")
        return None

df = load_data()
if df is not None and not df.empty:
    st.success("✅ 실시간 데이터 연동 성공!")
    st.dataframe(df, use_container_width=True)
