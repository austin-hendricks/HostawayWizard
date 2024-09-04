from db import db


# Table for storing reservation revisions
class ReservationRevision(db.Model):
    __tablename__ = "reservation_revisions"

    id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(
        db.Integer, db.ForeignKey("reservations.id"), nullable=False
    )
    revision_data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
