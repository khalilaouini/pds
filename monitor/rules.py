# monitor/rules.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict

from monitor.features import WindowFeatures


@dataclass(frozen=True)
class RuleHit:
    issue_type: str
    severity: str       # LOW/MED/HIGH
    reason: str

    def to_dict(self) -> dict:
        return {"issue_type": self.issue_type, "severity": self.severity, "reason": self.reason}


def apply_rules(feat: WindowFeatures) -> List[RuleHit]:
    hits: List[RuleHit] = []

    # Crash-loop / misconfig signals: high repeat + errors
    if feat.total >= 5 and feat.error >= 2 and feat.repeat_ratio >= 0.6:
        hits.append(RuleHit(
            issue_type="crash_loop_or_misconfig",
            severity="HIGH",
            reason=f"repeat_ratio={feat.repeat_ratio}, error={feat.error}, total={feat.total}"
        ))

    # Generic instability
    if feat.error >= 3:
        hits.append(RuleHit(
            issue_type="service_errors",
            severity="MED",
            reason=f"errors={feat.error}"
        ))

    # Suspicious command-like patterns
    if feat.pattern_hits.get("curl_pipe_bash", 0) > 0 or feat.keyword_hits.get("curl", 0) > 0:
        hits.append(RuleHit(
            issue_type="suspicious_command",
            severity="HIGH",
            reason="curl execution pattern observed"
        ))

    if feat.pattern_hits.get("base64_decode", 0) > 0 or feat.keyword_hits.get("base64", 0) > 0:
        hits.append(RuleHit(
            issue_type="encoded_payload_activity",
            severity="HIGH",
            reason="base64 decode pattern observed"
        ))

    if feat.pattern_hits.get("reverse_shell", 0) > 0 or feat.keyword_hits.get("reverse shell", 0) > 0:
        hits.append(RuleHit(
            issue_type="reverse_shell_indicator",
            severity="HIGH",
            reason="reverse shell indicator observed"
        ))

    # Brute-force / scanning / noisy behavior
    if feat.pattern_hits.get("failed_password", 0) >= 2 or feat.keyword_hits.get("failed password", 0) >= 2:
        hits.append(RuleHit(
            issue_type="bruteforce_attempts",
            severity="HIGH",
            reason=f"failed_password_hits={max(feat.pattern_hits.get('failed_password',0), feat.keyword_hits.get('failed password',0))}"
        ))

    if feat.pattern_hits.get("port_scan", 0) > 0 or feat.keyword_hits.get("portscan", 0) > 0:
        hits.append(RuleHit(
            issue_type="port_scan_activity",
            severity="MED",
            reason="port scan indicators observed"
        ))

    # Dependency down / refused
    if feat.keyword_hits.get("refused", 0) > 0 or feat.keyword_hits.get("timeout", 0) > 0:
        hits.append(RuleHit(
            issue_type="dependency_down_or_network",
            severity="MED",
            reason="connection refused / timeout indicators"
        ))

    return hits

