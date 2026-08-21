#!/usr/bin/env python3
"""Audit repository cleanliness for publication readiness.

Checks for:
1. Absolute local paths (C:\\Users, C:/Users, Antigravity, Gemini, Desktop, Downloads)
2. Stale references (HPMCAS, Eudragit L100, POL-003, POL-004) in active non-archive files
3. Security/secrets (API keys, passwords, tokens)
4. Overstated claims ('guaranteed', 'proven', 'industry validated', etc.)
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()

IGNORE_DIRS = {
    ".git",
    "archive",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    "dist",
}

IGNORE_EXTENSIONS = {
    ".pyc",
    ".png",
    ".pdf",
    ".db",
    ".sqlite",
    ".jpg",
    ".jpeg",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
}


def should_skip(path: Path) -> bool:
    for part in path.parts:
        if part in IGNORE_DIRS:
            return True
    if path.suffix.lower() in IGNORE_EXTENSIONS:
        return True
    return False


def run_cleanliness_audit():
    print("=" * 60)
    print("PUBLICATION REPOSITORY CLEANLINESS AUDIT")
    print("=" * 60)

    # 1. Absolute local paths
    local_path_patterns = [
        ("Windows User Path", re.compile(r"[a-zA-Z]:[\\/]Users[\\/]", re.IGNORECASE)),
        ("Antigravity Keyword", re.compile(r"\bantigravity\b", re.IGNORECASE)),
        ("Gemini Keyword", re.compile(r"\bgemini\b", re.IGNORECASE)),
        ("Desktop Path", re.compile(r"Desktop[\\/]", re.IGNORECASE)),
        ("Downloads Path", re.compile(r"Downloads[\\/]", re.IGNORECASE)),
    ]

    path_issues = []
    stale_issues = []
    secret_issues = []
    claim_issues = []

    stale_patterns = [
        ("HPMCAS", re.compile(r"\bHPMCAS\b", re.IGNORECASE)),
        ("Eudragit L100", re.compile(r"\bEudragit\s+L100\b", re.IGNORECASE)),
        ("POL-003", re.compile(r"\bPOL-003\b", re.IGNORECASE)),
        ("POL-004", re.compile(r"\bPOL-004\b", re.IGNORECASE)),
    ]

    secret_patterns = [
        ("API Key Pattern", re.compile(r"(?:api_key|apikey|secret_key|access_token|password)\s*[:=]\s*['\"][a-zA-Z0-9_\-]{8,}['\"]", re.IGNORECASE)),
        ("Generic Secret", re.compile(r"(?:BEGIN RSA PRIVATE KEY|BEGIN PRIVATE KEY)", re.IGNORECASE)),
    ]

    claim_patterns = [
        ("Overstated 'guaranteed'", re.compile(r"\bguaranteed\b", re.IGNORECASE)),
        ("Overstated 'industry validated'", re.compile(r"\bindustry\s+validated\b", re.IGNORECASE)),
        ("Overstated '100% accuracy'", re.compile(r"\b100%\s+accuracy\b", re.IGNORECASE)),
        ("Overstated 'proven polymer'", re.compile(r"\bproven\s+polymer\b", re.IGNORECASE)),
    ]

    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Prune ignored directories in-place
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            p = Path(root) / file
            if should_skip(p):
                continue

            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            rel_path = str(p.relative_to(PROJECT_ROOT))


        # Check local paths
        for name, pat in local_path_patterns:
            for line_no, line in enumerate(text.splitlines(), 1):
                if pat.search(line):
                    path_issues.append((rel_path, line_no, name, line.strip()[:100]))

        # Check stale content (excluding historical/explanatory documentation)
        # Docs that legitimately explain historical exclusion: source_of_truth, changelog, README, pre_cleanup
        allowed_stale_docs = {
            "docs/source_of_truth.md",
            "docs/study_overview.md",
            "docs/pre_cleanup_dependency_audit.md",
            "CHANGELOG.md",
            "README.md",
            "scripts/audit_repository_cleanliness.py",
            "scripts/validate_final_dataset.py",
        }
        if rel_path.replace("\\", "/") not in allowed_stale_docs:
            for name, pat in stale_patterns:
                for line_no, line in enumerate(text.splitlines(), 1):
                    if pat.search(line):
                        stale_issues.append((rel_path, line_no, name, line.strip()[:100]))

        # Check secrets
        for name, pat in secret_patterns:
            for line_no, line in enumerate(text.splitlines(), 1):
                if pat.search(line):
                    secret_issues.append((rel_path, line_no, name, line.strip()[:100]))

        # Check claims
        for name, pat in claim_patterns:
            for line_no, line in enumerate(text.splitlines(), 1):
                if pat.search(line):
                    claim_issues.append((rel_path, line_no, name, line.strip()[:100]))

    print(f"\n1. Local Path Check: {len(path_issues)} findings")
    for f, l, n, s in path_issues:
        print(f"   [{n}] {f}:{l} -> {s}")

    print(f"\n2. Stale Content Check (in active pipeline): {len(stale_issues)} findings")
    for f, l, n, s in stale_issues:
        print(f"   [{n}] {f}:{l} -> {s}")

    print(f"\n3. Secrets / Privacy Check: {len(secret_issues)} findings")
    for f, l, n, s in secret_issues:
        print(f"   [{n}] {f}:{l} -> {s}")

    print(f"\n4. Overstated Claims Check: {len(claim_issues)} findings")
    for f, l, n, s in claim_issues:
        print(f"   [{n}] {f}:{l} -> {s}")

    print("\n" + "=" * 60)
    total_issues = len(path_issues) + len(stale_issues) + len(secret_issues) + len(claim_issues)
    if total_issues == 0:
        print("ALL CLEANLINESS AUDITS PASSED CLEANLY (0 ISSUES)")
    else:
        print(f"TOTAL FINDINGS TO REVIEW/RESOLVE: {total_issues}")
    print("=" * 60)


if __name__ == "__main__":
    run_cleanliness_audit()
