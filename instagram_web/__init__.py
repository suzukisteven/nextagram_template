import os
import braintree

from app import app
from flask import render_template

from flask_assets import Environment, Bundle
from .util.assets import bundles
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager

assets = Environment(app)
assets.register(bundles)

login_manager = LoginManager(app)
csrf = CSRFProtect(app)

TRANSACTION_SUCCESS_STATUSES = [
    braintree.Transaction.Status.Authorized,
    braintree.Transaction.Status.Authorizing,
    braintree.Transaction.Status.Settled,
    braintree.Transaction.Status.SettlementConfirmed,
    braintree.Transaction.Status.SettlementPending,
    braintree.Transaction.Status.Settling,
    braintree.Transaction.Status.SubmittedForSettlement
]

@login_manager.user_loader
def load_user(id):
        return User.get_or_none(id=id)

login_manager.login_view = "sessions.new"
login_manager.login_message = u"You must be logged in to view this content."
login_manager.login_message_category = "danger"

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id=app.config.get('BT_MERCHANT_ID'),
        public_key=app.config.get('BT_PUBLIC_KEY'),
        private_key=app.config.get('BT_PRIVATE_KEY')
    )
)

def generate_client_token():
    return gateway.client_token.generate()

def transact(options):
    return gateway.transaction.sale(options)

def find_transaction(id):
    return gateway.transaction.find(id)

from instagram_web.blueprints.users.views import users_blueprint, User
from instagram_web.blueprints.images.views import images_blueprint
from instagram_web.blueprints.sessions.views import sessions_blueprint
from instagram_web.blueprints.donations.views import donations_blueprint

app.register_blueprint(users_blueprint, url_prefix="/users")
app.register_blueprint(images_blueprint, url_prefix="/images")
app.register_blueprint(sessions_blueprint, url_prefix="/")
app.register_blueprint(donations_blueprint, url_prefix="/donations")

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(404)
def internal_server_error(e):
    return render_template('404.html'), 404

@app.route("/")
def home():
    logo = app.config['S3_LOCATION'] + "33instagram-logo2019-03-14_041326.230982"
    return render_template('home.html')

