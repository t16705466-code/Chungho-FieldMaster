import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_handler import load_site_data

# Page Configuration
st.set_page_config(
    page_title="필드 마스터 프로",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Global Background */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Sidebar Styling - Dark Theme */
    [data-testid="stSidebar"] {
        background-color: #0F172A;
        color: white;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] span, [data-testid="stSidebar"] p {
        color: white !important;
    }
    [data-testid="stSidebar"] a {
        color: #94A3B8 !important;
    }
    [data-testid="stSidebar"] a:hover {
        color: white !important;
        background-color: #1E293B;
    }

    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #E2E8F0;
    }

    /* Custom Project Card */
    .project-card {
        background-color: white;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        transition: transform 0.2s, box-shadow 0.2s;
        margin-bottom: 20px;
    }
    .project-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    
    /* Badges */
    .badge {
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border: 1px solid transparent;
    }
    .badge-ongoing { background-color: #EFF6FF; color: #2563EB; border-color: #DBEAFE; }
    .badge-estimate { background-color: #F1F5F9; color: #64748B; border-color: #E2E8F0; }
    .badge-completed { background-color: #F0FDF4; color: #16A34A; border-color: #DCFCE7; }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("🏗️ 필드 마스터 프로")
st.sidebar.markdown("---")
# Only show Site Detail link, Dashboard is main
# st.sidebar.page_link("app.py", label="📊 대시보드", icon="📊")
st.sidebar.page_link("pages/현장_상세.py", label="📋 현장 상세", icon="📋")

st.sidebar.markdown("---")

# Main Content: Dashboard
# st.title("📊 프로젝트 대시보드") # Removed old title

# Custom Header with Company Branding
st.markdown("""
<div style="text-align: center; margin-bottom: 40px; background-color: #FFFFFF; padding: 20px;">
    <!-- Logo Placeholder or Icon if available -->
    <div style="font-size: 60px; margin-bottom: 20px;">🐦</div> 
    <h3 style="font-size: 24px; color: #000000; margin: 0; font-weight: 700; letter-spacing: -0.5px;">위험물 관련 전문 기업</h3>
    <h1 style="font-size: 48px; color: #000000; margin: 10px 0 0 0; font-weight: 900; letter-spacing: 2px;">청 호 방 재</h1>
</div>
""", unsafe_allow_html=True)


from utils.data_handler import load_all_data, save_all_data

# ... (Previous Config & CSS remains) ...

# Load Data
data = load_all_data()
df = data['master']

# ID Based Classification
# Ongoing: Contains '-' (e.g., 25-01)
# Estimate: 6 digits (e.g., 260210)
df['is_ongoing'] = df['site_mgmt_id'].astype(str).str.contains('-')
df['is_estimate'] = df['site_mgmt_id'].astype(str).str.len() == 6

ongoing_df = df[df['is_ongoing']]
estimate_df = df[df['is_estimate']]

# Metrics Row
col1, col2, col3, col4 = st.columns(4)

total_projects = len(df)
ongoing_count = len(ongoing_df)
estimate_count = len(estimate_df)
completed_count = len(df[df['status'] == '완공']) # Keep status check for completed?

with col1:
    st.metric("총 프로젝트", total_projects)
with col2:
    st.metric("진행 중 (Ongoing)", ongoing_count)
with col3:
    st.metric("견적 중 (Estimate)", estimate_count)
with col4:
    st.metric("완공", completed_count)

st.markdown("---")

# Recent Lists (Split by Type)
c1, c2 = st.columns(2)

with c1:
    st.subheader("🚀 진행 중 현장 (Recent)")
    recent_ongoing = ongoing_df.sort_values('site_mgmt_id', ascending=False).head(5)
    for _, site in recent_ongoing.iterrows():
        label = f"[{site['site_mgmt_id']}] {site['site_name']}"
        if st.button(label, key=f"ongoing_{site['site_mgmt_id']}", use_container_width=True):
            st.session_state['selected_site_id'] = site['site_mgmt_id']
            st.switch_page("pages/현장_상세.py")

with c2:
    st.subheader("📄 견적 중 현장 (Recent)")
    recent_estimate = estimate_df.sort_values('site_mgmt_id', ascending=False).head(5)
    for _, site in recent_estimate.iterrows():
        label = f"[{site['site_mgmt_id']}] {site['site_name']}"
        if st.button(label, key=f"est_{site['site_mgmt_id']}", use_container_width=True):
            st.session_state['selected_site_id'] = site['site_mgmt_id']
            st.switch_page("pages/현장_상세.py")

st.markdown("---")

# Full List Table
st.subheader("📋 전체 현장 목록")

# Filter
filter_type = st.radio("보기 선택", ["전체", "진행중", "견적중"], horizontal=True)
if filter_type == "진행중":
    display_df = ongoing_df
elif filter_type == "견적중":
    display_df = estimate_df
else:
    display_df = df

st.dataframe(
    display_df[['site_mgmt_id', 'site_name', 'company_name', 'status', 'contract_amount']],
    column_config={
        "site_mgmt_id": "관리번호",
        "site_name": "현장명",
        "company_name": "업체명",
        "status": "상태",
        "contract_amount": "계약금액"
    },
    use_container_width=True,
    hide_index=True
)
