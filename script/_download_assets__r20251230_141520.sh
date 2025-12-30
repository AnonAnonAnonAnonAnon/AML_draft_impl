#!/usr/bin/env bash
set -e

# Safe wrapper of `script/_download_assets.sh`:
# - avoids `rm -rf` deletions (keeps downloaded zip artifacts)
# - otherwise keeps the original behavior

cd assets
python _download.py

# background_texture
unzip background_texture.zip

# embodiments
unzip embodiments.zip

# objects
unzip objects.zip

cd ..
echo "Configuring Path ..."
python ./script/update_embodiment_config_path.py

