# Cheatsheet Policy Adaptation

This project can consume or adapt external cheatsheets only when they fit the visible security scope of AUTOHACK.

## Allowed scope

- personal lab environments
- CTFs
- homelabs
- training and workshops
- authorized security assessments

## What to remove or reject

Cheatsheets focused on any of the following should be rejected or rewritten:

- malware
- stealth or evasion
- malicious persistence
- credential theft
- phishing
- unauthorized use
- exfiltration outside an authorized scope

## What to keep

Keep the useful parts:

- command structure
- arguments and defaults
- tags and categories
- prerequisites
- short usage notes
- safe context notes

## Recommended adaptation

1. Rename the sheet around audit, review, or lab usage.
2. Add a policy label such as `safe` or `lab_only`.
3. Remove any wording that suggests concealment or abuse.
4. Keep only transparent, reviewable steps.
5. Run the entry through the local policy helper before import.

## Policy helper

The repository now includes a small helper that can classify external cheatsheets and reject entries that conflict with the published policy.

