import aiohttp
import asyncio

# Define token pairs and their PancakeSwap pair addresses
TOKENS = {
    "USDT-WBNB": "0x16b9a82891338f9ba80e2d6970fdda79d1eb0dae",
    "USDC-WBNB": "0xd99c7f6c65857ac913a8f880a4cb84032ab2fc5b",
    "BUSD-WBNB": "0x1b96b92314c44b159149f7e0303511fb2fc4774f",
    # Add more pairs as needed
}

# Virtual investment amount (simulate trade with this amount)
VIRTUAL_INVESTMENT = 12  # USD
GAS_COST = 0.15  # Estimated gas cost per trade in USD
ARBITRAGE_THRESHOLD = 0.01  # Minimum % profit to consider

# Total profit tracker for simulation
total_virtual_profit = 0

async def fetch_price(session, pair_name, pair_address):
    url = f"https://api.dexscreener.com/latest/dex/pairs/bsc/{pair_address}"
    try:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"[ERROR] {pair_name}: Failed to fetch data (Status: {response.status})")
                return None
            data = await response.json()
            price_info = data.get("pair")
            if not price_info or "priceUsd" not in price_info:
                print(f"[ERROR] {pair_name}: Incomplete data")
                return None
            return {
                "name": pair_name,
                "price": float(price_info["priceUsd"]),
                "dex": "pancakeswap"
            }
    except Exception as e:
        print(f"[ERROR] {pair_name}: {e}")
        return None

async def check_arbitrage():
    global total_virtual_profit
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[
            fetch_price(session, name, address)
            for name, address in TOKENS.items()
        ])

        prices = [r for r in results if r]

        if len(prices) < 2:
            print("[WARN] Not enough token data.")
            return

        found = False
        print("\n\U0001F50D Checking for Arbitrage Opportunities...")

        for i in range(len(prices)):
            for j in range(i + 1, len(prices)):
                p1 = prices[i]
                p2 = prices[j]
                profit_pct = ((p2["price"] - p1["price"]) / p1["price"]) * 100

                gross_return = VIRTUAL_INVESTMENT * (1 + profit_pct / 100)
                net_profit = gross_return - VIRTUAL_INVESTMENT - GAS_COST

                print(f"\n🔎 Comparing: {p1['name']} ➡ {p2['name']}")
                print(f"   {p1['price']:.4f} → {p2['price']:.4f}")
                print(f"   Profit: {profit_pct:.4f}% | Net Profit: ${net_profit:.4f}")

                if net_profit > 0:
                    found = True
                    total_virtual_profit += net_profit
                    print(f"💰 [TRADE SIMULATION] Profit: ${net_profit:.4f} ✅")
                    print(f"   Total Virtual Profit: ${total_virtual_profit:.2f}")

        if not found:
            print("❌ No profitable trades this round.")

async def main():
    while True:
        await check_arbitrage()
        await asyncio.sleep(10)  # Check every 10 seconds

if __name__ == "__main__":
    asyncio.run(main())
