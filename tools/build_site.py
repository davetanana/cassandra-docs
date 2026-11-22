#!/usr/bin/env python3
"""Stage the guide as a searchable static site (MkDocs + Material) for GitHub Pages.

Usage:
  python3 tools/build_site.py [--repo-url https://github.com/<owner>/<repo>] [--branch main]
                              (--repo-url defaults to the git origin remote)
  pip install -r tools/site-requirements.txt
  mkdocs build -f build/site/mkdocs.yml        # writes build/site/public/

This script only stages files (standard library only): it copies every Markdown page into
build/site/docs/, rewrites links that point at non-Markdown files (LICENSE, workflow files, folders) to
GitHub URLs when --repo-url is given, copies llms.txt, and writes build/site/mkdocs.yml with the
navigation taken from the README's Table of Contents, the same source as llms.txt. The pages
themselves are not changed, so GitHub and the site render the same Markdown.
CI builds it on every pull request (.github/workflows/docs.yml); .github/workflows/pages.yml publishes it when run by hand.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_ai_bundle import ROOT, title, toc  # noqa: E402  (same TOC source as llms.txt)

SKIP_DIRS = {'.git', '.github', '.claude', '.gemini', 'build', 'dist', 'node_modules', '__pycache__'}
LINK = re.compile(r'(\]\()([^)\s#]+)(#[^)\s]*)?(\))')
OUT = os.path.join(ROOT, 'build', 'site')
DOCS = os.path.join(OUT, 'docs')


def md_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            rel = os.path.relpath(os.path.join(dirpath, fn), ROOT)
            # Run outputs are git-ignored except the committed full-run summary.
            if rel.startswith(os.path.join('test_env', 'results')) and fn != 'LATEST.md':
                continue
            if fn.endswith('.md'):
                yield rel


def rewrite_links(rel, text, repo_url, branch):
    """Point links at files the site doesn't serve (LICENSE, .yml, folders) to GitHub instead."""
    def sub(m):
        target = m.group(2)
        if re.match(r'^[a-z]+:', target) or target.endswith('.md') or target == 'llms.txt':
            return m.group(0)
        resolved = os.path.normpath(os.path.join(os.path.dirname(rel), target))
        if resolved.startswith('..') or not repo_url:
            return m.group(0)
        kind = 'tree' if os.path.isdir(os.path.join(ROOT, resolved)) else 'blob'
        return f'{m.group(1)}{repo_url}/{kind}/{branch}/{resolved}{m.group(3) or ""}{m.group(4)}'
    return LINK.sub(sub, text)


def origin_url():
    """https://github.com/<owner>/<repo> from the git origin remote, or '' if there isn't one."""
    try:
        url = subprocess.run(['git', '-C', ROOT, 'remote', 'get-url', 'origin'], capture_output=True,
                             text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ''
    m = re.match(r'^(?:git@github\.com:|https://github\.com/)([^/]+/[^/]+?)(?:\.git)?$', url)
    return f'https://github.com/{m.group(1)}' if m else ''


def nav():
    items = [{'Home': 'README.md'}]
    for phase, pages in toc():
        items.append({phase: [{title(p): p} for p, _ in pages]})
    project = [p for p in ('AI_USAGE.md', 'AGENTS.md', 'CONTRIBUTING.md', 'ROADMAP.md', 'test_env/README.md',
                           'test_env/results/LATEST.md', 'tools/README.md')
               if os.path.exists(os.path.join(ROOT, p))]
    items.append({'About this guide': [{title(p): p} for p in project]})
    return items


def config(repo_url, branch):
    # JSON is valid YAML, except for the one !!python/name tag that Material's mermaid support needs.
    cfg = {
        'site_name': 'Field Guide for Apache Cassandra® 5.0',
        'site_description': 'Independent runbooks and guidance for Apache Cassandra 5.0.x, checked against '
                            'the source and tested on a live cluster. Not affiliated with the ASF.',
        'docs_dir': 'docs',
        'site_dir': 'public',
        'use_directory_urls': False,
        'copyright': 'Independent community guide, Apache-2.0. Not affiliated with, endorsed by, or sponsored '
                     'by The Apache Software Foundation. Apache Cassandra® is a trademark of the ASF.',
        'theme': {
            'name': 'material',
            'features': ['navigation.sections', 'navigation.top', 'navigation.footer', 'search.suggest',
                         'search.highlight', 'content.code.copy', 'toc.follow'],
            'palette': [
                {'media': '(prefers-color-scheme: light)', 'scheme': 'default',
                 'toggle': {'icon': 'material/weather-night', 'name': 'Dark mode'}},
                {'media': '(prefers-color-scheme: dark)', 'scheme': 'slate',
                 'toggle': {'icon': 'material/weather-sunny', 'name': 'Light mode'}},
            ],
        },
        'plugins': ['search'],
        # Fail the --strict build on a link to a missing heading anchor, not only a missing page.
        'validation': {'anchors': 'warn', 'unrecognized_links': 'warn'},
        'markdown_extensions': [
            'tables', 'attr_list', 'md_in_html', 'admonition', 'github-callouts',
            {'toc': {'permalink': True, 'slugify': '__SLUGIFY__'}},
            {'pymdownx.highlight': {'anchor_linenums': True}},
            'pymdownx.inlinehilite',
            {'pymdownx.superfences': {'custom_fences': [
                {'name': 'mermaid', 'class': 'mermaid', 'format': '__MERMAID__'}]}},
            {'pymdownx.arithmatex': {'generic': True}},
        ],
        'extra_javascript': ['https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js'],
        'nav': nav(),
    }
    if repo_url:
        cfg.update({'repo_url': repo_url, 'edit_uri': f'edit/{branch}/'})
    text = json.dumps(cfg, indent=2, ensure_ascii=False)
    # GitHub-compatible heading anchors, so links like #2-enabling-it-two-switches work on both.
    text = text.replace('"__SLUGIFY__"', '!!python/object/apply:pymdownx.slugs.slugify {kwds: {case: lower}}')
    return text.replace('"__MERMAID__"', '!!python/name:pymdownx.superfences.fence_code_format')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--repo-url', default='', help='e.g. https://github.com/<owner>/<repo>')
    ap.add_argument('--branch', default='main')
    a = ap.parse_args()
    repo_url = (a.repo_url or origin_url()).rstrip('/')
    if not repo_url:
        print('warning: no --repo-url and no GitHub origin remote; links to LICENSE, NOTICE and other '
              'non-Markdown files will be reported by mkdocs', file=sys.stderr)

    shutil.rmtree(OUT, ignore_errors=True)
    n = 0
    for rel in md_files():
        dest = os.path.join(DOCS, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(os.path.join(ROOT, rel), encoding='utf-8') as f:
            text = f.read()
        with open(dest, 'w', encoding='utf-8') as f:
            f.write(rewrite_links(rel, text, repo_url, a.branch))
        n += 1
    shutil.copy(os.path.join(ROOT, 'llms.txt'), os.path.join(DOCS, 'llms.txt'))
    with open(os.path.join(OUT, 'mkdocs.yml'), 'w', encoding='utf-8') as f:
        f.write(config(repo_url, a.branch) + '\n')
    print(f'staged {n} pages in {os.path.relpath(DOCS, ROOT)}; now run: mkdocs build -f build/site/mkdocs.yml')


if __name__ == '__main__':
    main()
