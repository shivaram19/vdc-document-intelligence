#!/usr/bin/env python3
"""
CLI for ingesting construction documents into a Medha project workspace.

Usage:
    python scripts/ingest_documents.py create-project "Project Name" --client "Client" --number "12345"
    python scripts/ingest_documents.py ingest <project_id> /path/to/drawing.pdf
    python scripts/ingest_documents.py list-projects
    python scripts/ingest_documents.py list-documents <project_id>
"""

import argparse
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from ingestion import DocumentIngestor, ProjectStore


def cmd_create_project(args):
    store = ProjectStore()
    ingestor = DocumentIngestor(store)
    project = ingestor.create_project(
        name=args.name,
        description=args.description or "",
        client_name=args.client or "",
        project_number=args.number or "",
    )
    print(f"Created project: {project.name}")
    print(f"  ID: {project.id}")
    print(f"  Workspace: {project.workspace_path}")


def cmd_ingest(args):
    store = ProjectStore()
    ingestor = DocumentIngestor(store)
    document = ingestor.ingest(
        project_id=args.project_id,
        file_path=args.file_path,
        title=args.title or "",
        extract_sheets=not args.no_sheets,
        extract_text=not args.no_text,
    )
    print(f"Ingested document: {document.original_filename}")
    print(f"  ID: {document.id}")
    print(f"  Type: {document.document_type.value}")
    print(f"  Discipline: {document.discipline.value}")
    print(f"  Status: {document.processing_status}")
    if document.processing_error:
        print(f"  Error: {document.processing_error}")
    print(f"  Sheets: {len(document.sheets)}")
    for sheet in document.sheets:
        print(f"    - {sheet.number}: {sheet.title} [{sheet.discipline.value}] rev={sheet.revision}")


def cmd_list_projects(args):
    store = ProjectStore()
    projects = store.list_projects()
    if not projects:
        print("No projects found.")
        return
    for project in projects:
        print(f"{project.id} | {project.name} | {project.client_name} | {project.created_at.date()}")


def cmd_list_documents(args):
    store = ProjectStore()
    documents = store.list_documents(args.project_id)
    if not documents:
        print("No documents found for project.")
        return
    for doc in documents:
        print(f"{doc.id} | {doc.original_filename} | {doc.document_type.value} | {doc.discipline.value} | {doc.processing_status}")


def main():
    parser = argparse.ArgumentParser(description="Medha document ingestion CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create-project", help="Create a new project")
    create_parser.add_argument("name", help="Project name")
    create_parser.add_argument("--description", help="Project description")
    create_parser.add_argument("--client", help="Client name")
    create_parser.add_argument("--number", help="Project number")
    create_parser.set_defaults(func=cmd_create_project)

    ingest_parser = subparsers.add_parser("ingest", help="Ingest a document")
    ingest_parser.add_argument("project_id", help="Project ID")
    ingest_parser.add_argument("file_path", help="Path to file")
    ingest_parser.add_argument("--title", help="Document title")
    ingest_parser.add_argument("--no-sheets", action="store_true", help="Skip sheet extraction")
    ingest_parser.add_argument("--no-text", action="store_true", help="Skip text extraction")
    ingest_parser.set_defaults(func=cmd_ingest)

    list_projects_parser = subparsers.add_parser("list-projects", help="List all projects")
    list_projects_parser.set_defaults(func=cmd_list_projects)

    list_docs_parser = subparsers.add_parser("list-documents", help="List documents in a project")
    list_docs_parser.add_argument("project_id", help="Project ID")
    list_docs_parser.set_defaults(func=cmd_list_documents)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
