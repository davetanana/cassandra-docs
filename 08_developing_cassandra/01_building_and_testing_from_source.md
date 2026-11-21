# Building, Running & Testing Cassandra from Source

This page is for engineers working **on** the Apache Cassandra source ([apache/cassandra](https://github.com/apache/cassandra), `cassandra-5.0` branch, currently `5.0.10` per `base.version` in `build.xml`) rather than running a packaged release. For the contribution process (JIRA, branch naming, CI artifacts), read [`CONTRIBUTING.md`](https://github.com/apache/cassandra/blob/cassandra-5.0/CONTRIBUTING.md). For what and how to test, read [`TESTING.md`](https://github.com/apache/cassandra/blob/cassandra-5.0/TESTING.md).

---

## 1. Prerequisites

| Tool | Requirement | Where it is enforced |
| :--- | :--- | :--- |
| JDK | **11 or 17** (`java.supported=11,17`; the default build JDK is 11) | `build.xml` fails with "Unsupported JDK version used". Using 17 prints "Non default JDK version used". |
| Apache Ant | **1.10 or later** | `<antversion atleast="1.10"/>` in `build.xml` |
| Python | 3.8–3.13 for `bin/cqlsh` | `is_supported_version()` in `bin/cqlsh` |
| Docker (optional) | For the `.build/docker/*` scripts that CI uses | [`.build/README.md`](https://github.com/apache/cassandra/blob/cassandra-5.0/.build/README.md) |

**Choosing the JDK**: the build compiles for whichever JDK Ant runs on (`source`/`target` = `${ant.java.version}`). Point `JAVA_HOME` at the JDK you want before running `ant`:

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 17)   # macOS example
ant -version && java -version
```

Run `ant realclean` when you switch JDKs, so that classes compiled for one JDK aren't mixed with the other.

---

## 2. Building

```bash
ant jar          # compile and produce build/apache-cassandra-<version>-SNAPSHOT.jar plus the tools jars
ant build        # compile classes only
ant clean        # remove build output; realclean also removes downloaded dependencies
ant check        # licence (RAT) and checkstyle checks; the same as GitHub Actions
```

> [!NOTE]
> Running plain `ant` with no target runs **`check`** (`default="check"` in `build.xml`), not a build.

`ant -p` lists every target. The CI-equivalent wrappers are in `.build/` and accept `-h`:

```bash
.build/build-jars.sh                  # build without docker
.build/docker/build-jars.sh 17        # build in docker with JDK 17
.build/docker/build-artifacts.sh      # tarballs and maven artifacts
.build/docker/build-debian.sh         # .deb (packaging only works in docker)
.build/docker/build-redhat.sh         # .rpm
```

---

## 3. Running a Local Node from the Source Tree

`bin/cassandra.in.sh` looks for `build/apache-cassandra*.jar`, so run `ant jar` first:

```bash
ant jar
bin/cassandra -f                     # run in the foreground, logging to stdout; Ctrl-C to stop
bin/nodetool status
bin/cqlsh                            # connects to localhost:9042
```

* With the shipped `conf/cassandra.yaml`, data, commit logs and logs go under `$CASSANDRA_HOME/data` and `$CASSANDRA_HOME/logs` in the checkout.
* To try the 5.0 feature set: `bin/cassandra -f -Dcassandra.config=file://$PWD/conf/cassandra_latest.yaml`.
* For multi-node clusters on one machine, the community uses [ccm](https://github.com/apache/cassandra-ccm) (not part of the Cassandra repository). The Python dtests rely on it.
* IDE setup: `ant generate-idea-files` (IntelliJ; templates are in `ide/idea`) or `ant generate-eclipse-files`.

---

## 4. Running Tests

### Unit tests (JUnit, `test/unit`)
```bash
ant test                                                     # all unit tests (slow: hours)
ant testsome -Dtest.name=org.apache.cassandra.db.compaction.CompactionsTest
ant testsome -Dtest.name=org.apache.cassandra.db.compaction.CompactionsTest -Dtest.methods=testSingleSSTableCompaction
ant cql-test-some -Dtest.name=<CQLTesterSubclass> -Dtest.methods=<method>
```

Variant suites run the same tests with different configurations: `test-latest` (`cassandra_latest.yaml`), `test-compression`, `test-cdc`, `test-oa`, `test-system-keyspace-directory`.

### In-JVM distributed tests (`test/distributed`)
These start several Cassandra instances inside one JVM, so you can test multi-node behavior without Docker or ccm:

```bash
ant test-jvm-dtest-some -Dtest.name=org.apache.cassandra.distributed.test.SimpleReadWriteTest
ant test-jvm-dtest                       # the whole suite
ant test-jvm-upgrade-dtest               # upgrade tests (need the dtest jars of older versions)
```

### The CI-equivalent scripts
```bash
.build/docker/run-tests.sh -a test -t "Compaction*Test$" -j 17     # unit tests matching a regex, on JDK 17
.build/docker/run-tests.sh -a test -c 1/64                         # one split of 64
.build/docker/run-tests.sh -a jvm-dtest -t SimpleReadWriteTest
.build/run-tests.sh -a jvm-dtest-repeat -t BooleanTest -e REPEATED_TESTS_COUNT=20   # flakiness hunting
.build/run-python-dtests.sh dtest                                  # python dtests (apache/cassandra-dtest)
```

Other suites: `long-test`, `test-burn`, `stress-test`, `fqltool-test`, `cqlsh-test` (`pylib/cassandra-cqlsh-tests.sh`), and `microbench` (JMH, `test/microbench`). Before you submit a patch, run the pre-commit CI with `.build/run-ci` and attach the results to the JIRA ticket (see `CONTRIBUTING.md`).

> [!NOTE]
> `CONTRIBUTING.md` has a section on git submodules (`modules/accord`). It applies to trunk. This branch has no `.gitmodules` file or `modules/` directory, so skip that section here.

---

## 5. Repository Layout

| Path | Contents |
| :--- | :--- |
| `src/java/org/apache/cassandra/` | The server. Important packages: `db/` (storage engine, memtables, compaction), `io/sstable/` (BIG and BTI formats), `index/sai/` (SAI and vector search), `service/` (coordination, Paxos), `locator/` (snitches, replication), `net/` (internode messaging), `transport/` (native protocol), `cql3/` (CQL), `auth/`, `repair/`, `tools/` (nodetool and offline tools). |
| `src/antlr/` | The CQL grammar (`Lexer.g`, `Parser.g`). |
| `src/resources/` | Resources bundled into the jar. |
| `conf/` | `cassandra.yaml`, `cassandra_latest.yaml`, `jvm*-server.options`, `cassandra-env.sh`, `logback.xml`, `cassandra-rackdc.properties`, `commitlog_archiving.properties`. |
| `bin/` | `cassandra`, `nodetool`, `cqlsh`, `sstableloader`, and the `sstable{scrub,upgrade,util,verify}` tools. |
| `tools/` | `cassandra-stress`, `fqltool`, and `tools/bin/` (`sstabledump`, `sstablemetadata`, `sstablepartitions`, `sstableexpiredblockers`, `auditlogviewer`, `jmxtool`, `generatetokens`, `hash_password`, ...). |
| `pylib/` | `cqlshlib`, the Python implementation of cqlsh, and its tests. |
| `test/` | `unit/`, `distributed/` (in-JVM dtests), `long/`, `burn/`, `memory/`, `microbench/`, `simulator/`, `conf/`, `data/` (test fixtures). |
| `doc/` | The official AsciiDoc documentation source (`doc/modules/cassandra/pages`) and the native protocol specs (`native_protocol_v*.spec`). |
| `debian/`, `redhat/` | Packaging. The Debian package uses a SysV `debian/init` script. |
| `.build/` | Build, test, packaging and CI scripts. |
| `NEWS.txt`, `CHANGES.txt` | Upgrade notes and the changelog for each release. **Read `NEWS.txt` before every upgrade.** |
| Design notes next to the code | `src/java/org/apache/cassandra/db/compaction/UnifiedCompactionStrategy.md`, `db/memtable/Memtable_API.md`, `io/sstable/SSTable_API.md`, `index/sai/README.md`. |

---

## 6. How This Guide Relates to the Official Docs

| | `doc/modules/cassandra/pages/` (official) | This guide |
| :--- | :--- | :--- |
| Format | AsciiDoc, built into cassandra.apache.org by Antora via the [cassandra-website](https://github.com/apache/cassandra-website) repo | Markdown, readable directly on GitHub or in an IDE |
| Scope | Reference material: every config option, nodetool command and CQL statement | Opinionated, lifecycle-ordered guidance and runbooks |
| Generated parts | `ant gen-asciidoc` generates the `cassandra.yaml` and nodetool reference pages from the source | The `cassandra.yaml` and nodetool references in [`09_reference/`](../09_reference/) are generated from a source checkout by [`tools/`](../tools/README.md). Everything else is hand-written; [`tools/check_docs.py`](../tools/README.md) catches renamed keys, commands and flags, and [`test_env/`](../test_env/README.md) checks behavior on a live cluster |
| Validation | Reviewed with code changes in the same repository | Checked against the source and a Docker cluster for each 5.0.x release |

When the two disagree, the **code and `conf/*.yaml` comments win**, then `NEWS.txt`, then the official docs. If you contribute a patch to Apache Cassandra that changes a default, an option name or nodetool behavior, update the official `doc/` pages in that patch, and open an issue or pull request against this guide as well.
