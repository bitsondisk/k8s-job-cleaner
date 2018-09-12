.PHONY: docker push latest

IMAGE    ?= gcr.io/freenome-build/k8s-job-cleaner
VERSION  ?= $(shell git describe --tags --always --dirty)
TAG      ?= $(VERSION)

default: docker

docker:
	docker build -t "$(IMAGE):$(TAG)" .
	@echo 'Docker image $(IMAGE):$(TAG) can now be used.'

push: docker
	docker push "$(IMAGE):$(TAG)"

latest:
	gcloud container images add-tag "$(IMAGE):$(TAG)" "$(IMAGE):latest"
