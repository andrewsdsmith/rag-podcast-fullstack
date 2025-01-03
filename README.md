## RAG Application for Zoe Science & Nutrition Podcast

> **Note:** This is a hobby project used to expand my own knowledge. The information contained here is based on the use of the application in this context.

[Zoe Science & Nutrition](https://www.youtube.com/@joinZOE) is a popular and informative health and nutrition podcast. This repo contains a Fullstack RAG application that allows users to make health queries that are answered using the podcast transcripts. Answers include episode titles and links to 5-minute youtube segments where the topic was discussed.

The application is deployed to an EC2 instance and is currently available at [healthchat.jasmine-tea.xyz](https://healthchat.jasmine-tea.xyz/) as a demonstration.

You can also run it locally using Docker by following the instructions in [Running the application locally](#running-the-application-locally).

Thank you amazing and clever people at:

- [Zoe Science & Nutrition](https://www.youtube.com/@joinZOE) for the podcast
- [Jina AI](https://jina.ai/) for the amazing embedding model and generous free tier
- FastAPI team for [FastAPI](https://fastapi.tiangolo.com/) and [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template)
- Contributors to [PgVector](https://github.com/pgvector/pgvector)

## Table of Contents

- [Intro](#rag-application-for-zoe-science--nutrition-podcast)
- [Prerequisites](#prerequisites)
- [Code Quality](#code-quality)
- [Testing](#testing)
- [Deployment Setup](#deployment-setup)
- [Running the application locally](#running-the-application-locally)

## Prerequisites

I did some preprocessing to the transcripts that included summarising 5 minute segments and creating embeddings using `jinaai/jina-embeddings-v3`. This model ranks highly on the [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard) considering it's size, has a small memory footprint and produces a rich 1024 dimensional embedding. Thereofore, the same model has been used for generating embeddings of user questions before cosine similarity search on the podcast transcripts.

> **Note:** The preprocessing has been left out of this repo as it doesn't fit the scope of this particular project. It was run "once-off" and not designed to be a real-time pipeline into our database.

For the answer generation I have used OpenAI's GPT-4 model.

Therefore, to run the application in any environment you will need to have the following:

- A Jina Embeddings API key. This is available for free at [Jina Embeddings API](https://jina.ai/embeddings/)
- An OpenAI API key.

I have provided a `.env.template` file in the root directory that you can use to set up a `.env` file for local development. For deployment you can update your Github secrets which will be used in the [workflow](.github/workflows/deploy.yml) to copy over the environment variables using AWS SSM.

# Code Quality

Linting and formatting checks are run on each push to the repository using the following [workflow](.github/workflows/linting-backend.yml). The checks are run using [ruff](https://docs.astral.sh/ruff/) and [mypy](https://mypy.readthedocs.io/en/stable/).

# Testing

Integration tests are run on pull requests and merges into main and a coverage report is saved as an artifact after each run. The workflow can be found [here](.github/workflows/integration-tests-backend.yml). Testing is done using [pytest](https://docs.pytest.org/en/6.2.x/) and coverage is calculated using [pytest-cov](https://github.com/pytest-dev/pytest-cov).

To run tests locally, you can use the following command from the root directory:

```bash
docker compose -f docker-compose-test.yml up --build
```

## Deployment Setup

The [backend](.github/workflows/build-and-push-backend.yml) and [frontend](.github/workflows/build-and-push-frontend.yml) images can be built and pushed separately using github actions and with a manual trigger. There is a [separate workflow](.github/workflows/deploy.yml) to copy over config and environment variables to AWS EC2 using SSM which is also triggered manually.

To run all the workflows and to deploy to AWS please ensure you have configured all of the repository secrets used in the workflows and configured AWS accordingly.

On your EC2 instance you can spinup the application using the deployment script copied over by the deploy workflow:

```bash
bash deploy.sh
```

> **Note:**
> If you haven't generated certificates before you will first need to register a domain and point it to your EC2 IP address. Then on your EC2 run the certbot container with a limited [nginx config](/nginx.conf) (allowing http traffic initially) to retrieve the certificate for your domain. Don't forget to use the [production nginx config](/nginx.deployment.conf) after you have the certificate.

## Running the application locally

> **Note:** Don't fogret to set up your environment variables in the `.env` file. See [Prerequisites](#prerequisites) for more information.

1. Clone the repo
2. In the root directory run `docker compose -f docker-compose-local.yml up --build`
3. The application will be available at `http://localhost:80`
