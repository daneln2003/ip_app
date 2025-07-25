# ip-app — Minimal Flask service with full CI/CD to EKS

A tiny **Python + Flask** web service that returns the machine’s **public IP**, fully **containerized**, **Helm-packaged**, and **continuously delivered** to **Kubernetes (EKS)** via **GitHub Actions**, with **Slack notifications** on every stage.

---

## Table of Contents

1. [What I Built (high level)](#-what-i-built-high-level)
2. [Why I Chose This Implementation](#-why-i-chose-this-implementation)
3. [Repository Layout](#-repository-layout)
4. [CI/CD Process (end-to-end)](#-cicd-process-end-to-end)
   - [Triggers](#triggers)
   - [Global Environment & Secrets](#global-environment--secrets)
   - [Jobs / Stages](#jobs--stages)
5. [The Scripts](#-the-scripts)
6. [Slack Notifications](#-slack-notifications)
7. [How to Run Everything (Conceptually)](#-how-to-run-everything-conceptually)
8. [Environment Variables & Secrets (Summary)](#-environment-variables--secrets-summary)

---

##  What I Built (high level)

- **Application**: Minimal **Python + Flask** web service that returns the **public IP**.
- **Tests**:
  - Unit & integration tests verifying:
    - `/health` returns **200**.
    - Response **structure/content** is correct.
- **Containerization**: The app is **Dockerized**.
- **Packaging & Deployment**: A **Helm chart** deploys the service to **Kubernetes**.
- **CI/CD**: A **GitHub Actions** pipeline that:
  - Runs **tests** on every push to `main`.
  - **Builds** a Docker image and **tags it dynamically** with the **build timestamp** (and also pushes `latest` for convenience).
  - **Pushes** the image to **Docker Hub**.
  - **Deploys** to a **Kubernetes cluster (EKS)** using **Helm**.
  - Sends **Slack notifications** for each stage outcome (**test / build / deploy**).

---

## Why I Chose This Implementation

- **GitHub Actions**: Native with GitHub, simple **secrets handling**, great ecosystem, fast to iterate.
- **Dynamic image tag (timestamp)**: Ensures every build is **immutable**, **uniquely traceable**, and easy to **roll back/forward**. Still publishing `latest` keeps local/dev workflows simple.
- **Separate `build.sh` & `deploy.sh`**: Clear separation of responsibilities → easier failure isolation and more accurate Slack notifications. Lets you re-run deployments without rebuilding.
- **Slack notifications**: Fast feedback loop; failures surface immediately with useful metadata (image tag, environment, error stage).

---

## Repository Layout

```text
.
├── .github/
│   └── workflows/
│       └── main.yml                  # GitHub Actions pipeline (tests, build, push, deploy, Slack)
├── app/
│   ├── main.py                       # Flask app (returns public IP, /health)
│   ├── requirements.txt
│   └── tests/                        # Unit & integration tests
│       ├── test_health.py
│       └── __init__.py
├── helm-chart/                       # Helm chart to deploy ip-app
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── templates/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
|   |   |── ingress.yaml
│   │   └── _helpers.tpl
├── Dockerfile                        # Container image definition
├── build.sh                          # Build & push Docker image (timestamp tag + latest)
├── deploy.sh                         # Deploy to EKS with Helm
└── README.md
```



---

## 🔄 CI/CD Process (end-to-end)

push to main  
   └── test  
        └── build & push (timestamp tag + latest)  
             └── deploy to EKS with Helm  
                  └── Slack notifications at every stage

### Triggers

- **On every push to `main`** (can easily be extended to PRs or tags).

### Global Environment & Secrets

- **Global env (in the pipeline)**:  
  `APP_NAME`, `CLUSTER_NAME`, `AWS_REGION`, and the dynamically computed `IMAGE_TAG`.
- **Secrets**:  
  - `DOCKER_USERNAME` / `DOCKER_PASSWORD` — Docker Hub authentication.  
  - `SLACK_WEBHOOK_URL` — Incoming webhook.  
  - `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_SESSION_TOKEN` *(optional)* — used to authenticate to EKS without shipping kubeconfig around.

---

### Jobs / Stages

#### 1) **Test**

- Checks out the repo.  
- Sets up Python.  
- Installs deps and test requirements.  
- Runs tests.  

**Why**: Prevents broken code from moving forward to build & deploy.

---

#### 2) **Build & Push**

- Generates a dynamic **`IMAGE_TAG`** based on the build timestamp (for example `2025-07-24T17-05-12Z`).
- Logs in to Docker Hub using GitHub Secrets.
- Executes `scripts/build.sh`, which:
  - Builds the image `DOCKER_USERNAME/APP_NAME:IMAGE_TAG`.
  - Pushes that image.
  - Also pushes `DOCKER_USERNAME/APP_NAME:latest`.
- Posts a **Slack notification** on success/failure.

---

#### 3) **Deploy**

- Authenticates to AWS (`configure-aws-credentials`) and uses the IAM role/keys to get a kube-auth token for the EKS cluster (**no kubeconfig stored**).
- Runs `scripts/deploy.sh`, which:
  - Calls `helm upgrade --install` with:
    - `image.repository=DOCKER_USERNAME/APP_NAME`
    - `image.tag=${IMAGE_TAG}` (the timestamp tag)
  - Any environment-specific overrides via `values.yaml` (replicas, resources, etc.).
- Posts a **Slack notification** on success/failure.

---

## The Scripts

### `build.sh`

- Reads `APP_NAME`, `DOCKER_USERNAME`.
- Receives `IMAGE_TAG` from the pipeline (build timestamp).
- Builds the Docker image.
- Pushes the timestamp-tagged image.
- Also tags & pushes `latest`.
- Exits with a proper status code (so CI can notify accordingly).

### `deploy.sh`

- Reads `APP_NAME`, `CLUSTER_NAME`, `AWS_REGION`, `IMAGE_TAG`, `DOCKER_USERNAME`.
- Assumes kubectl/helm context is already authenticated.
- Runs `helm upgrade --install` with the correct chart path (`helm-chart/`) and values set from env vars.
- Exits properly to signal success/failure.

---

## Slack Notifications

- A **Slack Incoming Webhook URL** is stored securely in GitHub Secrets.
- Each stage (**test / build / deploy**) posts a message on:
  - **Success** – includes image tag and stage name.
  - **Failure** – includes the same plus the failing step, making it easy to jump to the logs.
- **Benefits**:
  - Immediate visibility without logging into GitHub.
  - Track which exact image tag was deployed.
  - Quickly distinguish build failures from deploy failures.

---

## How to Run Everything 

1. **Push code** to `main` → CI triggers automatically.  
2. CI **runs tests** → fails fast if tests break.  
3. CI **builds & pushes** image → Docker Hub receives both **timestamp** & **latest**.  
4. CI **deploys to EKS via Helm** → K8s updates the running app.  
5. **Slack** gets the final outcome messages for each stage.

## Output
- The output of my app is "My public IP is: 13.60.9.188" - the external ip of the Kubernetes cluster node the pod is running on.
- I used Service type LoadBalancer to check the validity of the app, but there is a ready helm chart to create an Ingress, all you need to do is to enable in values and set the hostname. 
---

