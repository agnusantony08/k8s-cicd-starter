# Secure, Auto-Scaling Web App with CI/CD on Kubernetes

A small Flask app packaged in Docker and deployed to Kubernetes. Every push to
`main` runs tests, builds the image, scans it for vulnerabilities, deploys it to
a temporary Kubernetes (kind) cluster and smoke-tests the live `/health` endpoint.

## Pipeline
GitHub push -> pytest -> Docker build -> Trivy scan -> kind cluster -> deploy -> smoke test

- A failing test blocks the build.
- HIGH or CRITICAL Trivy findings fail the pipeline.
- A failing `/health` smoke test fails the release.

## Project layout
```
app.py                     Flask app (/ and /health)
requirements.txt           runtime dependencies
requirements-dev.txt       test dependencies (pytest)
pytest.ini                 pytest config
tests/test_app.py          3 automated tests
Dockerfile                 non-root container image
.dockerignore / .gitignore
k8s/deployment.yaml        2 replicas, probes, resource limits, non-root
k8s/service.yaml           ClusterIP service (80 -> 8080)
k8s/hpa.yaml               autoscaler: 2-5 replicas at 50% CPU
.github/workflows/ci-cd.yml  the pipeline
```

## Run locally
```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest -v
python -m flask --app app run --port 8080
```

## Try it on a local Kubernetes cluster (needs Docker, kind, kubectl)
```bash
docker build -t k8s-cicd-starter:ci .
kind create cluster --name ci-cluster
kind load docker-image k8s-cicd-starter:ci --name ci-cluster
kubectl apply -f k8s/
kubectl rollout status deployment/web
kubectl port-forward svc/web 8080:80
curl http://localhost:8080/health
```

### See the autoscaler work (optional)
kind has no metrics-server by default, so the HPA shows `<unknown>` until you add it:
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl patch -n kube-system deployment metrics-server --type=json \
  -p '[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
kubectl get hpa web --watch
```
In another terminal, generate load:
```bash
kubectl run load --rm -it --image=busybox --restart=Never -- \
  /bin/sh -c "while true; do wget -q -O- http://web/health; done"
```

## Security notes
- Container runs as a non-root user (UID 10001); privilege escalation is disabled and all Linux capabilities are dropped
- Every pod has resource requests/limits and readiness/liveness probes
- Trivy fails the pipeline on HIGH/CRITICAL findings (unfixed ones are ignored)
- Trivy runs from a pinned container image rather than a mutable GitHub Action tag
- For stronger supply-chain safety, pin `actions/*` and `helm/kind-action` to full commit SHAs
