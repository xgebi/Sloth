from typing import Dict
import bcrypt
import psycopg

from app.repositories.user_repository import repository_get_user_by_id, repository_update_password, \
	repository_get_password


def get_user_by_id(connection: psycopg.Connection, uuid: str) -> Dict:
	user = repository_get_user_by_id(connection=connection, uuid=uuid)
	if len(user) > 0:
		return {
			"uuid": user[0],
			"username": user[1],
			"display_name": user[2],
			"email": user[3],
			"permissions_level": user[4]
		}
	return {}


def update_password(connection: psycopg.Connection, uuid: str, password: str) -> bool:
	password_hash = bcrypt.hashpw(password=password.encode('utf8'), salt=bcrypt.gensalt()).decode('utf-8')
	return repository_update_password(connection=connection, uuid=uuid, password_hash=password_hash)


def verify_password(connection: psycopg.Connection, uuid: str, password: str) -> bool:
	password_list = repository_get_password(connection=connection, uuid=uuid)
	if len(password_list) == 1:
		return bcrypt.checkpw(password=password.encode('utf8'), hashed_password=password_list[0].encode('utf8'))
	return False
