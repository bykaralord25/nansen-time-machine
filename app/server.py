import os
from flask import Flask
from dotenv import load_dotenv
from .routes import bp

def create_app():
    load_dotenv()
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.register_blueprint(bp)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=int(os.getenv("FLASK_PORT", "5050")), debug=os.getenv("FLASK_DEBUG", "0") == "1")
