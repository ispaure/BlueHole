"""Print reproducible catalog evidence without importing Blender or the addon.

python Scripts/keymap_inventory.py --output tmp/test-results/keymaps/inventory.json
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from keymaps.catalog_inventory import inventory, read_catalog


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', type=Path, default=ROOT / 'keymaps/deluxe-defaults.json')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--write-factory', action='store_true', help='Refresh the release snapshot after authoring shipped defaults')
    args = parser.parse_args()
    catalog, sources = read_catalog(args.catalog)
    if args.write_factory:
        target = args.catalog.with_name('factory-defaults.json')
        target.write_text(json.dumps(catalog, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    report = inventory(catalog, sources)
    report['source_commit'] = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
    report['source_dirty'] = bool(subprocess.check_output(['git', '-C', str(ROOT), 'status', '--porcelain']))
    content = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding='utf-8')
    else:
        print(content, end='')


if __name__ == '__main__':
    main()
