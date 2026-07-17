class DbError(Exception):
    pass


def create_adapter(driver):
    if driver == "mysql":
        from .mysql_adapter import MysqlAdapter
        return MysqlAdapter()
    if driver == "pgsql":
        from .pgsql_adapter import PgsqlAdapter
        return PgsqlAdapter()
    if driver == "sqlite":
        from .sqlite_adapter import SqliteAdapter
        return SqliteAdapter()
    raise DbError(f"unknown DB_DRIVER '{driver}' (expected mysql, pgsql or sqlite)")
