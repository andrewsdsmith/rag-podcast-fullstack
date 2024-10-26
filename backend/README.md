## Overview

[Zoe Science & Nutrition](https://www.youtube.com/@joinZOE) is the No. 1 health podcast in the UK and my personal favorite. Each episode includes any number of "in-house" scientists and/or guest experts discussing the latest health and nutrition research.

To show my appreciation for their content I created a simple [RAG]() application that allows users to make health queries and get a summarised response based on the podcast episodes. The response includes episode titles and links to 5-minute segments where the topic was discussed.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)

## Prerequisites

I did some preprocessing to the transcripts that included summarising 5 minute segments and creating embeddings using `jinaai/jina-embeddings-v3`. This model ranks highly on the [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard) considering it's size, has a small memory footprint and produces a rich 1024 dimensional embedding.

The preprocessing has been left out of this repo as I don't want to encourage any form of copyright infringement. This project is for educational purposes only.

To use this repo you will need the following:

1. Preprocessed transcripts in the form `title`, `url_at_time` (this is the start time for a summarry segment), `summary`, `embedding`
