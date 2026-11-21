#!/usr/bin/env bash
# DOC: 02_data_modeling_and_indexing/*.md, 03_application_development/*.md, 09_reference/04_cql_quick_reference.md
# CLAIMS: SAI vs legacy index creation, SAI operator limits and analyzer options, ALLOW FILTERING,
#         ANN query rules, masking function output, DDM off by default, TTL limit, batch fail
#         threshold, table option defaults, grammar points (IF NOT EXISTS before USING, no BETWEEN).
set -uo pipefail
source "$(dirname "$0")/../scripts/lib.sh"
require_nodes cass1
IDX=02_data_modeling_and_indexing/02_indexing_and_vector_search.md
CQLREF=09_reference/04_cql_quick_reference.md
WR=03_application_development/01_performant_writes.md
DDM=03_application_development/04_consistency_and_transactions.md#5-dynamic-data-masking-ddm-new-in-50

# claim DOC_REF "description" ok|err|out "needle-or-empty" "CQL"
claim() {
  local ref="$1" desc="$2" expect="$3" needle="$4" q="$5" out rc
  out=$(cq $SEED "USE claims; $q" 2>&1); rc=$?
  case "$expect" in
    ok)  if [ $rc -eq 0 ] && ! grep -q 'Error' <<<"$out"; then pass "$ref" "$desc"; else fail "$ref" "$desc" "$out"; fi ;;
    err) if [ $rc -ne 0 ] || grep -q 'Error' <<<"$out"; then
           if [ -z "$needle" ] || grep -qiF -- "$needle" <<<"$out"; then pass "$ref" "$desc"; else fail "$ref" "$desc" "rejected, but without '$needle': $out"; fi
         else fail "$ref" "$desc" "expected an error, statement succeeded"; fi ;;
    out) if grep -qF -- "$needle" <<<"$out"; then pass "$ref" "$desc"; else fail "$ref" "$desc" "expected '$needle' in: $out"; fi ;;
  esac
}

cq $SEED "DROP KEYSPACE IF EXISTS claims;
  CREATE KEYSPACE claims WITH replication = {'class':'NetworkTopologyStrategy','dc1':3};
  CREATE TABLE claims.products (cat text, id int, brand text, price decimal, note text, tags set<text>, PRIMARY KEY ((cat), id));
  CREATE TABLE claims.docs (tenant text, id int, emb vector<float, 3>, PRIMARY KEY ((tenant), id));
  CREATE TABLE claims.pii (id int PRIMARY KEY, s text, l list<int>);
  INSERT INTO claims.products (cat,id,brand,price,note,tags) VALUES ('tv',1,'Sony',499.99,'n',{'wireless'});
  INSERT INTO claims.products (cat,id,brand,price,note,tags) VALUES ('tv',2,'LG',299.00,'n',{'wired'});
  INSERT INTO claims.pii (id, s, l) VALUES (1, '123-45-6789', [3,1,2]);" >/dev/null || { fail "setup" "create claims keyspace" "cqlsh failed"; exit 1; }

# --- indexes ---------------------------------------------------------------------------------
claim "$IDX#1" "plain CREATE INDEX builds a legacy 2i with the shipped yaml" ok "" \
  "CREATE INDEX legacy_note_idx ON products (note);"
claim "$IDX#1" "  ...system_schema shows kind COMPOSITES (legacy), not CUSTOM" out "COMPOSITES" \
  "SELECT kind FROM system_schema.indexes WHERE keyspace_name='claims' AND table_name='products' AND index_name='legacy_note_idx';"
claim "$IDX#1" "CREATE INDEX ... USING 'sai' with case_sensitive/normalize options" ok "" \
  "CREATE INDEX brand_idx ON products (brand) USING 'sai' WITH OPTIONS = {'case_sensitive': false, 'normalize': true};"
claim "$IDX#1" "  ...system_schema records it as an SAI index (class_name 'sai')" out "'class_name': 'sai'" \
  "SELECT options FROM system_schema.indexes WHERE keyspace_name='claims' AND table_name='products' AND index_name='brand_idx';"
claim "$IDX#1" "SAI numeric index supports range queries" ok "" \
  "CREATE INDEX price_idx ON products (price) USING 'sai';"
sleep 3
claim "$IDX#1" "  ...price <= 499.99 query runs without ALLOW FILTERING" out "(2 rows)" \
  "SELECT id FROM products WHERE price <= 499.99;"
claim "$IDX#1" "case_sensitive:false makes brand = 'sony' match 'Sony'" out "(1 rows)" \
  "SELECT id FROM products WHERE brand = 'sony';"
claim "$IDX#1" "SAI text index rejects range queries" err "" \
  "SELECT id FROM products WHERE brand > 'a';"
claim "$IDX#1" "collection index with values() supports CONTAINS" ok "" \
  "CREATE INDEX tags_idx ON products (values(tags)) USING 'sai';"
sleep 2
claim "$IDX#1" "  ...tags CONTAINS 'wireless' returns the row" out "(1 rows)" \
  "SELECT id FROM products WHERE cat='tv' AND tags CONTAINS 'wireless';"
claim "02_data_modeling_and_indexing/01_schema_design_patterns.md" "non-key, non-indexed filter requires ALLOW FILTERING" err "ALLOW FILTERING" \
  "SELECT * FROM pii WHERE s = 'x';"

