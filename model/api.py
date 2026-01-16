import requests
import os
from dotenv import load_dotenv

load_dotenv()


def get_eth_price():
    """
    Get ETH price from CoinMarketCap API.
    Used for Base network (ETH is native currency).
    """
    api_key = os.getenv('CMC_API_KEY')
    if not api_key:
        raise ValueError("Please set the 'CMC_API_KEY' environment variable.")

    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
        'symbol': 'ETH',
        'convert': 'USD'
    }

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key
    }

    response = requests.get(url, headers=headers, params=parameters)
    data = response.json()

    try:
        price = data['data']['ETH']['quote']['USD']['price']
        return price
    except KeyError:
        print("ETH data not found in the API response.")
        return 0.0


def get_token_price(symbol: str):
    """
    Get any token price from CoinMarketCap API.
    """
    api_key = os.getenv('CMC_API_KEY')
    if not api_key:
        raise ValueError("Please set the 'CMC_API_KEY' environment variable.")

    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
        'symbol': symbol.upper(),
        'convert': 'USD'
    }

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key
    }

    response = requests.get(url, headers=headers, params=parameters)
    data = response.json()

    try:
        price = data['data'][symbol.upper()]['quote']['USD']['price']
        return price
    except KeyError:
        print(f"{symbol} data not found in the API response.")
        return 0.0


# Backward compatibility - keep old function name but fetch ETH
def get_swell_price():
    """
    Legacy function - now returns ETH price for Base network.
    """
    return get_eth_price()
