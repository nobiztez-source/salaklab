#!/usr/bin/env python3
"""สร้างหน้าแชร์ของสลากแล็บ: ดึงผลล่าสุด -> ทำรูป og -> เขียน index.html
รันบน GitHub Actions (ดู .github/workflows/og.yml) หรือรันเองก็ได้:
  python3 build.py            # สร้างเมื่อมีงวดใหม่
  python3 build.py --force    # สร้างใหม่ทุกครั้ง
"""
import datetime, html, json, os, pathlib, subprocess, sys, tempfile, urllib.request

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
    desc = 'ตรวจหวยรัฐบาลครบทุกรางวัล ฟรี! กดเลย ใส่เลขสลากแล้วรู้ผลทันที พร้อมเลขเด็ดจากหลายสำนักและสถิติความแม่น'
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
<link rel="icon" href="data:,">
<meta name="theme-color" content="#0B3B33">
<style>html,body{{margin:0;height:100%;background:#0B3B33}}
#app{{position:fixed;inset:0;width:100%;height:100%;border:0;display:block;background:#0B3B33}}
#fb{{position:fixed;inset:0;display:grid;place-items:center;color:#fff;font-family:system-ui,sans-serif;text-align:center;padding:16px;box-sizing:border-box}}
#fb a{{display:inline-block;margin-top:14px;background:#FFC233;color:#1f1600;font-weight:800;padding:12px 24px;border-radius:40px;text-decoration:none}}</style>
</head><body>
<div id="fb"><div>กำลังเปิดสลากแล็บ…<br><a href="{a}">ถ้าไม่ขึ้น กดที่นี่</a></div></div>
<iframe id="app" title="สลากแล็บ" allow="clipboard-write; web-share; camera" referrerpolicy="no-referrer-when-downgrade"></iframe>
<script>
(function(){{
  var app={aj}, q=location.search.replace(/^\\?/,'').split('&').filter(function(p){{return p&&p.indexOf('d=')!==0;}}).join('&');
  document.getElementById('app').src=app+(q?'?'+q:'')+location.hash;
}})();
</script>
</body></html>'''.format(t=e(title), d=e(desc), u=e(url + '?d=' + d['date'].replace('-', '')), i=e(img), dt=e(th_date(d['date'])), f=e(d['first']),
                         n=e(img_name), a=e(APP_URL), aj=json.dumps(APP_URL))


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
<style>body{{margin:0;background:#eef3ef;color:#0f2a24;font:16px/1.6 system-ui,sans-serif}}main{{max-width:640px;margin:0 auto;padding:20px 16px 40px}}
h1{{font-size:24px;line-height:1.3;margin:8px 0 16px}}.p1{{font:800 44px/1.1 system-ui,sans-serif;letter-spacing:6px;background:#0B3B33;color:#fff;border-radius:18px;padding:18px;text-align:center}}
table{{width:100%;border-collapse:collapse;margin:16px 0;background:#fff}}td,th{{padding:12px;border-bottom:1px solid #d6e2db;text-align:left}}td b{{font-size:20px;letter-spacing:1px}}
.cta{{display:block;text-align:center;background:#FFC233;color:#1f1600;font-weight:800;font-size:18px;padding:14px;border-radius:40px;text-decoration:none;margin:20px 0}}
.muted{{color:#4d6a62;font-size:14px}}a{{color:#0b3b33}}</style>
</head><body><main>
<p class="muted"><a href="../../">สลากแล็บ</a> › ผลหวยย้อนหลัง</p>
<h1>ผลสลากกินแบ่งรัฐบาล งวด {dt}</h1>
<p class="muted">รางวัลที่ 1</p>
<div class="p1">{f}</div>
<table>
<tr><th>เลขหน้า 3 ตัว</th><td><b>{f3}</b></td></tr>
<tr><th>เลขท้าย 3 ตัว</th><td><b>{l3}</b></td></tr>
<tr><th>เลขท้าย 2 ตัว</th><td><b>{l2}</b></td></tr>
</table>
<a class="cta" href="../../">ตรวจสลากของคุณ ครบทุกรางวัล ฟรี</a>
<p class="muted">ตรวจผลจริงกับใบตรวจของสำนักงานสลากกินแบ่งรัฐบาล (glo.or.th) อีกครั้งก่อนขึ้นเงิน ข้อมูลเพื่อความสะดวกเท่านั้น</p>
{more}
</main></body></html>'''.format(t=e(title), ds=e(desc), u=e(url + 'r/' + key + '/'), dt=e(dt), f=e(d['first']), f3=e(f3), l3=e(l3), l2=e(d['last2']), more=more)


def write_archive(d):
    """เขียนหน้าผลงวดนี้ (เก็บของงวดเก่าไว้) + sitemap.xml + robots.txt"""
    base = ROOT / 'r'
    key = d['date'].replace('-', '')
    older = sorted([p.name for p in base.iterdir() if p.is_dir() and p.name.isdigit() and p.name != key], reverse=True) if base.is_dir() else []
    page = base / key / 'index.html'
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(archive_html(d, older), 'utf-8')
    url = site_url()
    keys = sorted([p.name for p in base.iterdir() if p.is_dir() and p.name.isdigit()], reverse=True)
    locs = [url] + [url + 'r/' + k + '/' for k in keys]
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                                      ''.join('<url><loc>%s</loc></url>\n' % html.escape(u) for u in locs) + '</urlset>\n', 'utf-8')
    (ROOT / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: %ssitemap.xml\n' % url, 'utf-8')


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
            page.write_text(archive_html({'date': d, 'first': r['first'], 'last2': r['last2'], 'front3': r.get('front3') or [], 'last3': r.get('last3') or []},
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
    locs = [url] + [url + 'r/' + k + '/' for k in keys]
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                                      ''.join('<url><loc>%s</loc></url>\n' % html.escape(u) for u in locs) + '</urlset>\n', 'utf-8')
    (ROOT / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: %ssitemap.xml\n' % url, 'utf-8')


def safe_backfill():
    try:
        backfill(int(os.environ.get('BACKFILL_MAX', '24')))
    except Exception as e:  # ห้ามทำให้งานหลักล้ม
        print('เติมผลย้อนหลังไม่สำเร็จรอบนี้: %r' % e)


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
    data_file = ROOT / 'data.json'
    old = json.loads(data_file.read_text('utf-8')) if data_file.exists() else {}
    img_name = 'og-%s.png' % d['date'].replace('-', '')
    image_file = ROOT / img_name
    result_keys = ('date', 'first', 'last2', 'front3', 'last3')
    unchanged = all(old.get(key) == d.get(key) for key in result_keys)
    if not force and unchanged and (ROOT / 'index.html').is_file() and image_file.is_file() and image_file.stat().st_size > 0:
        if not (ROOT / 'r' / d['date'].replace('-', '') / 'index.html').is_file() or not (ROOT / 'sitemap.xml').is_file():
            write_archive(d)
        print('ไม่มีงวดใหม่ (%s) ไม่ต้องสร้างใหม่' % d['date'])
        safe_backfill()
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
    print('สร้างหน้าแชร์งวด %s แล้ว: %s' % (d['date'], img_name))
    safe_backfill()


if __name__ == '__main__':
    main()
