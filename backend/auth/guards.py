from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..dependencies import get_current_user, get_db
from ..models.trip import Trip

def check_trip_ownership(tripid: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)) -> Trip:
    trip = db.query(Trip).filter(Trip.id == tripid).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    if trip.userid != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this trip"
        )
    return trip
