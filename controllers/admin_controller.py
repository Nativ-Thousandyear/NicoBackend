from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models import Election, Candidate, Vote, UserVote
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
from zoneinfo import ZoneInfo
import logging

admin_bp = Blueprint('admin', __name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash("You do not have permission to access this page.", "error")
            return redirect(url_for("election.index"))
        return f(*args, **kwargs)
    return decorated_function

def convert_local_to_utc(date_str):
    """Convert local datetime string to UTC datetime object."""
    if not date_str or date_str == "No range":
        return None
        
    local_dt = datetime.fromisoformat(date_str)
    pacific = ZoneInfo('America/Los_Angeles')
    local_dt = local_dt.replace(tzinfo=pacific)
    utc_dt = local_dt.astimezone(timezone.utc)
    return utc_dt

def safe_int_conversion(value, default=0):
    """Attempt to convert a value to int, defaulting to a provided value if conversion fails."""
    try:
        return int(value)
    except (TypeError, ValueError):
        logger.warning(f"Conversion failed for value '{value}', defaulting to {default}")
        return default

@admin_bp.route("/setup_restaurant_election", methods=["GET", "POST"])
@login_required
@admin_required
def setup_restaurant_election():
    if request.method == "POST":
        city = request.form.get('city')
        state = request.form.get('state')
        number_of_restaurants = safe_int_conversion(request.form.get('number_of_restaurants'))
        max_votes = safe_int_conversion(request.form.get('max_votes'))
        threshold_votes = safe_int_conversion(request.form.get('threshold_votes'))
        election_name = request.form.get('election_name')

        start_date = convert_local_to_utc(request.form.get('start_date'))
        end_date = convert_local_to_utc(request.form.get('end_date'))

        if start_date and end_date and start_date >= end_date:
            flash("End date must be after start date.", "error")
            return redirect(url_for("admin.setup_restaurant_election"))

        candidates = current_app.election_service.get_restaurant_candidates(
            number_of_restaurants, city, state
        )

        logger.info(
            f"Creating restaurant election with candidates: {candidates}, "
            f"max_votes={max_votes}, threshold_votes={threshold_votes}, election_name='{election_name}'"
        )

        try:
            election_id = current_app.election_service.start_election(
                candidates, 
                max_votes, 
                "restaurant",  
                election_name=election_name,
                start_date=start_date,
                end_date=end_date,
                threshold_votes=threshold_votes
            )

            pacific = ZoneInfo('America/Los_Angeles')
            local_start = start_date.astimezone(pacific) if start_date else None
            flash(f"Restaurant election '{election_name}' created successfully.", "info")
            logger.info(f"Restaurant election '{election_name}' created successfully with ID {election_id}.")
            return redirect(url_for("election.index"))

        except SQLAlchemyError as e:
            db.session.rollback()
            flash("An error occurred while creating the election.", "error")
            logger.error(f"Database error while creating restaurant election '{election_name}': {str(e)}")
        
    return render_template("restaurant_election.html")

@admin_bp.route("/setup_custom_election", methods=["GET", "POST"])
@login_required
@admin_required
def setup_custom_election():
    if request.method == "POST":
        max_votes = safe_int_conversion(request.form.get('max_votes_custom'))
        threshold_votes = safe_int_conversion(request.form.get('threshold_votes_custom'))
        election_name = request.form.get('election_name')
        candidate_names = request.form.getlist('candidate_names[]')

        start_date = convert_local_to_utc(request.form.get('start_date'))
        end_date = convert_local_to_utc(request.form.get('end_date'))

        candidates = [name for name in candidate_names if name.strip() != ""]

        if not candidates:
            flash("Please enter at least one candidate.", "error")
            return redirect(url_for("admin.setup_custom_election"))

        if start_date and end_date and start_date >= end_date:
            flash("End date must be after start date.", "error")
            return redirect(url_for("admin.setup_custom_election"))

        logger.info(
            f"Creating custom election with candidates: {candidates}, "
            f"max_votes={max_votes}, threshold_votes={threshold_votes}, election_name='{election_name}'"
        )

        try:
            election_id = current_app.election_service.start_election(
                candidates, 
                max_votes, 
                "custom",  
                election_name=election_name,
                start_date=start_date,
                end_date=end_date,
                threshold_votes=threshold_votes
            )

            pacific = ZoneInfo('America/Los_Angeles')
            local_start = start_date.astimezone(pacific) if start_date else None
            flash(f"Custom election '{election_name}' created successfully.", "info")
            logger.info(f"Custom election '{election_name}' created successfully with ID {election_id}.")
            return redirect(url_for("election.index"))

        except SQLAlchemyError as e:
            db.session.rollback()
            flash("An error occurred while creating the custom election.", "error")
            logger.error(f"Database error while creating custom election '{election_name}': {str(e)}")

    return render_template("custom_election.html")

@admin_bp.route("/delete_election/<int:election_id>", methods=["POST"])
@login_required
@admin_required
def delete_election(election_id):
    try:
        election = Election.query.get(election_id)
        if not election:
            flash("Election not found.", "error")
            logger.warning(f"Attempted to delete non-existent election with ID {election_id}")
            return redirect(url_for("election.index"))

        db.session.delete(election)
        db.session.commit()
        flash("Election deleted successfully.", "success")
        logger.info(f"Deleted election with ID {election_id}.")
    except SQLAlchemyError as e:
        db.session.rollback()
        flash("An error occurred while deleting the election.", "error")
        logger.error(f"Error deleting election with ID {election_id}: {str(e)}")
    
    return redirect(url_for("election.index"))
