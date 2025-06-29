import json  # Import json to parse response body

import scrapy

from scripts.utils import EnvUtil as env


class MiddlewareTestSpider(scrapy.Spider):
    name = "middleware_test"

    start_urls = []

    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 0.5,
        "LOG_FILE": env.root + "/scripts/collectors/scraper/logs/test.log",
        "LOG_FILE_APPEND": False,
        "DUPEFILTER_CLASS": "scrapy.dupefilters.BaseDupeFilter",
    }

    def start_requests(self):
        yield scrapy.Request(url="https://httpbin.org/headers", callback=self.parse_headers, meta={'request_label': 'First Headers Check'})

        yield scrapy.Request(url="https://httpbin.org/headers", callback=self.parse_headers, meta={'request_label': 'Second Headers Check'})

        for i in range(5):
            yield scrapy.Request(
                url="https://httpbin.org/ip", callback=self.parse_ip, meta={"request_num": i + 1}
            )

    def parse_headers(self, response):
        """Parses the response from httpbin.org/headers to show all sent headers."""
        request_label = response.meta.get('request_label', 'Unnamed Headers Check')
        try:
            data = json.loads(response.text)
            self.logger.info(f"--- Headers for URL: {response.url} ({request_label}) ---")
            for header_name, header_value in data.get("headers", {}).items():
                self.logger.info(f"   {header_name}: {header_value}")
            self.logger.info(f"------------------------------------")

            yield {"response_type": "headers_dump", "request_label": request_label, "headers": data.get("headers")}

        except json.JSONDecodeError:
            self.logger.error(
                f"Failed to decode JSON from {response.url} ({request_label}): {response.text[:200]}..."
            )
            yield {
                "response_type": "headers_dump_error",
                "request_label": request_label,
                "url": response.url,
                "status": response.status,
            }

    def parse_ip(self, response):
        """Parses the response from httpbin.org/ip to show the originating IP."""
        request_num = response.meta.get("request_num", "N/A")
        try:
            data = json.loads(response.text)
            origin_ip = data.get("origin")
            self.logger.info(f"Request #{request_num} URL: {response.url}, Origin IP: {origin_ip}")

            yield {"response_type": "ip_check", "request_num": request_num, "origin_ip": origin_ip}

        except json.JSONDecodeError:
            self.logger.error(
                f"Failed to decode JSON from {response.url}: {response.text[:200]}..."
            )
            yield {
                "response_type": "ip_check_error",
                "url": response.url,
                "status": response.status,
            }