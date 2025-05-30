from fastapi import FastAPI
from app.routes import router
from app import init_db

from app.middleware.rate_limiter import RateLimitMiddleware

app = FastAPI()
app.add_middleware(RateLimitMiddleware, max_calls=50, period=60)
app.include_router(router)

init_db()