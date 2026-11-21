#!/usr/bin/env python3
# Licensed under the Apache License, Version 2.0.
"""Generate a Markdown nodetool reference from a Cassandra source checkout.

Usage:
    python3 gen_nodetool_reference.py /path/to/cassandra [-o OUTPUT.md]

Reads the commands registered in src/java/org/apache/cassandra/tools/NodeTool.java
and the airline annotations (@Command, @Arguments, @Option) on each command class.
Python 3 standard library only.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cassandra_source import checkout_version, parse_nodetool  # noqa: E402

OFFICIAL = "https://cassandra.apache.org/doc/5.0/cassandra/managing/tools/nodetool/nodetool.html"


def anchor(name):
    return re.sub(r"[^a-z0-9_-]", "-", name.lower())


def esc(text):
    return re.sub(r"\s+", " ", text or "").replace("|", "\\|").strip()


def render(root, regen_cmd):
    version, sha = checkout_version(root)
    commands, group_cmds, groups, global_opts = parse_nodetool(root)
    out = []
    w = out.append
    w("# nodetool Reference (generated)")
    w("")
    w("> [!NOTE]")
    w(f"> **Generated** from Apache Cassandra **{version}** at git commit `{sha}` "
      "(`src/java/org/apache/cassandra/tools/NodeTool.java` and `tools/nodetool/*.java`). Do not edit by hand.")
    w(f"> Regenerate with: `{regen_cmd}`")
    w(">")
    w("> Descriptions are taken from the Apache Cassandra source, used under the "
      "[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0). "
      f"Official equivalent: [nodetool]({OFFICIAL}).")
    w("")
    w(f"{len(commands)} top-level commands and {len(group_cmds)} grouped subcommands. "
      "Run `nodetool help <command>` on a node for the authoritative help text of the version you run.")
    w("")

    w("## Global options")
    w("")
    w("These connection options apply to every command and go before the command name, "
      "for example `nodetool -h 10.0.1.10 -p 7199 status`.")
    w("")
    w("| Option | Description |")
    w("| :--- | :--- |")
    for names, desc, _ in global_opts:
        w(f"| {', '.join('`' + n + '`' for n in names)} | {esc(desc)} |")
    w("")

    w("## Index")
    w("")
    w("| Command | Description |")
    w("| :--- | :--- |")
    allc = sorted(list(commands.items()) + list(group_cmds.items()), key=lambda kv: kv[0])
    for name, c in allc:
        flag = " **(deprecated)**" if c.deprecated else ""
        flag += " *(hidden)*" if c.hidden else ""
        w(f"| [`{name}`](#{anchor(name)}) | {esc(c.description)}{flag} |")
    w("")

    if groups:
        w("Command groups: " + "; ".join(f"`{g}` ({esc(d)})" for g, (d, _) in groups.items()) + ".")
        w("")

    w("## Commands")
    w("")
    for name, c in allc:
        w(f'<a id="{anchor(name)}"></a>')
        w("")
        w(f"### `{name}`")
        w("")
        if c.deprecated:
            w("> [!WARNING]")
            w("> The source marks this command as deprecated.")
            w("")
        w(esc(c.description) or "*(no description in source)*")
        w("")
        usage = " ".join(u for u, _ in c.arguments if u)
        opt_hint = " [options]" if c.options else ""
        w("```")
        w(f"nodetool [global options] {name}{opt_hint}" + (f" {usage}" if usage else ""))
        w("```")
        w("")
        for u, d in c.arguments:
            if d:
                w(f"* **Arguments** `{esc(u)}`: {esc(d)}")
        if c.arguments:
            w("")
        if c.options:
            w("| Option | Description |")
            w("| :--- | :--- |")
            for names, desc, req in c.options:
                r = " **(required)**" if req else ""
                w(f"| {', '.join('`' + n + '`' for n in names)} | {esc(desc)}{r} |")
            w("")
        rel = os.path.relpath(c.path, root)
        w(f"<sub>Source: `{rel}` (class `{c.cls}`)</sub>")
        w("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cassandra", help="path to an Apache Cassandra source checkout")
    ap.add_argument("-o", "--output", help="write to this file (default: stdout)")
    args = ap.parse_args()
    root = os.path.abspath(args.cassandra)
    if not os.path.exists(os.path.join(root, "src/java/org/apache/cassandra/tools/NodeTool.java")):
        sys.exit(f"{root} does not look like a Cassandra checkout (no tools/NodeTool.java)")
    cmd = "python3 tools/gen_nodetool_reference.py <cassandra-checkout> -o 09_reference/02_nodetool_reference.md"
    text = render(root, cmd)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
