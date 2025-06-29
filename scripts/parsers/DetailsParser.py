import pandas as pd
from sqlalchemy import exists, func, not_, select

from scripts.parsers.AbstractParser import AbstractParser
from scripts.shared.Models import Details, RawListing
from scripts.utils.DbUtil import DbConnector as db
from scripts.utils.DbUtil import postgres_upsert


class DetailsParser(AbstractParser):
    STRIP_EXP = "-, _•"

    STATUS_PROCESSING = "processing"
    STATUS_ERROR = "error"
    STATUS_FINISHED = "finished"

    def __init__(self):
        super().__init__()

    def get_total_records(self, only_missing: bool):
        if only_missing:
            query = select(func.count(RawListing.id)).where(
                not_(exists(select(1).where(Details.id == RawListing.id)))
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
                select(RawListing.id, RawListing.raw_details)
                .where(not_(exists(select(1).where(Details.id == RawListing.id))))
                .limit(batch_size)
            )
        else:
            query = select(RawListing.id, RawListing.raw_details).limit(batch_size).offset(offset)

        return pd.read_sql_query(sql=query, con=self.engine)

    def _save_parsed_text_df(self, df_parsed: pd.DataFrame):
        postgres_upsert(table=Details, conn=self.session, df=df_parsed, update_time=True)

    def _parse(self, df: pd.DataFrame) -> pd.DataFrame:
        from_col = RawListing.raw_details.name

        df[[Details.is_stamped.name, from_col]] = df.apply(
            self._extract_pattern_to_boolean,
            args=(from_col, Details.is_stamped.name, r"\bPodbite\b"),
            axis=1,
        )

        df[[Details.is_featured.name, from_col]] = df.apply(
            self._extract_pattern_to_boolean,
            args=(from_col, Details.is_featured.name, r"\bWyróżnione\b"),
            axis=1,
        )

        df[[Details.is_verified.name, from_col]] = df.apply(
            self._extract_pattern_to_boolean,
            args=(from_col, Details.is_verified.name, r"\bZweryfikowane dane\b"),
            axis=1,
        )

        df[[Details.mileage.name, from_col]] = df.apply(
            self._extract_pattern,
            args=(from_col, Details.mileage.name, r"mileage\s*([0-9]+(?:\s+[0-9]+)*)\s*km", int),
            axis=1,
        )

        df[[Details.fuel_type.name, from_col]] = df.apply(
            self._extract_pattern,
            args=(from_col, Details.fuel_type.name, r"fuel_type\s+(\S+)\s*", str),
            axis=1,
        )

        df[[Details.gearbox_type.name, from_col]] = df.apply(
            self._extract_pattern,
            args=(from_col, Details.gearbox_type.name, r"gearbox\s+(\S+)\s*", str),
            axis=1,
        )

        df[[Details.year.name, from_col]] = df.apply(
            self._extract_pattern,
            args=(from_col, Details.year.name, r"year\s+(\d+)\s*", int),
            axis=1,
        )

        df[[Details.city.name, from_col]] = df.apply(
            self._extract_pattern,
            args=(from_col, Details.city.name, r"([^(]+?)(?=\s*\()", str),
            axis=1,
        )

        df[[Details.voivodeship.name, from_col]] = df.apply(
            self._extract_pattern,
            args=(from_col, Details.voivodeship.name, r"\(([^)]+)\)", str),
            axis=1,
        )

        df[from_col] = df.apply(
            self._remove_words_from_row,
            args=(from_col, ["()", "Opublikowano", "Zobacz ogłoszenia"]),
            axis=1,
        )

        df[[Details.seller_info.name, from_col]] = df.apply(
            self._extract_pattern,
            args=(from_col, Details.seller_info.name, r"Usługi finansowe(.*$)", str),
            axis=1,
        )

        df.rename(columns={from_col: Details.seller_type.name}, inplace=True)

        return df
