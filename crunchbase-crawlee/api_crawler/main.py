import os
import json

from crawlee.http_crawler import HttpCrawler
from crawlee.http_clients import HttpxHttpClient
from crawlee import ConcurrencySettings, HttpHeaders, Request

from .routes import router

CRUNCHBASE_TOKEN = os.getenv("CRUNCHBASE_TOKEN", "")
SEARCH = True

async def main() -> None:
    """The crawler entry point."""

    concurrency_settings = ConcurrencySettings(max_tasks_per_minute=120)

    http_client = HttpxHttpClient(headers=HttpHeaders({
        "accept-encoding": "gzip, deflate, br, zstd",
        "X-cb-user-key": CRUNCHBASE_TOKEN
        }))
    crawler = HttpCrawler(
        request_handler=router,
        concurrency_settings=concurrency_settings,
        http_client=http_client,
        max_requests_per_crawl=30,
    )

    if SEARCH:
        payload = {'field_ids': ['identifier',
                                 'location_identifiers',
                                 'short_description',
                                 'website_url'],
                    'limit': 200,
                    'order': [{'field_id': 'rank_org', 'sort': 'asc'}],
                    'query': [{'field_id': 'location_identifiers',
                               'operator_id': 'includes',
                                'type': 'predicate',
                                'values': ['e0b951dc-f710-8754-ddde-5ef04dddd9f8']},
                                {'field_id': 'facet_ids',
                                 'operator_id': 'includes',
                                 'type': 'predicate',
                                 'values': ['company']}]}

        payload = json.dumps(payload)
        await crawler.run([Request.from_url(
            url="https://api.crunchbase.com/api/v4/searches/organizations",
            method="POST",
            payload=payload,
            use_extended_unique_key=True,
            headers=HttpHeaders({'Content-Type': 'application/json'}),
            label="search"
            )])
    else:
        await crawler.run(['https://api.crunchbase.com/api/v4/autocompletes?query=apify&collection_ids=organizations&limit=25'])

    await crawler.export_data_json("crunchbase_data.json")