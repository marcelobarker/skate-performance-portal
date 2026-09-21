import streamlit as st
from google.oauth2 import service_account
from google.auth.transport.requests import Request

DRIVE_SCOPE = "https://www.googleapis.com/auth/drive"

def get_drive_credentials():
    info = dict(st.secrets["gcp_service_account"])
    creds = service_account.Credentials.from_service_account_info(info, scopes=[DRIVE_SCOPE])
    creds.refresh(Request())
    return creds

def get_drive_access_token():
    return get_drive_credentials().token

def get_drive_folder_id():
    return str(st.secrets["GOOGLE_DRIVE_FOLDER_ID"])

def is_drive_path(path):
    return isinstance(path, str) and path.startswith("gdrive:")

def drive_file_id(path):
    return path.split(":",1)[1] if is_drive_path(path) else None

def drive_preview_url(path_or_id):
    fid = drive_file_id(path_or_id) or path_or_id
    return f"https://drive.google.com/file/d/{fid}/preview"

def drive_stream_url(path_or_id):
    """URL de mídia para arquivos do Drive publicados como 'qualquer pessoa com o link'."""
    fid = drive_file_id(path_or_id) or path_or_id
    return f"https://drive.usercontent.google.com/download?id={fid}&export=download&confirm=t"
