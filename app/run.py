from typing import Dict
from flask import Flask
import pytoml as toml
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from routes.shorten_url import blueprint as shorten_url_blueprint
from shorted.shortener import Shortener


def create_app() -> Flask:
    # create and configure the app
    app = Flask(__name__)
    load_config(app)
    app.db = create_db(app.config['db'])
    app.shortener = Shortener(app.db)
    app.register_blueprint(shorten_url_blueprint)

    @app.route('/ping')
    def ping() -> str:  # pylint:disable=unused-variable
        return 'pong'

    return app


def load_config(app: Flask) -> None:
    with open('config.toml', 'rb') as config:
        for key, value in toml.loads(config.read()).items():
            app.config[key] = value


def create_db(config: Dict) -> Engine:
    user = config['user']
    password = config['password']
    host = config['host']
    port = config['port']
    name = config['name']
    db: Engine = create_engine(
        f'postgresql://{user}:{password}@{host}:{port}/{name}',
        pool_size=config.get('pool_size', 5),
    )
    return db


if __name__ == '__main__':
    print('hello world')
