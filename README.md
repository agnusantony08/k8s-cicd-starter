# Secure, Auto-Scaling Web App with CI/CD on Kubernetes

A small Flask app that is containerized, scanned for vulnerabilities, tested on a
Kubernetes cluster in CI, and auto-scaled under load.

## Architecture
GitHub push -> GitHub Actions (build -> Trivy scan -> deploy to test cluster -> push image to GHCR)
Kubernetes: Deployment (2 replicas) + Service + HorizontalPodAutoscaler (2 to 5 pods)

## Run it locally (Minikube)
```bash
minikube start
minikube addons enable metrics-server
eval $(minikube docker-env)          # build inside Minikube's Docker
docker build -t webapp:local .
kubectl apply -f deployment.yaml -f service.yaml -f hpa.yaml
minikube service webapp --url        # open the URL in your browser
```

## Test autoscaling
```bash
# in one terminal
kubectl get hpa webapp -w
# in another (install "hey" first), replace URL with the one from above
hey -z 120s -c 50 <URL>/cpu
```
Replicas should rise from 2 toward 5, then fall back after the load stops.

## Security measures
- Container runs as a non-root user; privilege escalation disabled
- Trivy scan fails the pipeline on HIGH/CRITICAL vulnerabilities
- Resource requests/limits and health probes on every pod
- No credentials in the repo (CI uses the built-in GITHUB_TOKEN)

## Results (fill in with your own numbers)
- Pipeline time: [FILL IN] minutes
- Autoscaled from 2 to [FILL IN] pods under load
- Trivy findings fixed: [FILL IN]

## Make it yours (do at least 3 before putting this on your resume)
1. Change the app (new endpoint, your own message) and watch the pipeline run.
2. Break the build on purpose (use an old base image) and screenshot Trivy failing.
3. Add a ConfigMap or Secret and read it from the app.
4. Deploy to Azure AKS instead of Minikube and note what changed.
5. Add a screenshot of `kubectl get hpa` scaling to this README.
