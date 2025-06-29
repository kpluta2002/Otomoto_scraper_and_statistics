import random
import string
import sys
import time
from itertools import cycle

import ua_generator
from scrapy import Spider, signals
from scrapy.crawler import Crawler
from scrapy.exceptions import IgnoreRequest, NotConfigured
from scrapy.http import Request, Response
from ua_generator.data.version import VersionRange
from ua_generator.options import Options

from scripts.utils import FreeProxyUtil as free_proxy
from scripts.utils.LoggerUtil import Logger

status_403_detected = "status_403"


class StickyProxyMiddleware:
    def __init__(self, proxy_list, crawler: Crawler):
        if not proxy_list:
            raise NotConfigured("HTTP_PROXY_LIST is not configured or is empty in settings.py")
        self.proxy_list = proxy_list
        self.logger = Logger(self.__class__.__name__)
        self.crawler = crawler
        self.spider_proxies = {}
        self._initialize_sticky_proxy()

    def _initialize_sticky_proxy(self):
        self.proxy_session_id = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=10)
        )

        base_proxy = str(self.proxy_list[0])
        try:
            scheme, rest = base_proxy.split("://", 1)
            auth_part, host_port = rest.split("@", 1)
            username_part, password_part = auth_part.split(":", 1)
            if "-zone-" in username_part:
                parts = username_part.split("-zone-")
                session_username = f"{parts[0]}-zone-{parts[1]}-session-{self.proxy_session_id}"
            else:
                session_username = f"{username_part}-session-{self.proxy_session_id}"

            self.sticky_proxy = f"{scheme}://{session_username}:{password_part}@{host_port}"
            self.logger.debug(
                f"Constructed sticky proxy URL (with session ID): {self.sticky_proxy}"
            )
        except Exception as e:
            self.logger.warning(
                f"Could not construct sticky proxy for Bright Data ({base_proxy}): {e}. Falling back to base proxy without session."
            )
            self.sticky_proxy = base_proxy

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        proxy_list = crawler.settings.getlist("HTTP_PROXY_LIST")
        instance = cls(proxy_list, crawler)
        return instance

    def process_request(self, request: Request, spider: Spider):
        if self.sticky_proxy:
            request.meta["proxy"] = self.sticky_proxy
            spider.logger.debug(f"Assigned sticky proxy: {self.sticky_proxy} for {request.url}")
        return None

    def process_response(self, request: Request, response: Response, spider: Spider):
        """
        Detects 403 responses, initiates a new proxy session, and passes the response.
        """
        self.logger.debug(f"RandomProxy processing response. Code: {response.status}")

        if response.status in (403, 429):
            self.logger.warning(f"Received 403 for {request.url}. Regenerating proxy session.")
            self._initialize_sticky_proxy()
            request.meta["proxy_refreshed"] = True
        return response

    def process_exception(self, request: Request, exception: Exception, spider: Spider):
        pass


