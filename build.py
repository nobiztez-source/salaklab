#!/usr/bin/env python3
"""สร้างหน้าแชร์ของสลากแล็บ: ดึงผลล่าสุด -> ทำรูป og -> เขียน index.html
รันบน GitHub Actions (ดู .github/workflows/og.yml) หรือรันเองก็ได้:
  python3 build.py            # สร้างเมื่อมีงวดใหม่
  python3 build.py --force    # สร้างใหม่ทุกครั้ง
"""
import datetime, html, json, os, pathlib, subprocess, sys, tempfile, urllib.error, urllib.parse, urllib.request

APP_URL = 'https://script.google.com/macros/s/AKfycbxhIOh8KTaJEmsvedhI3ISnYBu2-YHDENgIs1xWBuEovL18AyrmJyP5eKSXrr25XMAyQw/exec'
ROOT = pathlib.Path(__file__).resolve().parent
TH_MONTHS = ['', 'ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.']


def site_url():
    repo = os.environ.get('GITHUB_REPOSITORY', 'owner/salaklab')
    owner, name = repo.split('/')
    if name.lower() == owner.lower() + '.github.io':
        return 'https://%s.github.io/' % owner.lower()
    return 'https://%s.github.io/%s/' % (owner.lower(), name)


def th_date(d):
    y, m, dd = d.split('-')
    return '%d %s %d' % (int(dd), TH_MONTHS[int(m)], int(y) + 543)


def fetch_latest():
    if os.environ.get('LATEST_JSON'):
        return json.loads(pathlib.Path(os.environ['LATEST_JSON']).read_text('utf-8'))
    req = urllib.request.Request(APP_URL + '?api=latest', headers={'User-Agent': 'salaklab-pages-builder'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))


def card_html(d):
    e = html.escape
    tiles = ''.join('<b>%s</b>' % e(c) for c in d['first'])
    f3 = ' '.join(d.get('front3') or []) or '-'
    l3 = ' '.join(d.get('last3') or []) or '-'
    return '''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:K;font-weight:800;src:url(fonts/Kanit-ExtraBold.ttf)}
@font-face{font-family:K;font-weight:600;src:url(fonts/Kanit-SemiBold.ttf)}
@font-face{font-family:A;font-weight:100 900;src:url(fonts/Anuphan.ttf)}
*{margin:0;box-sizing:border-box}
html,body{width:1200px;height:630px;overflow:hidden}
body{background:#0B3B33;color:#fff;font-family:A,K,sans-serif;position:relative;padding:54px 64px}
.ring{position:absolute;right:-170px;top:-230px;width:640px;height:640px;border-radius:50%%;border:110px solid rgba(255,255,255,.05)}
.top{display:flex;align-items:center;gap:18px;font:600 36px K}
.free{background:#FFC233;color:#1f1600;font:800 26px K;padding:4px 18px;border-radius:30px}
.lab{margin-top:30px;color:#b9d6cb;font-size:30px;font-weight:500}
.row{display:flex;gap:14px;margin-top:16px;align-items:stretch}
.row b{width:112px;height:150px;border-radius:20px;background:rgba(255,255,255,.12);display:grid;place-items:center;font:800 104px/1 K;color:#fff}
.two{margin-left:16px;background:#FFC233;color:#1f1600;border-radius:20px;width:236px;display:flex;flex-direction:column;justify-content:center;padding:0 26px}
.two small{font:600 24px A;color:#3d2c00}.two strong{font:800 96px/1 K}
.sub{display:flex;gap:40px;margin-top:26px;font-size:28px;color:#d3e6df}
.sub em{font:600 30px K;color:#fff;font-style:normal;letter-spacing:1px;margin-left:10px}
.cta{position:absolute;left:64px;right:64px;bottom:44px;display:flex;justify-content:space-between;align-items:center}
.cta span{font:800 40px K;color:#FFC233}
.cta i{font-style:normal;font-size:22px;color:#8fb3a6}
</style></head><body><div class="ring"></div>
<div class="top">สลากแล็บ <span class="free">ตรวจฟรี</span></div>
<div class="lab">ผลสลากกินแบ่งรัฐบาล งวด %s · รางวัลที่ 1</div>
<div class="row">%s<div class="two"><small>เลขท้าย 2 ตัว</small><strong>%s</strong></div></div>
<div class="sub"><span>เลขหน้า 3 ตัว<em>%s</em></span><span>เลขท้าย 3 ตัว<em>%s</em></span></div>
<div class="cta"><span>กดตรวจสลากของคุณ →</span><i>ข้อมูลเพื่อความบันเทิง ตรวจผลจริงกับกองสลากอีกครั้ง</i></div>
</body></html>''' % (e(th_date(d['date'])), tiles, e(d['last2']), e(f3), e(l3))


