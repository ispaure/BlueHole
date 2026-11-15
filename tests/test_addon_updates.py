"""Update selection, environment retention and reversible publication."""
import base64
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('update_service', Path(__file__).parents[1] / 'blenderUtils/update_service.py')
service = importlib.util.module_from_spec(spec)
spec.loader.exec_module(service)


class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name).resolve()
        self.root = self.folder / 'preset/scripts/addons/BlueHole'
        self.staged = self.root.parent / '.update/snapshot'
        self.release = dict(repository=service.REPOSITORY, branch='blender-5.2.2/main', channel='main',
                            commit='a' * 40, version='6.9.22', package_digest='c' * 64)
        for root, version in ((self.root, '6,9,21'), (self.staged, '6,9,22')):
            for name in ('Lib/commonUtils/__init__.py', 'operators/operators_register.py',
                         'preferences/addon_prefs.py', 'envFiles/default/settings.ini'):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('new' if root == self.staged else 'old')
            (root / '__init__.py').write_text('bl_info = '+repr(dict(name='Blue Hole', blender=(5,2,2), version=tuple(map(int,version.split(','))))))

    def test_channels_choose_highest_compatible_baseline_without_crossing_channels(self):
        names = ['main', 'blender-4.5.1/main', 'blender-5.2.2/main', 'blender-5.3.0/main', 'blender-5.1.0/alpha']
        self.assertEqual(service.select_branch(names, 'main', (5,2,2)), 'blender-5.2.2/main')
        self.assertEqual(service.select_branch(names, 'main', (5,4,0)), 'blender-5.3.0/main')
        self.assertEqual(service.select_branch(names, 'alpha', (5,2,2)), 'blender-5.1.0/alpha')
        self.assertEqual(service.select_branch(names, 'main', (4,0,0)), 'main')
        with self.assertRaisesRegex(ValueError, 'No Blue Hole beta'):
            service.select_branch(names, 'beta', (5,2,2))

    def test_remote_metadata_is_pinned_and_actual_blender_minimum_is_checked(self):
        source = (self.staged / '__init__.py').read_bytes()
        calls = []
        def get(url):
            calls.append(url)
            if '/branches?' in url:return [dict(name='blender-5.2.2/main')]
            if '/branches/' in url:return {'commit': {'sha':'a'*40}}
            return {'encoding':'base64','content':base64.b64encode(source).decode()}
        release = service.latest('main', (5,2,2), get)
        self.assertEqual(release['commit'], 'a'*40)
        self.assertIn('blender-5.2.2%2Fmain', calls[1])
        self.assertTrue(calls[2].endswith('ref='+'a'*40))
        with self.assertRaisesRegex(ValueError, 'newer Blender'):
            service.addon_info(source, (4,5,1))

    def test_reload_publication_keeps_custom_environments_and_replaces_default(self):
        custom = self.root / 'envFiles/My Studio/nested/config.ini'
        custom.parent.mkdir(parents=True)
        custom.write_bytes(b'personal\x00settings')
        preset = self.root.parents[2]
        (preset / 'config').mkdir()
        prefs = preset / 'config/userpref.blend'
        prefs.write_bytes(b'preferences must stay untouched')
        install = service.Installation(self.root, self.staged, self.release, (5,2,2))
        install.prepare(); install.publish()
        self.assertEqual(custom.read_bytes(), b'personal\x00settings')
        self.assertEqual((self.root/'envFiles/default/settings.ini').read_text(), 'new')
        self.assertEqual(prefs.read_bytes(), b'preferences must stay untouched')
        self.assertEqual(service.installed_commit(self.root), 'a'*40)
        install.finish()
        self.assertIsNone(install.lock)

    def test_failed_reload_restores_old_files_and_environments(self):
        before = (self.root/'__init__.py').read_bytes()
        install = service.Installation(self.root, self.staged, self.release, (5,2,2))
        install.prepare(); install.publish(); install.rollback()
        self.assertEqual((self.root/'__init__.py').read_bytes(), before)
        self.assertEqual((self.root/'envFiles/default/settings.ini').read_text(), 'old')
        self.assertFalse((self.root/service.MARKER).exists())
        self.assertIsNone(install.lock)

    def test_logistics_revision_channel_and_digest_follow_a_successful_update(self):
        path = self.root.parents[2]/'.logistics-addons.json'
        initial = dict(selected=['legacy:Other'], installed={'legacy:BlueHole':dict(path='scripts/addons/BlueHole',module='BlueHole',digest='b'*64)},
                       bluehole=dict(enabled=True, branch='alpha', auto_update=False), installed_bluehole=dict(commit='b'*40))
        path.write_text(json.dumps(initial))
        install = service.Installation(self.root,self.staged,self.release,(5,2,2))
        install.prepare(); install.publish(); install.finish()
        state = json.loads(path.read_text())
        self.assertEqual(state['selected'],initial['selected'])
        self.assertFalse(state['bluehole']['auto_update'])
        self.assertEqual(state['bluehole']['branch'],'main')
        self.assertEqual(state['installed_bluehole']['commit'],'a'*40)
        self.assertEqual(state['installed']['legacy:BlueHole']['digest'],'c'*64)

    def test_checkouts_and_links_are_never_replaced(self):
        (self.root/'.git').mkdir()
        with self.assertRaisesRegex(ValueError,'Development checkout'):
            service.Installation(self.root,self.staged,self.release,(5,2,2))
        link = self.folder/'linked'
        link.symlink_to(self.root,target_is_directory=True)
        self.assertIn('checkout/link',service.install_blocker(link))

    def test_failed_folder_swap_restores_installation(self):
        install = service.Installation(self.root,self.staged,self.release,(5,2,2))
        install.prepare()
        replace = service.os.replace
        def fail(source, destination):
            if source == self.staged:raise OSError('file locked')
            return replace(source,destination)
        with patch.object(service.os,'replace',side_effect=fail), self.assertRaisesRegex(OSError,'locked'):
            install.publish()
        install.unlock()
        self.assertEqual((self.root/'envFiles/default/settings.ini').read_text(),'old')

    def test_parallel_installation_is_rejected_without_removing_its_lock(self):
        lock = self.root.with_name('.BlueHole.lock');lock.mkdir()
        install = service.Installation(self.root,self.staged,self.release,(5,2,2))
        with self.assertRaisesRegex(ValueError,'Another update'):
            install.prepare()
        self.assertTrue(lock.is_dir())
