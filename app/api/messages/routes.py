from flask import request, abort, make_response
import json
from psycopg2 import sql

from app.authorization.authorize import authorize_rest
from app.utilities.db_connection import db_connection

from app.api.messages import messages

reserved_folder_names = ('tag', 'category')


@messages.route("/api/messages/delete", methods=["POST", "PUT", "DELETE"])
@authorize_rest(0)
@db_connection
def delete_message(*args, connection, **kwargs):
    if connection is None:
        abort(500)

    filled = json.loads(request.data)
    cur = connection.cursor()
    try:
        cur.execute(
            sql.SQL("DELETE FROM sloth_messages WHERE uuid = %s"), [filled["message_uuid"]]
        )
        connection.commit()
        response = make_response(json.dumps({"cleaned": False}))
        code = 204
    except Exception as e:
        print(e)
        response = make_response(json.dumps({"cleaned": False}))
        code = 500

    response.headers['Content-Type'] = 'application/json'
    return response, code
