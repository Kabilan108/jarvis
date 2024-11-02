from pydantic import BaseModel, Field


class APIResponse(BaseModel):
    data: dict | None = Field(
        None,
        description="Payload to be returned to the user. Populated by endpoints that need to return data.",
    )
    error: str | None = Field(
        None, description="Error messages from caught exceptions."
    )
    message: str | None = Field(None, description="Response message to the user.")


class ChatMetadata(BaseModel):
    sender: int
    chat_id: int
    message: str | None


class TelegramMessage(BaseModel):
    chat_id: str = Field(..., description="The chat ID (user/group/channel/bot)")
    message: str = Field(..., description="The message to send")
