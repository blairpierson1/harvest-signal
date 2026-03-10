from dotenv import load_dotenv

load_dotenv()  # Load .env file before anything else reads os.environ

import logging  # noqa: E402

from app.logging_config import setup_logging  # noqa: E402

setup_logging()

logger = logging.getLogger(__name__)

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from slowapi import _rate_limit_exceeded_handler  # noqa: E402
from slowapi.errors import RateLimitExceeded  # noqa: E402

from app.dependencies import ALLOWED_ORIGINS, limiter, log_startup_warnings  # noqa: E402
from app.routes import router  # noqa: E402

app = FastAPI(title="Harvest Signal API", version="1.0.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(router)

log_startup_warnings()

logger.info("Harvest Signal API starting")
