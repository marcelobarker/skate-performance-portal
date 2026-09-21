import streamlit as st
from google.oauth2 import service_account
from google.auth.transport.requests import Request, AuthorizedSession

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

@st.cache_data(ttl=3600, show_spinner=False)
def drive_video_metadata(path_or_id):
    """Lê largura/altura/duração do vídeo no Drive para montar o player responsivo."""
    fid = drive_file_id(path_or_id) or path_or_id
    try:
        creds = get_drive_credentials()
        session = AuthorizedSession(creds)
        r = session.get(
            f"https://www.googleapis.com/drive/v3/files/{fid}",
            params={"fields": "id,name,mimeType,videoMediaMetadata", "supportsAllDrives": "true"},
            timeout=15,
        )
        r.raise_for_status()
        meta = r.json().get("videoMediaMetadata") or {}
        return {
            "width": int(meta.get("width") or 0),
            "height": int(meta.get("height") or 0),
            "durationMillis": int(meta.get("durationMillis") or 0),
        }
    except Exception:
        return {"width":0,"height":0,"durationMillis":0}

def drive_player_geometry(path_or_id):
    m=drive_video_metadata(path_or_id)
    w,h=m.get("width",0),m.get("height",0)
    if w and h and h>w:
        return {"max_width": 360, "aspect": f"{w}/{h}", "orientation": "vertical"}
    if w and h:
        return {"max_width": 525, "aspect": f"{w}/{h}", "orientation": "horizontal"}
    return {"max_width": 525, "aspect": "16/9", "orientation": "unknown"}

def delete_drive_file(path_or_id):
    """Remove definitivamente um vídeo do Google Drive usando a service account."""
    fid = drive_file_id(path_or_id) or path_or_id
    if not fid:
        return False
    creds = get_drive_credentials()
    session = AuthorizedSession(creds)
    r = session.delete(
        f"https://www.googleapis.com/drive/v3/files/{fid}",
        params={"supportsAllDrives": "true"},
        timeout=30,
    )
    if r.status_code not in (200, 204):
        raise RuntimeError(f"Google Drive recusou a exclusão ({r.status_code}).")
    drive_video_metadata.clear()
    return True