def index_html(d, img_name):
    e = html.escape
    url = site_url()
    title = 'ผลหวย งวด %s รางวัลที่ 1: %s ท้าย 2 ตัว: %s | สลากแล็บ' % (th_date(d['date']), d['first'], d['last2'])
    desc = 'ตรวจหวยรัฐบาลครบทุกรางวัล ฟรี! ใส่เลขหรือถ่ายรูปสลากแล้วรู้ผลทันที พร้อมทำนายฝัน และสถิติเลขสำนักว่าแม่นจริงหรือแค่ดวง'
    f3 = ' '.join(d.get('front3') or []) or '-'
    l3 = ' '.join(d.get('last3') or []) or '-'
    digits = ''.join('<b>%s</b>' % e(c) for c in d['first'])
    img = url + img_name
    return '''<!doctype html><html lang="th"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="สลากแล็บ">
<meta property="og:url" content="{u}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:image" content="{i}">
<meta property="og:image:secure_url" content="{i}">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="ผลสลากงวด {dt} รางวัลที่ 1 {f}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="{i}">
<link rel="icon" href="icon.svg" type="image/svg+xml">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="สลากแล็บ">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#0B3B33">
<style>html,body{{margin:0;height:100%;background:#0B3B33}}
#inst{{position:fixed;left:50%;top:calc(10px + env(safe-area-inset-top));transform:translateX(-50%);z-index:9;display:none;align-items:center;gap:8px;width:max-content;max-width:min(440px,calc(100% - 32px));box-sizing:border-box;background:#FFC233;color:#1f1600;font:700 14px/1.35 system-ui,sans-serif;padding:8px 8px 8px 14px;border-radius:24px;box-shadow:0 6px 20px rgba(0,0,0,.3)}}
#inst button{{font:inherit;border:0;border-radius:18px;cursor:pointer;white-space:nowrap;flex:none}}#inst .go{{background:#0B3B33;color:#fff;padding:7px 14px}}#inst .x{{background:transparent;color:#1f1600;padding:4px 8px;font-size:18px;line-height:1}}
#app{{position:fixed;inset:0;width:100%;height:100%;border:0;display:block;background:#0B3B33;opacity:0;transition:opacity .35s}}
#app.ready{{opacity:1}}
#fb{{position:fixed;inset:0;display:grid;place-items:center;color:#fff;font-family:system-ui,sans-serif;text-align:center;padding:16px;box-sizing:border-box;overflow:auto}}
#fb .c{{width:100%;max-width:420px}}
#fb .k{{color:#b9d6cb;font-size:14px;margin:0 0 6px}}
#fb .d{{display:flex;gap:6px;justify-content:center;margin:6px 0 12px}}
#fb .d b{{flex:1;max-width:56px;background:#fff;color:#0B3B33;border-radius:12px;font:800 34px/1 system-ui,sans-serif;padding:12px 0}}
#fb .s{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;font-size:13px;color:#b9d6cb}}
#fb .s div{{background:rgba(255,255,255,.08);border-radius:12px;padding:8px 4px}}#fb .s strong{{display:block;color:#fff;font-size:18px}}
#fb .s .two{{background:#FFC233;color:#3d2f00}}#fb .s .two strong{{color:#1f1600;font-size:24px}}
#fb .w{{margin-top:16px;font-size:14px;color:#b9d6cb}}
#fb .sp{{display:inline-block;width:14px;height:14px;border:2px solid #b9d6cb;border-top-color:transparent;border-radius:50%;animation:r 1s linear infinite;vertical-align:-2px;margin-right:6px}}
@keyframes r{{to{{transform:rotate(360deg)}}}}
@media (prefers-reduced-motion:reduce){{#fb .sp{{animation:none}}#app{{transition:none}}}}
#fb a{{display:inline-block;margin-top:10px;color:#FFC233;font-weight:700;font-size:14px}}</style>
</head><body>
<div id="fb"><div class="c">
<p class="k">ผลสลากกินแบ่งรัฐบาล งวด {dt} · รางวัลที่ 1</p>
<div class="d" aria-label="รางวัลที่ 1 {f}">{dg}</div>
<div class="s"><div>เลขหน้า 3 ตัว<strong>{f3}</strong></div><div>เลขท้าย 3 ตัว<strong>{l3}</strong></div><div class="two">ท้าย 2 ตัว<strong>{l2}</strong></div></div>
<p class="w"><span class="sp" aria-hidden="true"></span>กำลังเปิดหน้าตรวจสลากของคุณ…</p>
<a href="{a}">ถ้าไม่ขึ้น กดที่นี่</a>
</div></div>
<iframe id="app" title="สลากแล็บ" allow="clipboard-write; web-share; camera" referrerpolicy="no-referrer-when-downgrade"></iframe>
<div id="inst" role="dialog" aria-label="ติดตั้งแอป"><span id="instTxt"></span><button class="go" id="instGo" type="button">ติดตั้ง</button><button class="x" id="instX" type="button" aria-label="ปิด">×</button></div>
<script>
(function(){{
  var app={aj}, q=location.search.replace(/^\\?/,'').split('&').filter(function(p){{return p&&p.indexOf('d=')!==0;}}).join('&');
  var f=document.getElementById('app'), done=false;
  function show(){{if(done)return;done=true;f.className='ready';}}
  f.addEventListener('load',function(){{setTimeout(show,1500);}});
  setTimeout(show,9000);
  f.src=app+(q?'?'+q:'')+location.hash;
}})();
if('serviceWorker' in navigator){{window.addEventListener('load',function(){{navigator.serviceWorker.register('sw.js').catch(function(){{}});}});}}
(function(){{
  var K='slk_inst_hide', box=document.getElementById('inst'), txt=document.getElementById('instTxt'), go=document.getElementById('instGo'), ev=null;
  function quiet(){{try{{return Date.now()-(+localStorage.getItem(K)||0)<12096e5;}}catch(e){{return false;}}}}
  function hide(remember){{box.style.display='none';if(remember){{try{{localStorage.setItem(K,String(Date.now()));}}catch(e){{}}}}}}
  function show(){{if(quiet())return;box.style.display='flex';setTimeout(function(){{hide(false);}},15000);}}
  var standalone=(window.matchMedia&&matchMedia('(display-mode: standalone)').matches)||navigator.standalone;
  if(standalone)return;
  document.getElementById('instX').onclick=function(){{hide(true);}};
  window.addEventListener('beforeinstallprompt',function(e){{e.preventDefault();ev=e;txt.textContent='ติดตั้งสลากแล็บไว้หน้าจอ ตรวจหวยได้ในแตะเดียว';go.style.display='';show();}});
  go.onclick=function(){{if(!ev)return;ev.prompt();ev.userChoice.then(function(){{ev=null;hide(true);}});}};
  var ios=/iphone|ipad|ipod/i.test(navigator.userAgent)&&!/crios|fxios/i.test(navigator.userAgent);
  if(ios){{txt.textContent='เพิ่มสลากแล็บไว้หน้าจอ: แตะปุ่มแชร์ แล้วเลือก "เพิ่มไปยังหน้าจอโฮม"';go.style.display='none';setTimeout(show,4000);}}
}})();
</script>
</body></html>'''.format(t=e(title), d=e(desc), u=e(url + '?d=' + d['date'].replace('-', '')), i=e(img), dt=e(th_date(d['date'])), f=e(d['first']),
                         n=e(img_name), a=e(APP_URL), aj=json.dumps(APP_URL),
                         dg=digits, f3=e(f3), l3=e(l3), l2=e(d['last2']))


FULL_KEYS = ('near1', 'second', 'third', 'fourth', 'fifth')


