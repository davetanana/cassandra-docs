#!/usr/bin/env python3
# Licensed under the Apache License, Version 2.0.
"""Check the Markdown docs for drift against a Cassandra source checkout.

Usage:
    python3 check_docs.py /path/to/cassandra [--docs DOCS_DIR] [--strict]

Reports:
  * cassandra.yaml keys used in ```yaml blocks (top-level keys) or as `key: value`
    in inline code that Cassandra does not accept (not in Config.java / the shipped yaml),
    and keys that are only deprecated aliases;
  * `nodetool <command>` invocations whose command does not exist, and flags that the
    command does not define.

DOCS_DIR defaults to the parent directory of this script. Exits 1 if errors are found
(with --strict, warnings also fail). Python 3 standard library only.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cassandra_source import (KEY_RE, all_yaml_keys, checkout_version, config_keys,  # noqa: E402
                              parse_nodetool, parse_yaml)

# Top-level keys that legitimately appear in yaml blocks but are not cassandra.yaml keys.
NON_CASSANDRA_YAML = {
    "network", "version", "ethernets", "apiversion", "kind", "metadata", "spec",
}
GLOBAL_FLAGS_WITH_VALUE = {"-h", "--host", "-p", "--port", "-u", "--username",
                           "-pw", "--password", "-pwf", "--password-file"}
GLOBAL_FLAGS = GLOBAL_FLAGS_WITH_VALUE | {"-pp", "--print-port"}


def java_literals(root):
    """All snake_case string literals in src/java (option and field names)."""
    out = set()
    src = os.path.join(root, "src/java")
    for dirpath, _, files in os.walk(src):
        for fn in files:
            if fn.endswith(".java"):
                with open(os.path.join(dirpath, fn), encoding="utf-8", errors="replace") as f:
                    out.update(re.findall(r'"(' + KEY_RE + r')"', f.read()))
    # Config fields of nested option classes are matched by name, not string literal
    for dirpath, _, files in os.walk(os.path.join(src, "org/apache/cassandra/config")):
        for fn in files:
            if fn.endswith(".java"):
                with open(os.path.join(dirpath, fn), encoding="utf-8", errors="replace") as f:
                    out.update(re.findall(r"public\s+(?:final\s+)?[\w.<>, ]+\s+(" + KEY_RE + r")\s*[;=]", f.read()))
    return out


def iter_md(docs):
    for dirpath, dirnames, files in os.walk(docs):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in ("tools", "dist", "results")]
        for fn in sorted(files):
            if fn.endswith(".md"):
                yield os.path.join(dirpath, fn)


def code_segments(text):
    """Yield (line_no, kind, content) for fenced block lines and inline code spans.
    kind is the fence language for block lines, or 'inline'."""
    lang = None
    for no, line in enumerate(text.splitlines(), 1):
        fm = re.match(r"^\s*(```|~~~)\s*([\w+-]*)", line)
        if fm:
            lang = None if lang is not None else (fm.group(2) or "text").lower()
            continue
        if lang is not None:
            yield no, lang, line
        else:
            for m in re.finditer(r"`([^`]+)`", line):
                yield no, "inline", m.group(1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cassandra", help="path to an Apache Cassandra source checkout")
    ap.add_argument("--docs", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    help="docs root to scan (default: parent of tools/)")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = ap.parse_args()
    root = os.path.abspath(args.cassandra)

    version, sha = checkout_version(root)
    fields, replaced = config_keys(root)
    valid = fields | set(replaced)
    base = parse_yaml(os.path.join(root, "conf/cassandra.yaml"), valid)
    latest_p = os.path.join(root, "conf/cassandra_latest.yaml")
    latest = parse_yaml(latest_p, valid) if os.path.exists(latest_p) else {}
    known_top = fields | set(base) | set(latest)
    # Broader set for inline `key: value` mentions: nested yaml keys, plus any snake_case
    # string literal in the Java source (table/compaction options, nested config fields).
    known_any = known_top | all_yaml_keys(base) | all_yaml_keys(latest) | java_literals(root)
    commands, group_cmds, groups, global_opts = parse_nodetool(root)
    cmd_names = set(commands) | set(groups)

    def flags_of(name, sub=None):
        c = group_cmds.get(f"{name} {sub}") if sub else commands.get(name)
        if not c:
            return None
        out = set()
        for names, _, _ in c.options:
            out.update(names)
        return out

    errors, warnings = [], []
    for path in iter_md(args.docs):
        rel = os.path.relpath(path, args.docs)
        if rel.startswith("09_reference"):
            continue  # generated pages
        with open(path, encoding="utf-8") as f:
            text = f.read()
        for no, kind, content in code_segments(text):
            # ---- yaml keys ----
            keys = []
            if kind == "yaml":
                m = re.match(r"^(" + KEY_RE + r"):(\s|$)", content)
                if m:
                    keys.append(m.group(1))
            elif kind == "inline":
                m = re.match(r"^(" + KEY_RE + r"):\s+\S", content.strip())
                if m and "_" in m.group(1):
                    keys.append(m.group(1))
            for k in keys:
                if k in NON_CASSANDRA_YAML:
                    continue
                if k in replaced:
                    warnings.append(f"{rel}:{no}: yaml key `{k}` is a deprecated alias of `{replaced[k]}`")
                elif kind == "yaml" and k not in known_top:
                    errors.append(f"{rel}:{no}: yaml key `{k}` is not a top-level cassandra.yaml/Config.java key")
                elif kind == "inline" and k not in known_any:
                    warnings.append(f"{rel}:{no}: `{k}` is not a known Cassandra config key or option")

            # ---- nodetool invocations ----
            scan = content
            if kind != "inline":
                # ignore shell comments and quoted strings (prose such as echo "...nodetool to...")
                scan = re.sub(r"(^|\s)#.*$", "", scan)
                scan = re.sub(r'"[^"]*"|\'[^\']*\'', "", scan)
            for m in re.finditer(r"(?:^|[\s;|&(`$])nodetool((?:\s+[^\s;|&#`)]+)*)", scan):
                toks = m.group(1).split()
                i = 0
                while i < len(toks) and toks[i] in GLOBAL_FLAGS:
                    i += 2 if toks[i] in GLOBAL_FLAGS_WITH_VALUE else 1
                if i >= len(toks):
                    continue
                cmd = toks[i]
                if not re.match(r"^[a-z_]+$", cmd):
                    continue  # placeholder like <command> or "$CMD"
                if cmd not in cmd_names:
                    errors.append(f"{rel}:{no}: `nodetool {cmd}` is not a nodetool command")
                    continue
                sub = None
                if cmd in groups and i + 1 < len(toks) and re.match(r"^[a-z_-]+$", toks[i + 1]):
                    sub = toks[i + 1]
                    if f"{cmd} {sub}" not in group_cmds:
                        errors.append(f"{rel}:{no}: `nodetool {cmd} {sub}` is not a nodetool subcommand")
                        continue
                allowed = flags_of(cmd, sub)
                if allowed is None:
                    continue
                for t in toks[i + 1:]:
                    if not t.startswith("-") or t == "--" or re.match(r"^-\d", t):
                        continue
                    flag = t.split("=", 1)[0]
                    if flag not in allowed and flag not in GLOBAL_FLAGS:
                        errors.append(f"{rel}:{no}: `nodetool {cmd}` has no option `{flag}`")

    print(f"Checked docs in {os.path.abspath(args.docs)} against Apache Cassandra {version} ({sha})")
    for e in errors:
        print("ERROR   " + e)
    for w in warnings:
        print("WARNING " + w)
    print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
    sys.exit(1 if errors or (args.strict and warnings) else 0)


if __name__ == "__main__":
    main()
