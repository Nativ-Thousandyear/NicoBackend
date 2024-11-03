from extensions import db

class Candidate(db.Model):
    __tablename__ = 'candidates'

    id = db.Column(db.Integer, primary_key=True)  # Primary key for the candidate
    name = db.Column(db.String(100), nullable=False)  # Name of the candidate
    election_id = db.Column(db.Integer, db.ForeignKey('elections.id'), nullable=False)  # Foreign key linking to the elections table

    # Relationship to the Vote model with a unique backref name
    votes = db.relationship('Vote', backref='candidate_votes', lazy=True)

    # Unique constraint to ensure a candidate's name is unique within an election
    __table_args__ = (db.UniqueConstraint('election_id', 'name', name='unique_candidate_per_election'),)
