# backup-tools

Scripts the ops team runs from cron on the file server.

- `bin/rotate.py DIR --keep N` deletes the oldest `*.tar.gz` archives in `DIR`
  so that exactly the newest `N` remain. Files that are not archives are never
  touched. `--dry-run` prints what would be deleted.
- `bin/nightly.sh` archives `/srv/share` into `/backups` and then rotates,
  keeping 14.

There are no automated tests yet.
