# Week 5 – CI/CD and Local AI Chat

## 1. Overview

This project implements a self-hosted AI chat application on Server A. The application uses Flask, Gunicorn, MariaDB and Ollama. GitHub Actions performs automated testing and deployment.

The application is available at:

- Chat: `http://193.166.25.4/viikko5/`
- Health check: `http://193.166.25.4/viikko5/health`

## 2. Architecture

The application runs on Server A.

- Nginx is the only public-facing application service.
- Nginx proxies `/viikko5/` to Gunicorn on `127.0.0.1:5002`.
- Gunicorn runs the Flask application as the dedicated Linux user `week5`.
- Ollama provides the local language model through `127.0.0.1:11434`.
- MariaDB stores chat messages in the separate database `week5db`.
- The application connects to MariaDB through its local Unix socket.

The application and Ollama are not exposed directly to the public network.

## 3. Technology

- Ubuntu Server 24.04
- Python and Flask
- Gunicorn
- MariaDB
- Ollama
- Nginx
- GitHub Actions
- Pytest and Ruff

The local model used is `smollm2:135m-instruct-q4_0`.


## 4. Security

- The application runs under a dedicated non-login Linux user named `week5`.
- Gunicorn listens only on `127.0.0.1:5002`.
- Ollama listens only on `127.0.0.1:11434`.
- Nginx provides the public HTTP endpoint.
- GitHub Actions uses a separate SSH key for deployment.
- No passwords or private keys are committed to the repository.


## 5. CI/CD pipeline

The workflow is defined in:

`.github/workflows/week5-ci-cd.yml`


### Deploy to Server A

Runs only after successful tests and only for pushes to the `main` branch.

The deployment:

1. Connects to Server A using the dedicated SSH key.
2. Copies the Week 5 application files to the server.
3. Installs Python dependencies.
4. Installs the Nginx and systemd configuration.
5. Tests the Nginx configuration before reloading it.
6. Restarts only the `week5` service.
7. Checks the health endpoint and verifies the deployed Git commit SHA.

A failed test prevents the deployment job from running.

## 6. Deployment verification

Two successful deployments have been verified using the health endpoint.

First successful deployment:

`61e7ee29088eb516f91c8d834395817ca778b296`

Second successful deployment:

`56442cd1c3eaa3d6eea8f92415beb0be8d411f06`


## 7. Failed test verification

The test job failed, and the deployment job was skipped.

GitHub Actions run:

https://github.com/Perttu13/linux/actions/runs/46127852906

## 8. Testing

The tests are located in `tests/`.

They verify:

- The home page loads.
- The health endpoint responds.
- Empty messages are rejected.
- Chat responses work with mocked database and Ollama services.


## 9. Week 4 compatibility

The Week 5 application is separate from the Week 4 application and database.

The existing Week 4 MariaDB replication and backup configuration are not changed by this deployment. Week 5 chat data is not replicated to Server B.

## 10. Files

- `app.py` – Flask application
- `templates/index.html` – chat interface
- `requirements.txt` – Python dependencies
- `schema.sql` – MariaDB schema
- `tests/` – automated tests
- `deploy.sh` – deployment script
- `nginx-week5.conf` – Nginx configuration
- `week5.service` – systemd service configuration
- `.github/workflows/week5-ci-cd.yml` – CI/CD workflow
