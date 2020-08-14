import os
import json
import psycopg2


config = os.path.join(os.getcwd(), 'config', f'{os.environ["FLASK_ENV"]}.py')

if os.path.isfile("migration.json"):
    con = psycopg2.connect(dbname=config["DATABASE_NAME"], user=config["DATABASE_USER"],
                           host=config["DATABASE_URL"], port=config["DATABASE_PORT"],
                           password=config["DATABASE_PASSWORD"])
    migrations = {}
    with open("migration.json") as migrations_file:
        migrations = json.load(migrations_file)
    for migration_type in migrations:

        sqls = [sql_file for sql_file in migrations[migration_type] if
                os.path.isfile(os.path.join(os.getcwd(), "database", migration_type, sql_file))]

        cur = con.cursor()
        for filename in sorted(sqls):
            with open(os.path.join(os.getcwd(), "database", "setup", filename)) as f:
                script = str(f.read())
                try:
                    cur.execute(script)
                    con.commit()
                except Exception as e:
                    print(e)
    os.remove("migration.json")

print("Migrations done")
