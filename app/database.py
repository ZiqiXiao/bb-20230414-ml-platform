"""Database models for the app.

This module contains the database models for the app.
"""
from app import db
import datetime

class ModelTable(db.Model):
    """Model table for the database.

    This class contains the model table for the database.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """The id of the model."""
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    """The time when the model was created."""
    model_class = db.Column(db.String(64), nullable=False)
    """The class of the model."""
    model_name = db.Column(db.String(64), nullable=False)
    """The name of the model."""
    model_path = db.Column(db.String(256), nullable=False)
    """The path of the model."""
    template_name = db.Column(db.String(64), nullable=False)
    """The name of the template."""
    template_path = db.Column(db.String(256), nullable=False)
    """The path of the template."""

    def __repr__(self):
        return f'<ModelTable {self.model_name}>'