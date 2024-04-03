#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()
        user = User(
            username = data.get('username'),
            image_url = data.get('image_url'),
            bio = data.get('bio')
        )
        password_hash = data.get('password')
        user.password_hash = password_hash
        
        try:
            db.session.add(user)
            db.session.commit()
            return user.to_dict(), 201
        
        except:
            return {'message':'User is Invalid'}, 422
        
class CheckSession(Resource):
    def get(self):
        user_id = session['user_id']
        if user_id is not None:
            user = User.query.filter(User.id == user_id).first()
            return user.to_dict(), 200
        else:
            return {'message':'Session unavailable'}, 401

class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter(User.username==data.get('username')).first()
        password = data.get('password')

        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(), 200
       
        return {'message': 'User not authorized'}, 401


class Logout(Resource):
    def delete(self):
        session['user_id'] = None
        return {'message':'Logout'}, 401

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.filter(User.id==user_id).first()
            if user:
                recipes = user.recipes
                recipe = [recipe.to_dict() for recipe in recipes]
                return recipe, 200
        return {'message':'unauthorized'}, 401
    
    def post(self):
        user_id = session['user_id']
        if user_id is not None:
            data = request.get_json()
            recipe = Recipe(
                title=data.get('title'),
                instructions=data.get('instructions'),
                minutes_to_complete= data.get('minutes_to_complete'),
                user_id = user_id
            )
            try:
                db.session.add(recipe)
                db.session.commit()
                return recipe.to_dict(), 201
            except:
                return {'message': 'Invalid recipe data.'}, 422
        else:
            return {'message': 'Unauthorized'}, 401

    
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)