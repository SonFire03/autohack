"""Policy helpers for adapting external cheatsheets to AUTOHACK's scope."""

from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class CheatsheetAssessment:
    policy: str
    reasons: tuple[str, ...] = ()

    @property
    def allowed(self) -> bool:
        return self.policy != "blocked"


_BLOCKED_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bmalware\b", re.I), "malware"),
    (re.compile(r"\b(ransomware|botnet|keylogger|backdoor)\b", re.I), "malicious payloads"),
    (re.compile(r"\bstealth\b|\bevasion\b|\bundetected\b", re.I), "stealth or evasion"),
    (re.compile(r"\bpersistence\b|\bpersist(ence)?\b", re.I), "malicious persistence"),
    (re.compile(r"\bcredential theft\b|\bsteal credentials?\b|\btoken theft\b", re.I), "credential theft"),
    (re.compile(r"\bphishing\b", re.I), "phishing"),
    (re.compile(r"\bexfiltrat(e|ion)\b", re.I), "exfiltration"),
    (re.compile(r"\bunauthori[sz]ed\b", re.I), "unauthorized use"),
)

_LAB_ONLY_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bexploit\b|\bexploitation\b", re.I), "exploit-oriented content"),
    (re.compile(r"\bpayload\b", re.I), "payload-oriented content"),
    (re.compile(r"\bcredential\b|\bpassword spraying\b|\bspraying\b", re.I), "credential-oriented content"),
    (re.compile(r"\bpivot\b|\bpost-exploitation\b|\bprivesc\b", re.I), "post-exploitation workflow"),
    (re.compile(r"\bbypass\b|\belevat(e|ion)\b", re.I), "bypass or elevation workflow"),
    (re.compile(r"\battack\b", re.I), "attack-oriented wording"),
)


def _combined_text(*parts: object) -> str:
    return " ".join(str(part) for part in parts if part is not None).strip()


def assess_cheatsheet(title: str, description: str = "", command: str = "", tags: tuple[str, ...] = ()) -> CheatsheetAssessment:
    """Classify an external cheatsheet against the project's visible security policy."""
    text = _combined_text(title, description, command, " ".join(tags))
    reasons: list[str] = []
    for pattern, reason in _BLOCKED_PATTERNS:
        if pattern.search(text):
            reasons.append(reason)
    if reasons:
        return CheatsheetAssessment(policy="blocked", reasons=tuple(sorted(set(reasons))))

    lab_reasons: list[str] = []
    for pattern, reason in _LAB_ONLY_PATTERNS:
        if pattern.search(text):
            lab_reasons.append(reason)
    if lab_reasons:
        return CheatsheetAssessment(policy="lab_only", reasons=tuple(sorted(set(lab_reasons))))

    return CheatsheetAssessment(policy="safe")


def sanitize_cheatsheet_entry(entry: dict[str, object]) -> dict[str, object]:
    """Return a normalized cheatsheet entry or raise when it conflicts with policy."""
    title = str(entry.get("title", "")).strip()
    description = str(entry.get("description", "")).strip()
    command = str(entry.get("command", "")).strip()
    tags = tuple(str(tag) for tag in entry.get("tags", []) if tag is not None)  # type: ignore[arg-type]
    assessment = assess_cheatsheet(title, description, command, tags)
    if not title or not command:
        raise ValueError("cheatsheet entry requires title and command")
    if assessment.policy == "blocked":
        reasons = ", ".join(assessment.reasons) or "policy conflict"
        raise ValueError(f"cheatsheet entry blocked: {reasons}")
    normalized = dict(entry)
    normalized["title"] = title
    normalized["description"] = description
    normalized["command"] = command
    normalized["tags"] = list(tags)
    normalized["policy"] = assessment.policy
    normalized["policy_reasons"] = list(assessment.reasons)
    return normalized
