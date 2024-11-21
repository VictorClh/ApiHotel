from flask import Flask
from flask_restful import Api
from resources.hotel import Hoteis, Hotel
from resources.usuario import Users, UserRegister, UserLogin
from flask_jwt_extended import JWTManager #Cuida da autenticação

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456789@localhost/hotel'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'KeepThisInSecret'  # Change this!
api = Api(app)
jwt = JWTManager(app)

@app.before_request
def cria_banco():
    banco.create_all()

api.add_resource(Hoteis, '/hoteis')
api.add_resource(Hotel, '/hoteis/<string:hotel_id>')
api.add_resource(Users, '/usuarios/<int:user_id>')
api.add_resource(UserRegister, '/cadastro')
api.add_resource(UserLogin, '/login')


if __name__ == '__main__':
    from sql_alchemy import banco
    banco.init_app(app)
    app.run(debug=True)