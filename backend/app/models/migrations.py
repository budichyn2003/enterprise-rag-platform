from sqlalchemy import inspect
from sqlalchemy.engine import Connection


_ADDITIVE_COLUMNS = {
    "conversations": {
        "language": "VARCHAR(8) NOT NULL DEFAULT 'id'",
        "updated_at": "DATETIME",
    },
    "messages": {
        "needs_escalation": "BOOLEAN NOT NULL DEFAULT 0",
    },
}


def migrate_legacy_schema(connection: Connection) -> None:
    inspector = inspect(connection)
    tables = set(inspector.get_table_names())
    for table_name, columns in _ADDITIVE_COLUMNS.items():
        if table_name not in tables:
            continue
        present = {column["name"] for column in inspector.get_columns(table_name)}
        for column_name, column_type in columns.items():
            if column_name not in present:
                connection.exec_driver_sql(
                    f'ALTER TABLE "{table_name}" ADD COLUMN "{column_name}" {column_type}'
                )
    if "conversations" in tables:
        connection.exec_driver_sql(
            "UPDATE conversations SET updated_at = created_at WHERE updated_at IS NULL"
        )
