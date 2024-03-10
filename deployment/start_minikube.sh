#!/usr/bin/env bash

# Basic wrapper script to launch minikube

# If the environment variable CPU is set use it, otherwise default to 2
CPUS=${CPU:-2}

# If the environment variable MEMORY is set use it, otherwise default to 4096
MEMORY=${MEMORY:-4096}

# Driver
VM_DRIVER="docker"

# Minikube Cluster Profile
CLUSTER_PROFILE="my-askbucky-cluster"

B64COMMAND="base64 -w 0"
if [[ "$OSTYPE" == "darwin"* ]]; then 
    B64COMMAND="base64"
fi

# Check for existence of minikube
if ! command -v minikube >/dev/null 2>&1; then
	echo "minikube is not installed. Install minikube from here: https://minikube.sigs.k8s.io/docs/start/"
	exit -1
fi

# Start Minikube cluster
minikube start --cpus=${CPUS} --memory=${MEMORY} --vm-driver=${VM_DRIVER} --profile=${CLUSTER_PROFILE}

# Wait for cluster to be ready
minikube status --profile=${CLUSTER_PROFILE}

# Create app namespace
kubectl create namespace app

# Apply manifests to setup serviceaccount, role, and role-binding
kubectl apply -f deployment/serviceaccount.yml
kubectl apply -f deployment/role.yml
kubectl apply -f deployment/role-binding.yml

# Create k8s secret that has access to our Docker Hub, using our shared credentials
kubectl create secret docker-registry dockerhub-secret \
	--docker-server=https://index.docker.io/v1/ \
	--docker-username='joshuajerome' \
	--docker-password='6srwK4vV3b.uuskng@s3dFKk' \
	--docker-email='joshua.jerome@gmail.com' -n app

# Get cluster info
kubectl cluster-info

# Verify cluster nodes
kubectl get nodes

# Verify running pods
kubectl get pods --all-namespaces