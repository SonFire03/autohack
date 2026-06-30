# External Cheatsheets

AUTOHACK can load optional external cheatsheets from a local JSON directory.

## Default location

By default, the loader looks for:

```text
catalog/external_cheatsheets
```

You can override it with:

```bash
export AUTOHACK_EXTRA_CHEATSHEET_DIR=/path/to/cheatsheets
```

## Format

Each file must be JSON and contain either:

- a list of template objects
- a single template object
- or an object with a `templates` array

Required fields:

- `title`
- `category`
- `command`
- `description`

Optional fields:

- `key`
- `tags`

## Duplicate handling

The importer skips templates that duplicate an existing command or key.

## Policy handling

Each entry is passed through the local cheatsheet policy helper before import. Entries that conflict with the visible security policy are rejected.

## Import script

You can convert a JSON source into an AUTOHACK-compatible file with:

```bash
python3 scripts/import_cheatsheets.py path/to/source.json
```

Use `--dry-run` to preview the result and `--output` to choose the destination file.