class FreeProxyMiddleware:
    def __init__(self, crawler):
        self.logger = Logger(self.__class__.__name__)
        self.proxies = None
        self.proxy_index = 0
        self.retry_delay = 10
        self.loading_deferred = None

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(crawler)
        crawler.signals.connect(middleware._spider_opened, signal=signals.spider_opened)
        return middleware

    def _spider_opened(self, spider):
        return self._reload_proxies()

    def _reload_proxies(self):
        if self.loading_deferred is not None:
            return self.loading_deferred

        self.loading_deferred = free_proxy.get_working_proxies()
        self.loading_deferred.addCallback(self._on_proxies_loaded)
        self.loading_deferred.addErrback(self._on_proxies_error)
        return self.loading_deferred

    def _on_proxies_loaded(self, proxies):
        self.loading_deferred = None
        if proxies:
            self.proxies = proxies
            self.logger.info(f"Successfully loaded {len(proxies)} proxies")
        else:
            self.logger.warning("No proxies were loaded")
            self.proxies = None

    def _on_proxies_error(self, failure):
        self.loading_deferred = None
        self.logger.error(f"Failed to load proxies: {failure.value}")
        self.proxies = None

    def process_request(self, request, spider):
        if not self.proxies:
            self.logger.warning("No proxies available")
            raise IgnoreRequest()

        proxy = self.proxies[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        request.meta["proxy"] = proxy
        self.logger.debug(f"Using proxy: {proxy}")
        return None

    def process_exception(self, request, exception, spider):
        """Handle connection errors and timeouts"""
        proxy = request.meta.get("proxy")
        if proxy and proxy in self.proxies:
            self.logger.warning(f"Removing failing proxy {proxy} due to: {str(exception)}")
            self.proxies.remove(proxy)
            
            if not self.proxies:
                self.logger.warning("No more proxies available")
                raise IgnoreRequest()
                
            new_request = request.copy()
            new_request.dont_filter = True
            return new_request
        return None

    def process_response(self, request, response, spider):
        proxy = request.meta.get("proxy")
        
        if response.status in (403, 407, 408, 429, 502, 503, 504) or hasattr(response, 'timed_out'):
            if proxy and proxy in self.proxies:
                self.logger.warning(f"Removing failing proxy {proxy} due to status {response.status}")
                self.proxies.remove(proxy)
                
                if not self.proxies:
                    self.logger.warning("No more proxies available")
                    raise IgnoreRequest()
                    
                new_request = request.copy()
                new_request.dont_filter = True
                return new_request
        return response


class RandomProxyMiddleware:
    def __init__(self, proxy_list: list[str], crawler: Crawler):
        if not proxy_list:
            raise NotConfigured("HTTP_PROXY_LIST is not configured or is empty in settings.py")
        self.proxy_list = cycle(proxy_list)
        self.logger = Logger(self.__class__.__name__)
        self.crawler = crawler
        self.spider_proxies = {}

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        proxy_list = crawler.settings.getlist("HTTP_PROXY_LIST")
        return cls(proxy_list, crawler)

    def process_request(self, request: Request, spider: Spider):
        proxy_address = next(self.proxy_list)

        if proxy_address:
            request.meta["proxy"] = proxy_address
        else:
            self.logger.error("No proxy provided!")
            sys.exit(0)
        return None


class UAGeneratorMiddleware:
    def __init__(self, crawler: Crawler):
        self.crawler = crawler
        self.logger = Logger(self.__class__.__name__)
        self._set_new_user_agent()

    def _set_new_user_agent(self):
        options = Options()
        options.version_ranges = {
            "chrome": VersionRange(min_version=100, max_version=126),
        }

        self.generated_result = ua_generator.generate(
            device="desktop",
            platform="windows",
            browser="chrome",
            options=options,
        )

        self.generated_headers = self.generated_result.headers.get()

        user_agent_bytes = self.generated_result.text
        self.user_agent_string = (
            user_agent_bytes if user_agent_bytes else "Default Scrapy/User-Agent (Fallback)"
        )

        self.logger.info(
            f"Initialized UAGeneratorMiddleware with User-Agent: {self.user_agent_string}"
        )

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        middleware = cls(crawler)
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware

    def spider_opened(self, spider: Spider):
        spider.logger.info(f"Spider {spider.name} opened with User-Agent: {self.user_agent_string}")

    def process_request(self, request: Request, spider: Spider):
        if "User-Agent" in request.headers:
            del request.headers["User-Agent"]

        for header_name, header_value in self.generated_headers.items():
            request.headers[header_name] = header_value

        return None

    def process_response(self, request: Request, response: Response, spider: Spider):
        """
        Detects 403 responses and regenerates the User-Agent.
        """
        self.logger.debug(f"UAGenerator processing response. Code: {response.status}")

        if response.status in (403, 429):
            self.logger.warning(
                f"Received 403 in UAGeneratorMiddleware for {request.url}. Regenerating User-Agent."
            )
            self._set_new_user_agent()
            request.meta["ua_refreshed"] = True

        return response


class ScraperSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        pass

    async def process_start(self, start):
        async for item_or_request in start:
            yield item_or_request

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ScraperDownloaderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
