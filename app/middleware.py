from flask import request, abort, current_app
from functools import wraps
import jwt
from app import redis_client


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            abort(401, description="토큰이 없습니다.")

        token = auth_header.split(" ")[1]

        # 1. Redis 블랙리스트 확인 (로그아웃 여부)
        if redis_client.get(f"blacklist:{token}"):
            abort(401, description="이미 로그아웃된 토큰입니다.")

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['sub']

        except jwt.ExpiredSignatureError:
            abort(401, description="토큰이 만료되었습니다.")
        except:
            abort(401, description="유효하지 않은 토큰입니다.")

        return f(current_user_id, *args, **kwargs)

    return decorated