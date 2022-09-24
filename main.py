from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
from fastapi.background import BackgroundTasks
import os
from starlette.requests import Request
import requests

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)
redis = get_redis_connection(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True,
)


class Order(HashModel):
    game_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str

    class Meta:
        database = redis


@app.get('/orders/{pk}')
def get(pk: str):
    return Order.get(pk)


@app.post('/orders')
async def create(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()

    req = requests.get('http://127.0.0.1:8000/games/%s' % body['id'])
    game = req.json()

    # order = Order(
    #     game_id=body['id'],
    #     price=game['price'],
    #     fee=0.2*game['price'],
    #     total=1.2*game['price'],
    #     quantity=body['quantity'],
    #     genre=game['genre'],
    #     status='pending',
    # )
    # order.save()
    #
    # background_tasks.add_task(order_completed, order)

    return req.json()


def order_completed(order: Order):
    order.status = 'completed',
    order.save()