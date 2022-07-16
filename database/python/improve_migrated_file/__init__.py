import os


def transform(connection):
    migrated_path = os.path.join(os.getcwd(), "migrated")
    with open(migrated_path, 'r') as f:
        data = f.read()
    with open(migrated_path, 'w') as f:
        f.write(data.replace(".sql", ".sql\n"))

    return True
