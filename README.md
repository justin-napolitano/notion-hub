
# Notion Task Hub (Docker)

This project bootstraps a clean **Task Hub** in Notion:
- Creates a **Dashboard** page under your chosen parent page
- Creates **📁 Projects** and **✅ Master Tasks** databases
- Adds a Relation from Tasks → Projects
- Seeds a few example projects/tasks
- Adds links on the Dashboard to both databases

## Prereqs
- A Notion **internal integration** with access to the destination workspace/databases
- Your integration token: `NOTION_TOKEN`
- The ID of an existing Notion page to use as the parent: `ROOT_PAGE_ID`
- Docker

## Quick Start

1. Build the image:
   ```bash
   docker build -t notion-task-hub .
   ```

2. Create a `.env` file from the example and fill in your values:
   ```bash
   cp .env.example .env
   # edit .env to set NOTION_TOKEN and ROOT_PAGE_ID
   ```

3. Run the container (one-time bootstrap):
   ```bash
   docker run --rm --env-file .env notion-task-hub
   ```

   If successful, you’ll see:
   ```
   ✅ Done. Open your Notion dashboard page to see '🧭 Task Hub'.
   ```

### Notes
- You can re-run the container safely; it won’t duplicate the schema. It checks for existing
  Dashboard/Databases by title under the parent page.
- The API cannot currently create **Linked Database views** with UI filters/grouping. Open the
  created databases and add your preferred **Board/Table** views in the UI (e.g., filter `Status is not Done`).

## Project Layout
```text
.
├─ Dockerfile
├─ requirements.txt
├─ .env.example
├─ src/
│  └─ bootstrap_notion_task_hub.py
└─ README.md
```

## Environment Variables
- `NOTION_TOKEN` — your internal integration token (e.g., starts with `secret_...`)
- `ROOT_PAGE_ID` — the **parent page ID** where the Dashboard and databases will be created

## Troubleshooting
- **403 / permission errors**: Ensure your integration is invited to the parent page and has access to create databases.
- **Invalid page ID**: Confirm the `ROOT_PAGE_ID` is a valid Notion page (UUID form works best).
- **Nothing appears**: Double-check the environment variables and that you’re in the correct workspace.
