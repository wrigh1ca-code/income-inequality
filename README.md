# Two Things Can Be True

A one-page briefing on US inequality and living standards. It measures the same households four ways. Under each, two charts show that things got better for everyone, and two show that the gap got wider:

1. **Market income**: Census household income at selected percentiles, 1967–2024
2. **Income after taxes and transfers**: CBO's distribution of household income, plus poverty measured against fixed standards
3. **Consumption and quality of life**: Meyer & Sullivan's work on consumption inequality, ownership of durable goods by income, and life expectancy by income
4. **Wealth**: shares from the Fed's Distributional Financial Accounts, bottom-50% real net worth, and Survey of Consumer Finances medians by income group

## Running it

`index.html` is self-contained (inline CSS, JavaScript and data, with Google Fonts from a CDN). Open it in a browser, or serve it with GitHub Pages: **Settings → Pages → Deploy from a branch → `main` / root**.

## Data

`data/` holds the derived series behind the charts:

| File | Contents |
|---|---|
| `census_income_percentiles_2024usd.csv` | Census P60-286 Table A-4a: household income at the 10th–95th percentiles, 2024 dollars |
| `bottom50_real_networth_per_household.csv` | Fed DFA bottom-50% net worth ÷ household count, deflated with annual-average CPI-U (author's calculation; refreshed monthly) |
| `dfa_wealth_shares_quarterly.csv` | Fed DFA wealth shares by wealth group, quarterly (created by the first automatic refresh) |
| `scf_median_networth_by_income_2025usd_thousands.csv` | SCF median net worth by income group, collected from Fed bulletins and converted to 2025 dollars with CPI-U (author's calculation) |

Other figures are hard-coded in `index.html` and cited next to each chart. The full source list is at the bottom of the page.

## Updates

Federal Reserve wealth data refresh automatically each month through a GitHub Action, and other figures are reviewed monthly. See [MAINTAINING.md](MAINTAINING.md).

## Caveats

- The Census percentiles are pre-tax money income. Survey redesigns cause breaks in 2013 and 2017.
- The 1989 DFA wealth shares are approximate, because the series is revised every quarter.
- The SCF grouped families by current income through 2007 and by "usual" income after that.
- The durable-goods comparisons combine sources whose income groups don't match exactly.
