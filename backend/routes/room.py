from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas.room import RoomCreate, RoomUpdate, RoomResponse, RoomListResponse
from services.room import (
    create_room,
    list_rooms,
    list_available_rooms,
    list_rooms_in_maintenance,
    get_room,
    update_room,
    delete_room,
    mark_room_reserved,
    mark_room_unreserved,
)

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


@router.post("/", response_model=RoomResponse, status_code=201)
def create_room_endpoint(room_data: RoomCreate, db: Session = Depends(get_db)) -> RoomResponse:
    return create_room(db, room_data)


@router.get("/", response_model=RoomListResponse)
def list_rooms_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: str = Query(None),
    db: Session = Depends(get_db),
) -> RoomListResponse:
    return list_rooms(db, skip, limit, name)


# Rotas estáticas devem vir ANTES de /{room_name}
@router.get("/available/list", response_model=List[RoomResponse])
def list_available_rooms_endpoint(db: Session = Depends(get_db)) -> List[RoomResponse]:
    return list_available_rooms(db)


@router.get("/maintenance/list", response_model=List[RoomResponse])
def list_rooms_in_maintenance_endpoint(db: Session = Depends(get_db)) -> List[RoomResponse]:
    return list_rooms_in_maintenance(db)


@router.get("/{room_name}", response_model=RoomResponse)
def get_room_endpoint(room_name: str, db: Session = Depends(get_db)) -> RoomResponse:
    return get_room(db, room_name)


@router.put("/{room_name}", response_model=RoomResponse)
def update_room_endpoint(room_name: str, room_data: RoomUpdate, db: Session = Depends(get_db)) -> RoomResponse:
    return update_room(db, room_name, room_data)


@router.delete("/{room_name}", status_code=204, response_model=None)
def delete_room_endpoint(room_name: str, db: Session = Depends(get_db)) -> None:
    delete_room(db, room_name)


@router.patch("/{room_name}/reserve", response_model=RoomResponse)
def mark_room_reserved_endpoint(room_name: str, db: Session = Depends(get_db)) -> RoomResponse:
    return mark_room_reserved(db, room_name)


@router.patch("/{room_name}/unreserve", response_model=RoomResponse)
def mark_room_unreserved_endpoint(room_name: str, db: Session = Depends(get_db)) -> RoomResponse:
    return mark_room_unreserved(db, room_name)
