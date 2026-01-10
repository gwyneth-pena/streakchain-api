

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from db import get_db
from schemas.notes import NoteCreate
from services.notes import remove_note, save_note
from utils.decorators import jwt_required
from utils.shared import validation_error


router = APIRouter(prefix="/notes", tags=["notes"])

@router.post("/create")
@jwt_required
def create_note(payload: NoteCreate, request: Request, db: Session = Depends(get_db)):
    payload.user_id = request.state.user_id
    note = save_note(payload, db)
    return note


@router.delete('/{note_id}')
@jwt_required
def delete_note(note_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    
    res = remove_note(note_id, user_id, db)

    if not res:
        validation_error("note", "Note not found.", "note", 404)

    return {"message": "Note deleted successfully."}