pkg=$( cd "$(dirname "${BASH_SOURCE[0]}")/../../.." ; pwd -P )

conda activate hiic

python -m knowledge.model.association \
    --config "${pkg}/run/apiv1/association/build_tree.json"