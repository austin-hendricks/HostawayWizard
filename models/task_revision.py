from db import db


# Table for storing task revisions
class TaskRevision(db.Model):
    __tablename__ = "task_revisions"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    revision_data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
