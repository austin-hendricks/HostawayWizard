from db import db


# Table for storing tasks
class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    listingMapId = db.Column(db.Integer)
    channelId = db.Column(db.Integer)
    reservationId = db.Column(db.Integer)
    autoTaskId = db.Column(db.Integer)
    assigneeUserId = db.Column(db.Integer)
    title = db.Column(db.String)
    description = db.Column(db.String)
    status = db.Column(db.String)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(
        db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now()
    )

    # Relationship to revisions
    revisions = db.relationship("TaskRevision", backref="task", lazy=True)
