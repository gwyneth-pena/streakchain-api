from sqlalchemy import and_, func
from models.notes import Note
from schemas.notes import NoteCreate, NoteUpdate
from sqlalchemy.orm import Session, with_loader_criteria

from utils.shared import validation_error


def save_note(payload: NoteCreate, db: Session):
    note = Note(**payload.model_dump(exclude_unset=True))

    db.add(note)
    db.commit()
    db.refresh(note)

    return note


def patch_note(payload: NoteUpdate, db: Session):
    note = db.query(Note).filter(Note.id == payload.id, Note.user_id == payload.user_id).first()

    if note is None:
        validation_error("note", "Note not found.", "note", 404)
    
    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(note, field, value)

    db.commit()
    db.refresh(note)

    return note


def remove_note(note_id: int, user_id: int, db: Session):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()

    if note is None:
        return False
    
    db.delete(note)
    db.commit()

    return True


def get_notes_by_user_id(payload, user_id: int, db: Session):
    options = [
    ]

    filters = []

    if payload.start_date:
        filters.append(func.date(Note.created_at) >= payload.start_date)
    
    if payload.end_date:
        filters.append(func.date(Note.created_at) <= payload.end_date)

    if len(filters) > 0:
        options.append(
            with_loader_criteria(
                Note,
                and_(*filters),
                include_aliases=True
            )
        )

    notes = (db.query(Note).options(*options)
                .filter(Note.user_id == user_id)
                .order_by(Note.created_at.asc())
                .all()
            )
    
    return notes