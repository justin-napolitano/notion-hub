#!/usr/bin/env python3
import os
import sys
from typing import Optional, Dict, Any, List
from notion_client import Client
from notion_client.helpers import collect_paginated_api

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
ROOT_PAGE_ID = os.environ.get("ROOT_PAGE_ID")

if not NOTION_TOKEN or not ROOT_PAGE_ID:
    print("ERROR: Please set NOTION_TOKEN and ROOT_PAGE_ID environment variables.")
    sys.exit(1)

notion = Client(auth=NOTION_TOKEN)

DASHBOARD_TITLE = "🧭 Task Hub"
PROJECTS_DB_TITLE = "📁 Projects"
TASKS_DB_TITLE = "✅ Master Tasks"

def ensure_dashboard(parent_page_id: str) -> str:
    # Try to find an existing child page named DASHBOARD_TITLE under ROOT_PAGE_ID
    children = collect_paginated_api(notion.blocks.children.list, block_id=parent_page_id)
    for ch in children:
        if ch.get("type") == "child_page" and ch.get("child_page", {}).get("title") == DASHBOARD_TITLE:
            return ch["id"]
    # Create it if missing
    page = notion.pages.create(
        parent={"type": "page_id", "page_id": parent_page_id},
        properties={
            "title": {
                "title": [{"type": "text", "text": {"content": DASHBOARD_TITLE}}]
            }
        }
    )
    return page["id"]

def find_database_under(parent_page_id: str, title: str) -> Optional[str]:
    # Look for a child_database with given title
    children = collect_paginated_api(notion.blocks.children.list, block_id=parent_page_id)
    for ch in children:
        if ch.get("type") == "child_database" and ch.get("child_database", {}).get("title") == title:
            return ch["id"]
    return None

def create_projects_db(parent_page_id: str) -> str:
    db = notion.databases.create(
        parent={"type": "page_id", "page_id": parent_page_id},
        title=[{"type": "text", "text": {"content": PROJECTS_DB_TITLE}}],
        properties={
            "Name": {"title": {}},
            "Status": {"status": {}},  # "Not started" / "In progress" / "Done"
            "Area": {"select": {"options": [
                {"name": "Work"}, {"name": "Personal"}, {"name": "Side Project"}
            ]}},
            "Notes": {"rich_text": {}}
        }
    )
    return db["id"]

def create_tasks_db(parent_page_id: str, projects_db_id: str) -> str:
    db = notion.databases.create(
        parent={"type": "page_id", "page_id": parent_page_id},
        title=[{"type": "text", "text": {"content": TASKS_DB_TITLE}}],
        properties={
            "Name": {"title": {}},
            "Status": {"status": {}},  # native Status property
            "Due": {"date": {}},
            "Priority": {"select": {"options": [
                {"name": "High"}, {"name": "Medium"}, {"name": "Low"}
            ]}},
            "Project": {"relation": {"database_id": projects_db_id, "single_property": {}}},
            "Estimate (hrs)": {"number": {"format": "number"}},
            "Notes": {"rich_text": {}},
            # convenience text field to store source id if you ever sync/migrate later
            "Source Page ID": {"rich_text": {}}
        }
    )
    return db["id"]

def ensure_projects_db(dashboard_id: str) -> str:
    existing = find_database_under(dashboard_id, PROJECTS_DB_TITLE)
    if existing:
        return existing
    return create_projects_db(dashboard_id)

def ensure_tasks_db(dashboard_id: str, projects_db_id: str) -> str:
    existing = find_database_under(dashboard_id, TASKS_DB_TITLE)
    if existing:
        return existing
    return create_tasks_db(dashboard_id, projects_db_id)

def seed_projects(projects_db_id: str) -> List[str]:
    sample = [
        ("Personal Systems", "Side Project", "In progress"),
        ("Career & Learning", "Personal", "Not started"),
        ("Household Ops", "Personal", "In progress")
    ]
    ids = []
    for name, area, status in sample:
        page = notion.pages.create(
            parent={"database_id": projects_db_id},
            properties={
                "Name": {"title": [{"type":"text","text":{"content": name}}]},
                "Area": {"select": {"name": area}},
                "Status": {"status": {"name": status}}
            }
        )
        ids.append(page["id"])
    return ids

def seed_tasks(tasks_db_id: str, projects: List[str]) -> None:
    samples = [
        ("Set up weekly review", "High", "In progress", None, projects[0]),
        ("Draft Q1 goals", "Medium", "Not started", None, projects[1]),
        ("Clean inbox to zero", "Low", "Not started", None, projects[2]),
    ]
    for name, priority, status, due, project_id in samples:
        props = {
            "Name": {"title": [{"type":"text","text":{"content": name}}]},
            "Priority": {"select": {"name": priority}},
            "Status": {"status": {"name": status}},
            "Project": {"relation": [{"id": project_id}]}
        }
        if due:
            props["Due"] = {"date": {"start": due}}
        notion.pages.create(parent={"database_id": tasks_db_id}, properties=props)

