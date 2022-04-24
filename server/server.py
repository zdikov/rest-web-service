from flask import Flask
from flask import request
from flask import abort
from flask import send_file

from dataclasses import dataclass, asdict
from io import BytesIO

from config import USERS_ENDPOINT, STATS_ENDPOINT, REPORTS_DIR, IMAGES_DIR

import json

import pika

count = '0'


@dataclass
class User:
    name: str
    avatar_url: str
    gender: str
    email: str


id_to_user_ = {}


def create_app() -> Flask:
    """
    Create flask application
    """
    app = Flask(__name__)

    @app.route(USERS_ENDPOINT, methods=['POST'])
    def add_user():
        global count
        count = str(int(count) + 1)

        id_to_user_[count] = User(name=request.json['name'], avatar_url=request.json['avatar_url'],
                                  gender=request.json['gender'],
                                  email=request.json['email'])
        return {'user_id': count}

    @app.route(f'{USERS_ENDPOINT}/<string:user_id>', methods=['GET'])
    def get_user(user_id):
        try:
            user = id_to_user_[user_id]
            response = asdict(user)
            return response
        except:
            abort(404)

    @app.route(USERS_ENDPOINT, methods=['GET'])
    def get_user_ids():
        return {'user_ids': id_to_user_.keys()}

    @app.route(f'{USERS_ENDPOINT}/stats/<string:user_id>', methods=['GET'])
    def make_stats(user_id):
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()

        channel.queue_declare(queue='queue', durable=True)

        channel.confirm_delivery()

        body_dict = asdict(id_to_user_[user_id])
        body_dict['id'] = user_id
        try:
            channel.basic_publish(exchange='', routing_key='queue',
                                  body=json.dumps(body_dict).encode(),
                                  properties=pika.BasicProperties(
                                      delivery_mode=2
                                  ))
        except pika.exceptions.UnroutableError:
            abort(500)

        connection.close()
        return {'url': f'{STATS_ENDPOINT}/{user_id}'}

    @app.route(f'{STATS_ENDPOINT}/<string:user_id>', methods=['GET'])
    def get_report(user_id):
        try:
            return send_file(REPORTS_DIR + '/' + str(user_id))
        except:
            abort(404)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
