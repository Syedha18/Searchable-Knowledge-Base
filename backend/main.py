from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.search.keyword_search import router as keyword_router
from backend.search.semantic_search import router as semantic_router

app = FastAPI()

# ✅ CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 👈 use "*" for local dev to ensure no restrictions
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers must come AFTER CORS
app.include_router(keyword_router, prefix="/api")
app.include_router(semantic_router, prefix="/api")
