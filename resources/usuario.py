from flask_restful import Resource, reqparse
from models.usuario import UserModel
from sql_alchemy import banco
from flask_jwt_extended import create_access_token, jwt_required

atributos = reqparse.RequestParser()
atributos.add_argument('login', type=str, required=True, help="The field 'login' cannot be left blank")
atributos.add_argument('senha', type=str, required=True, help="The field 'senha' cannot be left blank")

class UserRegister(Resource):
    # Cadastro
    def post(self):
        dados = atributos.parse_args()

        if UserModel.find_by_login(dados['login']):
            return {'message': 'User already exists'}, 400
        
        user = UserModel(**dados)
        try:
            user.save_user()
            return {'message': 'User created successfully'}, 201
        except:
            return {"message": "An internal error ocurred trying to save hotel"}, 500 #internal server error
        


class Users(Resource):
    #/usuarios/{user_id}
    def get(self, user_id):
        user = UserModel.query.filter_by(user_id=user_id).first()
        if user:
            return user.json()
        return{'Message':'Usuário inexistente'},404

    @jwt_required()
    def delete(self, user_id):
        user = UserModel.query.filter_by(user_id=user_id).first()
        if user:
            try:
                banco.session.delete(user)
                banco.session.commit()
                return{'message':'Usuário excluido!'}
            except:
                return {'message': 'An internal error ocurred trying to delete user'}, 500 #internal
        return {'message': 'Usuário não encontrado.'}, 400

class UserLogin(Resource):
    @classmethod
    def post(cls):
        dados = atributos.parse_args()

        user = UserModel.find_by_login(dados['login'])

        if user and user.senha == dados['senha']:
            token_de_acesso = create_access_token(identity=user.user_id)
            return {'access_token': token_de_acesso}, 200
        return {'message': 'User or password is incorrect'}, 401 # Unauthorized