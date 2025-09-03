from fastapi import FastAPI
from api.article_router import router as article_router
from core.set_env import set_env

set_env()


app = FastAPI()

# Include the article router
app.include_router(article_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
