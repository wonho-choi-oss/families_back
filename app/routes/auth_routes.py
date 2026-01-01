import jwt

from flask import Blueprint, request, jsonify, current_app
from app.models import User
from datetime import datetime, timedelta
from app import redis_client,db

auth_bp = Blueprint('auth_bp', __name__)

# 1. 회원가입 (Signup)
@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "이미 존재하는 아이디입니다."}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)  # 해싱 저장

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "회원가입 성공"}), 201

# 2. 로그인 (Login)
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # user = User.query.filter_by(username=data.get('username')).first()

    # if not user or not user.check_password(data.get('password')):
    #     return jsonify({"message": "인증 정보가 틀립니다."}), 401

    user = data

    # Access Token 생성 (30분)
    access_token = jwt.encode({
        # 'sub': user.id ,
        'sub': user.get('id', data.get('username')),
        'exp': datetime.utcnow() + timedelta(minutes=30)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    # Refresh Token 생성 (14일)
    refresh_token = jwt.encode({
        # 'sub': user.id ,
        'sub': user.get('id', data.get('username')),
        'exp': datetime.utcnow() + timedelta(days=14)
    }, current_app.config['REFRESH_SECRET_KEY'], algorithm='HS256')

    # Redis에 Refresh Token 저장 (보안 및 성능)
    # redis_client.setex(f"refresh_token:{user.id}", timedelta(days=14), refresh_token)
    redis_client.setex(f"refresh_token:{user.get('id', data.get('username'))}", timedelta(days=14), refresh_token)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200

# 3. 로그아웃 (Logout) - 비용 절감형 최적화 로직
@auth_bp.route('/logout', methods=['POST'])
def logout():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"message": "이미 로그아웃 상태입니다."}), 200

    token = auth_header.split(" ")[1]

    try:
        # 만료 여부 상관없이(verify_exp=False) 내부 ID만 확인하여 비용 절감
        data = jwt.decode(token, current_app.config['SECRET_KEY'],
                          options={"verify_exp": False}, algorithms=['HS256'])
        user_id = data.get('sub')
        exp_timestamp = data.get('exp')

        # 1. Redis에서 리프레시 토큰 삭제
        redis_client.delete(f"refresh_token:{user_id}")

        # 2. 액세스 토큰이 유효하다면 블랙리스트에 추가
        now = datetime.utcnow().timestamp()
        if exp_timestamp and exp_timestamp > now:
            remain_time = int(exp_timestamp - now)
            redis_client.setex(f"blacklist:{token}", remain_time, "logout")

    except Exception as e:
        # 토큰 형식이 잘못된 경우 등 에러 무시하고 로그아웃 처리
        pass

    return jsonify({"message": "성공적으로 로그아웃되었습니다."}), 200

# 4. 토큰 갱신 (Refresh)
@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    refresh_token = request.json.get('refresh_token')
    if not refresh_token:
        return jsonify({"message": "리프레시 토큰 필요"}), 401

    try:
        data = jwt.decode(refresh_token, current_app.config['REFRESH_SECRET_KEY'], algorithms=['HS256'])
        user_id = data['sub']

        # Redis에 저장된 토큰과 대조 (가장 확실한 보안)
        saved_token = redis_client.get(f"refresh_token:{user_id}")
        if not saved_token or saved_token != refresh_token:
            return jsonify({"message": "세션 만료"}), 401

        # 새 Access Token 발급
        new_access = jwt.encode({
            'sub': user_id,
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({"access_token": new_access}), 200
    except:
        return jsonify({"message": "재로그인 필요"}), 401