from fastapi import FastAPI, Request, HTTPException
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from routers.users import router as users_router
from routers.profiles import router as profiles_router
from routers.tasks import router as tasks_router
import time
from utils.exceptions import (
    validation_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
)

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Scheduler started")
    yield
    print("Scheduler stopped")



app = FastAPI(
    lifespan=lifespan, 
    docs_url="/swagger", 
    title="Todo Application",
    description="This is a small todo app project whit user profile, user auth, tasks ",
    version="0.0.1",
    )


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


origins = [
    "*"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


app.include_router(users_router)
app.include_router(profiles_router)
app.include_router(tasks_router)