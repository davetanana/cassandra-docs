YAML fragments in this folder are mounted read-only at `/test_config` in every node.
Use `apply_yaml <node> <file>` (scripts/lib.sh) to append one to a node's cassandra.yaml, and only for keys that are commented out by default, such as `auto_repair:`.
For top-level scalar keys, use `set_yaml <node> <key> <value>` instead. Restart the node (`restart_node`) to apply either.
