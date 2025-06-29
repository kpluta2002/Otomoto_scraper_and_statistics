import re
from typing import Optional

import pandas as pd

from scripts.utils.DbUtil import DbConnector as db
from scripts.utils.LoggerUtil import Logger


class AbstractParser:
    STRIP_EXP = "-, _•"

    STATUS_PROCESSING = "processing"
    STATUS_ERROR = "error"
    STATUS_FINISHED = "finished"

    def __init__(self):
        self.engine = db().get_engine()
        self.session = db().get_session()
        self.log = Logger(self.__class__.__name__)

    def get_total_records(self, only_missing: bool):
        raise NotImplementedError()

    def _get_text_to_parse_as_df(
        self, batch_size: int, offset: int, only_missing: bool
    ) -> pd.DataFrame:
        raise NotImplementedError()

    def _save_parsed_text_df(self, df_parsed: pd.DataFrame):
        raise NotImplementedError()

    def _remove_words_from_string(self, text: str, words_to_remove: str | list[str]):
        """
        Removes exact matches of words from text, handling UTF-8 characters.
        Splits words on special characters except dots.

        Args:
            text (str): Text to process (UTF-8 encoded)
            words_to_remove (str or list): Words to remove, can contain special chars

        Returns:
            str: Text with specified words removed

        Examples:
            >>> remove_words_from_string("banger-danger", "banger danger")
            '-'
            >>> remove_words_from_string("test.com", "test")
            '.com'
            >>> remove_words_from_string("my-test•text", "test text")
            'my-•'
        """
        if not isinstance(text, str):
            return text

        if isinstance(words_to_remove, str):
            words_to_remove = re.split(r"[^a-zA-Z0-9.\s]+", words_to_remove)
            words_to_remove = [word for w in words_to_remove for word in w.split()]

        escaped_words = [
            re.escape(word.strip()) for word in words_to_remove if word and isinstance(word, str)
        ]

        if not escaped_words:
            return text.strip(self.STRIP_EXP)

        full_list = escaped_words + words_to_remove

        pattern = r"(?:" + "|".join(full_list) + r")"

        result = re.sub(pattern, "", text, flags=re.IGNORECASE | re.UNICODE)
        result = re.sub(r"\s+", " ", result, flags=re.UNICODE).strip()

        return result.strip(self.STRIP_EXP)

    def _remove_words_from_row(
        self, row: pd.Series, from_col: str, words_to_remove: str | list[str]
    ):
        """
        Removes words from specified column in a DataFrame row.

        Args:
            row (pd.Series): DataFrame row
            from_col (str): Column name to process
            words_to_remove (str or list): Words to remove, can be space-separated string or list

        Returns:
            pd.Series: Series with updated column value

        Example:
            df[from_col] = df.apply(
                parser._remove_words_from_column,
                args=(from_col, ["word1", "word2"]),
                axis=1
            )
        """
        text = str(row[from_col])

        if isinstance(words_to_remove, str):
            parts = re.split(r"[^a-zA-Z0-9.\s]+", words_to_remove)
            words_to_remove = [w for part in parts for w in part.split() if w]

        escaped_words = [
            re.escape(w.strip()) for w in words_to_remove if isinstance(w, str) and w.strip()
        ]

        if not escaped_words:
            return text

        pattern = r"(?:" + "|".join(escaped_words + words_to_remove) + r")"
        result = re.sub(pattern, "", text, flags=re.IGNORECASE | re.UNICODE)
        result = re.sub(r"\s+", " ", result, flags=re.UNICODE).strip()
        return result

    def _extract_pattern(
        self, row: pd.Series, col_from: str, col_to: str, pattern: str, cast: Optional[type] = None
    ):
        """
        Extracts and removes pattern match from row['working'].

        Args:
            row (pd.Series): DataFrame row with 'working' column
            col_from (str): column name to extract from
            pattern (str): Regex pattern with one capturing group
            cast (type, optional): Type to cast extracted value to

        Returns:
            pd.Series: Series with extracted value and updated working text

        Example:
            df[['engine_cc', 'working']] = df.apply(
                extract_pattern,
                pattern=r'(\\d+)\\s?cm3',
                cast=float,
                axis=1
            )
        """
        working = str(row[col_from]).strip()
        match = re.search(pattern, working, re.IGNORECASE | re.UNICODE)

        if not match:
            return pd.Series([None, working], index=[col_to, col_from])

        full_match = match.group(0)
        captured = match.group(1)

        if cast and captured:
            try:
                if cast in [float, int]:
                    cleaned = re.sub(r"[\s,\.]", "", captured)
                    captured = cast(cleaned)
                else:
                    captured = cast(captured)
            except (ValueError, TypeError):
                captured = None

        if isinstance(captured, str):
            captured = re.sub(r"^\W+|\W+$", "", captured, flags=re.UNICODE).strip(self.STRIP_EXP)

        working = self._remove_words_from_string(working, [full_match])

        return pd.Series([captured, working], index=[col_to, col_from])

    def _extract_pattern_to_boolean(self, row: pd.Series, col_from: str, col_to: str, pattern: str):
        """
        Checks if pattern exists in text and removes it.
        Returns boolean indicating if pattern was found.

        Args:
            row (pd.Series): DataFrame row
            col_from (str): Column name to check pattern in
            col_to (str): Column name to store boolean result
            pattern (str): Regex pattern to search for

        Returns:
            pd.Series: Series with boolean value and updated text

        Example:
            df[['is_verified', 'working']] = df.apply(
                parser._extract_pattern_to_boolean,
                args=('working', 'is_verified', 'Zweryfikowane'),
                axis=1
            )
        """
        working = str(row[col_from]).strip()
        match = re.search(pattern, working, re.IGNORECASE | re.UNICODE)

        if match:
            full_match = match.group(0)
            working = self._remove_words_from_string(working, [full_match])
            return pd.Series([True, working], index=[col_to, col_from])

        return pd.Series([False, working], index=[col_to, col_from])

    def _parse(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError()

    def validate_parsing(self, original_df: pd.DataFrame, parsed_df: pd.DataFrame):
        original_ids = set(original_df["id"])
        parsed_ids = set(parsed_df["id"])
        missing_ids = original_ids - parsed_ids
        if missing_ids:
            raise ValueError(
                f"Missing {len(missing_ids)} IDs after parsing: {list(missing_ids)[:10]} ..."
            )

    def run(self, batch_size: int, only_missing: bool, total: int):
        offset = 0
        while True:
            df = self._get_text_to_parse_as_df(batch_size, offset, only_missing)
            if df.empty or offset > total:
                break
            offset += batch_size

            df_parsed = self._parse(df)

            self.validate_parsing(df, df_parsed)

            try:
                self._save_parsed_text_df(df_parsed)
                yield self.STATUS_PROCESSING
            except Exception as e:
                self.log.error(f"Failed to save dataframe.\n{e}")
                return self.STATUS_ERROR
        return self.STATUS_FINISHED
