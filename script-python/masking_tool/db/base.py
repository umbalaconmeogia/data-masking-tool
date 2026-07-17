"""Database adapter interface.

Adapters expose keyset-paginated reads and batched UPDATEs by primary key.
Only single-column primary keys are supported; get_primary_key returns None
otherwise and the masker skips the table with an error.
"""
from abc import ABC, abstractmethod


class DbAdapter(ABC):
    placeholder = "%s"
    quote_char = '"'

    @abstractmethod
    def connect(self, env):
        ...

    @abstractmethod
    def get_primary_key(self, table):
        """Column name of the table's single-column PK, or None."""

    def quote_ident(self, name):
        q = self.quote_char
        return f"{q}{name.replace(q, q + q)}{q}"

    def fetch_batch(self, table, pk, columns, after_pk_value, limit):
        """Rows (as tuples: pk value first, then columns) with pk > after_pk_value."""
        cur = self.connection.cursor()
        select_list = ", ".join(self.quote_ident(c) for c in [pk] + columns)
        table_q = self.quote_ident(table)
        pk_q = self.quote_ident(pk)
        if after_pk_value is None:
            cur.execute(
                f"SELECT {select_list} FROM {table_q} "
                f"ORDER BY {pk_q} LIMIT {int(limit)}"
            )
        else:
            cur.execute(
                f"SELECT {select_list} FROM {table_q} "
                f"WHERE {pk_q} > {self.placeholder} "
                f"ORDER BY {pk_q} LIMIT {int(limit)}",
                (after_pk_value,),
            )
        rows = cur.fetchall()
        cur.close()
        return rows

    def update_rows(self, table, pk, columns, rows):
        """rows: list of tuples (new values in `columns` order..., pk value)."""
        if not rows:
            return
        cur = self.connection.cursor()
        set_list = ", ".join(
            f"{self.quote_ident(c)} = {self.placeholder}" for c in columns
        )
        sql = (
            f"UPDATE {self.quote_ident(table)} SET {set_list} "
            f"WHERE {self.quote_ident(pk)} = {self.placeholder}"
        )
        cur.executemany(sql, rows)
        cur.close()

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()
