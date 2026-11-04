"""Build the static official-observation panel and exports from a reviewed snapshot.

No network requests, imputation, normalisation or composite scoring are performed.
Run with --check to detect drift without writing files.
"""
import argparse
import csv
import html
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/working-life/turkiye-2025.json'
START = '<!-- WORKING_LIFE_PILOT_START -->'
END = '<!-- WORKING_LIFE_PILOT_END -->'

def validate(data):
    if data.get('status') != 'official-release-snapshot' or data.get('geography') != 'TUR':
        raise ValueError('An official Türkiye release snapshot is required')
    if data.get('frequency') != 'annual' or not isinstance(data.get('year'), int):
        raise ValueError('Use an explicit annual reference year')
    if data.get('index_score') is not None or data.get('rank') is not None:
        raise ValueError('The pilot must not invent a score or rank')
    source = data['source']
    for key in ('bulletin_id','url','release_date','accessed_date','release_title','metadata_url','verification','vintage'):
        if not source.get(key):
            raise ValueError(f'Missing provenance: {key}')
    if not source['url'].startswith('https://veriportali.tuik.gov.tr/'):
        raise ValueError('Expected the official TÜİK portal')
    if int(source['release_date'][:4]) <= data['year'] or source['accessed_date'] < source['release_date']:
        raise ValueError('Invalid reference-year/publication/access chronology')
    ids = set()
    for row in data['indicators']:
        value = row.get('value')
        if isinstance(value, bool) or not isinstance(value, (int,float)) or not 0 <= value <= 100:
            raise ValueError('A rate must be a finite numeric percentage')
        change = row.get('published_yoy_change_pp')
        if isinstance(change,bool) or not isinstance(change,(int,float)) or not -100 <= change <= 100:
            raise ValueError('A published change must use percentage points')
        if row['unit'] != 'percent' or row['comparison_year'] != data['year'] - 1:
            raise ValueError('Mismatched unit or change period')
        if row['id'] in ids or row.get('included_in_composite') is not False:
            raise ValueError('Duplicate indicator or unapproved scoring')
        ids.add(row['id'])
        for key in ('name','age_group','numerator','denominator','source_locator','role'):
            if not row.get(key):
                raise ValueError(f'Missing indicator field: {key}')
    if ids != {'WL-01','WL-02','WL-03','WL-04','WL-05'}:
        raise ValueError('Unexpected pilot indicator coverage')
    return data

def csv_text(data):
    out = io.StringIO(newline='')
    fields = ['dataset_id','data_status','geography','observation_year','frequency','sex','population_scope','indicator_id','indicator','value','unit','age_group','numerator','denominator','published_yoy_change_pp','comparison_year','role','included_in_composite','source_institution','source_bulletin_id','source_release_date','source_accessed_date','source_url','source_locator','source_series_id','vintage']
    writer = csv.DictWriter(out,fields,lineterminator='\n')
    writer.writeheader()
    for row in data['indicators']:
        source = data['source']
        writer.writerow(dict(zip(fields,[data['dataset_id'],data['status'],data['geography'],data['year'],data['frequency'],data['sex'],data['population_scope'],row['id'],row['name'],f'{row["value"]:.1f}',row['unit'],row['age_group'],row['numerator'],row['denominator'],f'{row["published_yoy_change_pp"]:+.1f}',row['comparison_year'],row['role'],'false',source['institution'],source['bulletin_id'],source['release_date'],source['accessed_date'],source['url'],row['source_locator'],row['source_series_id'] or '',source['vintage']])))
    return out.getvalue()

