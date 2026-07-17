"""Masking orchestration: iterate rows in batches, generate values, UPDATE."""
import csv

from .generators import generate_value


class BackupWriter:
    """Streams a real-value -> masked-value mapping CSV while masking runs."""

    HEADER = ["table_name", "column_name", "pk_value", "original_value", "new_value"]

    def __init__(self, path):
        self._file = open(path, "w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._file)
        self._writer.writerow(self.HEADER)

    def record(self, table, column, pk_value, original, new):
        self._writer.writerow([table, column, pk_value, original, new])

    def close(self):
        self._file.close()


class TableReport:
    def __init__(self, table):
        self.table = table
        self.rows = 0
        self.samples = []  # first few (column, before, after)
        self.skipped_reason = None


class Masker:
    SAMPLE_LIMIT = 5

    def __init__(self, adapter, tables, persona_factory, rng,
                 default_locale, batch_size, backup=None, log=print):
        self._adapter = adapter
        self._tables = tables
        self._factory = persona_factory
        self._rng = rng
        self._default_locale = default_locale
        self._batch_size = batch_size
        self._backup = backup
        self._log = log

    def run(self, dry_run=False, tables_filter=None):
        """Mask all configured tables; returns list of TableReport."""
        reports = []
        for table_name, table_rules in self._tables.items():
            if tables_filter and table_name not in tables_filter:
                continue
            reports.append(self._mask_table(table_name, table_rules, dry_run))
        return reports

    def _mask_table(self, table, table_rules, dry_run):
        report = TableReport(table)
        pk = self._adapter.get_primary_key(table)
        if pk is None:
            report.skipped_reason = (
                f"table '{table}' skipped: no single-column primary key "
                f"(composite or absent PKs are not supported)"
            )
            self._log(f"ERROR: {report.skipped_reason}")
            return report

        locale = table_rules.locale or self._default_locale
        rules = table_rules.rules
        columns = [r.column_name for r in rules]
        last_pk = None
        while True:
            rows = self._adapter.fetch_batch(
                table, pk, columns, last_pk, self._batch_size
            )
            if not rows:
                break
            updates = []
            for row in rows:
                pk_value, originals = row[0], row[1:]
                persona = self._factory.create(locale)
                new_values = []
                for rule, original in zip(rules, originals):
                    new_value = generate_value(
                        rule, persona, pk_value, original, self._rng
                    )
                    new_values.append(new_value)
                    if new_value != original:
                        if self._backup:
                            self._backup.record(
                                table, rule.column_name, pk_value, original, new_value
                            )
                        if len(report.samples) < self.SAMPLE_LIMIT:
                            report.samples.append(
                                (rule.column_name, original, new_value)
                            )
                updates.append(tuple(new_values) + (pk_value,))
                report.rows += 1
            if not dry_run:
                self._adapter.update_rows(table, pk, columns, updates)
                self._adapter.commit()
            last_pk = rows[-1][0]
        return report
