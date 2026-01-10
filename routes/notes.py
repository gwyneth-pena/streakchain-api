

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from db import get_db
from schemas.notes import NoteCreate, NoteGet, NoteUpdate
from services.notes import get_notes_by_user_id, patch_note, remove_note, save_note
from utils.decorators import jwt_required
from utils.shared import validation_error


router = APIRouter(prefix="/notes", tags=["notes"])

@router.post("/create")
@jwt_required
def create_note(payload: NoteCreate, request: Request, db: Session = Depends(get_db)):
    payload.user_id = request.state.user_id
    note = save_note(payload, db)
    return note


@router.get('')
@jwt_required
def get_notes(request: Request, db: Session = Depends(get_db), start_date: Optional[date] = Query(None), end_date: Optional[date] = Query(None)):
    user_id = request.state.user_id
    payload = NoteGet(start_date=start_date, end_date=end_date, user_id=user_id)
    notes = get_notes_by_user_id(payload, user_id, db)

    return notes


@router.patch('/{note_id}')
@jwt_required
def update_note(note_id: int, payload: NoteUpdate, request: Request, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    payload.user_id = user_id
    payload.id = note_id
    note = patch_note(payload, db)
    
    return note

@router.delete('/{note_id}')
@jwt_required
def delete_note(note_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = request.state.user_id

    res = remove_note(note_id, user_id, db)

    if not res:
        validation_error("note", "Note not found.", "note", 404)

    return {"message": "Note deleted successfully."} 