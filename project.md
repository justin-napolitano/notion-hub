---
slug: github-notion-hub
id: github-notion-hub
title: Automate Notion Task Management with Python and Docker
repo: justin-napolitano/notion-hub
githubUrl: https://github.com/justin-napolitano/notion-hub
generatedAt: '2025-11-24T21:35:47.041Z'
source: github-auto
summary: >-
  Set up a task management workspace in Notion using Python and Docker with this
  straightforward automation tool.
tags:
  - python
  - docker
seoPrimaryKeyword: notion task hub automation
seoSecondaryKeywords:
  - notion workspace setup
  - python docker integration
  - task management tool
  - notion api usage
  - automate task management
seoOptimized: true
topicFamily: null
topicFamilyConfidence: null
kind: project
entryLayout: project
showInProjects: true
showInNotes: false
showInWriting: false
showInLogs: false
---

Notion Task Hub is a Python-based tool that automates the creation of a task management workspace within Notion. It bootstraps a clean Task Hub setup including a Dashboard page, Projects and Master Tasks databases, and the necessary relations between them.

## Features

- Creates a Dashboard page under a specified parent page in Notion
- Creates two databases: Projects and Master Tasks
- Adds a relation property linking Tasks to Projects
- Seeds example projects and tasks for immediate use
- Runs safely multiple times without duplicating schema

## Tech Stack

- Python 3
- Notion API (via notion-client Python SDK)
- Docker for containerization

## Getting Started

### Prerequisites

- A Notion internal integration with access to your workspace
- Integration token (`NOTION_TOKEN`)
- ID of an existing Notion page to serve as the parent (`ROOT_PAGE_ID`)
- Docker installed

### Installation and Usage

1. Clone the repository:

   ```bash
   git clone https://github.com/justin-napolitano/notion-hub.git
   cd notion-hub
   ```

2. Build the Docker image:

   ```bash
   docker build -t notion-task-hub .
   ```

3. Create a `.env` file from the example and set your environment variables:

   ```bash
   cp .env.example .env
   # Edit .env to set NOTION_TOKEN and ROOT_PAGE_ID
   ```

4. Run the container to bootstrap the Task Hub:

   ```bash
   docker run --rm --env-file .env notion-task-hub
   ```

   On success, you will see:

   ```
   ✅ Done. Open your Notion dashboard page to see 'Task Hub'.
   ```

### Notes

- The script checks for existing Dashboard and databases by title and will not duplicate them.
- Linked database views with UI filters/grouping must be configured manually in Notion.

## Project Structure

```
.
├─ Dockerfile
├─ requirements.txt
├─ .env.example
├─ src/
│  └─ bootstrap_notion_task_hub.py
├─ README.md
├─ build.sh
└─ run.sh
```

- `Dockerfile`: Defines the container image
- `requirements.txt`: Python dependencies
- `.env.example`: Example environment variables
- `src/bootstrap_notion_task_hub.py`: Main Python script to create the Task Hub
- `build.sh` and `run.sh`: Convenience scripts for building and running the Docker container

## Future Work / Roadmap

- Add support for creating linked database views with filters and grouping via the API
- Expand seeded example data for more comprehensive templates
- Add CLI flags for customization without rebuilding the container
- Improve error handling and logging
- Support for updating existing schema properties

---

This project assumes familiarity with Notion API tokens and page IDs, as well as basic Docker usage. It is designed for users who want to quickly set up a task management workspace in Notion programmatically.

