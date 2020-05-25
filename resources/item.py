from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    jwt_optional,
    get_jwt_identity,
    fresh_jwt_required
)
from models.item import ItemModel
from models.store import StoreModel


class Item(Resource):
    parser = reqparse.RequestParser() #initialise parser
    parser.add_argument('price',
        type=float,
        required=True,
        help="This argument cannot be blank"
    )
    parser.add_argument('store_id',
        type=float,
        required=True,
        help="Every item needs a store id"
    )

    @jwt_required
    def get(self, name):
        item = ItemModel.find_by_name(name)

        if item:
            return item.json()
        return {'message': 'Item does not exist'}, 404

    @fresh_jwt_required
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': f'An item with name \'{name}\' already exists'}, 400

        data = Item.parser.parse_args()

        if not StoreModel.find_by_id(data['store_id']):
            return {'message': f'Store with store_id: {int(data["store_id"])} not found, please create a store first'}, 400

        item = ItemModel(name, **data)

        try:
            item.save_to_db()
        except:
            return {'message': 'An error occured while creating the item'}, 500
        
        return item.json(), 201

    @fresh_jwt_required
    def delete(self, name):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Admin access is required'}, 401

        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {'message': 'Item deleted'}

        return {'message': 'Item not found'}, 404

    @jwt_required
    def put(self, name):
        data = Item.parser.parse_args()

        if not StoreModel.find_by_id(data['store_id']):
            return {'message': f'Store with store_id: {int(data["store_id"])} not found, please create a store first'}, 400

        item = ItemModel.find_by_name(name)
        
        if item is None:
            item = ItemModel(name, **data)
        else:
            item.price = data['price']

        item.save_to_db()

        return item.json()


class ItemList(Resource):
    @jwt_optional
    def get(self):
        user_id = get_jwt_identity()
        items = [item.json() for item in ItemModel.find_all()]
        if user_id:
            return {'items': items}
        return {
            'items': [item['name'] for item in items],
            'message': 'Product details are available only for logged in users'
        }, 200
