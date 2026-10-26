<!-- kubectl get secrets won't work here either. -->

<a href="https://mella7.me">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/mella7/mella7/main/assets/header-dark.svg">
    <img alt="Terminal running kubectl describe engineer mella7: Mohamed Ali Mellah, Cloud Security Engineer" src="https://raw.githubusercontent.com/mella7/mella7/main/assets/header-light.svg" width="100%">
  </picture>
</a>

<p align="center">
  <a href="https://mella7.me"><img src="https://img.shields.io/badge/web-mella7.me-2dd4bf?style=flat-square&labelColor=161b22" alt="mella7.me"></a>
  <a href="https://www.linkedin.com/in/MellahMedAli"><img src="https://img.shields.io/badge/linkedin-MellahMedAli-2dd4bf?style=flat-square&labelColor=161b22" alt="LinkedIn"></a>
  <a href="https://medium.com/@mellahmohamedali"><img src="https://img.shields.io/badge/medium-@mellahmohamedali-2dd4bf?style=flat-square&labelColor=161b22" alt="Medium"></a>
  <a href="mailto:mellah.mohamedali@outlook.com"><img src="https://img.shields.io/badge/mail-mellah.mohamedali@outlook.com-2dd4bf?style=flat-square&labelColor=161b22" alt="Email"></a>
</p>

### `$ whoami`

Cloud security engineer working on Kubernetes security and platform engineering. Most of my time goes into runtime detection with eBPF and into the identities nobody audits: CI/CD pipelines, service accounts, and now MCP servers.

Studying for my master's in Informatik at the University of Passau. Open to junior DevOps, DevSecOps and Platform Engineering roles in Switzerland, Luxembourg and Germany.

```yaml
apiVersion: people.mella7.me/v1
kind: Engineer
metadata:
  name: mohamed-ali-mellah
  labels:
    role: cloud-security
    focus: kubernetes-runtime-security
spec:
  certifications: [CKA, CKAD, RHCSA, eJPT]
  inProgress: [CKS]
  education:
    - Diplôme National d'Ingénieur, Informatique - TEK-UP University
    - MSc Informatik - University of Passau (ongoing)
  speaks: [arabic, french, english, german]
status:
  phase: Running
  conditions:
    - type: OpenToWork
      status: "True"
```

### `$ kubectl get certs`

<p>
  <img src="https://img.shields.io/badge/CKA-certified-326CE5?style=for-the-badge&labelColor=161b22" alt="CKA">
  <img src="https://img.shields.io/badge/CKAD-certified-326CE5?style=for-the-badge&labelColor=161b22" alt="CKAD">
  <img src="https://img.shields.io/badge/RHCSA-certified-EE0000?style=for-the-badge&labelColor=161b22" alt="RHCSA">
  <img src="https://img.shields.io/badge/eJPT-certified-2dd4bf?style=for-the-badge&labelColor=161b22" alt="eJPT">
  <img src="https://img.shields.io/badge/CKS-in_progress-d29922?style=for-the-badge&labelColor=161b22" alt="CKS in progress">
</p>

<!-- Tip: wrap each badge in <a href="YOUR_CREDLY_BADGE_URL"> so people can verify it. -->

### `$ cat events.log`

| when | where | what |
|---|---|---|
| `Nov 2026` | **Cloud Identity Summit**, Frankfurt | Talk: [*Your CI/CD Pipeline Is Over-Privileged: Identity Risks in Modern Cloud Platforms*](https://mella7.me/en/talks/cloud-identity-summit-2026-cicd) |
| `2026` | **ContainerDays**, Hamburg | Talk: [*How Clusters Fail Under Attack and How We Detect It at Runtime with eBPF Signals*](https://mella7.me/en/talks/containerdays-2026-ebpf) · [slides](https://mella7.me/talks/slides/containerdays-2026-ebpf.pdf) |
| `2026` | **Huawei ICT Competition**, Shenzhen | Global 1st Prize, Computing Track |

### `$ ls ~/projects`

| project | what it does | built with |
|---|---|---|
| [**MCP Sentinel**](https://github.com/mella7/mcp-sentinel) | Least-privilege auditor for MCP servers. Treats them as non-human identities and flags over-privileged Kubernetes RBAC and credentials. | `Python` `Kubernetes` |
| [**Falco MCP server**](https://github.com/mella7/falco-mcp) | Cuts down eBPF alert noise and correlates Falco alerts with RBAC and identity risk, so an agent can triage runtime events. | `Python` `Falco` `gRPC` |
| [**ProjectClaim**](https://github.com/mella7/projectclaim) | Kubernetes operator for OKD/OpenShift with custom CRDs, finalizer-based cleanup and CEL immutability rules. | `Go` `controller-runtime` |
| [**cloudstack-dc**](https://github.com/mella7/cloudstack-dc) | CloudStack provisioning portal with live log streaming over SSE, two-stage Terraform apply and a dry-run mode. | `FastAPI` `React` `Terraform` |

### `$ git log --upstream`

- **kubermatic/kubermatic** - [#16246](https://github.com/kubermatic/kubermatic/issues/16246): seed-proxy applies `overwriteRegistry` to its util image when it shouldn't
- **k8up-io/k8up** - [#1232](https://github.com/k8up-io/k8up/issues/1232): status patches for SetStarted/SetFinished are no-ops, [#1192](https://github.com/k8up-io/k8up/issues/1192): `successfulJobsHistoryLimit: 0` behaves inconsistently

### `$ kubectl get nodes -L pool`

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/mella7/mella7/main/assets/stack-dark.svg">
  <img alt="Tech stack as a cluster. Orchestration: Kubernetes, OpenShift, Helm, Operators. Runtime security: eBPF, Tetragon, Falco, RBAC audit. Infra as code: Terraform, CloudStack, GitOps. Languages: Go, Python, TypeScript, Bash. Apps: FastAPI, React, Next.js, MCP. Linux: RHEL, Fedora, systemd, networking." src="https://raw.githubusercontent.com/mella7/mella7/main/assets/stack-light.svg" width="100%">
</picture>

### `$ kubectl top engineer mella7`

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/mella7/mella7/main/profile-3d-contrib/profile-night-green.svg">
  <img alt="3D contribution graph" src="https://raw.githubusercontent.com/mella7/mella7/main/profile-3d-contrib/profile-green-animate.svg" width="100%">
</picture>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://streak-stats.demolab.com?user=mella7&background=0d1117&border=30363d&stroke=30363d&ring=2dd4bf&fire=2dd4bf&currStreakNum=f0f6fc&sideNums=c9d1d9&currStreakLabel=2dd4bf&sideLabels=8b949e&dates=8b949e">
    <img alt="Contribution streak" src="https://streak-stats.demolab.com?user=mella7&background=ffffff&border=d0d7de&stroke=d0d7de&ring=0f766e&fire=0f766e&currStreakNum=0d1117&sideNums=24292f&currStreakLabel=0f766e&sideLabels=57606a&dates=57606a">
  </picture>
</p>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/mella7/mella7/output/github-snake-dark.svg">
  <img alt="Snake eating the contribution graph" src="https://raw.githubusercontent.com/mella7/mella7/output/github-snake.svg" width="100%">
</picture>

<p align="center"><sub><code>kubectl logs mella7 --follow</code> · graphs refresh daily via GitHub Actions</sub></p>
