# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template
from flask_login import login_required,current_user

from main.extensions import cache

from main.models.auth.users import User
from main.models.auth.users import UserRole
from main.models.auth.roles import Role

blueprint = Blueprint("user", __name__, url_prefix="/users", static_folder="../static")


@blueprint.route("/")
@login_required
def members():
    """List members."""
    user = User.query.with_entities(User,UserRole,Role)\
        .join(UserRole,UserRole.user_id==User.id)\
        .join(Role,Role.id==UserRole.role_id)\
        .filter(User.id==current_user.id)\
        .first()
        
    return render_template("users/members.html",user=user)
