from urllib.parse import urlparse
import requests
from scrapy.robotstxt import PythonRobotParser

class PageValidator:
    def __init__(self, homePageUrl: str):
        self.homePageUrl = homePageUrl
        try:
            robots_txt_url = self.homePageUrl.rstrip('/') + "/robots.txt"
            response = requests.get(robots_txt_url)
            response.raise_for_status()
            
            self.parser = PythonRobotParser(response.text.encode(), None)
            print(f"Fetched robots.txt from {robots_txt_url}")
        except Exception as e:
            print(f"Error fetching robots.txt: {e}")
            self.parser = None

    def can_fetch(self, url: str, agent: str = "*") -> bool:
        if self.parser is None:
            return True

        # Check both with and without trailing slash
        url_no_slash = url.rstrip('/')
        url_with_slash = url_no_slash + '/'
        
        # If either version is disallowed, consider it disallowed
        allowed_no_slash = self.parser.allowed(url_no_slash, agent)
        allowed_with_slash = self.parser.allowed(url_with_slash, agent)
        
        is_allowed = allowed_no_slash and allowed_with_slash
        print(f"Checking if {agent} can fetch {url}: {is_allowed}")
        return is_allowed
