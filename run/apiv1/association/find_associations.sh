
pkg=$( cd "$(dirname "${BASH_SOURCE[0]}")/../../.." ; pwd -P )

echo "${pkg}"

python3 "${pkg}/deploy/association_standalone.py" \
    --config "${pkg}/run/apiv1/association/find_associations.json" \
    --specs "${pkg}/scripts/knowledge/model/association/specs.json" \
    --pkg false