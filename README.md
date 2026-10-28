# SMM Panel Price Index

An open, daily price index for **SMM panels**, the wholesale resellers behind social-media engagement services
(followers, likes, views, plays, comments). Every day [PanelCompare](https://panelcompare.com) reads the public
catalogues of 140+ panels, maps each listing onto one of 180+ canonical services across 43 platforms, and publishes
the distribution of prices per 1,000 units for each service.

This repository is a dated, versioned mirror of that data, refreshed every night from
[panelcompare.com/price-index](https://panelcompare.com/price-index). Licence: **CC BY 4.0**.

| | |
|---|---|
| Live index | https://panelcompare.com/price-index |
| Methodology | https://panelcompare.com/methodology |
| API (no key, CORS open) | https://panelcompare.com/api-docs · [OpenAPI 3.1](https://panelcompare.com/openapi.json) |
| Coverage | 2026-09-07 onward |
| Update | Daily at 23:35 UTC, by [`.github/workflows/update.yml`](.github/workflows/update.yml) |

## Files

| Path | What it holds |
|---|---|
| `data/price-index.csv` / `.json` | The latest index: one row per service, with min, quartiles, median, max and the quotable range. |
| `data/panel-facts.csv` / `.json` | Per panel: domain registration and expiry, registrar, TLS issuer, Tranco rank, and the daily movement of the order counter on its home page. |
| `snapshots/price-index/YYYY-MM-DD.csv` | One frozen copy of `price-index.csv` per index day, never rewritten. |
| `history/price-index-history.csv` | One row per service per day since 2026-09-07: min, median, max, quotable range and panels sampled. |

Daily price-change events (about 25,000 rows a day) are too large to mirror here. They are published per UTC day at
`https://panelcompare.com/data/price-changes/YYYY-MM-DD.csv`.

## Columns of `price-index.csv`

| Column | Meaning |
|---|---|
| `platform_slug`, `platform` | Platform, e.g. `instagram` |
| `service_slug`, `service`, `unit` | Canonical service, e.g. `followers` / Instagram Followers |
| `day` | UTC day the row describes |
| `currency` | Always `USD` |
| `min_price_per_1000` … `max_price_per_1000` | Min, 25th percentile, median, 75th percentile and max over every active listing |
| `panels_sampled` | Distinct panels selling the service (a service needs at least 2 to get a row) |
| `quotable_min_price_per_1000`, `quotable_max_price_per_1000` | Cheapest and dearest listing that is not a single-order package and sits within 10x of the median |
| `comparable` | Whether listings of this service are comparable enough to rank on price |
| `computed_at` | When the row was last recomputed; the current day is recomputed several times a day |
| `url` | The service's page on PanelCompare |

**Quote the quotable range, not `min` and `max`.** Raw extremes include category headings priced as services,
single-order packages and mis-filed rows that the panels themselves publish. The median and quartiles are robust to
them; the min and max are not.

## Caveats

- Prices are what panels list, not what an order delivers. Quality varies widely inside one service.
- A panel quoting in another currency is converted to USD at a dated, stored rate.
- `history/` before 2026-10-26 has no quotable range; that column was introduced then.
- 2026-10-27 is missing from `history/`: the site's rebuild job failed that day.

## Citation

> PanelCompare (2026). *SMM Panel Price Index* [Data set]. https://panelcompare.com/price-index. Licensed under CC BY 4.0.

Machine-readable citation: [`CITATION.cff`](CITATION.cff). Attribution for reuse: "Data: PanelCompare
(panelcompare.com), CC BY 4.0", with a link where the medium allows one.

## Disclosure

PanelCompare is an independent directory. It shows one labelled sponsored panel above its rankings and carries
affiliate links to some panels; neither enters the price index, which is computed from catalogues alone.
Details: https://panelcompare.com/disclosure.

## Contact

hello@panelcompare.com · Issues and corrections welcome in this repository.
