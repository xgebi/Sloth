from flask import request, flash, url_for, current_app, abort, redirect
from app.web.design import design


@design.route("/design")
def serve_design():
    pass
# return render_toe(template="design.toe", path_to_templates=current_app.config["TEMPLATES_PATH"], data={ "page_title": "Sloth - Design System", "design_system": True, "test": "<br /> Hello" } )
