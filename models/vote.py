from extensions import db
from models.base import TimestampMixin

class Vote(db.Model, TimestampMixin):
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('elections.id'), nullable=False)

    candidate = db.relationship('Candidate', backref='candidate_votes', lazy=True)
    election = db.relationship('Election', backref='election_votes', lazy=True)  # This can remain as it is

    def __repr__(self):
        return f'<Vote id={self.id}, candidate_id={self.candidate_id}, election_id={self.election_id}>'

class UserVote(db.Model, TimestampMixin):
    __tablename__ = 'user_votes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('elections.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'election_id', name='unique_user_election'),)

    user = db.relationship('User', backref='related_user_votes', lazy=True)
    election = db.relationship('Election', backref='related_user_votes', lazy=True)

    def __repr__(self):
        return f'<UserVote id={self.id}, user_id={self.user_id}, election_id={self.election_id}>'
