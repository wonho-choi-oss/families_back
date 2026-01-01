from flask import Blueprint, request, abort, current_app, jsonify
from openai import OpenAI
from app.middleware import token_required
from app.services.gpt_service import get_gpt_reply
from app import db

gpt_bp = Blueprint('gpt_bp', __name__)


@gpt_bp.route('', methods=['post'])
@token_required
def gpt(current_user_id):
    data = request.get_json()
    user_message = data.get("messages")
    if not user_message or not user_message[0] :
        abort(400, description="메시지가 없습니다.")

    try:

        gpt_reply = get_gpt_reply(user_message)
        db.session.commit()

        return jsonify({"reply": gpt_reply})


    except Exception as e:
       db.session.rollback()

       current_app.logger.error(f"gpt chat 저장중 에러: {str(e)}")
       abort(500,f"!!! OpenAI API Error: {e}")





