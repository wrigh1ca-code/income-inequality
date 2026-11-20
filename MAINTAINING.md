# Keeping the site current

The site updates in two ways.

1. **Automatic (GitHub Action).** On the 3rd of every month, `.github/workflows/update-data.yml` runs `scripts/update_data.py`. The script pulls the Federal Reserve's wealth data from FRED, checks it, rewrites the `const DATA=` line in `index.html` and the files in `data/`, and commits any change. It refreshes:
   - Bottom-50% real net worth per household (wealth section, left column)
   - Wealth shares of the top 1%, next 9%, next 40% and bottom 50% (wealth section, right column)
   - The "top 1% share" headline figure and its record flag
   - The "Last updated" date in the footer

   Optional: add a free FRED API key as the repository secret `FRED_API_KEY` (Settings → Secrets and variables → Actions). Without one, the script uses FRED's public CSV download, which works but is less reliable.

2. **Monthly review (Claude scheduled task).** A few days after the Action runs, Claude checks the sources below for new releases, updates hand-entered figures in `index.html`, and pushes the change with a note on what changed. Most months there will be nothing new.

## Hand-entered figures and when they change

| Chart / figure | Source | Usually released |
|---|---|---|
| Income at each percentile, growth since 1967, headline +59% / +130%, income ratios | Census, *Income in the United States* (P60 series), Table A-4a | September |
| Before/after taxes and transfers by fifth, top 1% and bottom 20% shares, 14× → 6× | CBO, *The Distribution of Household Income* | Irregular, roughly yearly |
| Full-income poverty | Burkhauser, Corinth, Elwell & Larrimore (NBER WP 26532) and updates | Occasional |
| Consumption poverty | Meyer & Sullivan, Consumption Poverty Report (Notre Dame) | Roughly yearly |
| Income vs spending gap (90/10) | Meyer & Sullivan | Occasional |
| Ownership by low-income households | EIA RECS (AC, dishwasher); Census ACS (computer, broadband); Pew Mobile Fact Sheet (smartphone) | RECS every ~4 years (2024 survey out); ACS each September; Pew irregular |
| Life expectancy by income | National Academies (2015); Chetty et al. (JAMA 2016) | New studies occasionally |
| Median net worth by income group | Federal Reserve Survey of Consumer Finances | Every 3 years (2025 survey published 2026; next ~2029) |

## Where things live in `index.html`

- `const DATA=` (one line near the bottom): the Census percentile table (`census`), bottom-50% series (`b50`), SCF medians (`scf`), Fed wealth shares (`dfa`) and `meta` (last-updated date, dollar base year).
- Other figures are literal values in the `bars(...)` and `dumbbell(...)` calls in the script block, next to the chart IDs (`d1`–`d4`, `c1`–`c4`, `w2`, `w4`), and in the captions and source notes in the HTML.
- When a number changes, update its caption and source note too, and set `meta.updated`.
