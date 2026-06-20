# Hardening Notes

The default behavior of AUTOHACK remains compatible with the current project.

If you want a stricter local setup, use an optional profile or a manual config file override rather than changing defaults globally.

## Example hardening profile

```json
{
  "strict_shell_mode": true,
  "enforce_command_allowlist": true,
  "require_secondary_approval": true,
  "enforce_catalog_signature": true,
  "command_timeout": 20,
  "redact_secrets_in_logs": true
}
```

## Suggested workflow

- apply the profile only on a machine or environment where you control the scope
- keep the default profile unchanged for compatibility
- use `autohack admin security-status` to review the current local state before a run

This document is informational only and does not change runtime defaults.
