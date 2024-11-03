from extensions import db
from models.user import User
from models.election import Election
from models.candidate import Candidate
from models.vote import Vote

# Import UserVote here only after Vote has been imported
from models.vote import UserVote

__all__ = ['User', 'Election', 'Candidate', 'Vote', 'UserVote']
