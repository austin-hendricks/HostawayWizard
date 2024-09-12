from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker

# Create a new SQLAlchemy instance
db = SQLAlchemy()

# Define the session factory and scoped session
session_factory = sessionmaker()
db_session = scoped_session(session_factory)


def initialize(app):
    """
    Initialize the database and session factory with the given Flask app.
    This function should be called from within the Flask application context.
    """
    with app.app_context():
        db.init_app(app)
        session_factory.configure(
            bind=db.engine
        )  # Bind the session factory to the engine within app context
