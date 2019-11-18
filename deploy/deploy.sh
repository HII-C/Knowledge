
# check that stickytape is installed

if ! [ -x "$(command -v stickytape)" ]; then
    echo 'error: "stickytape" not installed; deployment failed'
    exit 1
fi

# create standalone files for all models

stickytape scripts/knowledge/model/association/__main__.py \
    --add-python-path scripts/ \
    --output-file deploy/association_standalone.py \