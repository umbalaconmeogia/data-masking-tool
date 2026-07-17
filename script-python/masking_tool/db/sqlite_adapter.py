import sqlite3

from .base import DbAdapter


class SqliteAdapter(DbAdapter):
    placeholder = "?"
    quote_char = '"'

    def connect(self, env):
        self.connection = sqlite3.connect(env["DB_NAME"])

    def get_primary_key(self, table):
        cur = self.connection.execute(f"PRAGMA table_info({self.quote_ident(table)})")
        pk_columns = [row[1] for row in cur.fetchall() if row[5] > 0]
        return pk_columns[0] if len(pk_columns) == 1 else None
