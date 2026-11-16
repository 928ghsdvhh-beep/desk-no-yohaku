import urllib.request,json,re
from pathlib import Path
import xml.etree.ElementTree as ET
base='https://desk-no-yohaku.pages.dev'
urls=[x.text for x in ET.parse('sitemap.xml').getroot().iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]+[base+'/robots.txt',base+'/sitemap.xml',base+'/missing-guide-check-20261116']
rows=[]
for url in urls:
 import subprocess
 result=subprocess.check_output(['curl','-sS','-L','--max-time','25','-w','\n%{http_code}\n%{url_effective}',url],text=True)
 text,code,final=result.rsplit('\n',2);status=int(code)
 row=dict(url=url,status=status,final_url=final)
 if url.endswith('20261116'):row['noindex']='noindex' in text
 elif '/notes/' in url or url==base+'/':row['canonical']=re.findall(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"',text)
 if url.endswith('/small-desk'):row['new_content']='机上5cmを使う収納' in text
 if url.endswith('/drawer-organization'):row['new_content']='浅い引き出しでトレーが入らない' in text
 rows.append(row)
Path('audits/guide-live-http-20261116.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');print(json.dumps(rows,ensure_ascii=False,indent=2))
