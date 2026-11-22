"""Generate the published fixture from the exact deterministic backend scenario.

This is synthetic output, not site observations. No databases are shipped.
"""
from __future__ import annotations
import argparse
import tempfile
from pathlib import Path
from server import database
from server.demo import demo_reset
from server.app import csv_measurements


def make(seed: int) -> str:
    with tempfile.TemporaryDirectory(prefix='jpo-demo-') as work:
        former = database.DB_PATH
        try:
            database.DB_PATH = Path(work) / 'scenario.sqlite3'
            database.initialize()
            with database.connect() as db:
                demo_reset(db, seed)
                candidates = [dict(x) for x in db.execute('SELECT * FROM candidates ORDER BY id')]
                criteria = [dict(x) for x in db.execute('SELECT * FROM criteria ORDER BY group_index,code')]
                rows = [dict(x) for x in db.execute('SELECT * FROM measurements ORDER BY candidate_id,code')]
                return csv_measurements(rows,candidates,criteria)
        finally:
            database.DB_PATH = former


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--seed',type=int,default=202611)
    parser.add_argument('--output',type=Path,default=Path('examples/synthetic_demo_seed_202611.csv'))
    args=parser.parse_args()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(make(args.seed),encoding='utf-8')
    print(f'Wrote {args.output} (seed {args.seed}). Not field data.')