from time import time
from typing import Union, Dict, Any
import uvicorn
from fastapi import Response
import json
from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()

class LoginData(BaseModel):
	username: str
	password: str

@app.post("/api/login")
def handle_login(login_data: LoginData):
	print(login_data)

	data = {"error": "Unable to login"}

	if login_data.username == "sarah" and login_data.password == "cypress":
		data = {
		  "uuid": "aa562c99-7144-4249-9128-2bc37776ec23",
		  "displayName": "sarah",
		  "token": "da48e60c-824f-4d18-8ecc-65c0546786e9",
		  "expiryTime": time() + 1800,
		  "permissionsLevel": 1
		}

	json_str = json.dumps(data, indent=4, default=str)
	return Response(content=json_str, media_type='application/json')


if __name__ == "__main__":
	uvicorn.run(app, port=5000)

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}