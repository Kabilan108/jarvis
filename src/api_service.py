from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader

from core.schema import APIResponse, TelegramMessage
from core.logger import get_api_logger
from core.bot import get_bot_instance
from core.settings import settings


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


def get_api_key(
    api_key: str = Security(APIKeyHeader(name="X-API-Key", auto_error=False)),
):
    if api_key == settings.API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


@app.get("/health", status_code=status.HTTP_200_OK)
async def health() -> dict:
    return {"status": "ok"}


@app.post("/send-message", response_model=APIResponse, status_code=status.HTTP_200_OK)
async def send_message(message: TelegramMessage, api_key: str = Depends(get_api_key)):
    try:
        logger.info(
            "Sending message to {chat_id=}",
            chat_id=message.chat_id,
            message=message.message,
        )
        await bot.send_message(chat_id=message.chat_id, text=message.message)
        return {"message": "Message sent successfully"}
    except Exception as e:
        logger.error("error sending message: {error=}", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
