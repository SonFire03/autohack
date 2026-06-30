# Security Policy

AUTOHACK is a security lab command organizer for controlled environments.

## Supported use scope

Contributions and usage are expected to stay within:

- personal lab environments
- CTFs
- homelabs
- training and workshops
- authorized security assessments

## Not allowed

Do not contribute content, templates, workflows, or examples that are focused on:

- malware
- stealth or evasion
- malicious persistence
- credential theft
- unauthorized access
- post-exploitation abuse outside authorized environments

## Reporting security issues

If you find a security issue in the project itself, report it privately through the repository owner or the GitHub security workflow if available.

## Scope note

This repository documents and organizes commands. It does not grant permission to use those commands outside a lawful and authorized scope.

## Local data

AutoHack stores history, variables, loot, and approvals locally on the machine where it runs. This storage is convenient, but it is not an encrypted vault and must not be treated as a safe place for real secrets.

## Policy note

Sensitive commands are classified with explicit execution policies such as `lab_only` or `dry_run_only` to make review easier. Those policies reduce accidental misuse, but they do not replace operator authorization or judgment.
