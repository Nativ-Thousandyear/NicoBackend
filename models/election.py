from extensions import db
from models.base import TimestampMixin
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Election(db.Model, TimestampMixin):
    __tablename__ = 'elections'

    id: int = db.Column(db.Integer, primary_key=True)
    election_name: str = db.Column(db.String(100), nullable=False, unique=True)
    election_type: str = db.Column(db.String(50), nullable=False)
    max_votes: int = db.Column(db.Integer, nullable=False)
    status: str = db.Column(db.String(20), default='ongoing')
    start_date: datetime = db.Column(db.DateTime(timezone=True), nullable=True)
    end_date: datetime = db.Column(db.DateTime(timezone=True), nullable=True)
    threshold_votes: int = db.Column(db.Integer, nullable=True)

    # Relationships
    candidates = db.relationship('Candidate', backref='election', lazy=True)
    user_votes = db.relationship('UserVote', backref='related_election', lazy=True)
    votes = db.relationship('Vote', backref='election_votes', lazy=True)  # Changed this line

    @property
    def is_active(self) -> bool:
        now = datetime.now(timezone.utc)
        if self.status != 'ongoing':
            return False
        return (self.start_date is None or self.start_date <= now) and (self.end_date is None or now <= self.end_date)

    @property
    def time_until_start(self) -> float:
        if not self.start_date:
            return None
        now = datetime.now(timezone.utc)
        if now < self.start_date:
            time_delta = self.start_date - now
            return round(time_delta.total_seconds() / 3600, 1)
        return None

    def get_local_time(self, dt: datetime) -> datetime:
        if dt:
            pacific = ZoneInfo('America/Los_Angeles')
            return dt.astimezone(pacific)
        return None

    @property
    def local_start_date(self) -> str:
        local_time = self.get_local_time(self.start_date)
        return local_time.strftime('%I:%M %p %Z on %B %d, %Y') if local_time else None

    @property
    def local_end_date(self) -> str:
        local_time = self.get_local_time(self.end_date)
        return local_time.strftime('%I:%M %p %Z on %B %d, %Y') if local_time else None

    def is_early_determination(self) -> bool:
        return self.threshold_votes is not None and self.get_total_votes() >= self.threshold_votes

    def get_total_votes(self) -> int:
        from models.vote import Vote  # Move the import here to avoid circular dependency
        total_votes = db.session.query(Vote).filter_by(election_id=self.id).count()
        logger.info(f"Total votes for election '{self.election_name}' (ID: {self.id}): {total_votes}")
        return total_votes

    def __repr__(self) -> str:
        return f'<Election id={self.id}, name={self.election_name}, type={self.election_type}, status={self.status}>'
