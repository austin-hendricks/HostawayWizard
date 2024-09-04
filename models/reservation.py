from db import db


# Table for storing reservations
class Reservation(db.Model):
    __tablename__ = "reservations"

    id = db.Column(db.Integer, primary_key=True)
    listingMapId = db.Column(db.Integer, nullable=False)
    channelId = db.Column(db.Integer, nullable=False)
    source = db.Column(db.String)
    status = db.Column(db.String)
    guestName = db.Column(db.String)
    arrivalDate = db.Column(db.Date)
    departureDate = db.Column(db.Date)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(
        db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now()
    )

    # Relationship to revisions
    revisions = db.relationship("ReservationRevision", backref="reservation", lazy=True)
    # Relationship to messages
    messages = db.relationship("ConversationMessage", backref="reservation", lazy=True)
    # Relationship to conversations
    conversations = db.relationship("Conversation", backref="reservation", lazy=True)