def panel(data):
    esc = html.escape
    cards = []
    for row in data['indicators']:
        cards.append(f'''<article class="ci-wl-card"><p class="ci-eyebrow">{esc(row['id'])} / {esc(row['role'])}</p><h3>{esc(row['name'])}</h3><p class="ci-wl-value">{row['value']:.1f}<span>%</span></p><p class="ci-wl-change">{row['published_yoy_change_pp']:+.1f} percentage points vs 2024</p><p class="ci-wl-age">Age {esc(row['age_group'])} · total</p><details><summary>Definition and provenance</summary><p>Numerator: {esc(row['numerator'])}. Denominator: {esc(row['denominator'])}.</p><p>Source section: <span lang="tr">{esc(row['source_locator'])}</span>.</p><a href="{esc(data['source']['url'])}">TÜİK bulletin 57996 ↗</a></details></article>''')
    return '''<section id="working-life-pilot" class="ci-wl" aria-labelledby="wl-title">
<div class="ci-section-heading"><div><p class="ci-eyebrow">TÜRKİYE / FIRST OFFICIAL-DATA PILOT</p><h2 id="wl-title">Working Life · 2025</h2><p>Five published annual observations. Actual percentages, not index scores.</p></div><span class="ci-wl-badge">Official survey estimates · source checked</span></div>
<p class="ci-wl-source">Source: <a href="https://veriportali.tuik.gov.tr/tr/press/57996">TÜİK, <span lang="tr">İşgücü İstatistikleri, 2025</span> · bulletin 57996</a>. Published 25 March 2026; checked 4 November 2026.</p>
<div class="ci-wl-grid">'''+''.join(cards)+'''</div>
<p class="ci-wl-reading"><strong>Read the measures together.</strong> Unemployment fell, while labour underutilisation rose and employment and participation declined. A falling unemployment rate alone does not establish an improvement across working life. Percentage-point changes are published comparisons, not percentage growth rates.</p>
<details class="ci-sse-details"><summary>Coverage, calculation and limits</summary><p>The pilot is a release-vintage snapshot, not a live feed or a reconstruction from rounded headcounts. The annual values are taken directly from one official bulletin. No monthly, seasonally adjusted or modelled international series is substituted.</p><p>Population coverage follows the Household Labour Force Survey: non-institutional households. Youth unemployment uses the youth labour force, not all young people. LU4 uses an extended labour-force denominator; see <a href="https://www.ilo.org/sites/default/files/wcmsp5/groups/public/%40dgreports/%40stat/documents/publication/wcms_220535.pdf">ILO measurement framework</a>. The rates have different denominators and must not be added.</p><p>No composite score, rank, weights or normalisation have been assigned. Unemployment is part of labour underutilisation, so equal-weight aggregation would risk double counting. Participation and youth unemployment are context measures here; potential overlap with other dimensions must be reviewed.</p><p>Wages, excessive hours, informal employment and occupational safety are not yet collected in this pilot. It is an initial labour-market view, not full coverage of job quality. Sampling uncertainty and later revisions have not been quantified; published changes are not claims of statistical significance.</p></details>
<div class="ci-sse-downloads"><a href="assets/index/working-life-turkiye-2025.csv" download>Official observations and provenance (CSV) ↓</a><a href="assets/index/working-life-turkiye-2025.json" download>Reviewed data snapshot (JSON) ↓</a><a href="assets/index/working-life-methodology.md" download>Pilot method and next steps ↓</a></div>
</section>'''

def outputs(data):
    page = ROOT / 'cahspar-index.qmd'
    text = page.read_text()
    if text.count(START) != 1 or text.count(END) != 1:
        raise ValueError('Expected exactly one generated panel region')
    before, rest = text.split(START)
    _, after = rest.split(END)
    return {page:before+START+'\n'+panel(data)+'\n'+END+after,
            ROOT/'assets/index/working-life-turkiye-2025.csv':csv_text(data),
            ROOT/'assets/index/working-life-turkiye-2025.json':json.dumps(data,ensure_ascii=False,indent=2)+'\n'}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    data = validate(json.loads(DATA.read_text()))
    for path, text in outputs(data).items():
        if args.check:
            if not path.exists() or path.read_text() != text:
                raise SystemExit(f'Generated output is out of date: {path.relative_to(ROOT)}')
        else:
            path.write_text(text)
    print('Working Life pilot: five official observations; no score or rank; generated outputs verified.' if args.check else 'Built Working Life pilot and exports.')

if __name__ == '__main__':
    main()
