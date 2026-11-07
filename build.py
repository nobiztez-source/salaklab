#!/usr/bin/env python3
"""สร้างหน้าแชร์ของสลากแล็บ: ดึงผลล่าสุด -> ทำรูป og -> เขียน index.html
รันบน GitHub Actions (ดู .github/workflows/og.yml) หรือรันเองก็ได้:
  python3 build.py            # สร้างเมื่อมีงวดใหม่
  python3 build.py --force    # สร้างใหม่ทุกครั้ง
"""
import html, json, os, pathlib, subprocess, sys, urllib.request

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
<style>body{{margin:0;background:#0B3B33;color:#fff;font-family:system-ui,sans-serif;display:grid;place-items:center;min-height:100vh;text-align:center;padding:16px;box-sizing:border-box}}
img{{max-width:100%;border-radius:14px}}a{{display:inline-block;margin-top:18px;background:#FFC233;color:#1f1600;font-weight:800;font-size:20px;padding:14px 28px;border-radius:40px;text-decoration:none}}</style>
</head><body><div><img src="{n}" alt="ผลสลากล่าสุด" width="600" height="315"><br>
<a id="go" href="{a}">เข้าสลากแล็บ ตรวจหวยฟรี</a><p style="opacity:.7">กำลังพาไปหน้าตรวจหวย…</p></div>
<script>location.replace({aj});</script>
</body></html>'''.format(t=e(title), d=e(desc), u=e(url + '?d=' + d['date'].replace('-', '')), i=e(img), dt=e(th_date(d['date'])), f=e(d['first']),
                         n=e(img_name), a=e(APP_URL), aj=json.dumps(APP_URL))


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
    if not force and old.get('date') == d['date'] and old.get('first') == d['first'] and (ROOT / 'index.html').exists():
        print('ไม่มีงวดใหม่ (%s) ไม่ต้องสร้างใหม่' % d['date'])
        return
    img_name = 'og-%s.png' % d['date'].replace('-', '')
    card = ROOT / '_card.html'
    card.write_text(card_html(d), 'utf-8')
    for p in ROOT.glob('og-*.png'):
        p.unlink()
    subprocess.run([find_chrome(), '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
                    '--force-device-scale-factor=1', '--window-size=1200,630', '--virtual-time-budget=8000',
                    '--screenshot=' + str(ROOT / img_name), card.as_uri()], check=True)
    card.unlink()
    (ROOT / 'index.html').write_text(index_html(d, img_name), 'utf-8')
    data_file.write_text(json.dumps(d, ensure_ascii=False, indent=1), 'utf-8')
    print('สร้างหน้าแชร์งวด %s แล้ว: %s' % (d['date'], img_name))


if __name__ == '__main__':
    main()
