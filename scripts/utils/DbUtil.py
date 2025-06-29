import datetime
from zoneinfo import ZoneInfo

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, sessionmaker

from scripts.shared.services import pg_url
from scripts.utils import EnvUtil as env
from scripts.utils.LoggerUtil import Logger

timezone = ZoneInfo(str(env.get_var("TIMEZONE")))
log = Logger("PGSQL")


def postgres_upsert(table, conn: Session, df: pd.DataFrame, update_time: bool = False):
    """
    Performs PostgreSQL upsert using DataFrame.

    Args:
        table: SQLAlchemy Table object
        conn: SQLAlchemy connection
        df: pandas DataFrame to upsert
    """

    if update_time:
        df["updated_at"] = datetime.datetime.now(timezone)

    df = df.replace({float("nan"): None})

    data = df.to_dict("records")

    insert_statement = insert(table).values(data)

    upsert_statement = insert_statement.on_conflict_do_update(
        constraint=f"{table.__tablename__}_pkey",
        set_={c.key: c for c in insert_statement.excluded if c.key not in ("id", "created_at")},
    ).returning(table.id)

    try:
        with conn.begin() as transaction:
            result = conn.execute(upsert_statement)
            affected_rows = len(result.fetchall())

            if affected_rows == 0:
                transaction.rollback()
                raise ValueError(
                    f"No rows were affected in {table.__tablename__}. Check your data and constraints."
                )

            if affected_rows != len(df):
                log.warning(
                    f"Only {affected_rows} rows were affected out of {len(df)} rows in DataFrame"
                )

            return affected_rows

    except Exception as e:
        log.error(f"Error during upsert to {table.__tablename__}: {str(e)}")
        raise


class DbConnector:
    def __init__(self):
        self.engine = create_engine(pg_url)

    def get_session(self) -> Session:
        """Returns a new database session."""
        return sessionmaker(bind=self.engine)()

    def get_engine(self):
        """Returns the SQLAlchemy engine."""
        return self.engine
