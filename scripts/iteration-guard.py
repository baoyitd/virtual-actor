#!/usr/bin/env python3
"""Check virtual-actor iteration dossier and delivery evidence alignment."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

ALLOWED_STATUSES = {"Draft", "Self-Tested", "User-Acceptance-Candidate", "Accepted"}
INTERFACE_DELTA_STATUSES = {
    "No Public Interface Change",
    "Public Interface Change",
    "Pending Adjudication",
    "Not Applicable",
}

DELIVERY_DOCS = [
    "delivery/test-plan.md",
    "delivery/test-results.md",
    "delivery/release-notes.md",
]
PORTFOLIO_DOC = "portfolio-sync.md"
REQUIRED_PROCESS_FILES = [
    "docs/process/product-iteration-control.md",
    "docs/process/rule-changelog.md",
    "docs/process/issue-and-optimization-log.md",
    "docs/process/quality-toolchain.md",
]
REQUIRED_TEMPLATE_FILES = [
    "docs/iterations/_template/scope.md",
    "docs/iterations/_template/design-delta.md",
    "docs/iterations/_template/implementation-notes.md",
    "docs/iterations/_template/traceability.md",
]
REQUIRED_DOSSIER_FILES = [
    "scope.md",
    "design-delta.md",
    "implementation-notes.md",
    "traceability.md",
]
HIGH_RISK_DOCS = [
    "delivery/test-plan.md",
    "delivery/test-results.md",
    "delivery/release-notes.md",
    "portfolio-sync.md",
    "docs/process/product-iteration-control.md",
    "docs/iterations/v0.3.0-commercial-trial/scope.md",
]

RE_VERSION = re.compile(r"^(?:>\s*)?版本[:：]\s*([^|\n]+)", re.MULTILINE)
RE_CURRENT_STATUS = re.compile(r"当前状态[:：]\s*`?([^`|\n]+?)`?(?:\s*[|]|$)", re.MULTILINE)
RE_FORMAL_STATUS = re.compile(r"^(?:>\s*)?Formal Status[:：]\s*`?([^`\n]+?)`?\s*$", re.MULTILINE)
RE_INTERFACE_STATUS = re.compile(r"状态[:：]\s*`?([^`\n]+?)`?\s*$", re.MULTILINE)


@dataclass(frozen=True)
class Metadata:
    version: str | None = None
    status: str | None = None


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def clean_value(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip().strip("*").strip("`").strip()


def extract_metadata(path: Path) -> Metadata:
    text = read_text(path)
    version = clean_value(RE_VERSION.search(text).group(1) if RE_VERSION.search(text) else None)
    status_match = RE_FORMAL_STATUS.search(text) or RE_CURRENT_STATUS.search(text)
    status = clean_value(status_match.group(1) if status_match else None)
    return Metadata(version=version, status=status)


def extract_interface_delta(text: str) -> str | None:
    marker = "## Interface Delta"
    start = text.find(marker)
    if start == -1:
        return None
    rest = text[start + len(marker) :]
    next_heading = rest.find("\n## ")
    section = rest if next_heading == -1 else rest[:next_heading]
    match = RE_INTERFACE_STATUS.search(section)
    return clean_value(match.group(1) if match else None)


def dossier_status(repo_root: Path, version: str) -> str | None:
    scope_path = repo_root / "docs" / "iterations" / version / "scope.md"
    if not scope_path.exists():
        return None
    return extract_metadata(scope_path).status


def check_dossier(repo_root: Path, version: str, label: str, errors: list[str]) -> None:
    dossier_dir = repo_root / "docs" / "iterations" / version
    if not dossier_dir.exists():
        errors.append(f"Missing {label} dossier dir: docs/iterations/{version}")
        return

    for name in REQUIRED_DOSSIER_FILES:
        if not (dossier_dir / name).exists():
            errors.append(f"Missing {label} dossier file: docs/iterations/{version}/{name}")

    scope_path = dossier_dir / "scope.md"
    if scope_path.exists():
        scope_text = read_text(scope_path)
        if "Scope In" not in scope_text or "Scope Out" not in scope_text:
            errors.append(f"Scope markers missing in {label} dossier: {scope_path.relative_to(repo_root)}")
        status = dossier_status(repo_root, version)
        if status not in ALLOWED_STATUSES:
            errors.append(f"Invalid Formal Status in {scope_path.relative_to(repo_root)}: {status}")

    trace_path = dossier_dir / "traceability.md"
    if trace_path.exists() and "| US-" not in read_text(trace_path):
        errors.append(f"Traceability rows missing in {label} dossier: {trace_path.relative_to(repo_root)}")


def has_negation(line: str) -> bool:
    markers = ["不", "未", "不得", "不能", "不应", "不外推", "不冻结", "暂不", "Scope Out", "非", "不是", "无"]
    return any(marker in line for marker in markers)


def check_overclaims(repo_root: Path, errors: list[str]) -> None:
    risky_patterns = [
        ("long-term frozen dependency", re.compile(r"长期冻结公共契约版本|稳定可冻结依赖版本|冻结依赖版本")),
        ("complete final signoff overclaim", re.compile(r"完整最终用户签收版本|上线完成版本|整体产品已(?:全部)?上线完成")),
        ("decision product integration overclaim", re.compile(r"决策产品.*(已完成|已接入|已集成|可消费|依赖已冻结)")),
    ]
    fixture_pattern = re.compile(r"(mock|stub|static fixture|manual fixture|fixture).{0,40}(real integration|真实集成)", re.IGNORECASE)

    for rel in HIGH_RISK_DOCS:
        path = repo_root / rel
        if not path.exists():
            continue
        for line_no, line in enumerate(read_text(path).splitlines(), start=1):
            for label, pattern in risky_patterns:
                if pattern.search(line) and not has_negation(line):
                    errors.append(f"Overclaim risk in {rel}:{line_no} ({label}): {line.strip()}")
            if fixture_pattern.search(line) and not has_negation(line):
                errors.append(f"Fixture/mock real-integration risk in {rel}:{line_no}: {line.strip()}")


def check_accepted_evidence(repo_root: Path, errors: list[str]) -> None:
    results_path = repo_root / "delivery" / "test-results.md"
    if not results_path.exists():
        errors.append("Accepted release requires delivery/test-results.md")
        return
    text = read_text(results_path)
    if "人工手动冒烟" not in text:
        errors.append("Accepted release requires manual smoke section in delivery/test-results.md")
    for case_id in ["H01", "H02", "H03", "H04", "H05"]:
        pattern = re.compile(rf"\|\s*{case_id}\b[^\n]*\|\s*PASS\s*\|")
        if not pattern.search(text):
            errors.append(f"Accepted release requires manual smoke PASS evidence for {case_id}")
    if text.count("real integration") < 3:
        errors.append("Accepted release requires real integration evidence in delivery/test-results.md")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check virtual-actor iteration and delivery alignment")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--mode", choices=["draft", "release"], default="release")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    for rel in REQUIRED_PROCESS_FILES + REQUIRED_TEMPLATE_FILES:
        if not (repo_root / rel).exists():
            errors.append(f"Missing required process/template file: {rel}")

    delivery_versions: dict[str, str] = {}
    for rel in DELIVERY_DOCS:
        path = repo_root / rel
        if not path.exists():
            errors.append(f"Missing delivery doc: {rel}")
            continue
        metadata = extract_metadata(path)
        if not metadata.version:
            errors.append(f"Missing version metadata in {rel}")
        else:
            delivery_versions[rel] = metadata.version

    delivered_version: str | None = None
    if delivery_versions:
        unique_versions = sorted(set(delivery_versions.values()))
        if len(unique_versions) != 1:
            errors.append(f"Delivery version mismatch: {delivery_versions}")
        delivered_version = unique_versions[0]

    release_path = repo_root / "delivery" / "release-notes.md"
    release_status = extract_metadata(release_path).status if release_path.exists() else None
    if release_status not in ALLOWED_STATUSES:
        errors.append(f"Invalid or missing release Formal Status/current status: {release_status}")

    portfolio_path = repo_root / PORTFOLIO_DOC
    portfolio_metadata = extract_metadata(portfolio_path) if portfolio_path.exists() else Metadata()
    if not portfolio_path.exists():
        errors.append(f"Missing {PORTFOLIO_DOC}")
    else:
        if portfolio_metadata.version and delivered_version and portfolio_metadata.version != delivered_version:
            errors.append(f"portfolio-sync version mismatch: {portfolio_metadata.version} != {delivered_version}")
        if portfolio_metadata.status not in ALLOWED_STATUSES:
            errors.append(f"Invalid or missing portfolio Formal Status: {portfolio_metadata.status}")
        if release_status and portfolio_metadata.status and release_status != portfolio_metadata.status:
            errors.append(f"Release status and portfolio Formal Status mismatch: {release_status} != {portfolio_metadata.status}")
        interface_delta = extract_interface_delta(read_text(portfolio_path))
        if interface_delta not in INTERFACE_DELTA_STATUSES:
            errors.append(f"Invalid or missing Interface Delta status: {interface_delta}")

    if delivered_version:
        check_dossier(repo_root, delivered_version, "delivered", errors)
        delivered_dossier_status = dossier_status(repo_root, delivered_version)
        if release_status and delivered_dossier_status and release_status != delivered_dossier_status:
            errors.append(
                f"Delivered dossier status mismatch: docs/iterations/{delivered_version}/scope.md "
                f"{delivered_dossier_status} != release {release_status}"
            )

    current_path = repo_root / "docs" / "iterations" / "current.txt"
    active_version: str | None = None
    active_status: str | None = None
    if not current_path.exists():
        errors.append("Missing docs/iterations/current.txt")
    else:
        active_version = read_text(current_path).strip()
        if not active_version:
            errors.append("docs/iterations/current.txt is empty")
        else:
            check_dossier(repo_root, active_version, "active", errors)
            active_status = dossier_status(repo_root, active_version)
            if active_status not in ALLOWED_STATUSES:
                errors.append(f"Invalid active iteration Formal Status: {active_status}")

    check_overclaims(repo_root, errors)

    if args.mode == "release" and release_status == "Accepted":
        check_accepted_evidence(repo_root, errors)

    if errors:
        print("Iteration guard FAILED")
        for item in errors:
            print(f"  ERROR: {item}")
        for item in warnings:
            print(f"  WARN: {item}")
        return 1

    print("Iteration guard passed")
    if delivered_version:
        print(f"  Delivered version: {delivered_version}")
    if release_status:
        print(f"  Delivered Formal Status: {release_status}")
    if active_version:
        print(f"  Active iteration: {active_version}")
    if active_status:
        print(f"  Active iteration Formal Status: {active_status}")
    if portfolio_path.exists():
        print(f"  Interface Delta: {extract_interface_delta(read_text(portfolio_path))}")
    for item in warnings:
        print(f"  WARN: {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