# --- vectors ---------------------------------------------------------------------------------
claim "$IDX#2" "vector index with similarity_function COSINE" ok "" \
  "CREATE INDEX emb_idx ON docs (emb) USING 'sai' WITH OPTIONS = {'similarity_function': 'COSINE'};"
cq $SEED "INSERT INTO claims.docs (tenant,id,emb) VALUES ('a',1,[0.1,0.2,0.3]); INSERT INTO claims.docs (tenant,id,emb) VALUES ('a',2,[0.3,0.2,0.1]);" >/dev/null
sleep 2
claim "$IDX#4" "ANN OF with LIMIT 5 scoped to a partition works" out "(2 rows)" \
  "SELECT id, similarity_cosine(emb, [0.1,0.2,0.3]) FROM docs WHERE tenant='a' ORDER BY emb ANN OF [0.1,0.2,0.3] LIMIT 5;"
claim "$IDX#4" "ANN OF requires a LIMIT" err "" \
  "SELECT id FROM docs WHERE tenant='a' ORDER BY emb ANN OF [0.1,0.2,0.3];"
claim "$IDX#4" "ANN OF LIMIT above 1000 is rejected" err "" \
  "SELECT id FROM docs WHERE tenant='a' ORDER BY emb ANN OF [0.1,0.2,0.3] LIMIT 1001;"
claim "$IDX#3" "COSINE index rejects an all-zero vector" err "" \
  "INSERT INTO docs (tenant,id,emb) VALUES ('a',3,[0,0,0]);"
claim "$IDX#4" "a vector index doesn't support equality" err "" \
  "SELECT id FROM docs WHERE emb = [0.1,0.2,0.3];"

# --- masking ---------------------------------------------------------------------------------
claim "$DDM" "mask_default(text) returns ****" out "****" "SELECT mask_default(s) FROM pii WHERE id=1;"
claim "$DDM" "mask_inner keeps length: 123-45-6789 -> 1XXXXXXXXX9" out "1XXXXXXXXX9" \
  "SELECT mask_inner(s, 1, 1, 'X') FROM pii WHERE id=1;"
claim "$DDM" "MASKED WITH is rejected while dynamic_data_masking_enabled is false (default)" err "" \
  "CREATE TABLE masked_t (id int PRIMARY KEY, email text MASKED WITH DEFAULT);"

# --- writes ----------------------------------------------------------------------------------
claim "$WR#5" "TTL above 630720000 (20 years) is rejected" err "" \
  "INSERT INTO pii (id, s) VALUES (2, 'x') USING TTL 630720001;"
claim "$WR#5" "with storage_compatibility_mode CASSANDRA_4 (default), a TTL expiring after 2038-01-19 is rejected" err "2038" \
  "INSERT INTO pii (id, s) VALUES (3, 'x') USING TTL 630720000;"
claim "$WR#5" "a TTL expiring before 2038 is accepted" ok "" \
  "INSERT INTO pii (id, s) VALUES (4, 'x') USING TTL 31536000;"
big=$(head -c 60000 /dev/zero | tr '\0' 'a')
claim "$WR#2" "a batch above batch_size_fail_threshold (50KiB) is rejected" err "" \
  "BEGIN BATCH INSERT INTO pii (id, s) VALUES (10, '$big'); INSERT INTO pii (id, s) VALUES (11, 'x'); APPLY BATCH;"
claim "$CQLREF" "INSERT ... IF NOT EXISTS USING TTL (IF before USING) parses" ok "" \
  "INSERT INTO pii (id, s) VALUES (20, 'x') IF NOT EXISTS USING TTL 60;"
claim "$CQLREF" "DELETE accepts only USING TIMESTAMP (USING TTL rejected)" err "" \
  "DELETE FROM pii USING TTL 10 WHERE id = 20;"

# --- grammar & functions ---------------------------------------------------------------------
claim "$CQLREF" "BETWEEN doesn't exist in 5.0" err "" "SELECT * FROM pii WHERE id BETWEEN 1 AND 3;"
claim "$CQLREF" "!= is not allowed in WHERE" err "" "SELECT * FROM pii WHERE id != 1;"
claim "$CQLREF" "5.0 collection function collection_count exists" out "3" "SELECT collection_count(l) FROM pii WHERE id=1;"
claim "$CQLREF" "5.0 math function abs exists" ok "" "SELECT abs(id) FROM pii WHERE id=1;"
claim "$CQLREF" "dateOf() was removed" err "" "SELECT dateOf(now()) FROM pii WHERE id=1;"

# --- table option defaults -------------------------------------------------------------------
claim "$CQLREF" "default gc_grace_seconds is 864000" out "864000" \
  "SELECT gc_grace_seconds FROM system_schema.tables WHERE keyspace_name='claims' AND table_name='pii';"
claim "$CQLREF" "default compaction is SizeTieredCompactionStrategy (shipped yaml)" out "SizeTieredCompactionStrategy" \
  "SELECT compaction FROM system_schema.tables WHERE keyspace_name='claims' AND table_name='pii';"
claim "$CQLREF" "default speculative_retry prints as 99p" out "99p" \
  "SELECT speculative_retry FROM system_schema.tables WHERE keyspace_name='claims' AND table_name='pii';"
claim "$CQLREF" "default bloom_filter_fp_chance is 0.01" out "0.01" \
  "SELECT bloom_filter_fp_chance FROM system_schema.tables WHERE keyspace_name='claims' AND table_name='pii';"
