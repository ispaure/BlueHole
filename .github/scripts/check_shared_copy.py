"""Compare the vendored library with its recorded upstream revision."""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
upstream = Path(sys.argv[1]).resolve()
expected = (root / 'Lib/commonUtils.revision').read_text().strip()
actual = subprocess.check_output(['git', '-C', str(upstream), 'rev-parse', 'HEAD'], text=True).strip()
if actual != expected:
    raise SystemExit(f'Wrong shared revision: {actual}, expected {expected}')
names = subprocess.check_output(['git', '-C', str(upstream), 'ls-files', '-z']).decode().split('\0')
failures = []
for name in names:
    if not name or name.startswith('.github/'):
        continue
    target = root / 'Lib/commonUtils' / name
    if not target.is_file() or target.read_bytes() != (upstream / name).read_bytes():
        failures.append(name)
if failures:
    raise SystemExit('Shared copy differs: ' + ', '.join(failures))
print('Vendored commonUtils matches', expected)
