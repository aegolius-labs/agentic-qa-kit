#!/usr/bin/env bash
set -euo pipefail
stamp=$(date +%Y%m%d)
tar -czf "/backups/share-$stamp.tar.gz" -C /srv share
"$(dirname "$0")/rotate.py" /backups --keep 14
