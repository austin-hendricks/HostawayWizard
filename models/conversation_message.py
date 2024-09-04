from db import db


# Table for storing conversation messages
class ConversationMessage(db.Model):
    __tablename__ = "conversation_messages"

    id = db.Column(db.Integer, primary_key=True)
    accountId = db.Column(db.Integer, nullable=False)
    reservationId = db.Column(
        db.Integer, db.ForeignKey("reservations.id"), nullable=True
    )
    conversationId = db.Column(
        db.Integer, db.ForeignKey("conversations.id"), nullable=False
    )
    body = db.Column(db.String, nullable=False)
    communicationType = db.Column(db.String, nullable=False)
    status = db.Column(db.String)
    isIncoming = db.Column(db.Boolean)
    date = db.Column(db.DateTime)
    insertedOn = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updatedOn = db.Column(
        db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now()
    )
