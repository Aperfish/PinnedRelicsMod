"""Verify the game-native distribution contains no external textures or runtime dependencies."""
from pathlib import Path
import hashlib
import json
import zipfile

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / 'src/PinnedRelicsMod.json').read_text(encoding='utf-8'))
version = manifest['version']
package = root / f'outputs/PinnedRelicsMod-{version}.zip'
rows = [line.split('\t') for line in (root / 'src/RelicCatalog.tsv').read_text(encoding='utf-8').splitlines()]
assert len(rows) == 90 and all(len(row) == 2 for row in rows)
assert {50024, 50082, 50041, 50086, 50078, 50079, 50080}.issubset({int(row[0]) for row in rows})
assert manifest['id'] == 'PinnedRelicsMod' and version == '1.2.0' and manifest['permissions'] == 129
installed = Path('D:/Steam/steamapps/common/Astral Party/8vJXn6CN/AstralParty_ModLoader/mods/PinnedRelicsMod')
with zipfile.ZipFile(package) as archive:
    names = {n.replace('\\', '/') for n in archive.namelist() if not n.endswith('/')}
    assert all(n.startswith('PinnedRelicsMod/') and '..' not in n.split('/') for n in names)
    assert not any('/assets/' in n or n.endswith('.png') for n in names)
    assert not (installed / 'assets').exists(), 'Old external images were not archived'
    required = ['PinnedRelicsMod.dll', 'PinnedRelicsMod.pdb', 'PinnedRelicsMod.json', 'config.json',
                'README.md', 'NOTICE.md', 'LICENSE', '支持的筹码.md']
    assert names == {'PinnedRelicsMod/' + name for name in required}
    for name in names:
        local = installed / name.split('/', 1)[1]
        if not name.endswith('/config.json'):
            assert local.read_bytes() == archive.read(name), str(local)
        else:
            config = json.loads(local.read_text(encoding='utf-8-sig'))
            assert config['IconSize'] == 30 and config['IconGap'] == 3 and 'PinnedRelicNames' in config
    print(json.dumps({'packageFiles': len(names), 'supportedRelics': len(rows), 'externalImages': 0,
                      'installedFilesMatch': True, 'zipBytes': package.stat().st_size,
                      'sha256': hashlib.sha256(package.read_bytes()).hexdigest()}, indent=2))
source_zip = root / f'outputs/PinnedRelicsMod-{version}-source.zip'
with zipfile.ZipFile(source_zip, 'w', zipfile.ZIP_DEFLATED) as archive:
    for file in root.rglob('*'):
        relative = file.relative_to(root)
        if file.is_file() and not any(part in {'bin', 'obj', 'work', 'outputs', '__pycache__'} for part in relative.parts):
            archive.write(file, 'PinnedRelicsMod/' + relative.as_posix())
print('Source package:', source_zip)
