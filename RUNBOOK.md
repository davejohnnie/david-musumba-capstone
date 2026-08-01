# RUNBOOK

Troubleshooting guide for common issues encountered in this project.

## Pod stuck in `ImagePullBackOff` / `ErrImagePull`

**Cause:** `ecr-pull-secret` missing, expired, or misconfigured. ECR auth tokens expire after 12 hours.

**Fix:**
```bash
aws ecr get-login-password --region eu-west-1 --profile capstone > ecr-password.txt
kubectl create secret docker-registry ecr-pull-secret \
  --docker-server=024848484634.dkr.ecr.eu-west-1.amazonaws.com \
  --docker-username=AWS \
  --docker-password=$(cat ecr-password.txt) \
  -n david-musumba \
  --dry-run=client -o yaml | kubectl apply -f -
rm ecr-password.txt
```

## Pod `CrashLoopBackOff` on backend

**Cause (encountered):** SQLAlchemy `VARCHAR requires a length on dialect mysql` — Postgres allows unbounded `String` columns; MySQL/MariaDB requires explicit lengths.

**Fix:** ensure all `String` columns in `models.py` specify a length, e.g. `String(255)`.

**Diagnosis:**
```bash
kubectl logs <pod-name> -n david-musumba
```
Look for a Python traceback — SQLAlchemy compile errors appear here clearly.

## Backend can't connect to database

**Checks, in order:**
```bash
kubectl get secrets -n david-musumba
kubectl describe secret db-credentials -n david-musumba
```
Confirm all 5 keys (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`) are present. Confirm `database.py`'s connection string protocol matches the actual database engine (`mysql+pymysql://` for MariaDB, not `postgresql://`).

## Frontend can't reach backend (502/404/500 via reverse proxy)

**Cause (encountered):** attempted an in-Nginx reverse proxy (`proxy_pass` with a variable, for request-time DNS resolution). Hit a sequence of issues: wrong resolver IP (Docker's `127.0.0.11` vs EKS CoreDNS's actual ClusterIP), short service names not resolving without FQDN, path-prefix not stripping correctly, and finally `invalid URL prefix` — a hard limitation of Nginx's variable-based `proxy_pass` syntax.

**Resolution:** abandoned the in-Nginx proxy approach. Routing is instead handled at the **Ingress** layer:
```yaml
annotations:
  nginx.ingress.kubernetes.io/rewrite-target: /$2
paths:
  - path: /api(/|$)(.*)   → backend-service
  - path: /()(.*)          → frontend-service
```
This is the standard, more reliable pattern for this use case.

## Ingress serving wrong content for static assets (e.g. `app.js` returns HTML)

**Cause:** Ingress path pattern for the frontend was rewriting all paths (including `/app.js`, `/style.css`) into the same target, causing them to resolve to `index.html`.

**Fix:** use `/()(.*)` (empty capture group) for the frontend's catch-all path, so Ingress passes the full original path through unchanged rather than rewriting it.

## kubectl pointed at wrong cluster (`127.0.0.1:6443` connection refused)

**Cause:** local Minikube/k3d context accidentally active instead of the real EKS context.

**Fix:**
```bash
aws eks update-kubeconfig --name innovation-lab --region eu-west-1 --profile capstone
kubectl config current-context
```
Confirm it shows the EKS cluster ARN, not a local cluster.

## High latency / slow responses

**Checks:**
```bash
kubectl top pods -n david-musumba
kubectl describe pod <pod-name> -n david-musumba
```
Check for pods near their resource `limits` (may indicate under-provisioned requests/limits) or frequent restarts (check `RESTARTS` column in `kubectl get pods`).