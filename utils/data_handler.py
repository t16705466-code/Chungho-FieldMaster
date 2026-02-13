import streamlit as st
import pandas as pd
from utils.google_api import load_sheet_data, update_sheet_data

# Keys from Secrets
SPREADSHEET_ID = st.secrets["connections"]["spreadsheet_id"]

# Column Mapping (Master DB)
MASTER_COLUMN_MAPPING = {
    "site_mgmt_id": "관리번호",
    "jurisdiction": "관할서",
    "site_name": "현장명",
    "company_address": "사업장주소",
    "site_address": "현장주소",
    "status": "진행상태",
    "contract_price": "계약금액",
    "vat": "부가세",
    "contract_amount": "총 계약금액",
    "down_payment": "선수금",
    "interim_payment": "중도금",
    "balance_payment": "잔금",
    "progress": "진행률",
    "designer": "설계담당자",
    "permit_staff": "인허가담당자",
    "company_name": "업체명",
    "facility_name": "시설명칭",
    "permit_volume": "허가량",
    "multiple": "지정수량배수",
    "start_date": "시작일",
    "photos": "사진수",
    "issues": "이슈수",
    "jibun_address": "지번주소"
}

REVERSE_MASTER = {v: k for k, v in MASTER_COLUMN_MAPPING.items()}
# Sub DB Mappings
CONTACT_MAPPING = {"site_mgmt_id": "관리번호", "role": "직함", "name": "이름", "phone": "연락처", "email": "이메일", "note": "비고"}
WORK_MAPPING = {"site_mgmt_id": "관리번호", "date": "상담일", "type": "업무형태", "content": "상담내용", "attachment": "첨부파일", "detail": "상세내용"}

REVERSE_CONTACT = {v: k for k, v in CONTACT_MAPPING.items()}
REVERSE_WORK = {v: k for k, v in WORK_MAPPING.items()}

def load_all_data():
    """Loads all sheets from Google Sheets."""
    if 'db_data' in st.session_state:
        return st.session_state['db_data']

    data = {'master': pd.DataFrame(), 'contacts': pd.DataFrame(), 'works': pd.DataFrame()}

    # 1. Master DB
    df_m = load_sheet_data(SPREADSHEET_ID, "Master_DB")
    if not df_m.empty:
        df_m = df_m.rename(columns=REVERSE_MASTER)
        # Ensure site_mgmt_id is string
        if 'site_mgmt_id' in df_m.columns:
            df_m['site_mgmt_id'] = df_m['site_mgmt_id'].astype(str)
        # Defaults
        for col in ['progress', 'photos', 'issues']:
            if col not in df_m.columns: df_m[col] = 0
    data['master'] = df_m

    # 2. Contact DB
    df_c = load_sheet_data(SPREADSHEET_ID, "연락처_DB")
    if not df_c.empty:
        df_c = df_c.rename(columns=REVERSE_CONTACT)
        if 'site_mgmt_id' in df_c.columns:
            df_c['site_mgmt_id'] = df_c['site_mgmt_id'].astype(str)
    data['contacts'] = df_c

    # 3. Work DB
    df_w = load_sheet_data(SPREADSHEET_ID, "Work_DB")
    if not df_w.empty:
        df_w = df_w.rename(columns=REVERSE_WORK)
        if 'site_mgmt_id' in df_w.columns:
            df_w['site_mgmt_id'] = df_w['site_mgmt_id'].astype(str)
    data['works'] = df_w

    st.session_state['db_data'] = data
    return data

def format_phone(phone):
    """Standardizes phone numbers."""
    if not isinstance(phone, str): return str(phone) if phone else ""
    digits = ''.join(filter(str.isdigit, phone))
    if len(digits) == 11 and digits.startswith("010"):
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    return phone

def apply_business_logic(data):
    """Applies Auto-Status and Financial Calculations."""
    df_m = data['master']
    for idx, row in df_m.iterrows():
        sid = str(row.get('site_mgmt_id', ''))
        # Auto-Status
        if '-' in sid and len(sid.split('-')) == 2:
            df_m.at[idx, 'status'] = '진행중'
        elif len(sid) == 6 and sid.isdigit():
            df_m.at[idx, 'status'] = '견적중'
            
        # Financials
        try:
            contract = float(str(row.get('contract_price', 0)).replace(',', '') or 0)
            vat = contract * 0.1
            total = contract + vat
            down = float(str(row.get('down_payment', 0)).replace(',', '') or 0)
            interim = float(str(row.get('interim_payment', 0)).replace(',', '') or 0)
            balance = total - (down + interim)
            
            df_m.at[idx, 'vat'] = vat
            df_m.at[idx, 'contract_amount'] = total
            df_m.at[idx, 'balance_payment'] = balance
        except: pass
    data['master'] = df_m
    return data

def save_all_data(data):
    """Saves data back to Google Sheets."""
    data = apply_business_logic(data)
    st.session_state['db_data'] = data
    
    # 1. Master
    df_m = data['master'].copy()
    df_m = df_m.rename(columns=MASTER_COLUMN_MAPPING)
    update_sheet_data(SPREADSHEET_ID, "Master_DB", df_m)
    
    # 2. Contacts
    df_c = data['contacts'].copy()
    if 'phone' in df_c.columns:
        df_c['phone'] = df_c['phone'].apply(format_phone)
    df_c = df_c.rename(columns={v: k for k, v in CONTACT_MAPPING.items() if k in df_c.columns})
    update_sheet_data(SPREADSHEET_ID, "연락처_DB", df_c)
    
    # 3. Work
    df_w = data['works'].copy()
    df_w = df_w.rename(columns={v: k for k, v in WORK_MAPPING.items() if k in df_w.columns})
    update_sheet_data(SPREADSHEET_ID, "Work_DB", df_w)

def load_site_data(): return load_all_data()['master']
def save_site_data(df): 
    d = load_all_data()
    d['master'] = df
    save_all_data(d)
