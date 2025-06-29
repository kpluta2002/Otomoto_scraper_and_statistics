import re

import pandas as pd
from sqlalchemy import exists, func, not_, select

from scripts.parsers.AbstractParser import AbstractParser
from scripts.shared.Models import Car, RawListing
from scripts.utils.DbUtil import DbConnector as db
from scripts.utils.DbUtil import postgres_upsert
from scripts.normalizers.StringNormalizer import StringNormalizer

class SummaryParser(AbstractParser):
    MULTI_WORD_MAKES = {"Land Rover", "Alfa Romeo", "Aston Martin", "Rolls Royce"}

    def __init__(self):
        super().__init__()
        self.multi_word_re = "|".join([re.escape(m) for m in self.MULTI_WORD_MAKES])
        self.s_normal = StringNormalizer()

    def get_total_records(self, only_missing):
        if only_missing:
            query = select(func.count(RawListing.id)).where(
                not_(exists(select(1).where(Car.id == RawListing.id)))
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
                select(RawListing.id, RawListing.raw_summary)
                .where(not_(exists(select(1).where(Car.id == RawListing.id))))
                .limit(batch_size)
            )
        else:
            query = select(RawListing.id, RawListing.raw_summary).limit(batch_size).offset(offset)

        return pd.read_sql_query(sql=query, con=self.engine)

    def _save_parsed_text_df(self, df_parsed: pd.DataFrame):
        postgres_upsert(table=Car, conn=self.session, df=df_parsed, update_time=True)

    def _extract_model_and_shrink(self, row: pd.Series, col_from: str, col_to: str):
        working = row[col_from].strip()
        working = re.sub(r"^[•.]+\s*", "", working)

        toks = working.split()

        if len(toks) > 1 and len(toks[1]) == 1:
            model = f"{toks[0]} {toks[1]}"
        else:
            model = toks[0] if toks else ""

        updated_working = self._remove_words_from_string(working, model)

        return pd.Series([model.strip(self.STRIP_EXP), updated_working], index=[col_to, col_from])

    def _extract_variant(self, row: pd.Series, col_from: str, col_to: str):
        """
        Extracts variant and removes its terms from remaining text.
        Example:
            Input:  'Renault Clio 1.2 TCe Limited EDC 1197 cm3 • 120 KM • Renault Clio 1.2 TCe EDC'
            Output: col_to='1.2 TCe Limited EDC',
                    col_from='120 KM • Renault Clio'
        """
        working_text = str(row[col_from]).strip() if row[col_from] is not None else ""

        if not working_text:
            return pd.Series([None, None], index=[col_to, col_from])

        if "•" in working_text:
            variant_part = working_text.split("•")[0].strip()
            remaining = "•".join(working_text.split("•")[1:]).strip()

            remaining = self._remove_words_from_string(remaining, variant_part)
            remaining = re.sub(r"^\s*•\s*", "", remaining).strip()

            return pd.Series(
                [variant_part.strip(self.STRIP_EXP), remaining], index=[col_to, col_from]
            )

        return pd.Series([None, working_text], index=[col_to, col_from])

    def _parse(self, df: pd.DataFrame) -> pd.DataFrame:
        from_col = RawListing.raw_summary.name

        df[[Car.engine_cc.name, from_col]] = df.apply(
            self._extract_pattern,
            args=(from_col, Car.engine_cc.name, r"(\d+)\s?cm3", float),
            axis=1,
        )

        df[[Car.power_hp.name, from_col]] = df.apply(
            self._extract_pattern,
            args=(from_col, Car.power_hp.name, r"(\d+)\s?KM", float),
            axis=1,
        )

        df[[Car.make.name, from_col]] = df.apply(
            self._extract_pattern,
            args=(from_col, Car.make.name, rf"({self.multi_word_re}|\S+)", None),
            axis=1,
        )
        df[Car.make.name] = self.s_normal.normalize_column_words(df[Car.make.name], Car, Car.make.name)

        df[[Car.model.name, from_col]] = df.apply(
            self._extract_model_and_shrink, args=(from_col, Car.model.name), axis=1
        )
        df[Car.model.name] = self.s_normal.normalize_column_words(df[Car.model.name], Car, Car.model.name)

        df[[Car.variant.name, from_col]] = df.apply(
            self._extract_variant, args=(from_col, Car.variant.name), axis=1
        )

        df.rename(columns={from_col: Car.description.name}, inplace=True)

        return df
