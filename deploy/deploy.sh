
pkg=$( cd "$(dirname "${BASH_SOURCE[0]}")/.." ; pwd -P )
echo 'running standalone module deployment script'

# check that stickytape is installed
if ! [ -x "$(command -v stickytape)" ]; then
    echo 'error: "stickytape" not installed; deployment failed'
    exit 1
fi

# create standalone files for all models

echo 'creating association model standalone script'
stickytape "${pkg}/scripts/knowledge/model/association/__main__.py" \
    --add-python-path "${pkg}/scripts/" \
    --output-file "${pkg}/deploy/association_standalone.py"