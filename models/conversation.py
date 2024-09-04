from db import db


# Table for storing conversations
class Conversation(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(
        db.Integer, db.ForeignKey("reservations.id"), nullable=False
    )
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    # Relationship to messages
    messages = db.relationship("ConversationMessage", backref="conversation", lazy=True)
