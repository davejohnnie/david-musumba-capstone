# Claims Tracker — Capstone Project (AWS EKS)

A lightweight claims-tracking application demonstrating a full DevOps pipeline: containerized build, automated CI/CD, and production-style deployment on a shared AWS EKS cluster.

## Tech Stack

- **Backend:** Python (FastAPI) + SQLAlchemy
- **Frontend:** Static HTML/JS + Bootstrap, served by Nginx
- **Database:** MariaDB (AWS RDS, private VPC)
- **Container Registry:** AWS ECR
- **Orchestration:** Kubernetes (AWS EKS, shared cluster)
- **CI/CD:** GitHub Actions
- **Ingress:** Nginx Ingress Controller

## Architecture
Browser → Ingress (ALB) → frontend-service → frontend pods (Nginx, static UI)
→ backend-service → backend pods (FastAPI) → MariaDB (RDS)

Ingress routes `/api/*` to the backend and everything else to the frontend, so the browser only ever talks to one public address.

## Repository Structure
david-musumba-capstone/
├── backend/ # FastAPI app, Dockerfile
├── frontend/ # Static UI, Nginx config, Dockerfile
├── k8s/ # Kubernetes manifests
├── .github/workflows/ # CI/CD pipeline
├── README.md
└── RUNBOOK.md

## Git Workflow

`main` → `staging` → `develop` → feature branches, merged via reviewed Pull Requests. Branch protection enforced on `main`, `staging`, and `develop` (1 required reviewer, required status checks). As a solo contributor, admin bypass is used to merge — in a team setting this would require a genuine second reviewer.

## CI/CD Pipeline

On every push to `main`, `.github/workflows/ci-cd.yml`:
1. Builds and pushes both Docker images to ECR (tagged `:latest` and `:<git-sha>`)
2. Applies all Kubernetes manifests to the `david-musumba` namespace
3. Restarts both deployments so new images take effect immediately

## Kubernetes Resources

- **Namespace:** `david-musumba`
- **Deployments:** `frontend` (3 replicas), `backend` (3 replicas) — both with resource requests/limits and liveness/readiness probes on `/health`
- **Services:** `frontend-service`, `backend-service` (ClusterIP)
- **Ingress:** routes external traffic; `/api/*` → backend, everything else → frontend
- **Secrets:** `db-credentials` (MariaDB connection details), `ecr-pull-secret` (image pull auth)

## Running Locally

```bash
# Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
python3 -m http.server 8081
```

Note: local runs cannot reach the real MariaDB (private VPC, cluster-only) or the Ingress-based `/api` routing — full functionality is only testable once deployed to EKS.

## Deploying

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment-backend.yaml
kubectl apply -f k8s/service-backend.yaml
kubectl apply -f k8s/deployment-frontend.yaml
kubectl apply -f k8s/service-frontend.yaml
kubectl apply -f k8s/ingress.yaml
```

(Handled automatically by CI/CD on every push to `main`.)

## Notable Design Decisions

- **Database engine:** the original spec listed PostgreSQL; the actual provisioned RDS instance is MariaDB (confirmed directly by the DevOps team). Backend was adjusted accordingly (SQLAlchemy + PyMySQL, explicit `VARCHAR` lengths for MySQL/MariaDB compatibility).
- **Frontend-to-backend routing:** initially attempted via an Nginx reverse proxy inside the frontend container; abandoned due to persistent Nginx variable-based `proxy_pass` limitations (see RUNBOOK). Routing is instead handled at the Ingress layer, which is simpler and more standard.