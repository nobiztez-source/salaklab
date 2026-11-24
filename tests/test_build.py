import copy
import importlib.util
import json
import pathlib
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location('salaklab_build', pathlib.Path(__file__).parents[1] / 'build.py')
build = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build)


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.data = {
            'site': 'สลากแล็บ', 'date': '2026-11-01', 'first': '423224',
            'last2': '85', 'front3': ['300', '950'], 'last3': ['393', '804'],
        }
        self.image_name = 'og-20261101.png'
        (self.root / 'data.json').write_text(json.dumps(self.data), encoding='utf-8')
        (self.root / 'index.html').write_text('old index', encoding='utf-8')
        (self.root / self.image_name).write_bytes(b'old image')
        self.icons = ('icon-192.png', 'icon-512.png', 'icon-maskable-512.png', 'apple-touch-icon.png')
        for name in self.icons:  # ในเว็บจริงไอคอนถูกสร้างไว้ตั้งแต่รอบแรกแล้ว
            (self.root / name).write_bytes(b'icon')
        self.history = {}
        self.dreams = []
        self.l6 = {}
        for target, value in [('ROOT', self.root), ('fetch_latest', lambda: self.data), ('find_chrome', lambda: 'chromium'),
                              ('fetch_result', lambda date: self.history.get(date, {'date': date, 'none': True})),
                              ('fetch_dreams', lambda: self.dreams), ('fetch_l6', lambda date: self.l6.get(date))]:
            p = patch.object(build, target, value)
            p.start()
            self.addCleanup(p.stop)
        self.argv = patch.object(build.sys, 'argv', ['build.py'])
        self.argv.start()
        self.addCleanup(self.argv.stop)

    @staticmethod
    def render(command, **kwargs):
        output = next(arg.split('=', 1)[1] for arg in command if arg.startswith('--screenshot='))
        pathlib.Path(output).write_bytes(b'new image')

    def test_unchanged_results_skip_render(self):
        with patch.object(build.subprocess, 'run') as render:
            build.main()
        render.assert_not_called()

    def test_corrected_results_rebuild(self):
        for field, value in [('last2', '01'), ('front3', ['001', '002']), ('last3', ['003', '004'])]:
            with self.subTest(field=field):
                old = copy.deepcopy(self.data)
                self.data[field] = value
                with patch.object(build.subprocess, 'run', side_effect=self.render) as render:
                    build.main()
                render.assert_called_once()
                self.assertEqual(json.loads((self.root / 'data.json').read_text())[field], value)
                self.data = old
                (self.root / 'data.json').write_text(json.dumps(old))

    def test_missing_image_rebuilds(self):
        (self.root / self.image_name).unlink()
        with patch.object(build.subprocess, 'run', side_effect=self.render) as render:
            build.main()
        render.assert_called_once()
        self.assertTrue((self.root / self.image_name).is_file())

    def test_empty_image_rebuilds(self):
        (self.root / self.image_name).write_bytes(b'')
        with patch.object(build.subprocess, 'run', side_effect=self.render) as render:
            build.main()
        render.assert_called_once()

    def test_force_rebuilds(self):
        with patch.object(build.sys, 'argv', ['build.py', '--force']), patch.object(build.subprocess, 'run', side_effect=self.render) as render:
            build.main()
        render.assert_called_once()

    def test_failed_render_preserves_existing_outputs(self):
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        self.data['date'] = '2026-11-16'
        with patch.object(build.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'chromium')):
            with self.assertRaises(subprocess.CalledProcessError):
                build.main()
        after = {p.name: p.read_bytes() for p in self.root.iterdir() if p.is_file()}
        self.assertEqual(before, after)

    def test_missing_screenshot_preserves_existing_outputs(self):
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        self.data['date'] = '2026-11-16'
        with patch.object(build.subprocess, 'run'):
            with self.assertRaises(RuntimeError):
                build.main()
        after = {p.name: p.read_bytes() for p in self.root.iterdir() if p.is_file()}
        self.assertEqual(before, after)

    def test_success_replaces_outputs_and_cleans_old_image(self):
        self.data['date'] = '2026-11-16'
        with patch.object(build.subprocess, 'run', side_effect=self.render):
            build.main()
        self.assertFalse((self.root / self.image_name).exists())
        self.assertEqual((self.root / 'og-20261116.png').read_bytes(), b'new image')
        self.assertIn('og-20261116.png', (self.root / 'index.html').read_text())
        self.assertEqual(json.loads((self.root / 'data.json').read_text())['date'], '2026-11-16')
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), sorted(['data.json', 'index.html', 'og-20261116.png', 'r', 'robots.txt', 'sitemap.xml', 'manifest.webmanifest', 'sw.js', 'offline.html', 'icon.svg'] + list(self.icons)))

    # ===== หน้าผลรายงวดสำหรับ Google (ข้อความจริง ไม่ใช่ iframe) =====
    def build_new(self, date='2026-11-16'):
        self.data['date'] = date
        with patch.object(build.subprocess, 'run', side_effect=self.render):
            build.main()

    def test_archive_page_has_indexable_results(self):
        self.build_new()
        page = (self.root / 'r' / '20261116' / 'index.html').read_text()
        self.assertIn('<h1>', page)
        self.assertIn('16 พ.ย. 2569', page)
        for n in ['423224', '85', '300', '950', '393', '804']:
            self.assertIn(n, page)
        self.assertNotIn('<iframe', page)
        self.assertIn('rel="canonical" href="%sr/20261116/"' % build.site_url(), page)
        self.assertIn('href="../../"', page)

    def test_archive_pages_accumulate_and_link(self):
        self.build_new('2026-11-16')
        self.build_new('2026-12-01')
        self.assertTrue((self.root / 'r' / '20261116' / 'index.html').is_file())
        newest = (self.root / 'r' / '20261201' / 'index.html').read_text()
        self.assertIn('href="../20261116/"', newest)

    def test_sitemap_and_robots(self):
        self.build_new()
        sm = (self.root / 'sitemap.xml').read_text()
        url = build.site_url()
        self.assertIn('<loc>%s</loc>' % url, sm)
        self.assertIn('<loc>%sr/20261116/</loc>' % url, sm)
        self.assertIn('Sitemap: %ssitemap.xml' % url, (self.root / 'robots.txt').read_text())

    def test_unchanged_run_backfills_missing_archive(self):
        with patch.object(build.subprocess, 'run') as render:
            build.main()
        render.assert_not_called()
        self.assertTrue((self.root / 'r' / '20261101' / 'index.html').is_file())
        self.assertTrue((self.root / 'sitemap.xml').is_file())

    # ===== เติมผลย้อนหลังทีละน้อยทุกรอบ =====
    def test_backfill_adds_past_draws_and_remembers_misses(self):
        self.history = {
            '2026-10-16': {'date': '2026-10-16', 'first': '011781', 'last2': '48', 'front3': ['402', '392'], 'last3': ['171', '255']},
            '2026-10-01': {'date': '2026-10-01', 'first': '402701', 'last2': '70', 'front3': ['791', '912'], 'last3': ['058', '396']},
        }
        calls = []
        orig = build.fetch_result
        def spy(date):
            calls.append(date)
            return orig(date)
        with patch.object(build, 'fetch_result', spy), patch.object(build, 'today', lambda: '2026-11-03'):
            added = build.backfill(max_new=2, max_calls=12)
        self.assertEqual(added, 2)
        page = (self.root / 'r' / '20261016' / 'index.html').read_text()
        self.assertIn('011781', page)
        self.assertTrue((self.root / 'r' / '20261001' / 'index.html').is_file())
        self.assertIn('r/20261016/', (self.root / 'sitemap.xml').read_text())
        tried = json.loads((self.root / 'r' / 'tried.json').read_text())
        self.assertIn('2026-10-02', tried)
        calls.clear()
        with patch.object(build, 'fetch_result', spy), patch.object(build, 'today', lambda: '2026-11-03'):
            build.backfill(max_new=2, max_calls=6)
        self.assertNotIn('2026-10-02', calls)
        self.assertNotIn('2026-10-16', calls)

    def test_backfill_never_breaks_main_build(self):
        def boom(date):
            raise OSError('network down')
        with patch.object(build, 'fetch_result', boom):
            with patch.object(build.subprocess, 'run') as render:
                build.main()
        render.assert_not_called()
        self.assertTrue((self.root / 'r' / '20261101' / 'index.html').is_file())

    # ---------- PWA ----------
    def test_pwa_files_written_and_icons_rendered(self):
        for name in self.icons:
            (self.root / name).unlink()
        with patch.object(build.subprocess, 'run', side_effect=self.render) as render:
            build.write_pwa(render=True)
        m = json.loads((self.root / 'manifest.webmanifest').read_text('utf-8'))
        self.assertEqual(m['display'], 'standalone')
        self.assertEqual(m['start_url'], './')
        self.assertEqual(m['scope'], './')
        sizes = {(i['sizes'], i.get('purpose', 'any')) for i in m['icons']}
        self.assertIn(('192x192', 'any'), sizes)
        self.assertIn(('512x512', 'any'), sizes)
        self.assertIn(('512x512', 'maskable'), sizes)
        for name in ('sw.js', 'offline.html', 'icon.svg', 'icon-192.png', 'icon-512.png', 'icon-maskable-512.png', 'apple-touch-icon.png'):
            self.assertTrue((self.root / name).is_file(), name)
        self.assertEqual(render.call_count, 4)
        sw = (self.root / 'sw.js').read_text('utf-8')
        self.assertIn("addEventListener('fetch'", sw)
        self.assertIn('offline.html', sw)
        self.assertIn('location.origin', sw)  # ไม่ยุ่งกับคำขอข้ามโดเมน (ตัวแอปใน iframe)
        # รันซ้ำ: มีรูปแล้วไม่ต้องเรนเดอร์ใหม่
        with patch.object(build.subprocess, 'run') as again:
            build.write_pwa(render=True)
        again.assert_not_called()

    def test_pwa_without_render_never_calls_chrome(self):
        with patch.object(build.subprocess, 'run') as render:
            build.write_pwa(render=False)
        render.assert_not_called()
        self.assertTrue((self.root / 'manifest.webmanifest').is_file())

    def test_index_and_archive_link_manifest(self):
        page = build.index_html(self.data, self.image_name)
        self.assertIn('rel="manifest" href="manifest.webmanifest"', page)
        self.assertIn('apple-touch-icon', page)
        self.assertIn("serviceWorker.register('sw.js')", page)
        self.assertIn('beforeinstallprompt', page)
        arch = build.archive_html(self.data, [])
        self.assertIn('href="../../manifest.webmanifest"', arch)
        self.assertIn('../../apple-touch-icon.png', arch)

    def test_main_writes_pwa_on_both_paths(self):
        with patch.object(build.subprocess, 'run') as render:
            build.main()  # งวดเดิม
        render.assert_not_called()
        self.assertTrue((self.root / 'sw.js').is_file())
        (self.root / 'sw.js').unlink()
        (self.root / 'icon-192.png').unlink()
        self.data = dict(self.data, first='111111')
        with patch.object(build.subprocess, 'run', side_effect=self.render):
            build.main()
        self.assertTrue((self.root / 'sw.js').is_file())
        self.assertTrue((self.root / 'icon-192.png').is_file())


    def test_index_shows_result_before_app_loads(self):
        page = build.index_html(self.data, self.image_name)
        self.assertIn('<b>4</b><b>2</b><b>3</b><b>2</b><b>2</b><b>4</b>', page)
        self.assertIn('<strong>85</strong>', page)
        self.assertIn('300 950', page)
        self.assertIn("f.className='ready'", page)
        self.assertNotIn('เลขเด็ด', page)

    FULL = {'near1': ['423223', '423225'], 'second': ['111111', '222222'], 'third': ['333333'], 'fourth': ['444444'], 'fifth': ['555555']}

    def test_archive_page_checks_tickets_without_app(self):
        self.data.update(self.FULL)
        self.build_new()
        page = (self.root / 'r' / '20261116' / 'index.html').read_text()
        self.assertIn('id="q"', page)
        self.assertIn('"second": ["111111", "222222"]', page)
        self.assertNotIn('script.google.com/macros', page.split('<script>')[1] if '<script>' in page else '')
        self.assertNotIn('ยังประกาศไม่ครบ', page.split('<script>')[0])

    def test_archive_checker_warns_when_prizes_incomplete(self):
        self.build_new()
        page = (self.root / 'r' / '20261116' / 'index.html').read_text()
        self.assertIn('id="q"', page)
        self.assertIn('ยังประกาศไม่ครบ', page)

    def test_full_prizes_arriving_later_update_archive_without_render(self):
        self.build_new()
        self.data = dict(self.data, **self.FULL)
        with patch.object(build, 'fetch_latest', lambda: self.data), patch.object(build.subprocess, 'run', side_effect=AssertionError('no render')):
            build.main()
        page = (self.root / 'r' / '20261116' / 'index.html').read_text()
        self.assertIn('"third": ["333333"]', page)
        self.assertEqual(json.loads((self.root / 'data.json').read_text())['fifth'], ['555555'])

    def test_checker_logic_in_node(self):
        import shutil, subprocess as sp
        node = shutil.which('node')
        if not node:
            self.skipTest('no node')
        d = dict(self.data, date='2026-11-16', **self.FULL)
        js = build.checker_js(d)
        code = js + """
;const t=(n)=>JSON.stringify(slkCheck(n).map(x=>x[0]));
console.log([t('423224'),t('423225'),t('111111'),t('300999'),t('000393'),t('000085'),t('999999')].join('|'));"""
        out = sp.run([node, '-e', code], capture_output=True, text=True, check=True).stdout.strip()
        self.assertEqual(out, '["รางวัลที่ 1"]|["ข้างเคียงรางวัลที่ 1"]|["รางวัลที่ 2"]|["เลขหน้า 3 ตัว"]|["เลขท้าย 3 ตัว"]|["เลขท้าย 2 ตัว"]|[]')

    @staticmethod
    def l6_row(first, f3, l3, l2):
        n = [first] + f3 + l3 + [l2, '%06d' % (int(first) - 1), '%06d' % (int(first) + 1)]
        n += ['%06d' % (100000 + i) for i in range(5 + 10 + 50 + 100)]
        return {'n': n, 'url': 'https://api.glo.or.th/utility/file/download/abc'}

    def test_parse_l6_maps_all_prizes(self):
        r = build.parse_l6('2026-11-01', self.l6_row('423224', ['300', '950'], ['393', '804'], '85'))
        self.assertEqual(r['first'], '423224'); self.assertEqual(r['front3'], ['300', '950']); self.assertEqual(r['last3'], ['393', '804'])
        self.assertEqual(r['last2'], '85'); self.assertEqual(r['near1'], ['423223', '423225'])
        self.assertEqual([len(r[k]) for k in ('second', 'third', 'fourth', 'fifth')], [5, 10, 50, 100])
        self.assertEqual(r['glo_url'], 'https://api.glo.or.th/utility/file/download/abc')
        self.assertIsNone(build.parse_l6('2026-11-01', {'n': ['1'] * 10}))
        bad = build.parse_l6('2026-11-01', dict(self.l6_row('423224', ['300', '950'], ['393', '804'], '85'), url='https://evil.example/x'))
        self.assertNotIn('glo_url', bad)

    def test_latest_enriched_from_codex_when_numbers_match(self):
        self.l6['2026-11-16'] = self.l6_row('423224', ['300', '950'], ['393', '804'], '85')
        self.build_new()
        page = (self.root / 'r' / '20261116' / 'index.html').read_text()
        self.assertNotIn('ยังประกาศไม่ครบ', page.split('<script>')[0])
        self.assertIn('api.glo.or.th/utility/file/download/abc', page)
        self.assertEqual(len(json.loads((self.root / 'data.json').read_text())['fifth']), 100)

    def test_codex_mismatch_is_ignored(self):
        self.l6['2026-11-16'] = self.l6_row('999999', ['300', '950'], ['393', '804'], '85')
        self.build_new()
        page = (self.root / 'r' / '20261116' / 'index.html').read_text()
        self.assertIn('ยังประกาศไม่ครบ', page)
        self.assertNotIn('fifth', json.loads((self.root / 'data.json').read_text()))

    def test_codex_down_never_breaks_build(self):
        def boom(date):
            raise OSError('down')
        with patch.object(build, 'fetch_l6', boom):
            self.build_new()
        self.assertTrue((self.root / 'r' / '20261116' / 'index.html').is_file())

    def test_old_archive_pages_upgraded_to_full_checker(self):
        old = self.root / 'r' / '20261016' / 'index.html'
        old.parent.mkdir(parents=True)
        old.write_text('<html>old page without checker 011781</html>')
        self.l6['2026-10-16'] = self.l6_row('011781', ['392', '402'], ['171', '255'], '48')
        n = build.upgrade_archive(max_pages=5)
        self.assertEqual(n, 1)
        page = old.read_text()
        self.assertIn('id="q"', page); self.assertIn('011781', page); self.assertNotIn('ยังประกาศไม่ครบ', page.split('<script>')[0])
        self.assertEqual(build.upgrade_archive(max_pages=5), 0)

    def test_upgrade_skips_when_first_prize_differs(self):
        old = self.root / 'r' / '20261016' / 'index.html'
        old.parent.mkdir(parents=True)
        old.write_text('<html>old 011781</html>')
        self.l6['2026-10-16'] = self.l6_row('222222', ['392', '402'], ['171', '255'], '48')
        self.assertEqual(build.upgrade_archive(max_pages=5), 0)
        self.assertNotIn('id="q"', old.read_text())

    def test_dream_pages_and_sitemap(self):
        self.dreams = [{'w': 'งู', 'a': 'งูเห่า', 'two': ['56', '66'], 'three': [], 'd': ['5', '6']},
                       {'w': 'ช้าง', 'a': '', 'two': ['19'], 'three': ['119'], 'd': []}]
        with patch.object(build.subprocess, 'run'):
            build.main()
        page = (self.root / 'dream' / 'งู' / 'index.html').read_text('utf-8')
        self.assertIn('ฝันเห็นงู ตีเป็นเลขอะไร', page)
        self.assertIn('<b>56</b>', page)
        self.assertIn('ความฝันไม่มีผลต่อโอกาสถูกรางวัล', page)
        self.assertIn('ฝันเห็นช้าง', page)
        self.assertTrue((self.root / 'dream' / 'index.html').is_file())
        sm = (self.root / 'sitemap.xml').read_text('utf-8')
        self.assertIn('dream/%E0%B8%87%E0%B8%B9/', sm)
        self.assertIn('/r/20261101/', sm)

    def test_dream_failure_never_breaks_build(self):
        def boom():
            raise OSError('offline')
        with patch.object(build, 'fetch_dreams', boom), patch.object(build.subprocess, 'run'):
            build.main()
        self.assertFalse((self.root / 'dream').exists())

if __name__ == '__main__':
    unittest.main()
