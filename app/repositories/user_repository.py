import psycopg
from typing import List, Dict


def repository_get_user_by_id(connection: psycopg.Connection, uuid: str) -> Dict:
	with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
		cur.execute(
			"SELECT uuid, username, display_name, email, permissions_level FROM sloth_users WHERE uuid = %s",
			(uuid,))
		return cur.fetchone()


def repository_update_password(connection: psycopg.Connection, uuid: str, password_hash: str) -> bool:
	with connection.cursor() as cur:
		cur.execute(
			"UPDATE sloth_users SET password = %s WHERE uuid = %s",
			(password_hash, uuid))
	connection.commit()
	return True


def repository_get_password(connection: psycopg.Connection, uuid: str) -> List:
	with connection.cursor() as cur:
		cur.execute(
			"SELECT password FROM sloth_users WHERE uuid = %s",
			(uuid,))
		return cur.fetchone()
