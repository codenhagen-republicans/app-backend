from flask_sqlalchemy import SQLAlchemy
from passlib.hash import pbkdf2_sha256 as sha256
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import Load, load_only
from sqlalchemy.sql import func
import os

db = SQLAlchemy()

def init_db(app):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
    db.init_app(app)
    return db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), unique = True, nullable = False)
    password = db.Column(db.String(120), nullable = False)
    carts = db.relationship('Cart', order_by='Cart.id', cascade="all, delete-orphan")

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

    @classmethod
    def find_by_username(cls, username):
       return cls.query.filter_by(username = username).first()

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'username': x.username,
                'password': x.password
            }
        return {'users': list(map(lambda x: to_json(x), User.query.all()))}

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Something went wrong'}


class ItemCart(db.Model):
    """Product Items in the basket"""

    __table__name = 'items_cart'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    ean = db.Column(db.String(120), nullable = False)
    name = db.Column(db.String(120))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    carbon_footprint = db.Column(db.Float)
    cart = db.relationship('Cart', backref=db.backref('items_cart', lazy=True))


    def __repr__(self):
        return "<ItemCart: {}>".format(self.id)


    def get_footprint(user_id, start_at, end_at):
        try:
            carts = db.session.query(ItemCart.id,
                                    ItemCart.ean,
                                    ItemCart.name,
                                    Cart.total_footprint,
                                    func.sum(ItemCart.carbon_footprint))\
                            .join(Cart)\
                            .filter(Cart.user_id == user_id)\
                            .filter(Cart.created_at.between(start_at, end_at))\
                            .options(
                                Load(ItemCart).load_only("ean", "name")
                            )\
                            .group_by(ItemCart.id,
                                      ItemCart.ean,
                                      ItemCart.name,
                                      Cart.total_footprint
                            ).all()
            return carts
        except:
            return 'Something went wrong'

class Cart(db.Model):
    """Users Basket"""

    __table__name = 'cart'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    update_date = db.Column(db.DateTime, default=db.func.current_timestamp(),
                            onupdate=db.func.current_timestamp())
    total_footprint = db.Column(db.Float)
    paid = db.Column(db.Boolean, default=False)
    carts = db.relationship('User', backref=db.backref('users', lazy=True))


    def __repr__(self):
        return "<Cart: {}>".format(self.id)

    def __init__(self, user_id, cart_items):
        self.user_id = user_id
        self.cart_items = cart_items
        self.total_footprint = sum(i['carbon_footprint'] for i in cart_items)
        db.session.add(self)
        db.session.flush()
        for item in self.cart_items:
            db.session.add(
                ItemCart(cart_id=self.id, ean=item['ean'], name=item['name'],
                    price=item['price'], quantity=item['quantity'],
                    carbon_footprint=item['carbon_footprint']
                )
            )
        db.session.commit()

    def save(self, user_id, cart_items):
        self.user_id = user_id
        self.cart_items = cart_items
        db.session.add(self)
        db.session.flush()
        print(self.cart_items)
        for item in self.cart_items:
            db.session.add(
                ItemCart(cart_id=self.id,ean=item['ean'], name=item['name'],
                    price=item['price'], quantity=item['quantity']
                )
            )
        db.session.commit()

    @staticmethod
    def get_all(user_id):
        return Cart.query.options(joinedload('items_cart')).filter_by(user_id=user_id).all()

    @staticmethod
    def get_one(user_id, cart_id):
        return Cart.query.options(joinedload('items_cart')).filter_by(user_id=user_id).filter_by(id=cart_id).first()

    @staticmethod
    def delete(cart_id):
        try:
            cart = Cart.query.get(cart_id)
            import pdb; pdb.set_trace()
            db.session.delete(cart)
            db.session.commit()
            return {'message': '{} cart deleted'.format(cart.id)}, 204
        except:
            return {'message': 'Something went wrong'}, 500

    @staticmethod
    def return_all(user_id):
        def items_to_json(x):
            return {
                'ean': x.ean,
                'name': x.name,
                'price': x.price,
                'quantity': x.quantity,
                'carbon_footprint': x.carbon_footprint
            }
        def carts_to_json(c):
            return {
                'id': c.id,
                'created_at': str(c.created_at),
                'total_footprint': c.total_footprint,
                'items': list(map(lambda i: items_to_json(i), c.items_cart))
            }
        return {'carts': list(map(lambda c: carts_to_json(c), Cart.get_all(user_id)))}


class RevokedToken(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key = True)
    jti = db.Column(db.String(120))

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti = jti).first()
        return bool(query)
