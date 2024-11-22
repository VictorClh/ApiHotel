from flask_restful import Resource, reqparse
from models.hotel import HotelModel
from sql_alchemy import banco
from flask_jwt_extended import jwt_required, get_jwt_identity
import sqlite3


def normalize_path_params(cidade=None,
                          estrelas_min = 0,
                          estrelas_max = 5,
                          diaria_min = 0,
                          diaria_max = 10000,
                          limit = 50,
                          offset = 0, **dados):
    if cidade:
        return{
            'estrelas_min': estrelas_min,
            'estrelas_max': estrelas_max,
            'diaria_min': diaria_min,
            'diaria_max': diaria_max,
            'cidade': cidade,
            'limit': limit,
            'offset': offset
        }
    return{
            'estrelas_min': estrelas_min,
            'estrelas_max': estrelas_max,
            'diaria_min': diaria_min,
            'diaria_max': diaria_max,
            'limit': limit,
            'offset': offset
        }

# path /hoteis?cidade=Rio de Janeiro&estrelas_min=4&diaria_max=400
path_params = reqparse.RequestParser()
path_params.add_argument('cidade', type=str)
path_params.add_argument('estrelas_min', type=float)
path_params.add_argument('estrelas_max', type=float)
path_params.add_argument('diaria_min', type=float)
path_params.add_argument('diaria_max', type=float)
path_params.add_argument('limit', type=float)
path_params.add_argument('offset', type=float)

class Hoteis(Resource):
    def get(self):
        connection = sqlite3.connect('banco.db')
        cursor = connection.cursor()
        

        dados = path_params.parse_args()
        dados_validos = {chave:dados[chave] for chave in dados if dados[chave] is not None}
        parametros = normalize_path_params(**dados_validos)

        if not parametros.get('cidade'):
            consulta = "SELECT * FROM hoteis \
            WHERE (estrelas > ? and estrelas < ?) \
            AND (diaria > ? and diaria < ?) \
                LIMIT ? OFFSET ?"
            tupla = tuple([parametros[chave] for chave in parametros])
            resultado = cursor.execute(consulta, tupla)
        else:
            consulta = "SELECT * FROM hoteis \
            WHERE (estrelas > ? and estrelas < ?) \
            AND (diaria > ? and diaria < ?) \
            AND cidade = ? LIMIT ? OFFSET ?"
            tupla = tuple([parametros[chave] for chave in parametros])
            resultado = cursor.execute(consulta, tupla)
        
        hoteis = []
        for linha in resultado:
            hoteis.append({
            'hotel_id': linha[0],
            'nome': linha[1],
            'estrelas': linha[2],
            'diaria': linha[3],
            'cidade': linha[4]
            })

        return {'hoteis': hoteis }

    @jwt_required()
    def post(self):
        #if HotelModel.find_hotel(hotel_id):
         #   return {"message": "Hotel id '{}' already exists.".format(hotel_id)}, 400 #bad request
        dados = Hotel.atributos.parse_args()
        hotel = HotelModel(**dados)
        try:
            hotel.save_hotel()
        except:
            return {"message": "An internal error ocurred trying to save hotel"}, 500 #internal server error
        return hotel.json(), 201


class Hotel(Resource):
    atributos = reqparse.RequestParser()
    atributos.add_argument('nome', type=str, required=True, help="The field 'nome' cannot be left blank")
    atributos.add_argument('estrelas', type=float, required=True, help="The field 'estrelas' cannot be left blank")
    atributos.add_argument('diaria')
    atributos.add_argument('cidade')

    def get(self, hotel_id):
        hotel = HotelModel.query.filter_by(hotel_id=hotel_id).first()
        if hotel:
            return hotel.json()
        return{'Message':'Sensor inexistente'},404
    
    @jwt_required()
    def put(self, hotel_id):
        dados = Hotel.atributos.parse_args()
        hotel_encontrado = HotelModel.query.filter_by(hotel_id=hotel_id).first()
        if hotel_encontrado:
            hotel_encontrado.query.filter_by(hotel_id=hotel_id).update({**dados})
            banco.session.commit()
            return hotel_encontrado.json(), 200
        hotel = HotelModel(**dados)
        try:
            hotel.save_hotel()
        except:
            return {"message": "An internal error ocurred trying to save hotel"}, 500 #internal server error
        return hotel.json(), 201

    @jwt_required()
    def delete(self, hotel_id):
        hotel = HotelModel.query.filter_by(hotel_id=hotel_id).first()
        if hotel:
            try:
                banco.session.delete(hotel)
                banco.session.commit()
                return{'message':'Hotel excluido!'}
            except:
                return {'message': 'An internal error ocurred trying to delete hotel'}, 500 #internal
        return {'message': 'Hotel não encontrado.'}, 400
