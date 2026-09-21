from drive_utils import is_drive_path, delete_drive_file

def can_delete_post(me, user_id, post):
    return me.get("role") == "admin"

def delete_video_post(sb, post):
    path = post.get("video_path")
    post_id = post.get("id")
    # Primeiro o banco. Se a política ainda não estiver instalada, preserva o arquivo.
    sb.table("athlete_posts").delete().eq("id", post_id).execute()
    if is_drive_path(path):
        delete_drive_file(path)
    elif path:
        try:
            sb.storage.from_("trick-videos").remove([path])
        except Exception:
            pass
