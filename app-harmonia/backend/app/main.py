from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.http.auth_router import router as auth_router
from app.adapters.http.tool_router import router as tool_router
from app.adapters.http.user_router import router as user_router

app = FastAPI(title='Backend Projeto HarmonIA', version='0.0.1')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:4200',
        'http://200.17.199.216',
        'http://200.17.199.216:4200',
        'http://localhost',
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(tool_router)
