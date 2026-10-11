import pandas as pd
import pyarrow.parquet as pq
from sqlalchemy import create_engine
from tqdm.auto import tqdm
import click


def read_chunks(source, chunksize):
    if source.endswith(".parquet"):
        parquet_file = pq.ParquetFile(source)
        for batch in parquet_file.iter_batches(batch_size=chunksize):
            yield batch.to_pandas()
    else:
        yield from pd.read_csv(source, iterator=True, chunksize=chunksize)


@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--target-table', required=True, help='Target table name')
@click.option('--source', required=True, help='Path or URL to a .parquet or .csv file')
@click.option('--chunksize', default=100000, type=int, help='Chunk size for reading data')
def run(pg_user, pg_pass, pg_host, pg_port, pg_db, target_table, source, chunksize):
    engine = create_engine(f'postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')

    first = True
    for df_chunk in tqdm(read_chunks(source, chunksize)):
        if first:
            df_chunk.head(0).to_sql(name=target_table, con=engine, if_exists="replace", index=False)
            first = False

        df_chunk.to_sql(name=target_table, con=engine, if_exists="append", index=False)


if __name__ == "__main__":
    run()
