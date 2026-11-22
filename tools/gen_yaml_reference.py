#!/usr/bin/env python3
# Licensed under the Apache License, Version 2.0.
"""Generate a Markdown reference for cassandra.yaml from a Cassandra source checkout.

Usage:
    python3 gen_yaml_reference.py /path/to/cassandra [-o OUTPUT.md]

Reads conf/cassandra.yaml, conf/cassandra_latest.yaml and
src/java/org/apache/cassandra/config/Config.java. Python 3 standard library only.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cassandra_source import checkout_version, config_keys, parse_yaml  # noqa: E402

OFFICIAL = "https://cassandra.apache.org/doc/5.0/cassandra/managing/configuration/cass_yaml_file.html"


def anchor(key):
    return key


def md_escape(text):
    return text.replace("|", "\\|")


def render(root, out_rel_cmd):
    version, sha = checkout_version(root)
    fields, replaced = config_keys(root)
    valid = fields | set(replaced)
    base = parse_yaml(os.path.join(root, "conf/cassandra.yaml"), valid)
    latest_path = os.path.join(root, "conf/cassandra_latest.yaml")
    latest = parse_yaml(latest_path, valid) if os.path.exists(latest_path) else {}

    out = []
    w = out.append
    w("# cassandra.yaml Reference (generated)")
    w("")
    w("> [!CAUTION]")
    w("> Commands and settings on this page can change or delete data and affect running clusters. Try them on a "
      "test or staging cluster first, and read the [disclaimer](../README.md#disclaimer). "
      "The guide is provided \"as is\", without warranty.")
    w("")
    w("> [!NOTE]")
    w(f"> **Generated** from Apache Cassandra **{version}** at git commit `{sha}` "
      "(`conf/cassandra.yaml`, `conf/cassandra_latest.yaml`, `Config.java`). Do not edit by hand.")
    w(f"> Regenerate with: `{out_rel_cmd}`")
    w(">")
    w("> Descriptions are the comments from the Apache Cassandra source files, used under the "
      "[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0). "
      f"Official equivalent: [cassandra.yaml file configuration]({OFFICIAL}).")
    w("")
    w("How to read this page:")
    w("")
    w("* **Active**: the key is set in the shipped `cassandra.yaml`. **Commented**: the shipped file "
      "contains it only as a `#` example, so Cassandra uses its built-in default (usually, but not "
      "always, the value shown).")
    w("* **cassandra_latest.yaml**: shown only when the value or block differs from `cassandra.yaml`.")
    w("* Keys accepted by `Config.java` but absent from both yaml files are listed at the end.")
    w("")

    # Index
    keys = sorted(set(base) | set(latest))
    w("## Index")
    w("")
    letters = {}
    for k in keys:
        letters.setdefault(k[0], []).append(k)
    for letter in sorted(letters):
        w(f"**{letter.upper()}**: " + ", ".join(f"[`{k}`](#{anchor(k)})" for k in letters[letter]))
        w("")

    # Sections in file order
    sections = []
    for e in base.values():
        if e.section not in sections:
            sections.append(e.section)
    only_latest = [k for k in latest if k not in base]

    def emit(key, e, l):
        w(f"### `{key}`")
        w("")
        w(f'<a id="{anchor(key)}"></a>')
        w("")
        status = "Active" if e.active else "Commented (built-in default applies)"
        w(f"*{status}* · `conf/cassandra.yaml` line {e.line_no}")
        if key in replaced.values():
            olds = sorted(o for o, n in replaced.items() if n == key)
            w(f" · deprecated old name(s): {', '.join('`' + o + '`' for o in olds)}")
        w("")
        w("```yaml")
        w(e.normalized())
        w("```")
        w("")
        if l is not None and l.normalized() != e.normalized() or (l is not None and l.active != e.active):
            w("**In `cassandra_latest.yaml`**" + ("" if l.active else " (commented)") + ":")
            w("")
            w("```yaml")
            w(l.normalized())
            w("```")
            w("")
        meaningful = [d for d in e.description if d.strip() and not d.strip().startswith("Min unit")]
        if e.description:
            w("\n".join("> " + md_escape(d) if d.strip() else ">" for d in e.description))
            w("")
        if len(meaningful) < 1 and e.follows:
            w(f"See the description of [`{e.follows}`](#{anchor(e.follows)}), which this setting accompanies in the yaml.")
            w("")

    for sec in sections:
        w(f"## {sec}")
        w("")
        for k, e in base.items():
            if e.section == sec:
                emit(k, e, latest.get(k))
    if only_latest:
        w("## Only in cassandra_latest.yaml")
        w("")
        for k in only_latest:
            emit(k, latest[k], None)

    undocumented = sorted(f for f in fields if f not in base and f not in latest)
    w("## Accepted by Config.java but not present in either yaml file")
    w("")
    w("These keys are valid but undocumented in the shipped files. Check `Config.java` "
      "and `NEWS.txt` before using them.")
    w("")
    w(", ".join(f"`{k}`" for k in undocumented))
    w("")
    w("## Deprecated key names still accepted")
    w("")
    w("| Old name | Current name |")
    w("| :--- | :--- |")
    for old, new in sorted(replaced.items()):
        w(f"| `{old}` | `{new}` |")
    w("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cassandra", help="path to an Apache Cassandra source checkout")
    ap.add_argument("-o", "--output", help="write to this file (default: stdout)")
    args = ap.parse_args()
    root = os.path.abspath(args.cassandra)
    if not os.path.exists(os.path.join(root, "conf/cassandra.yaml")):
        sys.exit(f"{root} does not look like a Cassandra checkout (no conf/cassandra.yaml)")
    cmd = "python3 tools/gen_yaml_reference.py <cassandra-checkout> -o 09_reference/01_cassandra_yaml_reference.md"
    text = render(root, cmd)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
