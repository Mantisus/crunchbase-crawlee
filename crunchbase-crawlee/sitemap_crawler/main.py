from crawlee.parsel_crawler import ParselCrawler
from crawlee.http_clients.curl_impersonate import CurlImpersonateHttpClient
from crawlee import ConcurrencySettings, HttpHeaders

from .routes import router

async def main() -> None:
    """The crawler entry point."""

    concurrency_settings = ConcurrencySettings(max_concurrency=1, max_tasks_per_minute=50)

    http_client = CurlImpersonateHttpClient(impersonate="safari17_0",
                                            timeout=50,
                                            headers=HttpHeaders({
                                                "accept": "*/*",
                                                "accept-encoding": "gzip, deflate, br, zstd",
                                                "accept-language": "en",
                                                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
                                            }))
    crawler = ParselCrawler(
        request_handler=router,
        max_request_retries=3,
        concurrency_settings=concurrency_settings,
        http_client=http_client,
        max_requests_per_crawl=30,
    )

    await crawler.run(['https://www.crunchbase.com/www-sitemaps/sitemap-index.xml'])

    await crawler.export_data_json("crunchbase_data.json")