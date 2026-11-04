# Working Life: Türkiye official-data pilot v0.1

## Data release

Reference year: 2025. Five annual rates and their published year-on-year changes are transcribed from [TÜİK bulletin 57996](https://veriportali.tuik.gov.tr/tr/press/57996), published 25 March 2026. The official release and its Metadata tab were inspected in the live portal on 4 November 2026. This is a fixed release-vintage snapshot, not a live data feed. It does not assert that a later revision audit has been completed.

The canonical input is `data/working-life/turkiye-2025.json`. CSV, public JSON and the page panel are generated from that input with `python3 scripts/build_working_life_pilot.py`; `--check` detects drift. No network request, interpolation or imputation is part of the build. Indicator IDs beginning WL are internal identifiers, not invented TÜİK series codes. Official series IDs remain null because this pilot uses the identified bulletin paragraphs, not an API series export.

## Measurement and provenance

Each record preserves rate, unit, age group, numerator/denominator, source heading, role, comparison period and the published change in percentage points. Publication year is distinct from observation year. Values are copied as published, not calculated from rounded person counts. The year-on-year changes are published comparisons; a separate 2024 observation series has not been collected or reconstructed.

The three core observations cover employment, unemployment and broad labour underutilisation. Participation and youth unemployment supply context. The [ILO framework](https://www.ilo.org/sites/default/files/wcmsp5/groups/public/%40dgreports/%40stat/documents/publication/wcms_220535.pdf) supplies the extended-denominator interpretation of LU4. It is not the source of the Türkiye values. Statistical denominators differ: percentages are not additive or directly interchangeable.

## Scoring decision

This is the first real-data dimension dashboard, not an approved composite index. No rank, normalisation, baseline or weights are assigned. Unemployment overlaps LU4, while participation and youth outcomes overlap wider index themes. A naive average would create substantive weighting choices and possible double counting without agreement.

A future score needs agreed outcome groups, non-overlapping indicator roles, fixed and defensible anchors, age/population harmonisation, weighting, coverage rules and sensitivity analysis. International comparisons will use one harmonised series per indicator including Türkiye; national observations cannot silently replace selected countries' values.

## Limits and next collection work

Wages, excessive hours, informal employment and occupational safety have not yet been collected. The panel is therefore an initial labour-market view with incomplete job-quality coverage. No confidence intervals or significance tests have been calculated. Published changes are not evidence of statistical significance on their own. National revisions, survey breaks and cross-country consistency require separate audits before a longitudinal or international release.

Next work: obtain machine-readable annual tables and exact series IDs; reconcile a documented historical vintage; collect working-hours and informality observations; evaluate earnings and safety comparability; audit overlap and decide the scoring specification. Missing values must remain missing. Public exports contain aggregate statistics only.
