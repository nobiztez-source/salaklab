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
        for target, value in [('ROOT', self.root), ('fetch_latest', lambda: self.data), ('find_chrome', lambda: 'chromium')]:
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
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ['data.json', 'index.html', 'og-20261116.png'])


if __name__ == '__main__':
    unittest.main()
