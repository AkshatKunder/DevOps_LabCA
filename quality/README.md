# QuizGenius quality and security checks

## SonarQube setup

Start SonarQube separately from the monitoring stack:

```powershell
docker compose -f quality\compose.yaml up -d
docker compose -f quality\compose.yaml logs -f sonarqube
```

Open `http://localhost:9000` after the server reports that it is operational. On a new installation, sign in with SonarQube's documented initial administrator account (`admin` / `admin`), change the password immediately, create a local project with key `quizgenius`, and generate an analysis token.

Store that token only in Jenkins as a **Secret text** credential with the ID `SONAR_TOKEN`. Never place it in `.env`, `sonar-project.properties`, the Compose file, or source control. The Jenkins scanner container reaches a Docker Desktop host service through `http://host.docker.internal:9000`.

The named `sonarqube-*` volumes retain server data. Do not run `docker compose -f quality\compose.yaml down -v` or prune those volumes unless you intentionally want to discard SonarQube data. This Compose configuration deliberately does not disable Elasticsearch/bootstrap checks; fix a failed host prerequisite rather than bypassing it.

## Local SonarQube analysis

After setting `SONAR_TOKEN` in the current PowerShell session, run:

```powershell
$projectPath = (Get-Location).Path
$env:SONAR_HOST_URL = "http://host.docker.internal:9000"
docker run --rm --mount "type=bind,source=$projectPath,target=/usr/src" -e SONAR_HOST_URL -e SONAR_TOKEN sonarsource/sonar-scanner-cli:12.2.0.4256_8.1.0
```

The project definition is in `sonar-project.properties`. It analyzes `app/` and `tests/`, and excludes virtual environments, caches, monitoring configuration, and generated report directories. Coverage is not configured because this project does not currently install `pytest-cov` or generate `coverage.xml`.

## Trivy image scanning

The Jenkins pipeline builds the deployment image without using cached layers, saves that exact image to a tar archive, and scans the archive with the official `aquasec/trivy:0.58.1` image. This avoids granting the scanner access to the Docker socket or to unrelated containers.

The Dockerfile installs available Debian security updates during every build and
updates `setuptools` (whose prior release vendors these packages),
`jaraco.context`, and `wheel` to tested remediated versions. Debian advisories
that report no fixed version cannot be resolved by `apt-get upgrade`; they
remain subject to a fresh Trivy scan until Debian publishes a fix or the base
image no longer contains the affected package.

The scan always writes `trivy-report.json` for Jenkins to archive and prints a table report. It fails the pipeline when an OS-package or Python-library vulnerability is rated `HIGH` or `CRITICAL`; lower-severity findings remain visible in the JSON report but do not block deployment.

To reproduce it locally without starting or replacing the application container:

```powershell
docker build --pull --no-cache -t quizgenius:local .
docker save quizgenius:local -o quizgenius-image.tar
$projectPath = (Get-Location).Path
docker run --rm --mount "type=bind,source=$projectPath,target=/workspace" aquasec/trivy:0.58.1 image --input /workspace/quizgenius-image.tar --scanners vuln --severity HIGH,CRITICAL --format json --output /workspace/trivy-report.json --exit-code 0
docker run --rm --mount "type=bind,source=$projectPath,target=/workspace" aquasec/trivy:0.58.1 image --input /workspace/quizgenius-image.tar --scanners vuln --severity HIGH,CRITICAL --exit-code 1
```

## Jenkins prerequisites and demo

1. Start SonarQube and wait for `http://localhost:9000` to load.
2. Add Jenkins Secret text credential `SONAR_TOKEN` containing the SonarQube analysis token.
3. Confirm the Windows Jenkins service account can use Docker and can bind-mount `%WORKSPACE%` into Linux Docker containers.
4. Run `DevOps-LabCA-CI-CD`. The expected order is Build, Unit Tests, Integration Tests, SonarQube Analysis, SonarQube Quality Gate, Docker Build, Trivy Security Scan, then Deploy.
5. Review the SonarQube project dashboard and Jenkins `trivy-report.json` artifact. Do not run the Deploy stage manually; it only runs automatically after all quality and security checks pass.

If the scanner cannot reach SonarQube, verify Docker Desktop is running and that `host.docker.internal:9000` is reachable from a Docker container. If bind mounts fail, grant the Jenkins service account access to the workspace and Docker Desktop shared files. If Trivy cannot download its database, allow the Jenkins host outbound access to Trivy's update registries.
