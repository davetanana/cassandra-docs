#!/usr/bin/env python3
# Licensed under the Apache License, Version 2.0.
"""Shared helpers for reading facts out of an Apache Cassandra source checkout.

Used by gen_yaml_reference.py, gen_nodetool_reference.py and check_docs.py.
Python 3 standard library only.
"""
import os
import re
import subprocess
from collections import OrderedDict

KEY_RE = r"[a-z][a-z0-9_]*"


# --------------------------------------------------------------------------
# Checkout metadata
# --------------------------------------------------------------------------
def checkout_version(root):
    """Return (base.version from build.xml, short git sha or 'unknown')."""
    version = "unknown"
    try:
        with open(os.path.join(root, "build.xml"), encoding="utf-8") as f:
            m = re.search(r'<property name="base\.version" value="([^"]+)"', f.read())
            if m:
                version = m.group(1)
    except OSError:
        pass
    sha = "unknown"
    try:
        sha = subprocess.check_output(["git", "-C", root, "rev-parse", "--short", "HEAD"],
                                      stderr=subprocess.DEVNULL, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        pass
    return version, sha


# --------------------------------------------------------------------------
# Config.java: the set of keys Cassandra actually accepts
# --------------------------------------------------------------------------
def config_keys(root):
    """Return (fields, replaced) where fields is the set of Config.java public field
    names and replaced maps deprecated old names (from @Replaces) to the new name."""
    path = os.path.join(root, "src/java/org/apache/cassandra/config/Config.java")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    fields = set()
    replaced = {}
    pending_old = []
    depth = 0
    for line in text.splitlines():
        code = re.sub(r'"(?:[^"\\]|\\.)*"', '""', line.split("//")[0])
        at_depth = depth
        depth += code.count("{") - code.count("}")
        if at_depth != 1:
            continue  # only fields declared directly in class Config, not nested option classes
        for m in re.finditer(r'@Replaces\(\s*oldName\s*=\s*"([^"]+)"', line):
            pending_old.append(m.group(1))
        fm = re.match(r"\s*public\s+(?:static\s+)?(?:volatile\s+)?(?:final\s+)?[\w.<>,\[\] ?]+?\s+(" + KEY_RE + r")\s*(?:=|;)", line)
        if fm and "static" not in line.split("=")[0]:
            name = fm.group(1)
            fields.add(name)
            for old in pending_old:
                replaced[old] = name
            pending_old = []
    return fields, replaced


# --------------------------------------------------------------------------
# cassandra.yaml parsing
# --------------------------------------------------------------------------
class YamlEntry:
    def __init__(self, key, active, block_lines, description, section, line_no):
        self.key = key
        self.active = active
        self.block_lines = block_lines      # the key line plus nested lines, comment '#' removed if commented
        self.description = description      # list of comment lines (without '# ')
        self.section = section
        self.line_no = line_no
        self.follows = None                 # key immediately above with no blank line between

    @property
    def is_block(self):
        return len(self.block_lines) > 1

    @property
    def value(self):
        first = self.block_lines[0]
        return first.split(":", 1)[1].strip() if ":" in first else ""

    def normalized(self):
        return "\n".join(l.rstrip() for l in self.block_lines if l.strip())


def _uncomment(line):
    """'#   foo: bar' -> '  foo: bar' (strip the '#' and exactly one following space)."""
    s = line[1:]
    return s[1:] if s.startswith(" ") else s


def parse_yaml(path, valid_keys):
    """Parse a Cassandra yaml file into an OrderedDict key -> YamlEntry.

    Top-level keys are either active ('key: value' at column 0) or commented
    ('# key: value' / '#key: value'). Commented keys are only accepted if the name
    is a real Config.java field (or deprecated alias), which filters out prose.
    """
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    active_re = re.compile(r"^(" + KEY_RE + r"):(\s|$)")
    commented_re = re.compile(r"^# ?(" + KEY_RE + r"):(\s|$)")
    banner_re = re.compile(r"^#{3,}\s*$")

    entries = []
    section = "General"
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        # Section banners:  ####\n# TITLE #\n####
        if banner_re.match(line) and i + 2 < n and banner_re.match(lines[i + 2]):
            title = lines[i + 1].strip("# ").strip()
            if title:
                section = title.title()
            i += 3
            continue

        m_active = active_re.match(line)
        m_comment = commented_re.match(line) if not m_active else None
        if m_comment and m_comment.group(1) not in valid_keys:
            m_comment = None
        if not (m_active or m_comment):
            i += 1
            continue

        key = (m_active or m_comment).group(1)
        active = bool(m_active)
        block = [line if active else _uncomment(line)]
        j = i + 1
        while j < n:
            nxt = lines[j]
            if active:
                if nxt.startswith((" ", "\t", "-")) and nxt.strip():
                    block.append(nxt)
                    j += 1
                    continue
                # tolerate commented nested examples inside an active block
                if re.match(r"^#\s{2,}\S", nxt) and len(block) > 1:
                    j += 1
                    continue
            else:
                if re.match(r"^#(\s{2,}|\s*- )\S", nxt) or re.match(r"^#\s{2,}-", nxt):
                    block.append(_uncomment(nxt))
                    j += 1
                    continue
                # an empty '#' line inside a commented block: keep going if the block resumes
                if nxt.strip() == "#" and j + 1 < n and re.match(r"^#\s{2,}\S", lines[j + 1]):
                    block.append("")
                    j += 1
                    continue
            break

        # Description: contiguous comment lines directly above, stopping at a blank
        # line, a banner, or another commented key line.
        desc = []
        follows = None
        k = i - 1
        while k >= 0:
            prev = lines[k]
            if not prev.startswith("#") or banner_re.match(prev):
                am = active_re.match(prev)
                if am:
                    follows = am.group(1)
                break
            pm = commented_re.match(prev)
            if pm and pm.group(1) in valid_keys:
                follows = pm.group(1)
                break
            desc.insert(0, _uncomment(prev).rstrip())
            k -= 1
        # strip leading/trailing empty comment lines
        while desc and not desc[0].strip():
            desc.pop(0)
        while desc and not desc[-1].strip():
            desc.pop()

        entry = YamlEntry(key, active, block, desc, section, i + 1)
        entry.follows = follows
        entries.append(entry)
        i = j

    # Deduplicate: prefer the active occurrence; keep the best description.
    result = OrderedDict()
    for e in entries:
        if e.key not in result:
            result[e.key] = e
            continue
        cur = result[e.key]
        if e.active and not cur.active:
            if not e.description:
                e.description = cur.description
            e.section = cur.section
            result[e.key] = e
        elif not cur.description and e.description:
            cur.description = e.description
    return result


def all_yaml_keys(entries):
    """Top-level plus nested key names that appear in parsed yaml entries."""
    keys = set(entries)
    for e in entries.values():
        for l in e.block_lines[1:]:
            m = re.match(r"^\s*-?\s*(" + KEY_RE + r"):", l)
            if m:
                keys.add(m.group(1))
    return keys


# --------------------------------------------------------------------------
# nodetool command parsing
# --------------------------------------------------------------------------
def _balanced(text, start):
    """Given text[start] == '(', return index just past the matching ')'."""
    depth = 0
    i = start
    in_str = False
    while i < len(text):
        c = text[i]
        if in_str:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return len(text)


def _strings(expr):
    """Concatenate Java string literals in an expression ("a" + "b")."""
    parts = re.findall(r'"((?:[^"\\]|\\.)*)"', expr)
    s = "".join(parts)
    return s.replace('\\"', '"').replace("\\n", " ").replace("\\t", " ")


def _attr(body, name):
    """Extract attribute `name = ...` from an annotation body. Returns str, list or None."""
    m = re.search(r"\b" + name + r"\s*=\s*", body)
    if not m:
        return None
    rest = body[m.end():]
    if rest.startswith("{"):
        end = rest.find("}")
        return re.findall(r'"((?:[^"\\]|\\.)*)"', rest[:end])
    # value runs until next top-level ',' followed by an identifier '=' or end
    depth = 0
    in_str = False
    out = []
    for idx, c in enumerate(rest):
        if in_str:
            out.append(c)
            if c == '"' and rest[idx - 1] != "\\":
                in_str = False
            continue
        if c == '"':
            in_str = True
        elif c in "({":
            depth += 1
        elif c in ")}":
            depth -= 1
        elif c == "," and depth == 0 and re.match(r",\s*\w+\s*=", rest[idx:]):
            break
        out.append(c)
    expr = "".join(out)
    if '"' in expr:
        return _strings(expr)
    return expr.strip()


class NodetoolCommand:
    def __init__(self, name, description, cls, path):
        self.name = name
        self.description = description
        self.cls = cls
        self.path = path
        self.arguments = []   # (usage, description)
        self.options = []     # (names list, description, required)
        self.group = None
        self.deprecated = False
        self.hidden = False


def _class_bodies(text):
    """Yield (class_name, extends, body_start, body_end, decl_start) for each class."""
    for m in re.finditer(r"\bclass\s+(\w+)(?:\s+extends\s+([\w.]+))?[^{;]*\{", text):
        start = m.end() - 1
        depth = 0
        i = start
        while i < len(text):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        yield m.group(1), m.group(2), start, i, m.start()


def _direct_annotations(text, start, end, nested_ranges):
    """Annotations in text[start:end] that are not inside nested class bodies."""
    out = []
    for m in re.finditer(r"@(Option|Arguments)\s*\(", text[start:end]):
        pos = start + m.start()
        if any(a < pos < b for a, b in nested_ranges):
            continue
        body_end = _balanced(text, start + m.end() - 1)
        out.append((m.group(1), text[start + m.end():body_end - 1]))
    return out


def parse_nodetool(root):
    """Return (commands dict name->NodetoolCommand, global_options list, groups dict)."""
    tools_dir = os.path.join(root, "src/java/org/apache/cassandra/tools")
    classes = {}   # simple class name -> dict(text, path, start, end, extends, decl)
    for dirpath, _, files in os.walk(tools_dir):
        for fn in files:
            if not fn.endswith(".java"):
                continue
            path = os.path.join(dirpath, fn)
            with open(path, encoding="utf-8") as f:
                text = f.read()
            bodies = list(_class_bodies(text))
            for name, ext, s, e, decl in bodies:
                nested = [(s2, e2) for (n2, _, s2, e2, _) in bodies if s < s2 and e2 < e]
                info = dict(text=text, path=path, start=s, end=e, extends=ext, decl=decl, nested=nested)
                # Several files can declare a class with the same simple name (e.g. JMXTool.Info);
                # prefer the one in tools/nodetool/, which is where command classes live.
                if name not in classes or ("/tools/nodetool/" in path and "/tools/nodetool/" not in classes[name]["path"]):
                    classes[name] = info

    nodetool_java = os.path.join(tools_dir, "NodeTool.java")
    with open(nodetool_java, encoding="utf-8") as f:
        nt = f.read()

    # Registered top-level commands
    m = re.search(r"commands\s*=\s*newArrayList\((.*?)\);", nt, re.S)
    top = re.findall(r"([\w.]+)\.class", m.group(1)) if m else []
    # Groups
    groups = OrderedDict()
    for gm in re.finditer(r'withGroup\("([^"]+)"\)(.*?);', nt, re.S):
        gname = gm.group(1)
        gdesc = re.search(r'withDescription\("([^"]*)"\)', gm.group(2))
        members = re.findall(r"withCommand\(([\w.]+)\.class\)", gm.group(2))
        groups[gname] = (gdesc.group(1) if gdesc else "", members)

    def build(cls_ref, group=None):
        simple = cls_ref.split(".")[-1]
        info = classes.get(simple)
        if not info:
            return None
        text = info["text"]
        # @Command annotation directly before the class declaration
        head = text[:info["decl"]]
        cm = None
        for cm in re.finditer(r"@Command\s*\(", head):
            pass
        if not cm:
            return None
        cbody = text[cm.end():_balanced(text, cm.end() - 1) - 1]
        # make sure no other class declaration sits between annotation and decl
        if re.search(r"\bclass\s+\w+", text[cm.end():info["decl"]]):
            return None
        name = _attr(cbody, "name")
        desc = _attr(cbody, "description") or ""
        cmd = NodetoolCommand(name, desc, simple, info["path"])
        cmd.group = group
        cmd.hidden = (_attr(cbody, "hidden") or "").strip() == "true"
        # walk the inheritance chain (stop at NodeToolCmd)
        chain = []
        cur = simple
        seen = set()
        while cur and cur in classes and cur not in seen and cur not in ("NodeToolCmd",):
            seen.add(cur)
            chain.append(cur)
            ext = classes[cur]["extends"]
            cur = ext.split(".")[-1] if ext else None
        for c in chain:
            ci = classes[c]
            for kind, body in _direct_annotations(ci["text"], ci["start"], ci["end"], ci["nested"]):
                if kind == "Arguments":
                    cmd.arguments.append((_attr(body, "usage") or "", _attr(body, "description") or ""))
                else:
                    names = _attr(body, "name")
                    if isinstance(names, str):
                        names = [names]
                    cmd.options.append((names or [], _attr(body, "description") or "",
                                        (_attr(body, "required") or "").strip() == "true"))
            seg = ci["text"][ci["start"]:ci["end"]]
            if re.search(r"@Deprecated|is deprecated|deprecated,? use", seg, re.I) and c == simple:
                cmd.deprecated = True
        if re.search(r"deprecated", desc, re.I):
            cmd.deprecated = True
        return cmd

    commands = OrderedDict()
    for ref in top:
        cmd = build(ref)
        if cmd is None and ref.split(".")[-1] == "CassHelp":
            # CassHelp inherits its @Command from the airline library's Help class.
            cmd = NodetoolCommand("help", "Display help information (nodetool help <command>)",
                                  "CassHelp", nodetool_java)
        if cmd and cmd.name:
            commands[cmd.name] = cmd
    group_cmds = OrderedDict()
    for gname, (gdesc, members) in groups.items():
        for ref in members:
            cmd = build(ref, gname)
            if cmd and cmd.name:
                group_cmds[gname + " " + cmd.name] = cmd

    # Global options from NodeToolCmd
    global_opts = []
    gi = classes.get("NodeToolCmd")
    if gi:
        for kind, body in _direct_annotations(gi["text"], gi["start"], gi["end"], gi["nested"]):
            if kind == "Option":
                names = _attr(body, "name")
                if isinstance(names, str):
                    names = [names]
                global_opts.append((names or [], _attr(body, "description") or "", False))
    return commands, group_cmds, groups, global_opts
