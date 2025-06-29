import re
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from scripts.utils.DbUtil import DbConnector
import pandas as pd
from sqlalchemy import text
from scripts.shared.Models import Base


class StringNormalizer:
    def __init__(self):
        self.engine = DbConnector().get_engine()
        self.session = DbConnector().get_session()

    def capitalize_column_first_char(self, column: "pd.Series[str]") -> "pd.Series[str]":
        return column.map(
            lambda x: x[:1].upper() + x[1:] if isinstance(x, str) and len(x) > 0 else x
        )

    def normalize_column_words(
        self, column: "pd.Series[str]", table: Base, column_name: str
    ) -> "pd.Series[str]":
        """
        Normalize words in a pandas column by handling:
        - Different encodings (Citroen vs Citroën)
        - Case differences (BMW vs Bmw vs bmw)
        - Punctuation variations (Mercedes-Benz vs Mercedes Benz)
        - Leading/trailing whitespace
        - Matches against existing database values for consistency

        Returns the most common variant of each normalized word, preferring existing database values.
        """

        def normalize_text(text):
            """Basic text normalization"""
            if pd.isna(text):
                return text

            text = str(text).strip()
            if not text:
                return text

            normalized = unicodedata.normalize("NFD", text)
            ascii_text = "".join(c for c in normalized if unicodedata.category(c) != "Mn")

            return ascii_text

        def create_comparison_key(text):
            """Create a key for comparing similar words"""
            if pd.isna(text):
                return text

            normalized = normalize_text(text)
            key = re.sub(r"[-_\s\.]+", "", normalized.lower())
            return key

        def similarity_ratio(a, b):
            """Calculate similarity ratio between two strings"""
            return SequenceMatcher(None, a, b).ratio()

        db_values_freq = self._get_existing_values(table, column_name)
        db_values = list(db_values_freq.keys())
        
        valid_mask = column.notna() & (column.str.strip() != "")
        valid_values = column[valid_mask]

        if len(valid_values) == 0:
            return column

        all_values = list(set(valid_values.tolist() + db_values))

        key_to_originals = {}
        for value in all_values:
            key = create_comparison_key(value)
            if key not in key_to_originals:
                key_to_originals[key] = []
            key_to_originals[key].append(value)

        normalization_map = {}

        for key, originals in key_to_originals.items():
            if len(originals) == 1:
                normalization_map[originals[0]] = originals[0]
            else:
                db_candidates = [val for val in originals if val in db_values]
                column_candidates = [val for val in originals if val in valid_values.tolist()]

                if db_candidates:
                    if len(db_candidates) == 1:
                        best_word = db_candidates[0]
                    else:
                        best_word = self.choose_best_db_format(db_candidates, db_values_freq)
                else:
                    column_freq_counter = Counter([val for val in originals if val in valid_values.tolist()])
                    
                    if column_freq_counter:
                        most_common = column_freq_counter.most_common()
                        max_freq = most_common[0][1]
                        top_candidates = [word for word, freq in most_common if freq == max_freq]
                    else:
                        top_candidates = originals

                    best_word = self.choose_best_format(top_candidates)

                for original in originals:
                    if original in valid_values.tolist():
                        normalization_map[original] = best_word

        result = column.copy()
        for original, normalized in normalization_map.items():
            if original in valid_values.tolist():
                result = result.replace(original, normalized)

        return result

    def _get_existing_values(self, table: Base, column_name: str) -> dict:
        """Get existing values from database with their frequencies"""
        try:
            table_name = table.__tablename__
            
            query = text(f"""
                SELECT {column_name}, COUNT(*) as frequency
                FROM {table_name} 
                WHERE {column_name} IS NOT NULL 
                    AND TRIM({column_name}) != ''
                GROUP BY {column_name}
                ORDER BY COUNT(*) DESC
            """)
            
            with self.engine.connect() as conn:
                result = conn.execute(query)
                db_values_freq = {row[0]: row[1] for row in result.fetchall() if row[0] is not None}
            
            return db_values_freq
            
        except Exception as e:
            print(f"Warning: Could not fetch existing values from database: {e}")
            return {}

    def choose_best_db_format(self, candidates, db_frequencies):
        """Choose the best formatted version from database candidates, prioritizing frequency"""
        if len(candidates) == 1:
            return candidates[0]

        max_freq = max(db_frequencies.get(candidate, 0) for candidate in candidates)
        most_frequent = [candidate for candidate in candidates if db_frequencies.get(candidate, 0) == max_freq]
        
        if len(most_frequent) == 1:
            return most_frequent[0]
        
        return self.choose_best_format(most_frequent)

    def choose_best_format(self, candidates):
        """Choose the best formatted version from candidates"""
        if len(candidates) == 1:
            return candidates[0]

        def score_word(word):
            score = 0

            if word[0].isupper() and not word[1:].isupper():  # Title case
                score += 10
            elif word.isupper() and len(word) <= 4:  # Acronyms
                score += 8
            elif any(c.isupper() for c in word[1:]):  # Mixed case (like iPhone)
                score += 7

            if any(ord(c) > 127 for c in word):
                score += 5

            if "-" in word:
                score += 3

            score += len(word) * 0.1

            score -= ord(word[0].lower()) * 0.01

            return score

        return max(candidates, key=score_word)

    def normalize_with_similarity_threshold(
        self, 
        column: "pd.Series[str]", 
        table: Base, 
        column_name: str,
        similarity_threshold: float = 0.8
    ) -> "pd.Series[str]":
        """
        Enhanced normalization that also considers fuzzy matching against database values
        for cases where exact key matching isn't sufficient.
        """
        result = self.normalize_column_words(column, table, column_name)
        
        db_values_freq = self._get_existing_values(table, column_name)
        db_values = list(db_values_freq.keys())
        
        if not db_values:
            return result
        
        def fuzzy_match_to_db(text):
            if pd.isna(text) or not isinstance(text, str):
                return text
                
            best_match = None
            best_score = 0
            
            for db_value in db_values:
                score = SequenceMatcher(None, text.lower(), db_value.lower()).ratio()
                if score > best_score and score >= similarity_threshold:
                    best_score = score
                    best_match = db_value
            
            return best_match if best_match else text
        
        return result.apply(fuzzy_match_to_db)