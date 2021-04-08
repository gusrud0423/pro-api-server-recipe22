from flask import request
from flask_restful import Resource
from http import HTTPStatus

from db.db import get_mysql_connection

# JWT 라이브러리
from flask_jwt_extended import jwt_required, get_jwt_identity

# 우리가 이 파일에서 작성하는 클래스는, 
# 플라스크 프레임워크에서, 경로랑 연결시킬 클래스 입니다.
# 따라서, 클래스 명 뒤에, Resource 클래스를 상속받아야 합니다.
# 플라스크 프레임워크의 레퍼런스 사용법에 나와 있습니다.

class RecipeListResource(Resource) :
    # get 메소드로 연결시킬 함수 작성.
    def get(self) :
        # recipe 테이블에 저장되어 있는 모든 레시피 정보를 가져오는 함수

        # 1. DB 커넥션을 가져온다.
        connection = get_mysql_connection()

        print(connection)

        # 2. 커넥션에서 커서를 가져온다.
        cursor = connection.cursor(dictionary=True)

        # 3. 쿼리문을 작성한다.
        query = """select * from recipe;"""

        # 4. sql 실행
        cursor.execute(query)

        # 5. 데이터를 페치한다.         
        records = cursor.fetchall()

        print(records)

        ret = []
        for row in records :
            row['created_at'] = row['created_at'].isoformat()
            row['updated_at'] = row['updated_at'].isoformat()
            ret.append(row)

        # 6. 커서와 커넥션을 닫아준다.
        cursor.close()
        connection.close()

        # 7. 클라언트에 리스판스 한다.
        return {'count' : len(ret), 'ret' : ret}, HTTPStatus.OK


    @jwt_required()   # 로그인한 유저만 이 API 이용할수 있다.
    def post(self) :
        # 1. 클라이언트가 요청한 request의 body 에 있는 
        # json 데이터를 가져오기

        #{ "name" : "된장찌게" ,  "description" : "된장찌게 끓이는 법", "num_of_servings":0,
        # "cook_time" : 40, "directions" : "물을 먼저 붓고, 맛있게 끓이세요. 두부도 넣으세요.", 
        # "is_publish" : 0 }
        
        data = request.get_json()
        
        # 2. 필수 항목이 있는지 체크
        if 'name' not in data :
            return {'message':'필수값이 없습니다.'} , HTTPStatus.BAD_REQUEST

        # JWT 인증토큰에서 유저아이디 뽑아온다.
        user_id = get_jwt_identity()
        
        # 3. 데이터베이스 커넥션 연결
        connection = get_mysql_connection()

        # 4. 커서 가져오기
        cursor = connection.cursor(dictionary=True)

        # 5. 쿼리문 만들기
        query = """ insert into recipe (name, description, num_of_servings, 
                                        cook_time, directions, is_publish, user_id)
                    values (%s, %s, %s, %s, %s, %s, %s); """
        param = ( data['name'], data['description'], data['num_of_servings'], data['cook_time'], data['directions'], data['is_publish'], user_id )

        # 6. 쿼리문 실행
        c_result = cursor.execute(query, param)
        print(c_result)

        connection.commit()

        # 7. 커서와 커넥션 닫기

        cursor.close()
        connection.close()

        # 8. 클라이언트에 reponse 하기

        return {'err_code':0}, HTTPStatus.OK



