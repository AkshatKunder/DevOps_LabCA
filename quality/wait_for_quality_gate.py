"""Wait for a SonarQube analysis and fail when its quality gate is not OK."""

import base64
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


POLL_INTERVAL_SECONDS = 5
TIMEOUT_SECONDS = 300


def get_json(url, token):
    """Fetch a SonarQube API response without logging the credential."""
    encoded_token = base64.b64encode(f"{token}:".encode()).decode()
    request = Request(url, headers={"Authorization": f"Basic {encoded_token}"})
    with urlopen(request, timeout=30) as response:  # nosec B310: controlled URL
        import json

        return json.load(response)


def main():
    host_url = os.environ.get("SONAR_HOST_URL", "").rstrip("/")
    token = os.environ.get("SONAR_TOKEN", "")
    report_path = Path(".scannerwork/report-task.txt")

    if not host_url or not token:
        raise SystemExit("SONAR_HOST_URL and SONAR_TOKEN must be configured.")
    if not report_path.is_file():
        raise SystemExit(f"SonarScanner task report was not created: {report_path}")

    report = dict(
        line.split("=", 1)
        for line in report_path.read_text(encoding="utf-8").splitlines()
        if "=" in line
    )
    task_id = report.get("ceTaskId")
    if not task_id:
        raise SystemExit("SonarScanner task report does not contain ceTaskId.")
    task_url = f"{host_url}/api/ce/task?{urlencode({'id': task_id})}"

    deadline = time.monotonic() + TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        task = get_json(task_url, token).get("task", {})
        status = task.get("status")
        if status == "SUCCESS":
            analysis_id = task.get("analysisId")
            if not analysis_id:
                raise SystemExit("SonarQube task completed without an analysis ID.")
            gate_url = f"{host_url}/api/qualitygates/project_status?{urlencode({'analysisId': analysis_id})}"
            gate_status = get_json(gate_url, token).get("projectStatus", {}).get("status")
            print(f"SonarQube quality gate: {gate_status}")
            if gate_status != "OK":
                raise SystemExit(f"Quality gate failed with status: {gate_status}")
            return
        if status in {"FAILED", "CANCELED"}:
            raise SystemExit(f"SonarQube compute-engine task ended with status: {status}")
        print(f"Waiting for SonarQube analysis (status: {status})...")
        time.sleep(POLL_INTERVAL_SECONDS)

    raise SystemExit("Timed out waiting for the SonarQube quality gate.")


if __name__ == "__main__":
    main()
