"""Command-line interface.

Exit codes: 0 = success, 1 = configuration/connection error,
2 = completed but some tables were skipped.
"""
import argparse
import os
import random
import sys
import time

from .datasources import DataSourceError, discover_locales
from .db import DbError, create_adapter
from .env import load_env
from .masker import BackupWriter, Masker
from .persona import PersonaFactory
from .rules import RuleError, load_rules


def build_parser():
    parser = argparse.ArgumentParser(
        prog="masking_tool",
        description="Mask confidential database columns with realistic fake data.",
    )
    parser.add_argument("--env", default=".env", help="path to .env file (default: .env)")
    parser.add_argument("--rule", default="masking-rule.csv",
                        help="path to rule CSV (default: masking-rule.csv)")
    parser.add_argument("--dry-run", action="store_true",
                        help="generate values and show a summary without writing to the DB")
    parser.add_argument("--tables", help="comma-separated list of tables to mask (default: all)")
    parser.add_argument("--backup",
                        help="write original->masked mapping CSV to this path "
                             "(contains real data - protect it!)")
    parser.add_argument("--batch-size", type=int, help="rows per batch (default: 500)")
    parser.add_argument("--seed", type=int, help="random seed for reproducible output")
    parser.add_argument("--data-dir", help="path to data-sample directory")
    return parser


def default_data_dir():
    return os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "..", "data-sample")
    )


def main(argv=None):
    args = build_parser().parse_args(argv)
    started = time.time()

    try:
        env = load_env(args.env)
    except OSError as exc:
        print(f"ERROR: cannot read env file: {exc}", file=sys.stderr)
        return 1

    data_dir = args.data_dir or env.get("MASK_DATA_DIR") or default_data_dir()
    batch_size = args.batch_size or int(env.get("MASK_BATCH_SIZE", "500"))
    default_locale = env.get("MASK_DEFAULT_LOCALE", "japanese")
    seed = args.seed if args.seed is not None else (
        int(env["MASK_SEED"]) if env.get("MASK_SEED") else None
    )
    rng = random.Random(seed)

    locales = discover_locales(data_dir)
    if not locales:
        print(f"ERROR: no locale data found under {data_dir}", file=sys.stderr)
        return 1

    try:
        tables = load_rules(args.rule, locales)
    except (OSError, RuleError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    tables_filter = None
    if args.tables:
        tables_filter = {t.strip() for t in args.tables.split(",") if t.strip()}
        unknown = tables_filter - set(tables)
        if unknown:
            print(f"ERROR: --tables names not in rule file: {', '.join(sorted(unknown))}",
                  file=sys.stderr)
            return 1

    driver = env.get("DB_DRIVER", "")
    try:
        adapter = create_adapter(driver)
        adapter.connect(env)
    except Exception as exc:
        print(f"ERROR: cannot connect to database: {exc}", file=sys.stderr)
        return 1

    backup = None
    if args.backup:
        backup = BackupWriter(args.backup)

    try:
        factory = PersonaFactory(data_dir, rng)
        masker = Masker(
            adapter, tables, factory, rng,
            default_locale=default_locale, batch_size=batch_size, backup=backup,
        )
        reports = masker.run(dry_run=args.dry_run, tables_filter=tables_filter)
    except DataSourceError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    finally:
        if backup:
            backup.close()
        adapter.close()

    skipped = [r for r in reports if r.skipped_reason]
    mode = "DRY RUN - no changes written" if args.dry_run else "masked"
    print(f"\n=== Summary ({mode}) ===")
    for report in reports:
        if report.skipped_reason:
            print(f"  {report.table}: SKIPPED - {report.skipped_reason}")
            continue
        print(f"  {report.table}: {report.rows} rows")
        for column, before, after in report.samples:
            print(f"    {column}: {before!r} -> {after!r}")
    if backup:
        print(f"Backup mapping written to {args.backup} (contains real data - protect it!)")
    print(f"Elapsed: {time.time() - started:.1f}s")
    return 2 if skipped else 0


if __name__ == "__main__":
    sys.exit(main())
