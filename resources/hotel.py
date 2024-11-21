from flask_restful import Resource, reqparse
from models.hotel import HotelModel
from sql_alchemy import banco
from flask_jwt_extended import jwt_required, get_jwt_identity

class Hoteis(Resource):
    def get(self):
        return {'hoteis': [hotel.json() for hotel in HotelModel.query.all()]}

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
