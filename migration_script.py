import os
import json
import psycopg2
import importlib

import database.python as py_scripts


def execute_sql_scripts(conn, migration_type, scripts):
    sqls = [sql_file for sql_file in scripts if
            os.path.isfile(os.path.join(os.getcwd(), "database", migration_type, sql_file))]

    cur = conn.cursor()
    for filename in sorted(sqls):
        with open(os.path.join(os.getcwd(), "database", "setup", filename)) as f:
            script = str(f.read())
            try:
                cur.execute(script)
                con.commit()
            except Exception as e:
                print(e)
    cur.close()


def execute_python_scripts(conn, scripts):
    for filename in scripts:
        module = importlib.import_module(f"database.python.{filename}")
        module.transform(conn)


config_filename = os.path.join(os.getcwd(), 'config', f'{os.environ["FLASK_ENV"]}.py')
try:
    with open(config_filename, mode="rb") as config_file:
        exec(compile(config_file.read(), config_filename, "exec"))
except IOError as e:
    print(e)

if os.path.isfile("migration.json"):
    con = psycopg2.connect(dbname=DATABASE_NAME, user=DATABASE_USER,
                           host=DATABASE_URL, port=DATABASE_PORT,
                           password=DATABASE_PASSWORD)
    migrations = {}
    with open("migration.json") as migrations_file:
        migrations = json.load(migrations_file)

    if len(migrations["setup"]) > 0:
        execute_sql_scripts(con, "setup", migrations["setup"])
    if len(migrations["setup_data"]) > 0:
        execute_sql_scripts(con, "setup_data", migrations["setup_data"])
    if len(migrations["scripts"]) > 0:
        execute_python_scripts(con, migrations["scripts"])

    con.close()
    #os.remove("migration.json")

print("Migrations done")
