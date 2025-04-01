import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/people', methods=['GET'])
def get_people():

    people = People.query.all()

    return jsonify([person.serialize() for person in people])

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):

    person = People.query.get_or_404(people_id)

    return jsonify(person.serialize())

@app.route('/planet', methods=['GET'])
def get_planets():

    planets = Planet.query.all()

    return jsonify([planet.serialize() for planet in planets])

@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):

    planet = Planet.query.get_or_404(planet_id)

    return jsonify(planet.serialize())

@app.route('/user', methods=['GET'])
def get_users():

    users = User.query.all()

    return jsonify([user.serialize() for user in users])

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):

    user = User.query.get_or_404(user_id)

    return jsonify(user.serialize())

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():

    user = User.query.first()
    favorites = Favorite.query.filter_by(user_id = user.id).all()

    return jsonify(favorite.serialize() for favorite in favorites)

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):

    planet = Planet.query.get(planet_id)
    user = User.query.first()
    new_favorite = Favorite(user_id = user.id, planet_id = planet_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"message":"Favorito añadido"}),201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_person(people_id):

    user = User.query.first()
    new_favorite = Favorite(user_id = user.id, people_id = people_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"message":"Favorito añadido"}),201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):

    user = User.query.first()
    result = db.session.query(Favorite).filter_by(user_id = user.id, planet_id = planet_id).delete()
    if result > 0: db.session.commit()

    return jsonify({"message":"Favorito borrado"})

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_person(people_id):

    user = User.query.first()
    result = db.session.query(Favorite).filter_by(user_id = user.id, people_id = people_id).delete()
    if result > 0: db.session.commit()

    return jsonify({"message":"Favorito borrado"})

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
