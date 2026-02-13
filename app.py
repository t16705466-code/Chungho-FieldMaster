import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account

# 1. 페이지 제목 및 레이아웃
st.set_page_config(page_title="청호방재 필드마스터", layout="wide")
st.title("🚀 청호방재 현장관리 시스템")

# 2. 구글 시트 연결 (금고에서 하나씩 꺼내 쓰기)
def load_data():
    try:
        # 금고(Secrets)의 [gcp_service_account] 구역에서 정보를 가져옴
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
        st.error(f"⚠️ 연결 대기 중: {e}")
        return None

# 3. 데이터 화면 표시
df = load_data()
if df is not None and not df.empty:
    st.success("✅ 실시간 데이터 연동 성공!")
    st.subheader("📋 현장 관리 리스트")
    st.dataframe(df, use_container_width=True)
else:
    st.info("💡 오른쪽 아래 'Manage app' -> 'Settings' -> 'Secrets'에 열쇠를 다시 넣어주세요!")
