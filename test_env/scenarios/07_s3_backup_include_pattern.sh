#!/usr/bin/env bash
# DOC: 06_operations_and_housekeeping/02_housekeeping_and_automations.md (section 3), 04_infrastructure_and_cloud/02_aws_deployment_guide.md (section 6)
# CLAIMS: the documented `aws s3 sync --exclude "*" --include "*/snapshots/${TAG}/*"` uploads ONLY the
#         current tag (not older snapshots), including schema.cql and manifest.json. Uses Adobe S3Mock as S3.
set -uo pipefail
source "$(dirname "$0")/../scripts/lib.sh"
require_nodes cass1
HK=06_operations_and_housekeeping/02_housekeeping_and_automations.md#3
AWS_IMAGE="${AWS_CLI_IMAGE:-amazon/aws-cli:2.42.1}"   # older CLIs (2.15, 2.27) fail against S3Mock with "Connection was closed"
aws_() { docker run --rm --network cassdocs_cassnet -v cassdocs_cass1-data:/var/lib/cassandra:ro \
           -e AWS_ACCESS_KEY_ID=testkey -e AWS_SECRET_ACCESS_KEY=testsecret -e AWS_DEFAULT_REGION=us-east-1 -e AWS_REQUEST_CHECKSUM_CALCULATION=when_required -e AWS_RESPONSE_CHECKSUM_VALIDATION=when_required \
           "$AWS_IMAGE" --endpoint-url http://172.30.0.40:9090 "$@"; }

"${COMPOSE[@]}" --profile s3 up -d s3 >/dev/null 2>&1
for i in $(seq 1 30); do aws_ s3 ls >/dev/null 2>&1 && break; sleep 2; done
aws_ s3 mb s3://backups >/dev/null 2>&1 || true

make_test_table bkks events 20
TAG="backup_$(date +%Y%m%d_%H%M%S)"
nt cass1 snapshot -t old_manual_snapshot bkks >/dev/null
nt cass1 snapshot -t "$TAG" bkks >/dev/null

# The exact command shape from the housekeeping backup script
check_ok "$HK" "aws s3 sync with the documented include pattern" \
  aws_ s3 sync /var/lib/cassandra/data/ "s3://backups/cass1/$TAG/data/" --exclude "*" --include "*/snapshots/${TAG}/*" --only-show-errors
keys=$(aws_ s3 ls --recursive "s3://backups/cass1/$TAG/" 2>&1)
total=$(grep -c . <<<"$keys")
if [ "$total" -gt 0 ] && [ "$(grep -c "/snapshots/$TAG/" <<<"$keys")" = "$total" ]; then
  pass "$HK" "only the current tag was uploaded ($total objects)"
else fail "$HK" "only the current tag was uploaded" "$keys"; fi
if grep -q old_manual_snapshot <<<"$keys"; then fail "$HK" "older snapshots are not uploaded" "found old_manual_snapshot"
else pass "$HK" "older snapshots are not uploaded"; fi
check_contains "$HK" "schema.cql is included in the upload" "schema.cql" echo "$keys"
check_contains "$HK" "manifest.json is included in the upload" "manifest.json" echo "$keys"

nt cass1 clearsnapshot -t "$TAG" >/dev/null; nt cass1 clearsnapshot -t old_manual_snapshot >/dev/null
"${COMPOSE[@]}" --profile s3 stop s3 >/dev/null 2>&1