class RecipeResource(Resource) : 

    def get(self, recipe_id) :
        # localhost:5000/recipes/1
        # 1. 경로에 붙어있는 값(레시피테이블의 아이디)을 가져와야 한다.
        # 위의 get 함수의 파라미터로 지정해준다.
        # 따라서 recipe_id 에 값이 들어있다.

        # 2. 디비 커넥션 가져온다.
        connection = get_mysql_connection()

        # 3. 커서 가져오고
        cursor = connection.cursor(dictionary=True)

        # 4. 쿼리문 만들고
        # query = """ select 
        #             name,description,num_of_servings, cook_time,
        #             directions,is_publish, 
        #             date_format(created_at, '%Y-%m-%d %H:%i:%S') as created_at,
        #             date_format(updated_at, '%Y-%m-%d %H:%i:%S') as updated_at
        #             from recipe where id = %s ; """

        query = """ select 
                    name,description,num_of_servings, cook_time,
                    directions,is_publish, 
                    date_format(created_at, '%Y-%m-%d %T') as created_at,
                    date_format(updated_at, '%Y-%m-%d %T') as updated_at
                    from recipe where id = %s ; """
        param = (recipe_id,)

        # 5. 쿼리 실행
        cursor.execute(query, param)

        records = cursor.fetchall()

        # 6. 커서, 커넥션 닫기.
        cursor.close()
        connection.close()
        
        # 7. 실행 결과를 클라이언트에 보내준다.

        if len(records) == 0 :
            return {'message':'패스로 셋팅한 레시피 아이디는 없다.'}, HTTPStatus.BAD_REQUEST

        # result = []
        # for row in records :
        #     row['created_at'] = row['created_at'].isoformat()
        #     row['updated_at'] = row['updated_at'].isoformat()
        #     result.append(row)

        return {'count' : len(records), 'ret' : records[0]} 

    @jwt_required()
    def put(self, recipe_id) :        
        # 업데이트 함수 작성.
        # cook_time과 directions 만 업데이트 할수 있도록 해주세요.
        # cook_time과 directions 은 필수값입니다.
        data = request.get_json()
        if 'cook_time' not in data or 'directions' not in data :
            return {'message':'파라미터 잘못됬습니다.'}, HTTPStatus.BAD_REQUEST

        # 커넥션 가져오기
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary= True)

        # 유저아이디가, 이 레시피 만든 유저가 맞는지 확인해 봐야 한다.
        user_id = get_jwt_identity()
        
        query = """ select user_id from recipe where id = %s; """
        param = (recipe_id, )
        cursor.execute(query, param)
        records = cursor.fetchall()
        if len(records) == 0 :
            return {'err_code' : 1}, HTTPStatus.BAD_REQUEST
        
        if user_id != records[0]['user_id'] :
            return {'err_code' : 2}, HTTPStatus.NOT_ACCEPTABLE

        # 업데이트 쿼리
        query = """ update recipe 
                set cook_time = %s, directions = %s
                where id = %s;  """
        param = (data['cook_time'],data['directions'], recipe_id)
        cursor.execute(query, param)
        connection.commit()

        cursor.close()
        connection.close()

        return {}, HTTPStatus.OK
        
    ### 실습. 레시피 삭제 API 에, 인증 토큰 적용해서
    ###       그 레시피를 작성한 유저만, 레시피를 삭제할 수 있게 변경.
    
    @jwt_required()
    def delete(self, recipe_id) :

        connection = get_mysql_connection()

        cursor = connection.cursor(dictionary=True)

        # 먼저, 인증토큰에서 유저아이디를 빼온다.
        user_id = get_jwt_identity()
        # 데이터베이스에 저장된 유저아이디와 같은지 비교한다.
        query = """ select * from recipe where id = %s; """ 
        param = (recipe_id, )
        cursor.execute(query, param)
        records = cursor.fetchall()
        
        if len(records) == 0 :
            return {'err_code': 1}, HTTPStatus.BAD_REQUEST
        if user_id != records[0]['user_id'] :
            return {'err_code' :2}, HTTPStatus.UNAUTHORIZED


        query = """ delete from recipe where id = %s; """

        param = (recipe_id , )

        cursor.execute(query, param)

        connection.commit()

        cursor.close()
        connection.close()

        return {}, HTTPStatus.OK


class RecipePublishResource(Resource) :
    # is_publish 를 1로 변경해주는 함수.
    def put(self, recipe_id) :
        connection = get_mysql_connection()
        cursor = connection.cursor()
        query = """ update recipe set is_publish = 1 where id = %s ; """
        param = (recipe_id, )
        cursor.execute(query, param)
        connection.commit()
        cursor.close()
        connection.close()
        return {}, HTTPStatus.OK

    # is_publish 를 0으로 변경해주는 함수.
    def delete(self, recipe_id) : 
        connection = get_mysql_connection()
        cursor = connection.cursor()
        query = """ update recipe set is_publish = 0 where id = %s ; """
        param = (recipe_id, )
        cursor.execute(query, param)
        connection.commit()
        cursor.close()
        connection.close()
        return {}, HTTPStatus.OK

#