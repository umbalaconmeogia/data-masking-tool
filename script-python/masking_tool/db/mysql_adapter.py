from . import DbError
from .base import DbAdapter


class MysqlAdapter(DbAdapter):
    placeholder = "%s"
    quote_char = "`"

    def connect(self, env):
        try:
            import pymysql
        except ImportError:
            raise DbError("PyMySQL is not installed (pip install PyMySQL)")
        self.connection = pymysql.connect(
            host=env.get("DB_HOST", "127.0.0.1"),
            port=int(env.get("DB_PORT", "3306")),
            database=env["DB_NAME"],
            user=env.get("DB_USER", ""),
            password=env.get("DB_PASSWORD", ""),
            charset=env.get("DB_CHARSET", "utf8mb4"),
        )
        self._db_name = env["DB_NAME"]

    def get_primary_key(self, table):
        cur = self.connection.cursor()
        cur.execute(
            "SELECT column_name FROM information_schema.key_column_usage "
            "WHERE table_schema = %s AND table_name = %s "
            "AND constraint_name = 'PRIMARY' ORDER BY ordinal_position",
            (self._db_name, table),
        )
        pk_columns = [row[0] for row in cur.fetchall()]
        cur.close()
        return pk_columns[0] if len(pk_columns) == 1 else None
