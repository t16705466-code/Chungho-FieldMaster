import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# Scopes
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_creds():
    """
    Returns Credentials object from st.secrets or local file.
    """
    if "gcp_service_account" in st.secrets:
        return Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=SCOPES
        )
    return None

def get_drive_service():
    """Returns Google Drive Service Resource."""
    creds = get_creds()
    if creds:
        return build('drive', 'v3', credentials=creds)
    return None

def get_sheets_client():
    """Returns gspread Client."""
    creds = get_creds()
    if creds:
        return gspread.authorize(creds)
    return None

# --- Sheets Operations ---
def load_sheet_data(spreadsheet_key, worksheet_name):
    """
    Loads data from a specific worksheet into a DataFrame.
    Assumes header is in the first row (gspread default).
    """
    client = get_sheets_client()
    if not client: return pd.DataFrame()
    
    try:
        sh = client.open_by_key(spreadsheet_key) # Open by ID is safer than name
        ws = sh.worksheet(worksheet_name)
        data = ws.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error loading {worksheet_name}: {e}")
        return pd.DataFrame()

def update_sheet_data(spreadsheet_key, worksheet_name, df):
    """
    Overwrites a worksheet with DataFrame content.
    """
    client = get_sheets_client()
    if not client: return
    
    try:
        sh = client.open_by_key(spreadsheet_key)
        ws = sh.worksheet(worksheet_name)
        ws.clear()
        # gspread expects list of lists, including header
        ws.update([df.columns.values.tolist()] + df.values.tolist())
    except Exception as e:
        st.error(f"Error saving {worksheet_name}: {e}")

# --- Drive Operations ---
def upload_file_to_drive(file_obj, folder_id, filename):
    """
    Uploads a file-like object to Google Drive.
    Returns the file ID and Web View Link.
    """
    service = get_drive_service()
    if not service: return None, None
    
    try:
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        
        media = MediaIoBaseUpload(file_obj, mimetype=file_obj.type, resumable=True)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink, thumbnailLink'
        ).execute()
        return file.get('id'), file.get('webViewLink')
        
    except Exception as e:
        st.error(f"Drive Upload Error: {e}")
        return None, None
