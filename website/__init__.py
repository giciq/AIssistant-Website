from bson import ObjectId
from flask import Flask
from flask_login import LoginManager
from langchain.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp
from pymongo import MongoClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


try:
    client = MongoClient("MongoDB_url")
    db = client['flask_database']
    user_collection = db.User
    note_collection = db.Note
    logger.info("Successfully connected to MongoDB.")
except Exception as e:
    logger.error(f"Error connecting to MongoDB: {e}")

template = """
<s>[INST] <<SYS>>
Your name is AIssistant.
Be helpful assistant ready to answer all different questions.
If you don't know the answer be kind and apologize.
Don't talk about politics and try to not be biased.
<</SYS>>

{text} [/INST]
"""

prompt = PromptTemplate(
    input_variables=["text"],
    template=template,
)

model_path = "llama-2-7b-chat.Q2_K.gguf"
llm = LlamaCpp(
    model_path=model_path,
    temperature=0.5,
    max_tokens=500,
    top_p=1
)


def answer(question):
    response = llm.invoke(prompt.format(text=question))
    return response


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'HEHEHE'

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")


    from .models import User, Note

    login_manager = LoginManager()
    login_manager.login_view = 'auth.main'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        user_data = user_collection.find_one({"_id": ObjectId(id)})
        if user_data:
            return User(user_data)
        return None

    return app
