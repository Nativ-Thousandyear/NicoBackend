from models import Election, Candidate, Vote
from extensions import db

class ElectionService:
    def __init__(self, model, db):
        """Initialize the ElectionService with the GPT-4 model and database session."""
        self.model = model
        self.db = db

    # Helper function for generating GPT-4 introductions
    def generate_gpt4_text_introduction(self, election):
        introductions = []
        for index, candidate in enumerate(election.candidates, start=1):
            gpt_text = self.model.invoke(f"""In a quirky and enthusiastic tone, welcome {candidate.name} to a show in a few words. 
                                            Example:
                                            Introducing first, the animated and lively Tony Hawk!
                                            Introducing second, the wonderful and endearing Mariah Carey!
                                            Introduce them as follows:
                                            Introducing {self.ordinal(index)}, the animated and lively {candidate.name}!""")
            introductions.append(gpt_text.content)
        return introductions

    # Helper function that returns the ordinal of a number
    def ordinal(self, n: int) -> str:
        if 10 <= n % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return f"{n}{suffix}"

    # Generate restaurant candidates using GPT-4
    def get_restaurant_candidates(self, number_of_restaurants: int, city: str, state: str) -> list[str]:
        prompt = f"Generate {number_of_restaurants} unique restaurant names in {city}, {state}."
        response = self.model.invoke(prompt)
        return response.content.strip().split("\n")[:number_of_restaurants]

    # Start a new election
    def start_election(self, candidates: list[str], max_votes: int, election_type: str, election_name: str, 
                      start_date: str = None, end_date: str = None, threshold_votes: int = None) -> int:
        election = Election(
            election_name=election_name,
            election_type=election_type,
            max_votes=max_votes,
            start_date=start_date,
            end_date=end_date,
            threshold_votes=threshold_votes
        )
        
        try:
            self.db.session.add(election)
            self.db.session.commit()

            for candidate_name in candidates:
                candidate = Candidate(name=candidate_name.strip(), election_id=election.id)
                self.db.session.add(candidate)
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise RuntimeError(f"Failed to start election: {e}")

        return election.id

    # Check early election determination
    def check_early_determination(self, election_id: int) -> bool:
        election = self.db.session.query(Election).filter_by(id=election_id).first()
        if not election or election.threshold_votes is None:
            return False

        candidate_votes = self.get_candidate_votes(election_id)
        for candidate_id, votes in candidate_votes.items():
            if votes >= election.threshold_votes:
                self.declare_winner(election_id, candidate_id)
                return True
        return False

    # Get candidate votes
    def get_candidate_votes(self, election_id: int) -> dict[int, int]:
        results = self.db.session.query(
            Vote.candidate_id, db.func.count(Vote.id).label('vote_count')
        ).filter_by(election_id=election_id).group_by(Vote.candidate_id).all()

        return {result.candidate_id: result.vote_count for result in results}

    # Declare winner
    def declare_winner(self, election_id: int, candidate_id: int) -> None:
        election = self.db.session.query(Election).filter_by(id=election_id).first()
        if election:
            election.status = 'completed'
            election.winner = candidate_id
            self.db.session.commit()
