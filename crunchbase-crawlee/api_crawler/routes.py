import json

from crawlee.crawlers import HttpCrawlingContext
from crawlee.router import Router
from crawlee import Request, HttpHeaders

router = Router[HttpCrawlingContext]()


@router.default_handler
async def default_handler(context: HttpCrawlingContext) -> None:
    """Default request handler."""
    context.log.info(f'default_handler processing {context.request.url} ...')

    data = json.loads(context.http_response.read())

    requests = []

    for entity in data['entities']:
        permalink = entity["identifier"]["permalink"]
        requests.append(Request.from_url(url=f"https://api.crunchbase.com/api/v4/entities/organizations/{permalink}?field_ids=short_description%2Clocation_identifiers%2Cwebsite_url", label='company'))

    await context.add_requests(requests)


@router.handler('company')
async def company_handler(context: HttpCrawlingContext) -> None:
    """Company request handler."""
    context.log.info(f'company_handler processing {context.request.url} ...')

    data = json.loads(context.http_response.read())

    await context.push_data({
        "Company Name": data['properties']["identifier"]["value"],
        "Short Description": data['properties']["short_description"],
        "Website": data['properties'].get("website_url"),
        "Location": "; ".join([item["value"] for item in data['properties'].get("location_identifiers", [])]),
    })

@router.handler('search')
async def search_handler(context: HttpCrawlingContext) -> None:
    """Company request handler."""
    context.log.info(f'company_handler processing {context.request} ...')

    data = json.loads(context.http_response.read())

    last_entity = None
    results = []

    for entity in data['entities']:
        last_entity = entity['uuid']
        results.append({
        "Company Name": entity['properties']["identifier"]["value"],
        "Short Description": entity['properties']["short_description"],
        "Website": entity['properties'].get("website_url"),
        "Location": "; ".join([item["value"] for item in entity['properties'].get("location_identifiers", [])]),
    })

    if results:
        await context.push_data(results)
    if last_entity:
        payload = json.loads(context.request.payload)
        payload["after_id"] = last_entity
        payload = json.dumps(payload)
        await context.add_requests([Request.from_url(
            url="https://api.crunchbase.com/api/v4/searches/organizations",
            method="POST",
            payload=payload,
            use_extended_unique_key=True,
            headers=HttpHeaders({'Content-Type': 'application/json'}),
            label="search"
            )])

