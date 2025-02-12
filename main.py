import requests
from aiohttp import web

SKYBLOCK_BASE_URL = "https://api.hypixel.net/v2/skyblock"
SKYBLOCK_BAZAAR_API_URL = SKYBLOCK_BASE_URL + "/bazaar"


def get_json(url: str, web_client: requests.Session) -> dict | None:
    response = web_client.get(url)
    if response.status_code != 200:
        return None
    return response.json()


def get_item_and_price(response: dict) -> list | None:
    if response and response.get("success"):
        products = []
        response = response["products"]
        for item_name in response:
            item_quick_status = response[item_name]["quick_status"]
            products.append(
                {
                    "item_id": item_name,
                    "sellPrice": item_quick_status["sellPrice"],
                    "sellVolume": item_quick_status["sellVolume"],
                    "sellOrders": item_quick_status["sellOrders"],
                    "sellMovingWeek": item_quick_status["sellMovingWeek"],
                    "buyPrice": item_quick_status["buyPrice"],
                    "buyVolume": item_quick_status["buyVolume"],
                    "buyOrders": item_quick_status["buyOrders"],
                    "buyMovingWeek": item_quick_status["buyMovingWeek"],
                }
            )
        return products
    return None


async def metrics_handler(request):
    web_client = requests.Session()
    prices = get_json(SKYBLOCK_BAZAAR_API_URL, web_client)
    items = get_item_and_price(prices)

    if not items:
        return web.Response(text="Failed to fetch data", status=500)

    metrics = []
    for item in items:
        item_id = item["item_id"]
        for key, value in item.items():
            if key != "item_id":
                metrics.append(f'skyblock_item{{item_id="{item_id}", type="{key}"}} {value}')

    return web.Response(text="\n".join(metrics).strip(), content_type="text/plain")


def webserver(port=9015):
    app = web.Application()
    app.router.add_get("/metrics", metrics_handler)
    web.run_app(app, port=port)


if __name__ == "__main__":
    webserver()
