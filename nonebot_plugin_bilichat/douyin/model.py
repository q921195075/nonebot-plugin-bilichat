from pydantic import BaseModel

class json_data(BaseModel):
    id_str: str
    status: int
    status_str: str
    title: str
    user_count_str: str
    cover: dict = {}
    stream_url: dict = {}
    mosaic_status: int
    mosaic_status_str: str
    admin_user_ids: list[int]
    admin_user_ids_str: list[str]
    owner: dict = {}
    room_auth: dict = {}
    live_room_mode: int
    stats: dict = {}
    anchor_name: str