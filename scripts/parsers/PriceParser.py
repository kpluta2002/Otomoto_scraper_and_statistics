import pandas as pd
from sqlalchemy import exists, func, not_, select

from scripts.parsers.AbstractParser import AbstractParser
from scripts.shared.Models import Price, RawListing
from scripts.utils.DbUtil import DbConnector as db
from scripts.utils.DbUtil import postgres_upsert


class PriceParser(AbstractParser):
    STRIP_EXP = "-, _•"

    STATUS_PROCESSING = "processing"
    STATUS_ERROR = "error"
    STATUS_FINISHED = "finished"

    def __init__(self):
        super().__init__()

    def get_total_records(self, only_missing: bool):
        if only_missing:
            query = select(func.count(RawListing.id)).where(
                not_(exists(select(1).where(Price.id == RawListing.id)))
            )
        else:
            query = select(func.count(RawListing.id))

        result = db().get_session().execute(query).scalar()
        return int(result)

    def _get_text_to_parse_as_df(
        self, batch_size: int, offset: int, only_missing: bool
    ) -> pd.DataFrame:
        if only_missing:
            query = (
                select(RawListing.id, RawListing.raw_price)
                .where(not_(exists(select(1).where(Price.id == RawListing.id))))
                .limit(batch_size)
            )
        else:
            query = select(RawListing.id, RawListing.raw_price).limit(batch_size).offset(offset)

        return pd.read_sql_query(sql=query, con=self.engine)

    def _save_parsed_text_df(self, df_parsed: pd.DataFrame):
        postgres_upsert(table=Price, conn=self.session, df=df_parsed, update_time=True)

    def _parse(self, df: pd.DataFrame) -> pd.DataFrame:
        from_col = RawListing.raw_price.name

        df[from_col] = df.apply(
            self._remove_words_from_row,
            args=(from_col, (["ad link", "Sprawdź możliwości finansowania"] + [str(year) for year in range(1900, 2101)])),
            axis=1,
        )

        df[[Price.amount.name, from_col]] = df.apply(
            self._extract_pattern,
            args=(from_col, Price.amount.name, r"([\d\s]+)(?=[A-Za-z])", int),
            axis=1
        )

        df[[Price.currency.name, from_col]] = df.apply(
            self._extract_pattern,
            args=(from_col, Price.currency.name, r"^\b(\w+)\b", str),
            axis=1
        )

        df.rename(columns={from_col: Price.segment.name}, inplace=True)

        return df