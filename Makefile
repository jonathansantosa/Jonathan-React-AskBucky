.DEFAULT_GOAL = all
VERSION=0.1.0 # This is the version of our project. No need to change this in most cases.

# This is the Docker image tag. Change this only when you want to use a custom tag for your dev purpose.
# Do not change this value within this Makefile. Instead, customize it when running `make` via `make TAG=<YOUR_DOCKER_TAG>`
TAG=latest
CONFIGMAP=configmap.yml
KUBECONFIG=$(HOME)/.kube/config

ifndef VERBOSE
.SILENT:
endif


ui-dev: ## Start the UI app locally
	@echo "Starting UI app..."
	@cd ui && yarn dev


build-ui: ## Build the UI bundle
	@echo "Building UI bundle..."
	@cd ui && yarn install
	@cd ui && yarn run build

build-server-image:
	@echo "Building docker image for AskBucky server..."
	docker build . -t joshuajerome/askbucky-server:$(TAG) -f dockerfiles/server/server.dockerfile --no-cache

build-ui-image:
	@echo "Building docker image for AskBucky UI..."
	docker build . -t joshuajerome/askbucky-ui:$(TAG) -f dockerfiles/ui/ui.dockerfile --no-cache

publish-server-image: ## Publish server image to dockerhub
	@echo "Publishing AskBucky server image..."
	docker push joshuajerome/askbucky-server:$(TAG)

publish-ui-image: ## Publish UI image to dockerhub
	@echo "Publishing AskBucky UI image..."
	docker push joshuajerome/askbucky-ui:$(TAG)

# DEPLOYMENT

check-minikube:
	@minikube status --profile my-askbucky-cluster | grep -q "Running" || (echo "Minikube cluster is not running" && exit 1)

# Start minikube cluster.
start-minikube: ## Start the minikube cluster
	@echo "Launching minikube cluster..."
	@cd deployment && ./start_minikube.sh
	
# Stop minikube cluster.
stop-minikube: check-minikube ## Stop the minikube cluster
	@echo "Stopping minikube cluster..."
	@minikube stop --profile my-askbucky-cluster

# Delete minikube cluster.
delete-minikube: ## Delete the minikube cluster
	@echo "Deleting minikube cluster..."
	@minikube delete --profile my-askbucky-cluster

check-secret:
	@if kubectl describe secret dockerhub-secret -n app > /dev/null 2>&1; then \
		echo "dockerhub secret exists" ;\
	else \
		echo "Please create a dockerhub secret using following command and deploy to cluster"; \
		echo "kubectl create secret docker-registry dockerhub-secret --docker-server=https://index.docker.io/v1/ --docker-username=<DOCKERHUB_USERNAME> --docker-password=<DOCKERHUB_PASSWORD> --docker-email=<DOCKERHUB_EMAIL>" && exit 1;\
	fi

deploy-server: ## Deploy server app service to k8s cluster
	@echo "Deploying server..."
	@cd deployment  && kubectl apply -f ${CONFIGMAP} --kubeconfig ${KUBECONFIG}
	@cd deployment  && \
		sed "s/TAG/${TAG}/g" deployment-server.yml |\
		kubectl apply -f - --kubeconfig ${KUBECONFIG}
	@cd deployment && kubectl apply -f service-server.yml --kubeconfig ${KUBECONFIG}

deploy-ui: ## Deploy UI service to k8s cluster
	@echo "Deploying UI..."
	@cd deployment && kubectl apply -f ${CONFIGMAP} --kubeconfig ${KUBECONFIG}
	@cd deployment && sed "s/TAG/${TAG}/g" deployment-ui.yml | kubectl apply -f - --kubeconfig ${KUBECONFIG}
	@cd deployment && kubectl apply -f service-ui.yml --kubeconfig ${KUBECONFIG}

server-restart:
	kubectl apply -f deployment/${CONFIGMAP} -n app --kubeconfig ${KUBECONFIG}
	kubectl rollout restart deployment server -n app --kubeconfig ${KUBECONFIG}

ui-restart:
	kubectl apply -f deployment/${CONFIGMAP} -n app --kubeconfig ${KUBECONFIG}
	kubectl rollout restart deployment ui -n app --kubeconfig ${KUBECONFIG}

minikube-restart: delete-minikube start-minikube deploy-server deploy-ui