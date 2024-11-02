from pydantic import BaseModel, Field
from fastapi import UploadFile
import mimetypes


class APIResponse(BaseModel):
    data: dict | None = Field(
        None,
        description="Payload to be returned to the user. Populated by endpoints that need to return data.",
    )
    error: str | None = Field(
        None, description="Error details, including code and message."
    )
    message: str | None = Field(None, description="Response message to the user.")


class ChatMetadata(BaseModel):
    sender: int
    chat_id: int
    message: str | None


class TelegramAttachment:
    def __init__(self, file: UploadFile):
        self.file = file
        self.mime_type = (
            file.content_type
            or mimetypes.guess_type(file.filename)[0]
            or "application/octet-stream"
        )

    @property
    def is_image(self) -> bool:
        return self.mime_type.startswith("image/")

    @property
    def is_video(self) -> bool:
        return self.mime_type.startswith("video/")

    @property
    def is_audio(self) -> bool:
        return self.mime_type.startswith("audio/")
