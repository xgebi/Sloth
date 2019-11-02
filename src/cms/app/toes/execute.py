from toes import render_toe
import os

print(render_toe(template="dashboard.html", path_to_templates=os.path.join(os.getcwd(), 'src', 'cms', 'app', 'templates'), title="Ahoy", description="I've got this"))