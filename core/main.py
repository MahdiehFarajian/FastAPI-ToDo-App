from fastapi import FastAPI
from routers.users import router as users_router
from routers.profiles import router as profiles_router


app = FastAPI()

app.include_router(users_router)
app.include_router(profiles_router)