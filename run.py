# run.py
import os
from app import create_app

# 환경 변수 'FLASK_ENV'가 설정되어 있지 않으면 기본값으로 'dev'를 사용합니다.
# 이는 config.py의 DevelopmentConfig를 불러오게 됩니다.
env = os.environ.get('FLASK_ENV', 'dev')
app = create_app(env)

if __name__ == '__main__':
    # host='0.0.0.0'으로 설정하면 같은 네트워크의 다른 기기에서도 접속 가능합니다.
    # debug=True는 코드를 수정하면 서버가 자동으로 재시작되는 기능입니다.
    app.run(host='0.0.0.0', port=8000, debug=True)