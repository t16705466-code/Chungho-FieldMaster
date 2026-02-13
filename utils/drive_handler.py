import streamlit as st
import pandas as pd
from utils.google_api import get_google_creds
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def get_drive_service():
    """Returns the Google Drive service resource."""
    creds = get_google_creds()
    if not creds:
        return None
    return build('drive', 'v3', credentials=creds)

def get_site_folder_id(site_name, parent_folder_id=None):
    """
    Searches for a folder with the site name.
    If parent_folder_id is provided, searches within that folder.
    """
    service = get_drive_service()
    if not service:
        return None

    query = f"mimeType='application/vnd.google-apps.folder' and name='{site_name}' and trashed=false"
    if parent_folder_id:
        query += f" and '{parent_folder_id}' in parents"

    try:
        results = service.files().list(q=query, fields="files(id, name, webViewLink)").execute()
        files = results.get('files', [])
        if files:
            return files[0]['id']
        return None
    except Exception as e:
        st.error(f"Error searching Google Drive: {e}")
        return None

def create_site_folder(site_name, parent_folder_id=None):
    """Creates a new folder for the site."""
    service = get_drive_service()
    if not service:
        return None

    file_metadata = {
        'name': site_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]

    try:
        file = service.files().create(body=file_metadata, fields='id').execute()
        return file.get('id')
    except Exception as e:
        st.error(f"Error creating folder: {e}")
        return None

def list_files_in_folder(folder_id):
    """Lists all files in a specific folder."""
    service = get_drive_service()
    if not service:
        # Return mock files if no service (for demo)
        return [
            {"name": "Site_Plan_v1.pdf", "mimeType": "application/pdf", "webViewLink": "#"},
            {"name": "Contract_Signed.pdf", "mimeType": "application/pdf", "webViewLink": "#"},
            {"name": "Site_Photo_01.jpg", "mimeType": "image/jpeg", "webViewLink": "#"},
        ]

    query = f"'{folder_id}' in parents and trashed=false"
    try:
        results = service.files().list(q=query, fields="files(id, name, mimeType, webViewLink, iconLink)").execute()
        return results.get('files', [])
    except Exception as e:
        st.error(f"Error listing files: {e}")
        return []

def upload_file_to_drive(file_obj, folder_id):
    """Uploads a Streamlit file object to Google Drive."""
    service = get_drive_service()
    if not service:
        return False

    file_metadata = {'name': file_obj.name, 'parents': [folder_id]}
    # Note: Direct upload like this works for small files. For large files, use resumable upload.
    # Streamlit UploadedFile is a BytesIO-like object.
    
    # We need to save it temporarily to disk or wrap it for MediaFileUpload
    # For simplicity in this demo, we assume small files or improve later.
    # Google API expects a file path or a stream.
    
    try:
        # Basic implementation: requires saving to temp file or using MediaIoBaseUpload
        # For now, just logging the intent
        st.info("Upload logic to be implemented with MediaIoBaseUpload for functionality.")
        return True
    except Exception as e:
        st.error(f"Upload error: {e}")
        return False
