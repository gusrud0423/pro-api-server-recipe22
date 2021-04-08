from flask import Flask
from flask_restful import Api

from db.db import get_mysql_connection
from config.config import Config

from resources.recipe import RecipeListResource, RecipeResource, RecipePublishResource 
from resources.user import UserListResource, UserResource, jwt_blocklist, UserLogoutResource

# JWT용 라이브러리
from flask_jwt_extended import JWTManager

app = Flask(__name__)

# 1. 환경변수 설정.
app.config.from_object(Config)

# 1-1. JWT 환경 설정.
jwt = JWTManager(app)
# 로그인/로그아웃 관리를 위한 JTW 설정
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload) :
    jti = jwt_payload['jti']
    return jti in jwt_blocklist

# 2. api 설정
api = Api(app)

# 3. 경로(Path)랑 리소스(Resource)를 연결한다.
# /recipes 


api.add_resource(RecipeListResource, '/recipes')
api.add_resource(RecipeResource, '/recipes/<int:recipe_id>') # 경로에 변수처리
api.add_resource(RecipePublishResource, '/recipes/<int:recipe_id>/publish')

api.add_resource(UserListResource, '/users')

api.add_resource(UserResource, '/users/login', '/users/<int:user_id>/my')

api.add_resource(UserLogoutResource, '/users/logout')

# 내 정보 가져오는 API 개발 
# /users/1/my  => UserResource Get
# id, email, username, is_acitve 이 4개 정보를 클라이언트에 응답하는 함수.


if __name__ == '__main__' :

    app.run(port=5003)
