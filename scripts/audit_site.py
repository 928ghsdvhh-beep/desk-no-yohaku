"""Static link inventory and regression checks. Run from repository root."""
import csv, json, re, subprocess
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, parse_qs, unquote
import xml.etree.ElementTree as ET

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.tags=[]; self.heading=''; self.in_heading=False; self.feed(text)
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag in ('h1','h2','h3'): self.in_heading=True; self.heading=''
        a['_heading']=self.heading
        self.tags.append((tag,a))
    def handle_data(self, data):
        if self.in_heading: self.heading+=data
    def handle_endtag(self, tag):
        if tag in ('h1','h2','h3'): self.in_heading=False

root=Path('.')
base=subprocess.check_output(['git','merge-base','HEAD','main'],text=True).strip()
rows=[]; errors=[]; warnings=[]; pages={}
for p in sorted(root.rglob('*.html')):
    t=p.read_text(); page=Page(t); pages[p]=page
    old=subprocess.check_output(['git','show',f'{base}:{p.as_posix()}'],text=True)
    # Preserve complete ad anchor markup, tracking scripts and pixels.
    protected=lambda x: re.findall(r'<a\b[^>]*href=["\'][^"\']*(?:amazon\.|amzn\.)[^"\']*["\'][^>]*>.*?</a>|<script\b[^>]*>.*?</script>|<img\b[^>]*>',x,re.S)
    if protected(t)!=protected(old): errors.append(f'{p}: protected markup changed')
    for tag,a in page.tags:
        u=a.get('href','') if tag=='a' else a.get('src','')
        s=urlsplit(u); host=s.hostname or ''
        if host.endswith('amazon.co.jp') or host.endswith('amzn.to') or 'amazon-adsystem' in host:
            asin=re.search(r'/(?:dp|gp/product)/([A-Z0-9]{10})(?:[/?#]|$)',s.path)
            kind='ASIN直リンク' if asin else '検索結果' if s.path=='/s' else 'その他'
            rows.append([str(p),tag,kind,asin[1] if asin else '',parse_qs(s.query).get('tag',[''])[0],u,'未確認（検索リンクは特定商品を保証しない）' if not asin else '未確認（Amazon本文取得不能）',a.get('_heading','')])
            if tag=='a' and not {'sponsored','noopener','noreferrer'} <= set(a.get('rel','').split()): warnings.append(f'{p}: existing affiliate rel incomplete: {u}')
        if u and not s.scheme and not s.netloc:
            target=(p.parent/unquote(s.path)) if s.path else p
            if s.path.startswith('/'): target=root/s.path.lstrip('/')
            if target.is_dir(): target=target/'index.html'
            if not target.exists() and not target.with_suffix('.html').exists(): errors.append(f'{p}: missing {u}')
            if s.fragment and target.exists() and target.suffix=='.html':
                ids={x.get('id') for _,x in Page(target.read_text()).tags}
                if s.fragment not in ids: errors.append(f'{p}: missing fragment {u}')
    if p.name not in ['404.html','googled51db09eaf8187a0.html']:
        canon=[a.get('href') for tag,a in page.tags if tag=='link' and a.get('rel')=='canonical']
        expected='https://desk-no-yohaku.pages.dev/'+('' if p.name=='index.html' else p.with_suffix('').as_posix())
        if canon!=[expected]: errors.append(f'{p}: canonical {canon}')
        if any('noindex' in a.get('content','').lower() for tag,a in page.tags if tag=='meta' and a.get('name')=='robots'): errors.append(f'{p}: noindex')
urls=[x.text for x in ET.parse('sitemap.xml').getroot().iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
expected={'https://desk-no-yohaku.pages.dev/'+('' if p.name=='index.html' else p.with_suffix('').as_posix()) for p in pages if p.name not in ['404.html','googled51db09eaf8187a0.html']}
if set(urls)!=expected or len(urls)!=len(set(urls)): errors.append('sitemap mismatch')
if 'Sitemap: https://desk-no-yohaku.pages.dev/sitemap.xml' not in Path('robots.txt').read_text(): errors.append('robots sitemap missing')
Path('audits').mkdir(exist_ok=True)
with open('audits/amazon-links.csv','w') as f:
    w=csv.writer(f);w.writerow(['file','element','classification','asin','tracking_id','url','verification','heading_context']);w.writerows(rows)
result={'base_commit':base,'html_files':len(pages),'amazon_occurrences':len(rows),'classification':dict(Counter(r[2] for r in rows)),'unique_asins':sorted({r[3] for r in rows if r[3]}),'tracking_ids':sorted({r[4] for r in rows if r[4]}),'sitemap_urls':len(urls),'warnings':warnings,'errors':errors}
Path('audits/static-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
