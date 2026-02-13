import streamlit as st
import pandas as pd
import plotly.express as px
from google.oauth2 import service_account
import gspread

# 1. 화면 제목 설정
st.set_page_config(page_title="청호방재 필드마스터", layout="wide")
st.title("🚀 청호방재 현장관리 마스터")

# 2. 구글 시트 직접 연결 함수
def load_data():
    try:
        # 설정창(Secrets)에 저장된 열쇠를 사용합니다
        creds_info = st.secrets["gcp_service_account"]
        spreadsheet_id = st.secrets["connections"]["spreadsheet_id"]
        
        creds = service_account.Credentials.from_service_account_info(creds_info)
        scoped_creds = creds.with_scopes([
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ])
        client = gspread.authorize(scoped_creds)
        
        # 장부(시트) 열기
        sh = client.open_by_key(spreadsheet_id)
        worksheet = sh.get_worksheet(0)
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"⚠️ 연결 대기 중: {e}")
        return None

# 3. 데이터 표시하기
df = load_data()

if df is not None and not df.empty:
    st.success("✅ 실시간 데이터 연동 성공!")
    st.dataframe(df, use_container_width=True)
    
    # 간단한 그래프
    status_col = '점검상태' if '점검상태' in df.columns else df.columns[-1]
    fig = px.pie(df, names=status_col, title="현장 진행 현황")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("💡 오른쪽 아래 'Manage app' -> 'Settings' -> 'Secrets'에 열쇠를 넣어주세요!")
