from fastapi import FastAPI
from user import endpoints
from receipt.endpoints import router
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

app = FastAPI()



app.include_router(endpoints.router)
app.include_router(router)
    
    
origins = [
    'http://localhost:8000',
    'http://localhost:3000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*']
)


app.mount('/media', StaticFiles(directory='media'), name='media')

add_pagination(app)