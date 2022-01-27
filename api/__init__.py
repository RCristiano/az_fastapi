import logging
from typing import Optional

import mimesis
from azure.functions import (
    AsgiMiddleware,
    Context,
    HttpRequest,
    HttpResponse,
    Out,
)
from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI(
    title="POCFastAPI",
    description="Simple POC for FastAPI on Azure Functions",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Deadpoolio the Amazing",
        "url": "http://x-force.example.com/contact/",
        "email": "dp@x-force.example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    docs_url="/api/doc",
    redoc_url="/api/redoc",
)


class FoodItem(BaseModel):
    id: int
    vegetable: str
    dish: str
    drink: str


@app.get("/food/{food_id}")
async def get_food(food_id: int):
    food = mimesis.Food()
    return food._data


@app.post(
    "/food/",
    status_code=status.HTTP_201_CREATED,
)
async def create_food(food: FoodItem):
    # Write the food item to the database here.
    app.eh.set(food.json())
    return {"status": "ok"}


@app.get("/users/{user_id}")
async def read_item(user_id: int, locale: Optional[str] = None):
    fake_user = mimesis.Person(locale=locale)
    return {
        "user_id": user_id,
        "username": fake_user.username(),
        "fullname": fake_user.full_name(),
        "age": fake_user.age(),
        "firstname": fake_user.first_name(),
        "lastname": fake_user.last_name(),
    }


def main(
    req: HttpRequest, context: Context, eventhub: Out[str]
) -> HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")
    try:
        app.eh = eventhub
        return AsgiMiddleware(app).handle(req, context)
    except Exception as e:
        logging.error(e)
        return HttpResponse(
            status_code=500,
            body=f"Internal server error: {e}",
            headers={"Content-Type": "text/plain"},
        )
