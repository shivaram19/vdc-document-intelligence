import sqlite3
import json
from typing import List, Tuple
from extractors.entity_extractor import Entity


class EntityStore:
    def __init__(self, db_path: str = "./medha_entities.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_tables()

    def _init_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                doc_id TEXT NOT NULL,
                chunk_id TEXT,
                text TEXT,
                entity_type TEXT,
                value TEXT,
                unit TEXT,
                confidence REAL
            );
            CREATE INDEX IF NOT EXISTS idx_entities_project ON entities(project_id);
            CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(project_id, entity_type);

            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                spec_entity_id TEXT NOT NULL,
                draw_entity_id TEXT NOT NULL,
                score REAL,
                UNIQUE(project_id, spec_entity_id, draw_entity_id)
            );
            CREATE INDEX IF NOT EXISTS idx_links_project ON links(project_id);
        """)
        self.conn.commit()

    def add_entities(self, project_id: str, entities: List[Entity]):
        cursor = self.conn.cursor()
        for e in entities:
            cursor.execute("""
                INSERT OR REPLACE INTO entities
                (id, project_id, doc_id, chunk_id, text, entity_type, value, unit, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (e.id, project_id, e.doc_id, e.chunk_id, e.text,
                  e.entity_type, e.value, e.unit, e.confidence))
        self.conn.commit()

    def get_by_type(self, project_id: str, entity_type: str) -> List[Entity]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, doc_id, chunk_id, text, entity_type, value, unit, confidence
            FROM entities WHERE project_id = ? AND entity_type = ?
        """, (project_id, entity_type))
        return [Entity(*row) for row in cursor.fetchall()]

    def get_all(self, project_id: str) -> List[Entity]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, doc_id, chunk_id, text, entity_type, value, unit, confidence
            FROM entities WHERE project_id = ?
        """, (project_id,))
        return [Entity(*row) for row in cursor.fetchall()]

    def get_by_doc(self, project_id: str, doc_id: str) -> List[Entity]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, doc_id, chunk_id, text, entity_type, value, unit, confidence
            FROM entities WHERE project_id = ? AND doc_id = ?
        """, (project_id, doc_id))
        return [Entity(*row) for row in cursor.fetchall()]

    def save_links(self, project_id: str, links: List[Tuple]):
        cursor = self.conn.cursor()
        for spec_e, draw_e, score in links:
            cursor.execute("""
                INSERT OR REPLACE INTO links
                (project_id, spec_entity_id, draw_entity_id, score)
                VALUES (?, ?, ?, ?)
            """, (project_id, spec_e.id, draw_e.id, score))
        self.conn.commit()

    def get_links(self, project_id: str) -> List[dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT l.spec_entity_id, l.draw_entity_id, l.score,
                   e1.text as spec_text, e1.value as spec_value, e1.unit as spec_unit,
                   e2.text as draw_text, e2.value as draw_value, e2.unit as draw_unit
            FROM links l
            JOIN entities e1 ON l.spec_entity_id = e1.id
            JOIN entities e2 ON l.draw_entity_id = e2.id
            WHERE l.project_id = ?
        """, (project_id,))

        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def delete_project(self, project_id: str):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM links WHERE project_id = ?", (project_id,))
        cursor.execute("DELETE FROM entities WHERE project_id = ?", (project_id,))
        self.conn.commit()
