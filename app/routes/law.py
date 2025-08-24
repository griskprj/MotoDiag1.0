from flask import Blueprint, render_template

law_bp = Blueprint('law_bp', __name__, url_prefix='/law')

@law_bp.route("/policy")
def policy():
    return render_template('/law/privacy_policy.html')

@law_bp.route("/terms_for_use")
def terms_for_use():
    return render_template('/law/terms_for_use.html')
