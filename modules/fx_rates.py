import requests

def fetch_fx_rates(base_currencies, target_currency="inr"):
    rates = {}
    for base in base_currencies:
        url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{base}.json"
        try:
            res = requests.get(url, timeout=5)
            data = res.json()
            rate = data.get(base, {}).get(target_currency)
            rates[f"{base.upper()}/{target_currency.upper()}"] = rate or "Unavailable"
        except:
            rates[f"{base.upper()}/{target_currency.upper()}"] = "Error"
    return rates