CODEX_URL = 'https://salaklab.ealaearendel.chatgpt.site'  # เว็บเวอร์ชัน Codex: ดึงผลจริงจากกองสลากครบทุกรางวัล


def fetch_l6(date):
    """ผลครบทุกรางวัลจากเว็บ Codex (ดึงจากประกาศกองสลาก) หรือ None"""
    req = urllib.request.Request(CODEX_URL + '/api/l6?date=' + date, headers={'User-Agent': 'salaklab-pages-builder'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError:
        return None


def parse_l6(date, row):
    """แปลงรูปแบบ n[173] ของ Codex: ที่1, หน้า3 x2, ท้าย3 x2, ท้าย2, ข้างเคียง x2, ที่2 x5, ที่3 x10, ที่4 x50, ที่5 x100"""
    n = (row or {}).get('n') or []
    if len(n) != 173:
        return None
    widths = [6, 3, 3, 3, 3, 2] + [6] * 167
    if any(not (isinstance(x, str) and x.isdigit() and len(x) == w) for x, w in zip(n, widths)):
        return None
    out = {'date': date, 'first': n[0], 'front3': n[1:3], 'last3': n[3:5], 'last2': n[5], 'near1': n[6:8],
           'second': n[8:13], 'third': n[13:23], 'fourth': n[23:73], 'fifth': n[73:173]}
    url = str(row.get('url') or '')
    if url.startswith('https://api.glo.or.th/') or url.startswith('https://www.glo.or.th/'):
        out['glo_url'] = url
    return out


def enrich(d):
    """เติมรางวัลที่ 2–5 + ลิงก์ประกาศกองสลากจากเว็บ Codex เฉพาะเมื่อเลขหลักตรงกับระบบเรา (ตรวจไขว้สองแหล่ง)"""
    if all(d.get(k) for k in FULL_KEYS) and d.get('glo_url'):
        return d
    try:
        r = parse_l6(d['date'], fetch_l6(d['date']))
    except Exception as e:  # ห้ามทำให้งานหลักล้ม
        print('ดึงผลจากเว็บ Codex ไม่สำเร็จ: %r' % e)
        return d
    if not r:
        return d
    if (r['first'], r['last2'], sorted(r['front3']), sorted(r['last3'])) != (d['first'], d['last2'], sorted(d.get('front3') or []), sorted(d.get('last3') or [])):
        print('ผลจากเว็บ Codex ไม่ตรงกับระบบเรา งวด %s: ไม่ใช้' % d['date'])
        return d
    out = dict(d)
    for k in FULL_KEYS + ('glo_url',):
        if r.get(k) and not out.get(k):
            out[k] = r[k]
    return out


def upgrade_archive(max_pages=25):
    """หน้าผลงวดเก่าที่ยังไม่มีช่องตรวจ: ดึงผลครบจากเว็บ Codex แล้วสร้างใหม่ทีละน้อย"""
    base = ROOT / 'r'
    if not base.is_dir():
        return 0
    keys = sorted([p.name for p in base.iterdir() if p.is_dir() and p.name.isdigit()], reverse=True)
    done = tries = 0
    for i, key in enumerate(keys):
        if done >= max_pages or tries >= max_pages * 2:
            break
        page = base / key / 'index.html'
        text = page.read_text('utf-8') if page.is_file() else 'id="q"'
        if 'id="q"' in text:
            continue
        date = '%s-%s-%s' % (key[:4], key[4:6], key[6:])
        tries += 1
        r = parse_l6(date, fetch_l6(date))
        if not r or r['first'] not in text:  # ตรวจไขว้: รางวัลที่ 1 ต้องตรงกับหน้าเดิม
            continue
        page.write_text(archive_html(r, keys[i + 1:]), 'utf-8')
        done += 1
    print('อัปเกรดหน้าผลเก่าให้ตรวจได้ครบ %d หน้า' % done)
    return done


def safe_upgrade():
    try:
        upgrade_archive(int(os.environ.get('UPGRADE_MAX', '25')))
    except Exception as e:  # ห้ามทำให้งานหลักล้ม
        print('อัปเกรดหน้าผลเก่าไม่สำเร็จรอบนี้: %r' % e)


def checker_js(d):
    """ตรวจสลากในหน้าเว็บเลย ไม่ต้องเรียก Apps Script (วันหวยออกคนเยอะก็ไม่ล่ม)"""
    data = {'first': [d['first']], 'last2': d['last2'], 'front3': d.get('front3') or [], 'last3': d.get('last3') or []}
    for k in FULL_KEYS:
        data[k] = d.get(k) or []
    return ('var SLK=' + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + ';'
            "var SLK_P=[['first','รางวัลที่ 1',6000000],['near1','ข้างเคียงรางวัลที่ 1',100000],['second','รางวัลที่ 2',200000],"
            "['third','รางวัลที่ 3',80000],['fourth','รางวัลที่ 4',40000],['fifth','รางวัลที่ 5',20000]];"
            "function slkCheck(n){var w=[];SLK_P.forEach(function(p){if(SLK[p[0]].indexOf(n)>=0)w.push([p[1],p[2]]);});"
            "if(SLK.front3.indexOf(n.slice(0,3))>=0)w.push(['เลขหน้า 3 ตัว',4000]);"
            "if(SLK.last3.indexOf(n.slice(3))>=0)w.push(['เลขท้าย 3 ตัว',4000]);"
            "if(SLK.last2===n.slice(4))w.push(['เลขท้าย 2 ตัว',2000]);return w;}")


def checker_html(d):
    full = all(d.get(k) for k in FULL_KEYS)
    note = '' if full else '<p class="warn">รางวัลที่ 2–5 และรางวัลข้างเคียงของงวดนี้ยังประกาศไม่ครบในระบบ ตอนนี้ตรวจได้เฉพาะรางวัลที่ 1, เลขหน้า 3 ตัว, เลขท้าย 3 ตัว และเลขท้าย 2 ตัว</p>'
    return ('<section class="chk"><h2>ตรวจสลากของคุณ งวดนี้</h2>'
            '<p class="muted">พิมพ์เลข 6 หลัก ใส่ได้หลายใบ คั่นด้วยเว้นวรรค</p>' + note +
            '<textarea id="q" inputmode="numeric" rows="2" placeholder="เช่น 123456 654321"></textarea>'
            '<button id="go" type="button">ตรวจเลย</button><div id="out" aria-live="polite"></div></section>'
            '<script>' + checker_js(d) +
            "(function(){var q=document.getElementById('q'),o=document.getElementById('out');"
            "function fmt(x){return x.toLocaleString('th-TH');}"
            "function run(){var input=q.value.trim().replace(/[๐-๙]/g,function(c){return String(c.charCodeAt(0)-3664);});"
            "if(!input){o.innerHTML='<p class=\"muted\">ใส่เลข 6 หลักก่อนนะ</p>';return;}"
            "var ns=input.split(/\\s+/);"
            "if(ns.length>20){o.innerHTML='<p class=\"warn\">ตรวจได้ครั้งละไม่เกิน 20 ใบ</p>';return;}"
            "if(ns.some(function(n){return !/^[0-9]{6}$/.test(n);})){o.innerHTML='<p class=\"warn\">เลขสลากต้องมี 6 หลักต่อใบ คั่นแต่ละใบด้วยเว้นวรรคหรือขึ้นบรรทัดใหม่</p>';return;}"
            "o.innerHTML=ns.map(function(n){var w=slkCheck(n),t=w.reduce(function(a,x){return a+x[1];},0);"
            "return '<div class=\"res '+(w.length?'win':'')+'\"><b>'+n+'</b> '+(w.length?w.map(function(x){return x[0]+' ('+fmt(x[1])+' บาท)';}).join(', ')+(w.length>1?' รวม '+fmt(t)+' บาท':''):'ไม่ถูกรางวัล')+'</div>';}).join('');}"
            "document.getElementById('go').onclick=run;q.addEventListener('keydown',function(e){if(e.key==='Enter'){e.preventDefault();run();}});})();"
            '</script>')


def archive_html(d, older):
    """หน้าผลรายงวดแบบข้อความล้วน ให้ Google เก็บได้ (หน้าแรกเป็น iframe ซึ่ง Google อ่านเนื้อหาไม่ได้)"""
    e = html.escape
    url = site_url()
    key = d['date'].replace('-', '')
    dt = th_date(d['date'])
    f3 = ' '.join(d.get('front3') or []) or '-'
    l3 = ' '.join(d.get('last3') or []) or '-'
    title = 'ตรวจหวย %s ผลสลากกินแบ่งรัฐบาล รางวัลที่ 1 %s เลขท้าย 2 ตัว %s | สลากแล็บ' % (dt, d['first'], d['last2'])
    desc = 'ผลสลากกินแบ่งรัฐบาล งวด %s รางวัลที่ 1 %s เลขหน้า 3 ตัว %s เลขท้าย 3 ตัว %s เลขท้าย 2 ตัว %s ตรวจสลากของคุณฟรีที่สลากแล็บ' % (dt, d['first'], f3, l3, d['last2'])
    links = ''.join('<li><a href="../%s/">ผลหวย งวด %s</a></li>' % (k, e(th_date('%s-%s-%s' % (k[:4], k[4:6], k[6:])))) for k in older[:24])
    more = ('<h2 style="font-size:18px">ผลหวยงวดก่อน ๆ</h2><ul>' + links + '</ul>') if links else ''
    return '''<!doctype html><html lang="th"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{t}</title>
<meta name="description" content="{ds}">
<link rel="canonical" href="{u}">
<meta property="og:type" content="article"><meta property="og:title" content="{t}"><meta property="og:description" content="{ds}"><meta property="og:url" content="{u}">
<meta name="theme-color" content="#0B3B33">
<link rel="icon" href="../../icon.svg" type="image/svg+xml"><link rel="manifest" href="../../manifest.webmanifest"><link rel="apple-touch-icon" href="../../apple-touch-icon.png">
<style>body{{margin:0;background:#eef3ef;color:#0f2a24;font:16px/1.6 system-ui,sans-serif}}main{{max-width:640px;margin:0 auto;padding:20px 16px 40px}}
h1{{font-size:24px;line-height:1.3;margin:8px 0 16px}}.p1{{font:800 44px/1.1 system-ui,sans-serif;letter-spacing:6px;background:#0B3B33;color:#fff;border-radius:18px;padding:18px;text-align:center}}
table{{width:100%;border-collapse:collapse;margin:16px 0;background:#fff}}td,th{{padding:12px;border-bottom:1px solid #d6e2db;text-align:left}}td b{{font-size:20px;letter-spacing:1px}}
.cta{{display:block;text-align:center;background:#FFC233;color:#1f1600;font-weight:800;font-size:18px;padding:14px;border-radius:40px;text-decoration:none;margin:20px 0}}
.muted{{color:#4d6a62;font-size:14px}}a{{color:#0b3b33}}
.chk{{background:#fff;border-radius:18px;padding:16px;margin:16px 0}}.chk h2{{font-size:19px;margin:0 0 4px}}.chk textarea{{width:100%;box-sizing:border-box;font:700 22px/1.4 system-ui,sans-serif;letter-spacing:2px;padding:10px;border:2px solid #b9cfc4;border-radius:12px}}.chk button{{width:100%;margin-top:10px;background:#0B3B33;color:#fff;border:0;border-radius:40px;padding:13px;font:800 18px system-ui,sans-serif}}.res{{padding:10px 12px;border-radius:12px;background:#eef3ef;margin-top:8px}}.res.win{{background:#FFE9A8}}.warn{{background:#fff4d6;border-radius:10px;padding:8px 10px;font-size:14px}}</style>
</head><body><main>
<p class="muted"><a href="../../">สลากแล็บ</a> › ผลหวยย้อนหลัง</p>
<h1>ผลสลากกินแบ่งรัฐบาล งวด {dt}</h1>
<p class="muted">รางวัลที่ 1</p>
<div class="p1">{f}</div>
{chk}
<table>
<tr><th>เลขหน้า 3 ตัว</th><td><b>{f3}</b></td></tr>
<tr><th>เลขท้าย 3 ตัว</th><td><b>{l3}</b></td></tr>
<tr><th>เลขท้าย 2 ตัว</th><td><b>{l2}</b></td></tr>
</table>
{glo}<a class="cta" href="../../">เก็บสลากไว้ใน "สลากของฉัน" ให้ตรวจอัตโนมัติทุกงวด</a>
<p class="muted">ตรวจผลจริงกับใบตรวจของสำนักงานสลากกินแบ่งรัฐบาล (glo.or.th) อีกครั้งก่อนขึ้นเงิน ข้อมูลเพื่อความสะดวกเท่านั้น</p>
{more}
</main></body></html>'''.format(t=e(title), ds=e(desc), u=e(url + 'r/' + key + '/'), dt=e(dt), f=e(d['first']), f3=e(f3), l3=e(l3), l2=e(d['last2']), more=more, chk=checker_html(d), glo=('<p class="muted"><a href="%s" rel="noopener">เปิดใบประกาศผลของกองสลาก (PDF) ↗</a></p>' % e(d['glo_url'])) if d.get('glo_url') else '')


def write_archive(d):
    """เขียนหน้าผลงวดนี้ (เก็บของงวดเก่าไว้) + sitemap.xml + robots.txt"""
    base = ROOT / 'r'
    key = d['date'].replace('-', '')
    older = sorted([p.name for p in base.iterdir() if p.is_dir() and p.name.isdigit() and p.name != key], reverse=True) if base.is_dir() else []
    page = base / key / 'index.html'
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(archive_html(d, older), 'utf-8')
    write_sitemap()


def today():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime('%Y-%m-%d')


def fetch_result(date):
    req = urllib.request.Request(APP_URL + '?api=result&date=' + date, headers={'User-Agent': 'salaklab-pages-builder'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))


def candidate_dates(stop_year=2006):
    """วันที่อาจเป็นวันออกรางวัล ไล่จากล่าสุดย้อนไป (งวดปกติ 1, 16 และวันเลื่อนที่พบบ่อย 2, 17, 30 ธ.ค.)"""
    t = today()
    y, m = int(t[:4]), int(t[5:7])
    while y >= stop_year:
        days = [17, 16, 2, 1] + ([30] if m == 12 else [])
        for dd in sorted(days, reverse=True):
            d = '%04d-%02d-%02d' % (y, m, dd)
            if d < t:
                yield d
        m -= 1
        if m == 0:
            y, m = y - 1, 12


def backfill(max_new=24, max_calls=60):
    """เติมหน้าผลงวดย้อนหลังทีละน้อยทุกรอบ จำวันที่ไม่มีงวดไว้ใน r/tried.json จะได้ไม่ถามซ้ำ"""
    base = ROOT / 'r'
    base.mkdir(exist_ok=True)
    tried_file = base / 'tried.json'
    try:
        tried = set(json.loads(tried_file.read_text('utf-8')))
    except (OSError, ValueError):
        tried = set()
    have = {p.name for p in base.iterdir() if p.is_dir() and p.name.isdigit()}
    added = calls = 0
    for d in candidate_dates():
        key = d.replace('-', '')
        if key in have or d in tried:
            continue
        # งวดเดียวกันมีได้วันเดียว: ถ้าครึ่งเดือนนี้มีหน้าแล้ว ไม่ต้องถามวันเลื่อน
        half = [k for k in have if k[:6] == key[:6] and ((int(k[6:]) <= 3) == (int(key[6:]) <= 3))]
        if half:
            continue
        if added >= max_new or calls >= max_calls:
            break
        calls += 1
        r = fetch_result(d)
        if r.get('first') and len(r['first']) == 6:
            page = base / key / 'index.html'
            page.parent.mkdir(parents=True, exist_ok=True)
            page.write_text(archive_html(dict({'date': d, 'first': r['first'], 'last2': r['last2'], 'front3': r.get('front3') or [], 'last3': r.get('last3') or []}, **{k: r.get(k) or [] for k in FULL_KEYS}),
                                         sorted(have, reverse=True)), 'utf-8')
            have.add(key)
            added += 1
        elif r.get('none'):
            tried.add(d)
    tried_file.write_text(json.dumps(sorted(tried)), 'utf-8')
    write_sitemap()
    print('เติมผลย้อนหลัง %d งวด (ถาม %d ครั้ง)' % (added, calls))
    return added


def write_sitemap():
    base = ROOT / 'r'
    url = site_url()
    keys = sorted([p.name for p in base.iterdir() if p.is_dir() and p.name.isdigit()], reverse=True) if base.is_dir() else []
    locs = [url] + [url + 'r/' + k + '/' for k in keys] + dream_urls()
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                                      ''.join('<url><loc>%s</loc></url>\n' % html.escape(u) for u in locs) + '</urlset>\n', 'utf-8')
    (ROOT / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: %ssitemap.xml\n' % url, 'utf-8')


# ---------------- หน้าทำนายฝันรายคำ (ให้ Google เจอ "ฝันเห็น___ เลขอะไร") ----------------
DREAM_SOURCES = 'Sanook, ไทยรัฐ, Wongnai, Shopee Blog, อมรินทร์ทีวี'


def fetch_dreams():
    with urllib.request.urlopen(APP_URL + '?api=dreams', timeout=60) as r:
        data = json.loads(r.read().decode('utf-8'))
    out = []
    for x in (data.get('dreams') or [])[:400]:
        w = str(x.get('w') or '').strip()
        if not w or '/' in w or w.startswith('.'):
            continue
        out.append({'w': w[:40], 'a': str(x.get('a') or '')[:120],
                    'two': [n for n in x.get('two') or [] if str(n).isdigit() and len(str(n)) == 2][:8],
                    'three': [n for n in x.get('three') or [] if str(n).isdigit() and len(str(n)) == 3][:8],
                    'd': [n for n in x.get('d') or [] if str(n).isdigit() and len(str(n)) == 1][:8]})
    return out


def dream_slug(w):
    return w.replace(' ', '-')


def dream_urls():
    f = ROOT / 'dream' / 'list.json'
    if not f.is_file():
        return []
    url = site_url()
    return [url + 'dream/'] + [url + 'dream/' + urllib.parse.quote(dream_slug(x['w'])) + '/' for x in json.loads(f.read_text('utf-8'))]


DREAM_CSS = '''body{margin:0;background:#eef3ef;color:#0f2a24;font:16px/1.6 system-ui,sans-serif}main{max-width:640px;margin:0 auto;padding:20px 16px 40px}
h1{font-size:24px;line-height:1.3;margin:8px 0 12px}h2{font-size:17px;margin:18px 0 6px}.muted{color:#4d6a62;font-size:14px}a{color:#0b3b33}
.nums{display:flex;flex-wrap:wrap;gap:8px}.nums b{font:800 26px/1 system-ui,sans-serif;letter-spacing:2px;background:#fff6db;border:1px solid #ffc233;border-radius:14px;padding:10px 16px}
.cta{display:block;text-align:center;background:#FFC233;color:#1f1600;font-weight:800;font-size:18px;padding:14px;border-radius:40px;text-decoration:none;margin:22px 0}
.note{background:#fff;border-radius:14px;padding:12px 14px;font-size:14px;color:#4d6a62}ul.all{columns:2;padding-left:18px}'''


def dream_page_html(x, all_items):
    e = html.escape
    url = site_url() + 'dream/' + urllib.parse.quote(dream_slug(x['w'])) + '/'
    nums = ' '.join(x['two'] + x['three'])
    title = 'ฝันเห็น%s ตีเป็นเลขอะไร%s | สลากแล็บ' % (x['w'], (' เลข ' + nums) if nums else '')
    desc = 'ทำนายฝันเห็น%s ตามตำราที่เล่าต่อกันมา%s เลือกเฉพาะเลขที่ตำราอย่างน้อย 2 แหล่งตรงกัน พร้อมตรวจสลากฟรีที่สลากแล็บ' % (
        x['w'], (' เลขสองตัว ' + ' '.join(x['two'])) if x['two'] else '')
    block = ''
    if x['two']:
        block += '<h2>เลขสองตัว</h2><div class="nums">%s</div>' % ''.join('<b>%s</b>' % e(n) for n in x['two'])
    if x['three']:
        block += '<h2>เลขสามตัว</h2><div class="nums">%s</div>' % ''.join('<b>%s</b>' % e(n) for n in x['three'])
    if x['d']:
        block += '<h2>เลขเด่นตามตำรา</h2><div class="nums">%s</div>' % ''.join('<b>%s</b>' % e(n) for n in x['d'])
    alias = ('<p class="muted">ใช้กับ: %s</p>' % e(x['a'])) if x['a'] else ''
    others = ''.join('<li><a href="../%s/">ฝันเห็น%s</a></li>' % (e(urllib.parse.quote(dream_slug(o['w']))), e(o['w'])) for o in all_items if o['w'] != x['w'])
    return '''<!doctype html><html lang="th"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{t}</title><meta name="description" content="{ds}"><link rel="canonical" href="{u}">
<meta property="og:type" content="article"><meta property="og:title" content="{t}"><meta property="og:description" content="{ds}"><meta property="og:url" content="{u}">
<meta name="theme-color" content="#0B3B33"><link rel="icon" href="../../icon.svg" type="image/svg+xml"><link rel="manifest" href="../../manifest.webmanifest">
<style>{css}</style></head><body><main>
<p class="muted"><a href="../../">สลากแล็บ</a> › <a href="../">ทำนายฝัน</a></p>
<h1>ฝันเห็น{w} ตีเป็นเลขอะไร</h1>{alias}
{block}
<a class="cta" href="../../#dream">ค้นความฝันอื่น และตรวจสลากฟรี</a>
<p class="note">เลขตามความเชื่อที่เล่าต่อกันมา แต่ละตำราให้เลขไม่ตรงกัน เราเลือกเฉพาะที่ตรงกันอย่างน้อย 2 แหล่ง ({src}) ความฝันไม่มีผลต่อโอกาสถูกรางวัล ทุกเลขมีโอกาสเท่ากัน ซื้อสลากอย่างพอประมาณ</p>
<h2>ความฝันอื่น ๆ</h2><ul class="all">{others}</ul>
</main></body></html>'''.format(t=e(title), ds=e(desc), u=e(url), css=DREAM_CSS, w=e(x['w']), alias=alias, block=block, src=e(DREAM_SOURCES), others=others)


def dream_index_html(all_items):
    e = html.escape
    url = site_url() + 'dream/'
    lis = ''.join('<li><a href="%s/">ฝันเห็น%s</a></li>' % (e(urllib.parse.quote(dream_slug(o['w']))), e(o['w'])) for o in all_items)
    return '''<!doctype html><html lang="th"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ทำนายฝัน ตีเป็นเลข {n} เรื่อง (ตำราตรงกันหลายแหล่ง) | สลากแล็บ</title>
<meta name="description" content="ทำนายฝันเป็นเลข {n} เรื่องยอดนิยม เช่น ฝันเห็นงู ช้าง แหวน คนตาย เลือกเฉพาะเลขที่ตำราอย่างน้อย 2 แหล่งตรงกัน">
<link rel="canonical" href="{u}"><meta name="theme-color" content="#0B3B33"><link rel="icon" href="../icon.svg" type="image/svg+xml"><link rel="manifest" href="../manifest.webmanifest">
<style>{css}</style></head><body><main>
<p class="muted"><a href="../">สลากแล็บ</a> › ทำนายฝัน</p>
<h1>ทำนายฝันเป็นเลข {n} เรื่อง</h1>
<p class="muted">เลือกเฉพาะเลขที่ตำราอย่างน้อย 2 แหล่งตรงกัน ({src})</p>
<ul class="all">{lis}</ul>
<a class="cta" href="../#dream">ค้นความฝันในแอป และตรวจสลากฟรี</a>
<p class="note">ความฝันไม่มีผลต่อโอกาสถูกรางวัล ทุกเลขมีโอกาสเท่ากัน ซื้อสลากอย่างพอประมาณ</p>
</main></body></html>'''.format(n=len(all_items), u=e(url), css=DREAM_CSS, src=e(DREAM_SOURCES), lis=lis)


def write_dreams(items):
    base = ROOT / 'dream'
    base.mkdir(exist_ok=True)
    for x in items:
        d = base / dream_slug(x['w'])
        d.mkdir(exist_ok=True)
        (d / 'index.html').write_text(dream_page_html(x, items), 'utf-8')
    (base / 'index.html').write_text(dream_index_html(items), 'utf-8')
    (base / 'list.json').write_text(json.dumps([{'w': x['w']} for x in items], ensure_ascii=False), 'utf-8')


def safe_dreams():
    try:
        items = fetch_dreams()
        if items:
            write_dreams(items)
            write_sitemap()
    except Exception as e:  # ห้ามทำให้งานหลักล้ม
        print('ทำหน้าทำนายฝันไม่สำเร็จรอบนี้: %r' % e)


def safe_backfill():
    try:
        backfill(int(os.environ.get('BACKFILL_MAX', '24')))
    except Exception as e:  # ห้ามทำให้งานหลักล้ม
        print('เติมผลย้อนหลังไม่สำเร็จรอบนี้: %r' % e)


# ---------------- PWA: ติดตั้งเป็นแอปบนมือถือ ----------------
PWA_VERSION = '1'
ICON_GLYPH = '''<defs><mask id="n"><rect width="64" height="64" fill="#fff"/><circle cx="3" cy="32" r="6" fill="#000"/><circle cx="61" cy="32" r="6" fill="#000"/></mask></defs>
<rect x="3" y="12" width="58" height="40" rx="9" fill="#0f5a4f" mask="url(#n)"/>
<line x1="23.5" y1="17" x2="23.5" y2="47" stroke="#e8eee8" stroke-width="2" stroke-dasharray="3 3" stroke-linecap="round" opacity=".55"/>
<rect x="10" y="22.5" width="7" height="3" rx="1.5" fill="#e8eee8" opacity=".85"/><rect x="10" y="30.5" width="7" height="3" rx="1.5" fill="#e8eee8" opacity=".85"/><rect x="10" y="38.5" width="7" height="3" rx="1.5" fill="#e8eee8" opacity=".85"/>
<circle cx="42.5" cy="32" r="12.5" fill="#f0b43a"/>
<path d="M36.6 32.4l4.2 4.2 7.6-8.6" fill="none" stroke="#0b463d" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>'''


def icon_svg(mode='any'):
    # maskable: พื้นเต็มกรอบ + ย่อรูปให้อยู่ในวงปลอดภัย (Android ตัดเป็นวงกลม/สี่เหลี่ยมมนเอง)
    # apple: พื้นเต็มกรอบ (iOS มนมุมเอง) รูปใหญ่ใกล้เคียงไอคอนปกติ
    bg = '<rect width="64" height="64" rx="14" fill="#e8eee8"/>' if mode == 'any' else '<rect width="64" height="64" fill="#e8eee8"/>'
    tf = {'any': 'translate(4 4) scale(.875)', 'maskable': 'translate(11.2 11.2) scale(.65)', 'apple': 'translate(5.8 5.8) scale(.82)'}[mode]
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">%s<g transform="%s">%s</g></svg>' % (bg, tf, ICON_GLYPH)


def manifest_json():
    return json.dumps({
        'name': 'สลากแล็บ — ตรวจหวยฟรี',
        'short_name': 'สลากแล็บ',
        'description': 'ตรวจหวยรัฐบาลฟรี สลากของฉันแจ้งผลอัตโนมัติ สถิติเลขสำนัก',
        'lang': 'th',
        'id': './',
        'start_url': './',
        'scope': './',
        'display': 'standalone',
        'background_color': '#0B3B33',
        'theme_color': '#0B3B33',
        'icons': [
            {'src': 'icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
            {'src': 'icon-512.png', 'sizes': '512x512', 'type': 'image/png'},
            {'src': 'icon-maskable-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'},
            {'src': 'icon.svg', 'sizes': 'any', 'type': 'image/svg+xml'},
        ],
    }, ensure_ascii=False, indent=1)


SW_JS = '''// สลากแล็บ service worker — ทำให้ติดตั้งเป็นแอปได้ และเปิดได้ตอนเน็ตหลุด
const CACHE = 'slk-v%s';
const SHELL = ['./', 'offline.html', 'manifest.webmanifest', 'icon-192.png', 'icon.svg', 'data.json'];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => Promise.all(SHELL.map(u => c.add(u).catch(() => null)))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('slk-') && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return; // ตัวแอป (script.google.com) ให้เบราว์เซอร์จัดการเอง
  const fresh = fetch(req).then(res => {
    if (res && res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
    return res;
  });
  if (req.mode === 'navigate' || url.pathname.endsWith('data.json')) {
    // หน้าเว็บ/ผลล่าสุด: เอาของใหม่ก่อน ถ้าเน็ตหลุดใช้ของที่เก็บไว้
    e.respondWith(fresh.catch(() => caches.match(req).then(r => r || (req.mode === 'navigate' ? caches.match('offline.html') : Response.error()))));
  } else {
    e.respondWith(caches.match(req).then(r => r || fresh));
  }
});
''' % PWA_VERSION

OFFLINE_HTML = '''<!doctype html><html lang="th"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>สลากแล็บ — ออฟไลน์</title>
<meta name="theme-color" content="#0B3B33">
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#0B3B33;color:#fff;font:16px/1.6 system-ui,sans-serif;text-align:center;padding:16px;box-sizing:border-box}
.c{max-width:420px}.p1{font:800 40px/1.1 system-ui,sans-serif;letter-spacing:5px;background:#fff;color:#0B3B33;border-radius:16px;padding:14px;margin:12px 0}
.m{opacity:.8;font-size:14px}button{margin-top:16px;background:#FFC233;color:#1f1600;font-weight:800;font-size:16px;border:0;padding:12px 24px;border-radius:40px}</style>
</head><body><div class="c">
<h1 style="font-size:22px;margin:0 0 6px">ตอนนี้ยังไม่มีอินเทอร์เน็ต</h1>
<div id="r" class="m">ต่อเน็ตแล้วกดลองใหม่ เพื่อตรวจสลากและดูเลขล่าสุด</div>
<button onclick="location.reload()">ลองใหม่</button>
</div>
<script>
(navigator.serviceWorker?navigator.serviceWorker.ready.then(function(g){return g.scope;}):Promise.resolve('./')).then(function(base){return fetch(base+'data.json');}).then(r=>r.json()).then(d=>{if(!d||!d.first)return;
var el=document.getElementById('r');el.innerHTML='';
var a=document.createElement('div');a.className='m';var M=['','ม.ค.','ก.พ.','มี.ค.','เม.ย.','พ.ค.','มิ.ย.','ก.ค.','ส.ค.','ก.ย.','ต.ค.','พ.ย.','ธ.ค.'],t=String(d.date).split('-');a.textContent='ผลล่าสุดที่เก็บไว้ งวด '+(+t[2])+' '+M[+t[1]]+' '+(+t[0]+543)+' · รางวัลที่ 1';
var b=document.createElement('div');b.className='p1';b.textContent=d.first;
var c=document.createElement('div');c.className='m';c.textContent='เลขท้าย 2 ตัว '+d.last2+' · ตรวจกับใบตรวจของกองสลากอีกครั้ง';
el.append(a,b,c);}).catch(function(){});
</script></body></html>
'''


def render_icon(svg, size, out, transparent):
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', prefix='_icon-', suffix='.html', dir=ROOT, delete=False) as f:
        page = pathlib.Path(f.name)
    try:
        page.write_text('<!doctype html><html><head><style>html,body{margin:0;background:transparent}svg{display:block;width:%dpx;height:%dpx}</style></head><body>%s</body></html>'
                        % (size, size, svg), 'utf-8')
        cmd = [find_chrome(), '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
               '--force-device-scale-factor=1', '--window-size=%d,%d' % (size, size)]
        if transparent:
            cmd.append('--default-background-color=00000000')
        with tempfile.TemporaryDirectory(prefix='_chrome-', dir=ROOT) as prof:
            subprocess.run(cmd + ['--user-data-dir=' + prof, '--screenshot=' + str(out), page.as_uri()], check=True)
    finally:
        page.unlink(missing_ok=True)


def write_pwa(render=True):
    """เขียนไฟล์แอป (manifest, service worker, หน้าออฟไลน์, ไอคอน) — ไอคอน PNG เรนเดอร์ครั้งเดียวด้วย Chrome"""
    (ROOT / 'manifest.webmanifest').write_text(manifest_json(), 'utf-8')
    (ROOT / 'sw.js').write_text(SW_JS, 'utf-8')
    (ROOT / 'offline.html').write_text(OFFLINE_HTML, 'utf-8')
    (ROOT / 'icon.svg').write_text(icon_svg(), 'utf-8')
    if not render:
        return
    for name, size, mode in (('icon-192.png', 192, 'any'), ('icon-512.png', 512, 'any'),
                             ('icon-maskable-512.png', 512, 'maskable'), ('apple-touch-icon.png', 180, 'apple')):
        out = ROOT / name
        if out.is_file() and out.stat().st_size > 0:
            continue
        try:
            render_icon(icon_svg(mode), size, out, transparent=(mode == 'any'))
        except Exception as e:  # ไอคอนพลาดต้องไม่ทำให้หน้าผลหวยล่ม
            print('ทำไอคอน %s ไม่สำเร็จ: %r' % (name, e))


def find_chrome():
    for c in ('google-chrome', 'chromium', 'chromium-browser', os.environ.get('CHROME', '')):
        if c and subprocess.run(['which', c], capture_output=True).returncode == 0:
            return c
    raise SystemExit('ไม่พบ Chrome')


def main():
    force = '--force' in sys.argv
    d = fetch_latest()
    if not (d.get('date') and len(d.get('first', '')) == 6):
        raise SystemExit('ยังไม่มีผลล่าสุดจากระบบ: %r' % d)
    d = enrich(d)
    data_file = ROOT / 'data.json'
    old = json.loads(data_file.read_text('utf-8')) if data_file.exists() else {}
    img_name = 'og-%s.png' % d['date'].replace('-', '')
    image_file = ROOT / img_name
    result_keys = ('date', 'first', 'last2', 'front3', 'last3')
    unchanged = all(old.get(key) == d.get(key) for key in result_keys)
    if not force and unchanged and (ROOT / 'index.html').is_file() and image_file.is_file() and image_file.stat().st_size > 0:
        if any(old.get(k) != d.get(k) for k in FULL_KEYS + ('glo_url',)):  # รางวัลที่ 2–5 ประกาศตามมาทีหลัง: อัปเดตหน้าตรวจ ไม่ต้องทำรูปใหม่
            data_file.write_text(json.dumps(d, ensure_ascii=False, indent=1), 'utf-8')
            write_archive(d)
        elif not (ROOT / 'r' / d['date'].replace('-', '') / 'index.html').is_file() or not (ROOT / 'sitemap.xml').is_file():
            write_archive(d)
        print('ไม่มีงวดใหม่ (%s) ไม่ต้องสร้างใหม่' % d['date'])
        write_pwa(render=False)
        safe_dreams()
        safe_backfill()
        safe_upgrade()
        return

    # Render and stage every output before replacing the last working page.
    # The card stays beside fonts/ so its relative font URLs remain valid.
    with tempfile.TemporaryDirectory(prefix='_build-', dir=ROOT) as temporary:
        stage = pathlib.Path(temporary)
        staged_image = stage / img_name
        (stage / 'index.html').write_text(index_html(d, img_name), 'utf-8')
        (stage / 'data.json').write_text(json.dumps(d, ensure_ascii=False, indent=1), 'utf-8')
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', prefix='_card-', suffix='.html', dir=ROOT, delete=False) as f:
            card = pathlib.Path(f.name)
        try:
            card.write_text(card_html(d), 'utf-8')
            subprocess.run([find_chrome(), '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
                            '--force-device-scale-factor=1', '--window-size=1200,630', '--virtual-time-budget=8000',
                            '--user-data-dir=' + str(stage / 'chrome-profile'),
                            '--screenshot=' + str(staged_image), card.as_uri()], check=True)
            if not staged_image.is_file() or staged_image.stat().st_size == 0:
                raise RuntimeError('Chrome did not create a nonempty screenshot')
        finally:
            card.unlink(missing_ok=True)
        staged_image.replace(image_file)
        (stage / 'index.html').replace(ROOT / 'index.html')
        (stage / 'data.json').replace(data_file)

    # Keep old images until the replacement page and image are safely in place.
    for p in ROOT.glob('og-*.png'):
        if p != image_file:
            p.unlink()
    write_archive(d)
    write_pwa(render=True)
    safe_dreams()
    print('สร้างหน้าแชร์งวด %s แล้ว: %s' % (d['date'], img_name))
    safe_backfill()
    safe_upgrade()


if __name__ == '__main__':
    main()
