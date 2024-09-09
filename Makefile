.PHONY: default env_install test build_container clean

ENV := .venv
SYSTEM_PYTHON := python3
PYTHON_VERSION := 3.12.5
ENV_PYTHON := ${ENV}/bin/python3
ENV_SITE_PACKAGES := ${ENV}/lib/python${PYTHON_VERSION}/site-packages
PROJECT_PACKAGE_NAME := eco_pytests
ENV_PROJECT_PACKAGE_PATH := ${ENV_SITE_PACKAGES}/${PROJECT_PACKAGE_NAME}-%
CONTAINER_NAME := weaviatest
VERSION ?= latest #$(shell git rev-parse --short HEAD)
PUSH_TAG ?= latest

default: test

${ENV_PYTHON}:
	@echo "Creating Python ${PYTHON_VERSION} environment..." >&2
	@${SYSTEM_PYTHON} -m venv ${ENV}
	@${ENV_PYTHON} -m pip install -U pip setuptools

${ENV_PROJECT_PACKAGE_PATH}: ${ENV_PYTHON}
	@echo "Installing Python project in ${ENV_SITE_PACKAGES}"
	@${ENV_PYTHON} -m pip install .

env_install: ${ENV_PROJECT_PACKAGE_PATH}

test: ${ENV_PROJECT_PACKAGE_PATH}

build_container:
	docker build -t ${CONTAINER_NAME}:${VERSION} .

clean:
	@rm -rf ${ENV}