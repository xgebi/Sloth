import os
import json
import psycopg2
import importlib
from pathlib import Path


def execute_sql_scripts(conn, migration_sql):
    cur = conn.cursor()

    with open(os.path.join(os.getcwd(), "database", migration_sql['folder'], migration_sql['file'])) as f:
        script = str(f.read())
        try:
            cur.execute(script)
            con.commit()
        except Exception as e:
            print(e)
    cur.close()


def execute_python_scripts(conn, migration_py):
    module = importlib.import_module(f"database.python.{migration_py['file']}")
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
    migrations = []
    with open("migration.json") as migrations_file:
        migrations = json.load(migrations_file)

    for migration in migrations:
        if os.environ["FLASK_ENV"] == "development":
            answer = input(f"Should process {migration['file']}? (y/N)")
            if answer.lower() != 'y':
                continue

        if os.environ['FLASK_ENV'] == "production":
            migrated_path = os.path.join(os.getcwd(), "migrated")
            if not Path(migrated_path).is_file():
                with open(migrated_path, 'w') as f:
                    f.write('')
            with open(migrated_path) as f:
                content = f.readlines()
            content = [x.strip() for x in content]
            if migration['file'] in content:
                continue

        if migration["type"] == "sql":
            execute_sql_scripts(con, migration)
        if migration["type"] == "py":
            execute_python_scripts(con, migration)
        print(f"Processed {migration['file']}")

        if os.environ['FLASK_ENV'] == "production":
            migrated_path = os.path.join(os.getcwd(), "migrated")
            with open(migrated_path, 'a') as f:
                f.write(migration['file'])

    con.close()
    if os.environ["FLASK_ENV"] != "development":
        os.remove("migration.json")

print("\nMigrations done")
