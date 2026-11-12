"""Build the Chinese-name index from user-supplied game tables. No images or DLL resources."""
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]


def varint(data, pos):
    result = shift = 0
    while pos < len(data):
        byte = data[pos]
        pos += 1
        result |= (byte & 127) << shift
        if byte < 128:
            return result, pos
        shift += 7
        if shift > 63:
            raise ValueError('Invalid varint')
    raise ValueError('Truncated varint')


def fields(data):
    pos = 0
    while pos < len(data):
        tag, pos = varint(data, pos)
        field, wire = tag >> 3, tag & 7
        if wire == 0:
            value, pos = varint(data, pos)
        elif wire == 2:
            size, pos = varint(data, pos)
            value = data[pos:pos + size]
            pos += size
        elif wire in (1, 5):
            size = 8 if wire == 1 else 4
            value = int.from_bytes(data[pos:pos + size], 'little')
            pos += size
        else:
            raise ValueError('Unsupported wire type')
        yield field, wire, value


def rows(path):
    for _, wire, raw in fields(path.read_bytes()):
        if wire == 2:
            yield {(f, w): v for f, w, v in fields(raw)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tables', required=True, help='Directory containing extracted Relic and STRRelic')
    args = parser.parse_args()
    tables = Path(args.tables)
    names = {}
    for row in rows(tables / 'STRRelic'):
        try:
            text = row.get((2, 2), b'').decode('utf-8')
        except UnicodeDecodeError:
            continue
        if (1, 5) in row and text and not any(ord(c) < 32 for c in text):
            names.setdefault(row[(1, 5)], text)
    catalogue = {}
    for row in rows(tables / 'Relic'):
        if (1, 5) in row and (2, 0) in row and (6, 2) in row:
            catalogue[row[(1, 5)]] = names[row[(7, 5)]]
    lines = [str(key) + '\t' + catalogue[key] for key in sorted(catalogue)]
    (ROOT / 'src/RelicCatalog.tsv').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    from generate_catalog_code import generate
    generate()
    supported = '# 可配置的筹码中文名\n\n当前支持以下 90 种筹码，图标和品质底圈由游戏原生 UI 加载。\n\n'
    supported += '\n'.join('- ' + catalogue[key] for key in sorted(catalogue)) + '\n'
    (ROOT / '支持的筹码.md').write_text(supported, encoding='utf-8')
    print('Game-native relic names:', len(catalogue))


if __name__ == '__main__':
    main()
