import advertools as adv
import pandas as pd

from scripts.collectors.PageValidator import PageValidator
from scripts.utils import EnvUtil as env

HOME_PAGE_URL = env.get_var("URL_HOME_PAGE", str)

class SitemapCollector:
    def __init__(self):
        self.validator = PageValidator(HOME_PAGE_URL)
        self.sitemap_url = HOME_PAGE_URL + "sitemap.xml"

    def collect_sitemap_to_df(self) -> pd.DataFrame:
        if self.validator.can_fetch(self.sitemap_url):
            return adv.sitemap_to_df(self.sitemap_url) # type: ignore
        return pd.DataFrame()  # Return empty DataFrame if cannot fetch