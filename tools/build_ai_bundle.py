#!/usr/bin/env python3
"""Build the files that make this guide easy to give to an AI assistant.

Usage:
  python3 tools/build_ai_bundle.py [--base-url URL] [--check]

Writes:
  llms.txt                          index of every page with a one-line summary (llmstxt.org format).
                                    Committed. Links are relative unless --base-url is given, e.g.
                                    https://raw.githubusercontent.com/<owner>/<repo>/main/
                                    (with --base-url it is written to dist/llms.txt instead, for publishing)
  dist/field-guide-cassandra-5.0.md every hand-written page in reading order, in one file, with the
                                    usage rules from AI_USAGE.md at the top. For chat uploads and
                                    "project knowledge". Not committed (dist/ is ignored); CI attaches it.
  dist/field-guide-cassandra-5.0-reference.md   the two generated reference pages, in one file.

--check exits 1 if llms.txt is out of date (for CI). Page summaries come from the
Table of Contents bullets in README.md, so keep those current. Standard library only.
"""
import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOC_ITEM = re.compile(r'^\* \*\*\[[^\]]+\]\(([^)]+\.md)\)\*\*:\s*(.+)$')
PHASE = re.compile(r'^### (Phase \d+: .+)$')
GENERATED = ('09_reference/01_cassandra_yaml_reference.md', '09_reference/02_nodetool_reference.md')


def toc():
    """[(phase, [(path, summary)])] in README order."""
    phases, cur = [], None
    with open(os.path.join(ROOT, 'README.md'), encoding='utf-8') as f:
        for line in f:
            m = PHASE.match(line.strip())
            if m:
                cur = (m.group(1), [])
                phases.append(cur)
                continue
            m = TOC_ITEM.match(line.strip())
            if m and cur:
                cur[1].append((m.group(1), m.group(2)))
    return phases


def title(path):
    with open(os.path.join(ROOT, path), encoding='utf-8') as f:
        for line in f:
            if line.startswith('# '):
                return line[2:].strip()
    return path


def llms_txt(base):
    out = ['# Field Guide for Apache Cassandra 5.0', '',
           '> Independent, opinionated runbooks and guidance for operating and developing against Apache '
           'Cassandra 5.0.x: data modeling, SAI and vector search, drivers, cloud deployment, configuration, '
           'security, upgrades, day-2 operations, auto-repair, troubleshooting and disaster recovery. '
           'Not affiliated with or endorsed by The Apache Software Foundation.', '',
           'Read ' + f'[AI_USAGE.md]({base}AI_USAGE.md)' + ' first: it gives the rules for answering from this guide '
           '(version scope, the two config templates, irreversible operations, and how to cite). Names and '
           'defaults were verified against the Cassandra 5.0 source; behavior was validated on a live cluster '
           f'([results]({base}test_env/results/LATEST.md)).', '']
    optional = []
    for phase, items in toc():
        section = []
        for path, summary in items:
            line = f'- [{title(path)}]({base}{path}): {summary}'
            (optional if path in GENERATED else section).append(line)
        if section:
            out += [f'## {phase}', ''] + section + ['']
    out += ['## Optional', ''] + optional + [
        f'- [Validation environment]({base}test_env/README.md): Docker cluster that tests the guide\'s claims.',
        f'- [Documentation tools]({base}tools/README.md): reference generators and drift checker.', '']
    return '\n'.join(out)


def strip_front(text):
    return text.rstrip() + '\n'


def bundle(paths, header):
    parts = [header]
    for p in paths:
        with open(os.path.join(ROOT, p), encoding='utf-8') as f:
            parts.append(f'\n\n---\n\n<!-- source: {p} -->\n\n' + strip_front(f.read()))
    return ''.join(parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--base-url', default='', help='prefix for links in llms.txt (default: relative)')
    ap.add_argument('--check', action='store_true', help='exit 1 if llms.txt is stale; write nothing')
    a = ap.parse_args()
    base = a.base_url if not a.base_url or a.base_url.endswith('/') else a.base_url + '/'

    txt = llms_txt(base)
    llms = os.path.join(ROOT, 'llms.txt')
    if a.check:
        cur = open(llms, encoding='utf-8').read() if os.path.exists(llms) else ''
        if cur != txt:
            print('llms.txt is out of date: run python3 tools/build_ai_bundle.py')
            return 1
        print('llms.txt is up to date')
        return 0
    os.makedirs(os.path.join(ROOT, 'dist'), exist_ok=True)
    out_llms = 'dist/llms.txt' if a.base_url else 'llms.txt'
    with open(os.path.join(ROOT, out_llms), 'w', encoding='utf-8') as f:
        f.write(txt)

    pages = [p for _, items in toc() for p, _ in items]
    guide = [p for p in pages if p not in GENERATED]
    with open(os.path.join(ROOT, 'AI_USAGE.md'), encoding='utf-8') as f:
        usage = f.read().rstrip()
    head = ('# Field Guide for Apache Cassandra 5.0 (single-file edition)\n\n'
            'Generated by tools/build_ai_bundle.py. Each page starts after a `<!-- source: path -->` marker; '
            'cite that path and the section heading.\n\n' + usage + '\n')
    with open(os.path.join(ROOT, 'dist', 'field-guide-cassandra-5.0.md'), 'w', encoding='utf-8') as f:
        f.write(bundle(['README.md'] + guide, head))
    with open(os.path.join(ROOT, 'dist', 'field-guide-cassandra-5.0-reference.md'), 'w', encoding='utf-8') as f:
        f.write(bundle(list(GENERATED), '# Field Guide for Apache Cassandra 5.0: generated reference\n'))
    for p in (out_llms, 'dist/field-guide-cassandra-5.0.md', 'dist/field-guide-cassandra-5.0-reference.md'):
        print(f'wrote {p} ({os.path.getsize(os.path.join(ROOT, p)) // 1024} KiB)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
