from __future__ import annotations
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.room import Room, RoomMaintenanceStatus
from schemas.room import RoomCreate, RoomUpdate


def create_room(db: Session, data: RoomCreate) -> Room:
    if db.query(Room).filter(Room.name == data.name).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe uma sala com o nome '{data.name}'",
        )
    room = Room(
        name=data.name,
        capacity=data.capacity,
        description=data.description,
        computers=data.computers,
        maintenance_status=data.maintenance_status,
        is_reserved=False,
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


def list_rooms(db: Session, skip: int, limit: int, name: Optional[str]) -> dict:
    query = db.query(Room)
    if name:
        query = query.filter(Room.name.ilike(f"%{name}%"))
    total = query.count()
    rooms = query.offset(skip).limit(limit).all()
    return {"total": total, "rooms": rooms}


def list_available_rooms(db: Session) -> List[Room]:
    return db.query(Room).filter(Room.is_reserved == False).all()


def list_rooms_in_maintenance(db: Session) -> List[Room]:
    return db.query(Room).filter(
        Room.maintenance_status.in_([
            RoomMaintenanceStatus.yes,
            RoomMaintenanceStatus.scheduled,
        ])
    ).all()


def get_room(db: Session, room_name: str) -> Room:
    room = db.query(Room).filter(Room.name == room_name).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sala '{room_name}' não encontrada",
        )
    return room


def update_room(db: Session, room_name: str, data: RoomUpdate) -> Room:
    room = get_room(db, room_name)
    if room.is_reserved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível editar a sala '{room.name}' que está reservada",
        )
    if data.name and data.name != room.name:
        if db.query(Room).filter(Room.name == data.name).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Já existe uma sala com o nome '{data.name}'",
            )
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(room, key, value)
    db.commit()
    db.refresh(room)
    return room


def delete_room(db: Session, room_name: str) -> None:
    room = get_room(db, room_name)
    if room.is_reserved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível remover a sala que está reservada",
        )
    db.delete(room)
    db.commit()


def mark_room_reserved(db: Session, room_name: str) -> Room:
    room = get_room(db, room_name)
    room.is_reserved = True
    db.commit()
    db.refresh(room)
    return room


def mark_room_unreserved(db: Session, room_name: str) -> Room:
    room = get_room(db, room_name)
    room.is_reserved = False
    db.commit()
    db.refresh(room)
    return room