def append_links_to_dashboard(dashboard_id: str, projects_db_id: str, tasks_db_id: str) -> None:
    notion.blocks.children.append(
        block_id=dashboard_id,
        children=[
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type":"text","text":{"content":"Your Databases"}}]}
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type":"text","text":{"content":"Open the databases below and add your preferred views (Board grouped by Status, Table filtered to \"Status is not Done\", etc.)."}}]}
            },
            {
                "object": "block",
                "type": "link_to_page",
                "link_to_page": {"type":"database_id","database_id": tasks_db_id}
            },
            {
                "object": "block",
                "type": "link_to_page",
                "link_to_page": {"type":"database_id","database_id": projects_db_id}
            },
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {"rich_text": [{"type":"text","text":{"content":"Tips"}}]}
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text":[{"type":"text","text":{"content":"In Master Tasks, group a Board view by Project and filter Status != Done."}}]}
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text":[{"type":"text","text":{"content":"Add a Table view sorted by Due asc; add a filter for next 7 days to create a \"This Week\" view."}}]}
            }
        ]
    )

def ensure_projects_schema(projects_db_id: str):
    db = notion.databases.retrieve(projects_db_id)
    props = db.get("properties", {})
    updates = {}

    # Name (title) will already exist. We won't touch it.

    if "Status" not in props or props["Status"]["type"] != "status":
        updates["Status"] = {"status": {}}

    if "Area" not in props or props["Area"]["type"] != "select":
        updates["Area"] = {
            "select": {
                "options": [
                    {"name": "Work"},
                    {"name": "Personal"},
                    {"name": "Side Project"},
                ]
            }
        }

    if "Notes" not in props or props["Notes"]["type"] != "rich_text":
        updates["Notes"] = {"rich_text": {}}

    if updates:
        notion.databases.update(projects_db_id, properties=updates)


def ensure_tasks_schema(tasks_db_id: str, projects_db_id: str):
    db = notion.databases.retrieve(tasks_db_id)
    props = db.get("properties", {})
    updates = {}

    if "Status" not in props or props["Status"]["type"] != "status":
        updates["Status"] = {"status": {}}

    if "Due" not in props or props["Due"]["type"] != "date":
        updates["Due"] = {"date": {}}

    if "Priority" not in props or props["Priority"]["type"] != "select":
        updates["Priority"] = {
            "select": {
                "options": [
                    {"name": "High"},
                    {"name": "Medium"},
                    {"name": "Low"},
                ]
            }
        }

    if "Project" not in props or props["Project"]["type"] != "relation":
        updates["Project"] = {
            "relation": {
                "database_id": projects_db_id,
                "type": "single_property",
                "single_property": {}
            }
        }

    if "Estimate (hrs)" not in props or props["Estimate (hrs)"]["type"] != "number":
        updates["Estimate (hrs)"] = {"number": {"format": "number"}}

    if "Notes" not in props or props["Notes"]["type"] != "rich_text":
        updates["Notes"] = {"rich_text": {}}

    if "Source Page ID" not in props or props["Source Page ID"]["type"] != "rich_text":
        updates["Source Page ID"] = {"rich_text": {}}

    if updates:
        notion.databases.update(tasks_db_id, properties=updates)


def main():
    dash_id = ensure_dashboard(ROOT_PAGE_ID)
    projects_db_id = ensure_projects_db(dash_id)
    ensure_projects_schema(projects_db_id)  # <-- add this
    
    tasks_db_id = ensure_tasks_db(dash_id, projects_db_id)

    ensure_tasks_schema(tasks_db_id, projects_db_id)  # <-- add this


    # Seed only if databases are empty
    def count_rows(db_id: str) -> int:
        res = notion.databases.query(database_id=db_id, page_size=1)
        return res.get("total", 0) if "total" in res else len(res.get("results", []))

    if count_rows(projects_db_id) == 0:
        project_ids = seed_projects(projects_db_id)
    else:
        # fetch first 3 to connect tasks if needed
        pages = collect_paginated_api(notion.databases.query, database_id=projects_db_id, page_size=3)
        project_ids = [p["id"] for p in pages[:3]]

    if count_rows(tasks_db_id) == 0 and project_ids:
        seed_tasks(tasks_db_id, project_ids)

    # Add helpful links to the dashboard (idempotent enough; multiple runs will add duplicates).
    append_links_to_dashboard(dash_id, projects_db_id, tasks_db_id)

    print("✅ Done. Open your Notion dashboard page to see '🧭 Task Hub'.")

if __name__ == "__main__":
    main()
