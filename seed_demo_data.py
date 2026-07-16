"""One-off helper to seed the RAG store with a demo portfolio + real news
articles, so the chatbot has something meatier to answer questions about.

Run manually:
    python seed_demo_data.py

Not part of the test suite - this pulls in real, dated news copy and there's
nothing stable to assert against. Just a demo data loader.
"""
from __future__ import annotations

from rag_store import RagStore
from ticker_lookup import company_name

# fake portfolio - not my real holdings, just enough spread to make the
# "what am I exposed to" style questions interesting
FAKE_PORTFOLIO = [
    ("AAPL", 25, 185.20, "Core long-term holding, dividend + buybacks"),
    ("MSFT", 15, 310.00, "Cloud + AI exposure via Azure"),
    ("NVDA", 40, 120.50, "AI datacenter growth story, added on dips"),
    ("TSLA", 10, 210.75, "Speculative, EV + robotaxi bet"),
    ("GOOGL", 20, 135.40, "Search + cloud + Waymo optionality"),
    ("VOO", 30, 410.00, "S&P 500 index fund, core diversification"),
    ("BND", 50, 72.10, "Bond ETF, ballast for the growth names above"),
]

# pulled from real July 2026 coverage, condensed - see urls for the source
ARTICLES = [
    (
        "Nvidia's $1 Trillion Slide Sends Valuation to Pre-AI Boom Levels",
        "https://www.bloomberg.com/news/articles/2026-07-08/nvidia-s-1-trillion-slide-sends-valuation-to-pre-ai-boom-levels",
        "Nvidia has quietly become the worst performer in its own chip group in "
        "2026, up just 5% for the year after losing roughly $1 trillion in "
        "market value in under two months. Reports that the Kyber NVL144 AI "
        "platform would slip to 2028 were denied by the company, and a Goldman "
        "Sachs analyst called the forward P/E of 21.7x 'compelling' given the "
        "5-year average sits near 72x. Blackwell chips remain sold out through "
        "mid-2026.",
    ),
    (
        "Tesla Q2 Deliveries Beat Estimates, Stock Falls Anyway",
        "https://www.forbes.com/sites/zacharyfolk/2026/07/02/tesla-suddenly-plunges-8-despite-beating-expectations-on-deliveries/",
        "Tesla delivered 480,126 vehicles in Q2 2026, up 25% year over year and "
        "well above the ~406,000 Wall Street expected, yet the stock fell "
        "7.49% on the news. The company also launched driverless robotaxi "
        "service in Miami, its third state after Texas and California. Despite "
        "the S&P 500's 9% YTD gain, Tesla is down 12% for the year, trading at "
        "a P/E over 350. Q2 earnings land July 22.",
    ),
    (
        "Apple Hits Record High as Traders Rotate Out of AI Spending Names",
        "https://www.bloomberg.com/news/articles/2026-07-13/apple-s-600-billion-rally-fueled-by-traders-fleeing-ai-selloff",
        "Apple shares climbed 16% since June 25 to a record $321.29 on July 13, "
        "making it the best-performing 'Magnificent Seven' stock in 2026. The "
        "rally is being driven by Apple's choice to skip the AI datacenter "
        "buildout and instead pay Google for frontier model access, now seen "
        "as a strength rather than a laggard move. Free cash flow is projected "
        "to hit a record $140B this year. Foldable iPhone production is "
        "running behind expectations, with the Q3 earnings release on July 30 "
        "seen as the next catalyst.",
    ),
    (
        "S&P 500 2026 Outlook: Wall Street Split Between 7,100 and 8,800",
        "https://fortune.com/2026/07/05/stock-market-outlook-sp500-target-7100-ai-boom-speculation-extreme-levels/",
        "Year-end S&P 500 targets range widely: Bank of America at 7,100 "
        "(implying a pullback from current levels), Goldman Sachs at 8,000 on "
        "24% EPS growth, and Yardeni Research at 8,250. Q2 earnings season "
        "kicked off July 13 with S&P 500 earnings projected to grow 23.3% "
        "year over year, driven partly by ~$754B in hyperscaler AI capex, an "
        "83% jump from 2025. Analysts flagged speculation 'hitting extreme "
        "levels' as a risk, alongside Fed policy, a SpaceX share unlock, and "
        "elevated margin debt.",
    ),
]


def seed() -> None:
    store = RagStore()

    for ticker, shares, cost_basis, note in FAKE_PORTFOLIO:
        name = company_name(ticker)
        ticker_label = f"{ticker} ({name})" if name else ticker
        text = f"Portfolio holding: {shares} shares of {ticker_label} at ${cost_basis:.2f} cost basis. {note}"
        store.add_document(text, source="portfolio", ticker=ticker)

    for title, url, summary in ARTICLES:
        text = f"{title} ({url}): {summary}"
        store.add_document(text, source="article")

    print(f"Seeded {len(store.documents)} documents into {store.path}")


if __name__ == "__main__":
    seed()
