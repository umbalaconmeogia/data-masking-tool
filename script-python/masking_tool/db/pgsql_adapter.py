from . import DbError
from .base import DbAdapter


class PgsqlAdapter(DbAdapter):
    placeholder = "%s"
    quote_char = '"'

    def connect(self, env):
        try:
            import psycopg
        except ImportError:
            raise DbError("psycopg is not installed (pip install 'psycopg[binary]')")
        self.connection = psycopg.connect(
            host=env.get("DB_HOST", "127.0.0.1"),
            port=int(env.get("DB_PORT", "5432")),
            dbname=env["DB_NAME"],
            user=env.get("DB_USER", ""),
            password=env.get("DB_PASSWORD", ""),
        )

    def get_primary_key(self, table):
        cur = self.connection.cursor()
        cur.execute(
            "SELECT a.attname "
            "FROM pg_index i "
            "JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey) "
            "WHERE i.indrelid = %s::regclass AND i.indisprimary",
            (table,),
        )
        pk_columns = [row[0] for row in cur.fetchall()]
        cur.close()
        return pk_columns[0] if len(pk_columns) == 1 else None
