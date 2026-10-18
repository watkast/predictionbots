"""Program-scope checker for the bounty pipeline.

Loads one program's scope from YAML and answers ``in_scope(target)``. The rule
is deny-by-default: a target is in scope only if it matches an entry under
``in_scope`` and no entry under ``out_of_scope``. Anything the checker cannot
classify (not a domain, repo, IP or CIDR) is refused.

Scope file shape (see ``scope_example.yaml``)::

    program: kubernetes
    platform: hackerone
    url: https://hackerone.com/kubernetes
    in_scope:
      repos:   ["github.com/kubernetes/kubernetes"]
      domains: ["*.example.com", "api.example.com"]   # "*." = subdomains only
      cidrs:   ["203.0.113.0/24", "198.51.100.7"]
    out_of_scope:
      repos: [], domains: ["legacy.example.com"], cidrs: []
    rules:                      # enforced by the pipeline, not by this file
      no_dos: true
      no_social_engineering: true
      no_production_data: true
      max_requests_per_second: 5
      allowed_methods: [static_analysis, local_reproduction]

CLI: ``python ventures/bounty/scope.py <scope.yaml> <target> [<target> ...]``
exits 0 only if every target is in scope.
"""
from __future__ import annotations

import ipaddress
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlsplit

import yaml

KINDS = ("repo", "domain", "ip")
_LABEL = re.compile(r"^(?!-)[a-z0-9-]{1,63}(?<!-)$")
_REPO = re.compile(r"^(?P<host>github\.com|gitlab\.com|codeberg\.org)/(?P<owner>[A-Za-z0-9_.-]+)/(?P<name>[A-Za-z0-9_.-]+)$")


@dataclass(frozen=True)
class Decision:
    target: str
    allowed: bool
    kind: str | None
    reason: str

    def __bool__(self) -> bool:  # pragma: no cover - convenience
        return self.allowed


@dataclass
class Scope:
    program: str
    platform: str = ""
    url: str = ""
    repos: list[str] = field(default_factory=list)
    domains: list[str] = field(default_factory=list)
    cidrs: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = field(default_factory=list)
    x_repos: list[str] = field(default_factory=list)
    x_domains: list[str] = field(default_factory=list)
    x_cidrs: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = field(default_factory=list)
    rules: dict[str, Any] = field(default_factory=dict)

    # ---------------------------------------------------------------- loading
    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Scope":
        if not isinstance(d, dict) or not d.get("program"):
            raise ValueError("scope needs a 'program' name")
        inc = d.get("in_scope") or {}
        exc = d.get("out_of_scope") or {}
        for blk, name in ((inc, "in_scope"), (exc, "out_of_scope")):
            if not isinstance(blk, dict):
                raise ValueError(f"'{name}' must be a mapping")
            unknown = set(blk) - {"repos", "domains", "cidrs"}
            if unknown:
                raise ValueError(f"'{name}' has unknown keys {sorted(unknown)}")
        s = cls(program=str(d["program"]), platform=str(d.get("platform", "")), url=str(d.get("url", "")),
                rules=dict(d.get("rules") or {}))
        s.repos = [normalize_repo(r) for r in inc.get("repos") or []]
        s.domains = [normalize_domain(x) for x in inc.get("domains") or []]
        s.cidrs = [ipaddress.ip_network(str(c), strict=False) for c in inc.get("cidrs") or []]
        s.x_repos = [normalize_repo(r) for r in exc.get("repos") or []]
        s.x_domains = [normalize_domain(x) for x in exc.get("domains") or []]
        s.x_cidrs = [ipaddress.ip_network(str(c), strict=False) for c in exc.get("cidrs") or []]
        for r in s.repos + s.x_repos:
            if r is None:
                raise ValueError("unparseable repo in scope file")
        return s

    @classmethod
    def load(cls, path: str | Path) -> "Scope":
        return cls.from_dict(yaml.safe_load(Path(path).read_text()) or {})

    # --------------------------------------------------------------- checking
    def in_scope(self, target: str) -> Decision:
        kind, value = classify(target)
        if kind is None:
            return Decision(target, False, None, f"refused: cannot classify '{target}' as repo/domain/ip")
        if kind == "repo":
            if value in self.x_repos:
                return Decision(target, False, kind, f"excluded repo {value}")
            if value in self.repos:
                return Decision(target, True, kind, f"listed repo {value}")
            return Decision(target, False, kind, f"repo {value} not listed for {self.program}")
        if kind == "domain":
            hit = _match_domain(value, self.x_domains)
            if hit:
                return Decision(target, False, kind, f"excluded by {hit}")
            hit = _match_domain(value, self.domains)
            if hit:
                return Decision(target, True, kind, f"matches {hit}")
            return Decision(target, False, kind, f"domain {value} not listed for {self.program}")
        # ip
        for net in self.x_cidrs:
            if value in net:
                return Decision(target, False, kind, f"excluded by {net}")
        for net in self.cidrs:
            if value in net:
                return Decision(target, True, kind, f"inside {net}")
        return Decision(target, False, kind, f"ip {value} not inside any listed CIDR for {self.program}")

    def check_all(self, targets: Iterable[str]) -> list[Decision]:
        return [self.in_scope(t) for t in targets]

    def forbids(self, activity: str) -> bool:
        """True when the rules block forbids an activity: 'dos', 'social_engineering', 'production_data'."""
        return bool(self.rules.get(f"no_{activity}", True))


# ------------------------------------------------------------- normalizers
def normalize_repo(s: str) -> str | None:
    s = str(s).strip()
    if "://" in s:
        u = urlsplit(s)
        s = f"{u.netloc}{u.path}"
    s = s.lower().rstrip("/")
    if s.endswith(".git"):
        s = s[:-4]
    if s.startswith("www."):
        s = s[4:]
    m = _REPO.match(s)
    return s if m else None


def normalize_domain(s: str) -> str:
    s = str(s).strip().lower().rstrip(".")
    if "://" in s:
        s = urlsplit(s).hostname or ""
    if "/" in s:
        s = s.split("/", 1)[0]
    if ":" in s and not s.startswith("["):
        s = s.split(":", 1)[0]
    return s


def _valid_hostname(h: str) -> bool:
    if not h or len(h) > 253 or "." not in h:
        return False
    return all(_LABEL.match(lbl) for lbl in h.split("."))


def classify(target: str) -> tuple[str | None, Any]:
    """Return (kind, normalized value). kind is 'repo', 'domain', 'ip' or None."""
    t = str(target).strip()
    if not t:
        return None, None
    repo = normalize_repo(t)
    if repo:
        return "repo", repo
    host = normalize_domain(t)
    try:
        return "ip", ipaddress.ip_address(host.strip("[]"))
    except ValueError:
        pass
    if host.startswith("*."):
        return None, None  # wildcards are scope entries, never targets
    if _valid_hostname(host):
        return "domain", host
    return None, None


def _match_domain(host: str, patterns: list[str]) -> str | None:
    for p in patterns:
        if p.startswith("*."):
            base = p[2:]
            if host != base and host.endswith("." + base):
                return p
        elif host == p:
            return p
    return None


# ------------------------------------------------------------------- CLI
def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) < 2:
        print(__doc__)
        return 2
    scope = Scope.load(argv[0])
    rc = 0
    for d in scope.check_all(argv[1:]):
        print(f"{'IN ' if d.allowed else 'OUT'} {d.target:40s} {d.reason}")
        rc |= 0 if d.allowed else 1
    return rc


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
