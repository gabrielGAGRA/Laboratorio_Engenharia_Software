"""SQLite implementation of the Jam session and queue persistence port."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import sqlite3

from app.application.ports.repositories.jam_repository import JamRepositoryPort
from app.domain.models.jam import Jam, JamQueueItem


def _row_to_jam(row: sqlite3.Row) -> Jam:
    created_at = (
        datetime.fromisoformat(row["created_at"]) if row["created_at"] else None
    )
    return Jam(
        jam_id=row["jam_id"],
        host_user_id=row["host_user_id"],
        room_name=row["room_name"],
        room_code=row["room_code"],
        is_active=bool(row["is_active"]),
        current_track_id=row["current_track_id"],
        created_at=created_at,
    )


def _row_to_queue_item(row: sqlite3.Row) -> JamQueueItem:
    added_at = datetime.fromisoformat(row["added_at"]) if row["added_at"] else None
    return JamQueueItem(
        jam_queue_id=row["jam_queue_id"],
        jam_id=row["jam_id"],
        track_id=row["track_id"],
        initial_vote_points=int(row["vote_points"]),
        added_at=added_at,
    )


class SQLiteJamRepository(JamRepositoryPort):
    """SQLite adapter implementing JamRepositoryPort."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def find_by_id(self, jam_id: int) -> Jam | None:
        cursor = self.conn.execute(
            "SELECT * FROM jams WHERE jam_id = ?",
            (jam_id,),
        )
        row = cursor.fetchone()
        return _row_to_jam(row) if row else None

    def find_by_code(self, room_code: str) -> Jam | None:
        cursor = self.conn.execute(
            "SELECT * FROM jams WHERE room_code = ? AND is_active = 1",
            (room_code,),
        )
        row = cursor.fetchone()
        return _row_to_jam(row) if row else None

    def save(self, jam: Jam) -> Jam:
        if jam.jam_id is not None:
            cursor = self.conn.execute(
                "SELECT jam_id FROM jams WHERE jam_id = ?",
                (jam.jam_id,),
            )
            if cursor.fetchone():
                self.conn.execute(
                    """
                    UPDATE jams
                    SET host_user_id = ?,
                        room_name = ?,
                        room_code = ?,
                        is_active = ?,
                        current_track_id = ?
                    WHERE jam_id = ?
                    """,
                    (
                        jam.host_user_id,
                        jam.room_name,
                        jam.room_code,
                        1 if jam.is_active else 0,
                        jam.current_track_id,
                        jam.jam_id,
                    ),
                )
                self.conn.commit()
                return self.find_by_id(jam.jam_id) or jam

        created_at_str = (jam.created_at or datetime.now(UTC)).isoformat()
        cursor = self.conn.execute(
            """
            INSERT INTO jams (
                host_user_id, room_name, room_code, is_active, current_track_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                jam.host_user_id,
                jam.room_name,
                jam.room_code,
                1 if jam.is_active else 0,
                jam.current_track_id,
                created_at_str,
            ),
        )
        self.conn.commit()
        new_id = cursor.lastrowid
        return self.find_by_id(new_id) or jam

    def find_queue_item(self, jam_id: int, track_id: int) -> JamQueueItem | None:
        cursor = self.conn.execute(
            """
            SELECT * FROM jam_queue_items
            WHERE jam_id = ? AND track_id = ?
            """,
            (jam_id, track_id),
        )
        row = cursor.fetchone()
        return _row_to_queue_item(row) if row else None

    def save_queue_item(self, item: JamQueueItem) -> JamQueueItem:
        cursor = self.conn.execute(
            """
            SELECT jam_queue_id FROM jam_queue_items
            WHERE jam_id = ? AND track_id = ?
            """,
            (item.jam_id, item.track_id),
        )
        existing = cursor.fetchone()
        if existing:
            self.conn.execute(
                """
                UPDATE jam_queue_items
                SET vote_points = ?
                WHERE jam_id = ? AND track_id = ?
                """,
                (item.vote_points, item.jam_id, item.track_id),
            )
            self.conn.commit()
            return self.find_queue_item(item.jam_id, item.track_id) or item

        added_at_str = (item.added_at or datetime.now(UTC)).isoformat()
        cursor = self.conn.execute(
            """
            INSERT INTO jam_queue_items (jam_id, track_id, vote_points, added_at)
            VALUES (?, ?, ?, ?)
            """,
            (item.jam_id, item.track_id, item.vote_points, added_at_str),
        )
        self.conn.commit()
        return self.find_queue_item(item.jam_id, item.track_id) or item

    def list_queue(self, jam_id: int) -> list[JamQueueItem]:
        cursor = self.conn.execute(
            """
            SELECT * FROM jam_queue_items
            WHERE jam_id = ?
            ORDER BY vote_points DESC, added_at ASC
            """,
            (jam_id,),
        )
        rows = cursor.fetchall()
        return [_row_to_queue_item(r) for r in rows]

    def remove_track_from_queue(self, jam_id: int, track_id: int) -> bool:
        cursor = self.conn.execute(
            """
            DELETE FROM jam_queue_items
            WHERE jam_id = ? AND track_id = ?
            """,
            (jam_id, track_id),
        )
        self.conn.commit()
        return cursor.rowcount > 0


__all__ = ["SQLiteJamRepository"]
