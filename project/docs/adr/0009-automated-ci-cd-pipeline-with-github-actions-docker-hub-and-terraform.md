# ADR-0009: Automated CI/CD Pipeline with GitHub Actions, Docker Hub, and Terraform on AWS

- **Status:** accepted
- **Date:** 2026-11-17
- **Deciders:** Engineering & DevOps Team
- **Related requirements:** NFR-02 (Maintainability), NFR-04 (Automated Delivery & DevOps Gates)

## Context

The Optima Coffee project requires continuous integration and automated deployment (CI/CD) to guarantee code quality, package containerized artifacts, provision cloud infrastructure as code (IaC), and deploy the application to AWS cloud environments without manual intervention.

Key operational constraints:
1. Every commit to release branches (`main`, `rc`) must pass all automated quality gates (code linting, formatting, test suite, API documentation verification).
2. Deployment artifacts must be packaged into standardized, reproducible OCI container images and published to a public registry (Docker Hub).
3. Cloud infrastructure on AWS must be managed declaratively using Terraform, targeting the `eu-north-1` (Stockholm) region on `t3.micro` instances with strict security groups (SSH, HTTP).
4. Deployments must be verified automatically using an end-to-end health check probe before concluding the pipeline.

## Decision

We adopt a 4-stage automated CI/CD pipeline using **GitHub Actions**, **Docker Hub**, **Terraform**, and **AWS EC2**:

1. **Stage 1: Quality Gates (`backend-checks`)**
   - Linting with Ruff (`ruff check`).
   - Formatting check with Ruff (`ruff format --check`).
   - Test suite execution with Pytest (50 unit & integration tests).
   - API documentation verification (`openapi.yaml` and Markdown endpoint references).

2. **Stage 2: Artifact Packaging (`build-and-push`)**
   - Multi-stage Docker image build using `Dockerfile`.
   - Automated authentication and publication to Docker Hub under tags `latest` and `${{ github.sha }}`.

3. **Stage 3: Infrastructure Provisioning (`terraform-apply`)**
   - Declarative Terraform configuration in `infra/` (`providers.tf`, `variables.tf`, `main.tf`, `outputs.tf`).
   - Automated state synchronization and resource import (`terraform import`) to ensure idempotency across ephemeral GitHub Actions runners without requiring external S3 backend storage.
   - Dynamic extraction and export of the provisioned EC2 instance's public IP address.

4. **Stage 4: Automated Deployment & Verification (`deploy`)**
   - Secure SSH key injection via `EC2_SSH_KEY_B64`.
   - Wait-loop polling for cloud-init and Docker Engine availability.
   - Pulling the latest image from Docker Hub, restarting the container with `--restart unless-stopped`.
   - Live HTTP health probe against `http://<EC2_IP>:8000/health`.

## Considered alternatives

| Option | Pros | Cons | Why not chosen |
|---|---|---|---|
| **GitHub Actions + Docker Hub + Terraform + EC2** | Fully automated, vendor-neutral IaC, reproducible images, automated health checks, integrated into GitHub | Ephemeral runner state requires synchronization logic | **Chosen.** Best match for course requirements, industry standards, and reproducible cloud delivery. |
| Manual SSH Deployment | No CI/CD setup overhead, simple for initial prototype | Error-prone, lacks auditability, completely breaks continuous delivery principles | Rejected due to lack of reproducibility and failure to meet DevOps requirements. |
| AWS CodePipeline / CodeBuild | Native AWS ecosystem integration, IAM role binding without static access keys | Vendor lock-in to AWS, separated from GitHub pull request UI, higher operational setup | Rejected in favor of GitHub Actions for unified developer experience and repository visibility. |

## Consequences

**Positive**
- Rapid feedback loop: developers receive immediate pass/fail feedback on every push and pull request.
- Infrastructure as Code (IaC) guarantees consistent environment creation without drift.
- Production deployments are completely automated and verified via healthcheck endpoints.

**Negative**
- Requires managing GitHub Secrets (`DOCKER_USERNAME`, `DOCKER_TOKEN`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `EC2_SSH_KEY_B64`).
- Ephemeral runners require pre-apply state synchronization to handle existing security groups and EC2 instances.

## Verification

Verified by automated GitHub Actions workflow runs triggered on push to `rc` and `main`, confirming green execution across all four jobs and a successful `HTTP 200` response from the live EC2 endpoint.
