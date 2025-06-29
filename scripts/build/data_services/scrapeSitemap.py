import datetime
import sys

import pandas as pd
from sqlalchemy import case, or_
from sqlalchemy.dialects.postgresql import insert

from scripts.collectors.sitemap.SitemapCollector import SitemapCollector
from scripts.shared.Models import Pages, Sitemap
from scripts.utils.DbUtil import DbConnector
from scripts.utils.LoggerUtil import Logger

SCRIPT_NAME = "scrapeSitemap"
log = Logger(SCRIPT_NAME)
db = DbConnector().get_session()


def scrape_sitemap() -> pd.DataFrame:
    try:
        df_sitemap = SitemapCollector().collect_sitemap_to_df()
    except Exception as e:
        msg = f"An error occurred while scraping the sitemap: {e}"
        log.error(msg)
        db_log.error(msg)
        return pd.DataFrame() # Return empty DataFrame on error

    return df_sitemap

def insert_or_update_sitemaps_data(df_sitemap: pd.DataFrame) -> bool:
    df_sitemap = df_sitemap.copy()
    if df_sitemap.empty:
        log.warning("No data to save, DataFrame is empty.")
        return False

    df = df_sitemap[['sitemap', 'etag', 'sitemap_size_mb']].drop_duplicates()
    now = datetime.datetime.now(datetime.timezone.utc)

    try:
        for _, row in df.iterrows():  # type: ignore
            stmt = (
                insert(Sitemap)
                .values({
                    Sitemap.sitemap_url: row['sitemap'],
                    Sitemap.etag: row['etag'],
                    Sitemap.size_mb: row['sitemap_size_mb'],
                    Sitemap.created_at: now,
                    Sitemap.updated_at: now,
                })
                .on_conflict_do_update(
                    index_elements=[Sitemap.sitemap_url],
                    set_={
                        Sitemap.etag: row['etag'],
                        Sitemap.size_mb: row['sitemap_size_mb'],
                        Sitemap.updated_at: case(
                            (
                                or_(
                                    Sitemap.etag != row['etag'],
                                    Sitemap.size_mb != row['sitemap_size_mb']
                                ),
                                now
                            ),
                            else_=Sitemap.updated_at
                        )
                    }
                )
            )
            db.execute(stmt)
        db.commit()
        log.info("Sitemap data saved/updated successfully.")
        return True
    except Exception as e:
        db.rollback()
        msg = f"Failed to save sitemap data: {e}"
        log.error(msg)
        db_log.error(msg)
        return False

def insert_or_update_pages_data(df_sitemap: pd.DataFrame) -> bool:
    df_sitemap = df_sitemap.copy()
    if df_sitemap.empty:
        log.warning("No data to save, DataFrame is empty.")
        return False

    df = df_sitemap[['loc', 'priority', 'changefreq', 'sitemap']].drop_duplicates()
    now = datetime.datetime.now(datetime.timezone.utc)

    try:
        # Query all sitemaps and create a mapping
        assert db.bind is not None, "Database connection is not established."
        sitemap_df = pd.read_sql(db.query(Sitemap).statement, db.bind) # type: ignore
        sitemap_map = sitemap_df.set_index('sitemap_url')['id'].to_dict() # type: ignore

        for _, row in df.iterrows():  # type: ignore
            sitemap_id = sitemap_map.get(row['sitemap']) # type: ignore

            stmt = (
                insert(Pages)
                .values({
                    Pages.page_url: row['loc'],
                    Pages.priority: row['priority'],
                    Pages.change_frequency: row['changefreq'],
                    Pages.sitemap_id: sitemap_id,
                    Pages.created_at: now,
                    Pages.modified_at: now,
                })
                .on_conflict_do_update(
                    index_elements=[Pages.page_url],
                    set_={
                        Pages.priority: row['priority'],
                        Pages.change_frequency: row['changefreq'],
                        Pages.sitemap_id: sitemap_id,
                        Pages.modified_at: case(
                            (
                                (
                                    or_(
                                        Pages.priority != row['priority'],
                                        Pages.change_frequency != row['changefreq'],
                                        Pages.sitemap_id != sitemap_id
                                    ),
                                    now
                                )
                            ),
                            else_=Pages.modified_at
                        )
                    }
                )
            )
            db.execute(stmt)
        db.commit()
        log.info("Page data saved/updated successfully.")
        return True
    except Exception as e:
        db.rollback()
        msg = f"Failed to save page data: {e}"
        log.error(msg)
        db_log.error(msg)
        return False

def main():
    df_sitemap = scrape_sitemap()

    if insert_or_update_sitemaps_data(df_sitemap):
        insert_or_update_pages_data(df_sitemap)
    else:
        log.error("Failed to insert or update sitemap data, skipping page data insertion.")


if __name__ == "__main__":
    sys.exit(main())
