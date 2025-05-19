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

@app.post("/api/dashboard-information")
def handle_login():
	data = {
		"post_types": [
			{
				"uuid": "1adbec5d-f4a1-401d-9274-3552f1219f36",
				"slug": "post",
				"display_name": "Post",
				"tags_enabled": True,
				"categories_enabled": True,
				"archive_enabled": True
			},
			{
				"uuid": "f00b6733-d38b-489d-90cc-76e7c4dc1651",
				"slug": "page",
				"display_name": "Page",
				"tags_enabled": True,
				"categories_enabled": True,
				"archive_enabled": False
			},
			{
				"uuid": "fa0404fb-ca02-465a-a2e3-08005825acd7",
				"slug": "desk",
				"display_name": "Desk",
				"tags_enabled": True,
				"categories_enabled": True,
				"archive_enabled": True
			},
			{
				"uuid": "2cbcc010-d8ea-4af4-b9ba-072b94ead93d",
				"slug": "today-i-learned",
				"display_name": "Today I Learned",
				"tags_enabled": True,
				"categories_enabled": False,
				"archive_enabled": True
			},
			{
				"uuid": "6fbd6b52-25db-4ec0-9750-00a11b83c033",
				"slug": "vlog",
				"display_name": "Vlog",
				"tags_enabled": True,
				"categories_enabled": True,
				"archive_enabled": True
			},
			{
				"uuid": "beef636c-1303-44c7-a796-8374ace19e9c",
				"slug": "case-studies",
				"display_name": "Case studies",
				"tags_enabled": True,
				"categories_enabled": True,
				"archive_enabled": True
			}
		],
		"recentPosts": [
			{
				"uuid": "1b344974-7370-43c2-a4c5-ea9632207a92",
				"title": "December Bullet Journal | plan with me | minimalistic",
				"publishDate": 1690897140000,
				"formattedPublishDate": "2023-08-01 16:39"
			},
			{
				"uuid": "59f9bf87-6930-4e2b-b36f-037fb7f61f9c",
				"title": "October Bullet Journal Planning",
				"publishDate": 1690897080000,
				"formattedPublishDate": "2023-08-01 16:38"
			},
			{
				"uuid": "372334a7-7ddc-4932-82ed-96d573244f38",
				"title": "Monday notes 2023-07-31",
				"publishDate": 1690828652540.7632,
				"formattedPublishDate": "2023-07-31 21:37"
			},
			{
				"uuid": "5d40862c-59d4-47d3-8b87-364708f83e08",
				"title": "Montagsnotizen 2023-06-12",
				"publishDate": 1686602053449.4263,
				"formattedPublishDate": "2023-06-12 23:34"
			},
			{
				"uuid": "b64e5018-9063-4fbb-bac4-27c2d3b23b9c",
				"title": "Monday notes 2023-06-12",
				"publishDate": 1686601920000,
				"formattedPublishDate": "2023-06-12 23:32"
			},
			{
				"uuid": "30972675-87c7-4934-a7e5-5419aa3e9c97",
				"title": "Escogiendo React Native",
				"publishDate": 1686303106758.6062,
				"formattedPublishDate": "2023-06-09 12:31"
			},
			{
				"uuid": "78cbca92-d88b-47bb-94e8-567709a4a910",
				"title": "React Native wählen",
				"publishDate": 1686303015706.763,
				"formattedPublishDate": "2023-06-09 12:30"
			},
			{
				"uuid": "aa5b7ea9-a4e2-4182-98de-20b701bedf10",
				"title": "Choosing React Native",
				"publishDate": 1686302880000,
				"formattedPublishDate": "2023-06-09 12:28"
			},
			{
				"uuid": "0acc0194-bb64-4ab9-b227-b5af6febc536",
				"title": "Montagsnotizen 2023-06-05",
				"publishDate": 1686085416144.4612,
				"formattedPublishDate": "2023-06-07 00:03"
			},
			{
				"uuid": "f2540f01-10c5-47d6-8e33-e7c011b620f5",
				"title": "Monday notes 2023-06-05",
				"publishDate": 1686032520000,
				"formattedPublishDate": "2023-06-06 09:22"
			}
		],
		"upcomingPosts": [],
		"drafts": [
			{
				"uuid": "71ff1c86-5c98-480e-a810-4adb55b3e18a",
				"title": "Notas de lunes 2023-06-12",
				"publishDate": 1686602244712.2507,
				"formattedPublishDate": "2023-06-12 23:37"
			},
			{
				"uuid": "aa037ba1-fcbf-47f6-a720-4fb3ba192088",
				"title": "Monday Batch of Links #6",
				"publishDate": 1661887721981.1248,
				"formattedPublishDate": "2022-08-30 22:28"
			},
			{
				"uuid": "4e258461-a5af-40af-a508-7cde41a44f93",
				"title": "A look back, 2023 edition",
				"publishDate": 1661169120627.9553,
				"formattedPublishDate": "2022-08-22 14:52"
			},
			{
				"uuid": "27f601e2-286a-4a39-ad70-5230d6632932",
				"title": "A look back, 2022 edition",
				"publishDate": 1661169091775.515,
				"formattedPublishDate": "2022-08-22 14:51"
			},
			{
				"uuid": "728242c3-0cee-4b1f-b8d3-da835bb9d77e",
				"title": "Monday Batch of Links #7",
				"publishDate": 1656587722252.1404,
				"formattedPublishDate": "2022-06-30 14:15"
			},
			{
				"uuid": "f2cbed7e-65cb-4472-87e1-792259f5cf1b",
				"title": "Data Sci Adventures - part 5: RSS scraping in Ruby",
				"publishDate": 1656452021618.229,
				"formattedPublishDate": "2022-06-29 00:33"
			},
			{
				"uuid": "85fd459f-2647-4372-8d2b-53dfdc360aa6",
				"title": "Tusee - services architecture",
				"publishDate": 1654096406280.8916,
				"formattedPublishDate": "2022-06-01 18:13"
			},
			{
				"uuid": "6c308c01-1c58-48e9-9acf-4b1efe9bc4b5",
				"title": "Going forward",
				"publishDate": 1652047397460.3306,
				"formattedPublishDate": "2022-05-09 01:03"
			},
			{
				"uuid": "97d32bf8-d2d6-4573-b404-43f39cc66801",
				"title": "[to be deleted] Monday Batch of Links #6",
				"publishDate": 1650007003221.1985,
				"formattedPublishDate": "2022-04-15 10:16"
			},
			{
				"uuid": "9a3deba1-1a94-4dd0-b4a1-a66fdfa35a17",
				"title": "[to be deleted] Monday Batch of Links #6",
				"publishDate": 1650006970008.631,
				"formattedPublishDate": "2022-04-15 10:16"
			}
		],
		"messages": [
			{
				"uuid": "6974de1b-c517-4148-9429-f8c95f108b2f",
				"sentDate": "2023-03-24 06:38",
				"status": "read"
			},
			{
				"uuid": "e0b5fa10-b9f4-49e2-922c-2094aabe4870",
				"sentDate": "2023-01-09 04:53",
				"status": "read"
			},
			{
				"uuid": "30c83fc0-d7b7-4b20-89e5-33dc22cfc6d6",
				"sentDate": "2023-01-09 04:53",
				"status": "read"
			},
			{
				"uuid": "c81636bd-ef04-4e96-be3a-e1d03b237bb6",
				"sentDate": "2023-01-09 04:53",
				"status": "read"
			},
			{
				"uuid": "396ba539-9510-44f4-a1f3-8d6bfea57587",
				"sentDate": "2022-12-01 11:32",
				"status": "read"
			},
			{
				"uuid": "007535e9-db2a-492e-80e5-e99810379709",
				"sentDate": "2022-10-13 08:15",
				"status": "read"
			},
			{
				"uuid": "1cb692d6-40db-44e3-9bcd-7b6fe1c18cf2",
				"sentDate": "2022-09-16 17:31",
				"status": "read"
			},
			{
				"uuid": "17031a7a-baf8-4f5b-aea1-109a5b748055",
				"sentDate": "2022-09-15 09:42",
				"status": "read"
			},
			{
				"uuid": "e816ffce-dfb7-47dc-b8ec-423f87b2f378",
				"sentDate": "2022-09-07 17:23",
				"status": "read"
			},
			{
				"uuid": "ba1bc5b0-728a-4791-9141-77458e58ff07",
				"sentDate": "2022-07-31 11:10",
				"status": "read"
			}
		]
	}

	json_str = json.dumps(data, indent=4, default=str)
	return Response(content=json_str, media_type='application/json')




if __name__ == "__main__":
	uvicorn.run(app, port=5000)

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}