from flask import Blueprint, request, jsonify
from election_service import ElectionService
from models import Election, db
import logging

# Change the blueprint name to 'election_v1'
election_bp = Blueprint('election_v1', __name__)
election_service = ElectionService(model=None, db=db)

@election_bp.route('/set_threshold', methods=['POST'])
def set_threshold():
    try:
        data = request.get_json()
        election_id = data.get('election_id')
        threshold = data.get('threshold_votes')

        # Validate input
        if election_id is None or threshold is None:
            return jsonify({"message": "Both 'election_id' and 'threshold_votes' are required."}), 400

        if not isinstance(threshold, int) or threshold <= 0:
            return jsonify({"message": "'threshold_votes' must be a positive integer."}), 400

        election = db.session.query(Election).filter_by(id=election_id).first()
        if not election:
            return jsonify({"message": f"No election found with ID {election_id}."}), 404

        election.threshold_votes = threshold
        db.session.commit()
        return jsonify({"message": "Threshold set successfully."}), 200

    except Exception as e:
        logging.error(f"Error in set_threshold: {str(e)}")
        return jsonify({"message": "An internal error occurred. Please try again later."}), 500

@election_bp.route('/check_early_determination/<int:election_id>', methods=['GET'])
def check_early_determination_api(election_id):
    try:
        if election_service.check_early_determination(election_id):
            return jsonify({"message": "The election has been determined early."}), 200
        else:
            return jsonify({"message": "No early determination for this election."}), 200
    except Exception as e:
        logging.error(f"Error in check_early_determination_api for election {election_id}: {str(e)}")
        return jsonify({"message": "An internal error occurred. Please try again later."}), 500
