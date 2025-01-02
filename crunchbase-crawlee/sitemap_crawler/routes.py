from gzip import decompress

from crawlee.crawlers import ParselCrawlingContext
from crawlee.router import Router
from crawlee import Request
from parsel import Selector

router = Router[ParselCrawlingContext]()


@router.default_handler
async def default_handler(context: ParselCrawlingContext) -> None:
    """Default request handler."""
    context.log.info(f'default_handler processing {context.request} ...')

    requests = (Request.from_url(url=url, label='sitemap') for url in context.selector.xpath('//loc[contains(., "sitemap-organizations-8")]/text()').getall())

    await context.add_requests(requests, limit=1)

@router.handler('sitemap')
async def sitemap_handler(context: ParselCrawlingContext) -> None:
    """Sitemap gzip request handler."""
    context.log.info(f'sitemap_handler processing {context.request} ...')

    data = context.http_response.read()
    data = decompress(data)

    selector = Selector(data.decode())

    requests = (Request.from_url(url=url, label='company') for url in selector.xpath('//loc/text()').getall())

    await context.add_requests(requests)

@router.handler('company')
async def company_handler(context: ParselCrawlingContext) -> None:
    """Company request handler."""
    context.log.info(f'company_handler processing {context.request} ...')

    json_selector = context.selector.xpath('//*[@id="ng-state"]/text()')

    await context.push_data({
        "Company Name": json_selector.jmespath('HttpState.*.data[].properties.identifier.value').get(),
        "Short Description": json_selector.jmespath('HttpState.*.data[].properties.short_description').get(),
        "Website": json_selector.jmespath('HttpState.*.data[].cards.company_about_fields2.website.value').get(),
        "Location": "; ".join(json_selector.jmespath('HttpState.*.data[].cards.company_about_fields2.location_identifiers[].value').getall()),
    })
