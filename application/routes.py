from flask import current_app as app, request
from flask_restx import Api, Namespace, Resource

from application.models import db
from application import models, schema

api: Api = app.config['api']
movie_ns: Namespace = api.namespace('movies')
director_ns: Namespace = api.namespace('directors')
genre_ns: Namespace = api.namespace('genres')

movie_schema = schema.Movie()
movies_schema = schema.Movie(many=True)

director_schema = schema.Director()
directors_schema = schema.Director(many=True)

genre_schema = schema.Genre()
genres_schema = schema.Genre(many=True)

"""
Фильмы
"""


@movie_ns.route('/')
class MoviesView(Resource):

    def get(self):
        movies_query = db.session.query(models.Movie)  # делаем запрос в БД

        args = request.args

        director_id = args.get('director_id')  # условие с режиссером
        if director_id is not None:
            movies_query = movies_query.filter(models.Movie.director_id == director_id)

        genre_id = args.get('genre_id')  # условие с жанром
        if genre_id is not None:
            movies_query = movies_query.filter(models.Movie.genre_id == genre_id)

        movies = movies_query.all()

        return movies_schema.dump(movies), 200

    def post(self):
        movie = movie_schema.load(request.json)

        db.session.add(models.Movie(**movie))
        db.session.commit()

        return "new data created", 201


@movie_ns.route('/<int:movie_id>')
class MovieView(Resource):
    def get(self, movie_id):
        movie = db.session.query(models.Movie).get_or_404(movie_id)

        return movie_schema.dump(movie), 200

    def put(self, movie_id):
        update_row = db.session.query(models.Movie).filter(models.Movie.id == movie_id).update(request.json)
        if update_row != 1:
            return None, 400
        db.session.commit()

        return "data update", 204

    def delete(self, movie_id):
        delete_row = db.session.query(models.Movie).filter(models.Movie.id == movie_id).delete()
        if delete_row != 1:
            return None, 400
        db.session.commit()

        return "", 200


'''
Режисеры
'''


@director_ns.route('/')
class DirectorsViews(Resource):
    def get(self):
        directors = models.Director.query.all()
        return directors_schema.dump(directors), 200


@director_ns.route('/<int:director_id>')
class DirectorViews(Resource):
    def get(self, director_id):
        director = db.session.query(models.Director).get_or_404(director_id)

        return director_schema.dump(director), 200


'''
Жанры
'''


@genre_ns.route('/')
class GenresViews(Resource):
    def get(self):
        genres = models.Genre.query.all()
        return genres_schema.dump(genres), 200


@genre_ns.route('/<int:genre_id>')
class GenreViews(Resource):
    def get(self, genre_id):
        genre = db.session.query(models.Genre).get(genre_id)

        if genre is None:
            return {}, 404

        return genre_schema.dump(genre), 200
