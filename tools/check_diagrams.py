#!/usr/bin/env python3
"""Check the Mermaid diagrams in every Markdown page.

Usage:
  python3 tools/check_diagrams.py            # fast lint, standard library only
  python3 tools/check_diagrams.py --render   # also render each diagram with the Mermaid CLI (needs Docker)

The lint catches the mistake that renders on GitHub as "Unsupported markdown: list": a flowchart node
label that starts with a number and a period, such as ["1. Repair"]. Mermaid reads it as a Markdown list.
Write "Step 1: Repair" or "§1 Repair" instead.

--render runs every diagram through the same Mermaid version family GitHub uses (minlag/mermaid-cli), so a
syntax error fails here instead of showing as an error box on GitHub. CI runs it.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {'.git', 'build', 'dist', 'node_modules', '__pycache__'}
BLOCK = re.compile(r'^```mermaid\n(.*?)^```', re.S | re.M)
LIST_LABEL = re.compile(r'(\["|\("|\{"|<br/>)\d+\. ')
MERMAID_IMAGE = 'minlag/mermaid-cli:11.4.2'


def diagrams():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            if not fn.endswith('.md'):
                continue
            path = os.path.join(dirpath, fn)
            text = open(path, encoding='utf-8').read()
            for m in BLOCK.finditer(text):
                line = text.count('\n', 0, m.start()) + 1
                yield os.path.relpath(path, ROOT), line, m.group(1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--render', action='store_true', help='render every diagram with the Mermaid CLI (Docker)')
    a = ap.parse_args()

    found = list(diagrams())
    errors = 0
    for rel, line, body in found:
        if re.match(r'\s*(graph|flowchart)\b', body):
            for i, l in enumerate(body.splitlines()):
                if LIST_LABEL.search(l):
                    print(f'{rel}:{line + 1 + i}: label starts with "N. ", which Mermaid renders as '
                          f'"Unsupported markdown: list": {l.strip()}')
                    errors += 1

    if a.render:
        if not shutil.which('docker'):
            print('error: --render needs Docker', file=sys.stderr)
            return 2
        with tempfile.TemporaryDirectory() as tmp:
            os.chmod(tmp, 0o777)   # the container runs as a non-root user
            names = {}
            for n, (rel, line, body) in enumerate(found):
                name = f'd{n}.mmd'
                names[name] = f'{rel}:{line}'
                with open(os.path.join(tmp, name), 'w', encoding='utf-8') as f:
                    f.write(body)
            script = ('cd /data; for f in *.mmd; do /home/mermaidcli/node_modules/.bin/mmdc '
                      '-p /puppeteer-config.json -q -i "$f" -o "${f%.mmd}.svg" >/dev/null 2>"$f.err" '
                      '|| echo "FAILED $f"; done')
            r = subprocess.run(['docker', 'run', '--rm', '--entrypoint', 'sh', '-v', f'{tmp}:/data', MERMAID_IMAGE,
                                '-c', script], capture_output=True, text=True)
            for name in re.findall(r'FAILED (\S+)', r.stdout):
                err = open(os.path.join(tmp, name + '.err'), encoding='utf-8').read().strip().splitlines()
                print(f'{names[name]}: Mermaid could not render this diagram: {" ".join(err[:3])}')
                errors += 1
            if r.returncode != 0:
                print(r.stderr, file=sys.stderr)
                return 2

    print(f'{len(found)} diagram(s) checked{" and rendered" if a.render else ""}, {errors} problem(s)')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
