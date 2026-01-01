from flask import Blueprint, request, jsonify, abort
from app.models import FamilyMember, User, db
from app.middleware import token_required

family_bp = Blueprint('family_bp', __name__)


@family_bp.route('', methods=['GET'])
@token_required
def get_families(current_user_id):
    user = User.query.get(current_user_id)
    # db.relationship('families') 덕분에 바로 접근
    family_list = [{"id": f.id, "name": f.name} for f in user.families]
    return jsonify(family_list), 200


@family_bp.route('/<int:member_id>', methods=['GET'])
@token_required
def get_family_detail(current_user_id, member_id):
    member = FamilyMember.query.get(member_id)

    # 조건 1: 해당 가족 멤버가 DB에 아예 없는 경우
    if not member:
        abort(404, description="가족 정보를 찾을 수 없습니다.")

    # 조건 2: 멤버는 존재하지만, '내 가족'이 아닌 경우 (중요 보안 체크!)
    if member.user_id != current_user_id:
        abort(403, description="이 정보에 대한 접근 권한이 없습니다.")

    return jsonify({"id": member.id, "name": member.name}), 200


@family_bp.route('', methods=['POST'])
@token_required
def add_family(current_user_id):
    data = request.get_json()
    if not data.get('name'):
        abort(400, description="이름을 입력하세요.")

    new_member = FamilyMember(name=data['name'], user_id=current_user_id)
    db.session.add(new_member)
    db.session.commit()
    return jsonify({"message": "등록 성공"}), 201