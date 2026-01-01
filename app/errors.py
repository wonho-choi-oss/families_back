from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "Unauthorized", "message": str(e.description)}), 401

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not Found", "message": "리소스를 찾을 수 없습니다."}), 404

    @app.errorhandler(Exception)
    def internal_error(e):
        return jsonify({"error": "Server Error", "message": "서버 내부 오류 발생"}), 500