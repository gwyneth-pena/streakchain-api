from models.notes import Note
from schemas.notes import NoteCreate
from sqlalchemy.orm import Session


def save_note(payload: NoteCreate, db: Session):
    note = Note(**payload.model_dump(exclude_unset=True))

    db.add(note)
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