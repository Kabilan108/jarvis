from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Security,
    status,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from typing import List, Optional
from datetime import datetime

from common.schema import APIResponse, TelegramAttachment
from common.logger import get_api_logger
from common.bot import get_bot_instance
from common.settings import settings


# TODO: implement some middleware that allows you to log request duration (with some
#       metadata) to logfire. use logfire.metric_histogram
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
bot = get_bot_instance()
logger = get_api_logger(app)

api_key_header = Security(APIKeyHeader(name="X-API-Key", auto_error=False))


def get_api_key(api_key: str = api_key_header):
    if api_key == settings.API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


@app.get("/health", status_code=status.HTTP_200_OK)
async def health(api_key: Optional[str] = api_key_header) -> dict:
    return {
        "application": settings.NAME,
        "version": settings.VERSION,
        "current_time": datetime.now().isoformat(),
        "authenticated": api_key is not None,
    }


@app.post("/send-message", response_model=APIResponse, status_code=status.HTTP_200_OK)
async def send_message(
    chat_id: int = Form(...),
    message: Optional[str] = Form(None),
    files: List[UploadFile] = File(None),
    api_key: str = Depends(get_api_key),
):
    try:
        if not files and not message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either message or files must be provided",
            )

        responses = []

        # Send text message if provided
        if message:
            logger.info(
                "Sending message to {chat_id=}",
                chat_id=chat_id,
                message=message,
            )
            await bot.send_message(chat_id=chat_id, text=message)
            responses.append("Text message sent")

        # Process attachments if any
        if files:
            for file in files:
                attachment = TelegramAttachment(file)
                file_content = await file.read()

                # Check if file is empty
                if len(file_content) == 0:
                    responses.append(f"File {file.filename} is empty - skipped")
                    continue

                try:
                    if attachment.is_image:
                        await bot.send_photo(
                            chat_id=chat_id, photo=file_content, filename=file.filename
                        )
                        responses.append(f"Image {file.filename} sent")

                    elif attachment.is_video:
                        await bot.send_video(
                            chat_id=chat_id, video=file_content, filename=file.filename
                        )
                        responses.append(f"Video {file.filename} sent")

                    elif attachment.is_audio:
                        await bot.send_audio(
                            chat_id=chat_id, audio=file_content, filename=file.filename
                        )
                        responses.append(f"Audio {file.filename} sent")

                    else:
                        await bot.send_document(
                            chat_id=chat_id,
                            document=file_content,
                            filename=file.filename,
                        )
                        responses.append(f"Document {file.filename} sent")

                finally:
                    # Reset file cursor for potential reuse
                    await file.seek(0)

        return {"message": "; ".join(responses)}

    except Exception as e:
        logger.error("Error sending message: {error=}", error=str(e), _exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
