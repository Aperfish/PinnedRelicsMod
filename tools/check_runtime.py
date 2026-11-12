"""Check the real loader's latest session, rather than treating a desktop CLR test as game validation."""
from pathlib import Path
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument('--logs', default='D:/Steam/steamapps/common/Astral Party/8vJXn6CN/AstralParty_ModLoader/logs')
parser.add_argument('--version', default='1.1.1')
parser.add_argument('--require-icons', action='store_true')
args = parser.parse_args()
logs = sorted(Path(args.logs).glob('activity-mod-*.log'), key=lambda path: path.stat().st_mtime, reverse=True)
if not logs:
    raise SystemExit('WAIT: no loader log')
path = logs[0]
text = path.read_text(encoding='utf-8-sig', errors='replace')
lines = [line for line in text.splitlines() if re.search(r'\[(PinnedRelics|PinnedRelicsMod)\]', line)]
print('Session:', path.name)
for line in lines:
    print(line)
if '关键筹码置顶 v' + args.version not in text:
    raise SystemExit('WAIT: the requested version has not started in this session')
if any('OnInitialize:' in line or '初始化失败' in line for line in lines):
    raise SystemExit('FAIL: runtime initialization failed')
if not any('[PinnedRelics] 初始化完成' in line for line in lines):
    raise SystemExit('WAIT: initialization is not complete')
if args.require_icons and not any('已创建并显示' in line for line in lines):
    raise SystemExit('WAIT: not yet observed a player with a matching owned relic')
print('PASS: real game initialized' + (' and created owned-relic icons' if args.require_icons else ''))
