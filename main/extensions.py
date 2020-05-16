# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory located in app.py."""
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_static_digest import FlaskStaticDigest
from flask_wtf.csrf import CSRFProtect

bcrypt = Bcrypt()
csrf_protect = CSRFProtect()
login_manager = LoginManager()
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
debug_toolbar = DebugToolbarExtension()
flask_static_digest = FlaskStaticDigest()


login_manager.session_protection = 'basic'
login_manager.login_view = 'auth.login'
login_manager.login_message = u"请登录后访问该页面."
login_manager.refresh_view = 'auth.login'

