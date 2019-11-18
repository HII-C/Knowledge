pkg=$( cd "$(dirname "${BASH_SOURCE[0]}")/../../.." ; pwd -P )

python deploy/association_standalone.py \
    --config "${pkg}/run/apiv1/find_associations.json"
    --sepcs "${pkg}/scripts/knowledge/model/association/specs.json"
    --pkg false