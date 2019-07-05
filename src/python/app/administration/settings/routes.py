from flask import render_template, request, flash, redirect, url_for, current_app
import psycopg2
import os

from app.administration.settings import settings as sloth_settings

@sloth_settings.route('/settings', methods=['GET', 'POST'])
def settings():
    config = current_app.config
    con = psycopg2.connect("dbname='"+config["DATABASE_NAME"]+"' user='"+config["DATABASE_USER"]+"' host='"+config["DATABASE_URL"]+"' password='"+config["DATABASE_PASSWORD"]+"'")
    cur = con.cursor()

    raw_items = []

    try:            
        cur.execute(
            "SELECT settings_name, display_name, settings_value FROM sloth_settings WHERE section_id = 'main'"
        )
        raw_items = cur.fetchall()
    except Exception as e:
        # TODO throw here 500
        return render_template('error.html')
    items = {item[0]:item for item in raw_items}
    return render_template('settings.html', sloth_settings = items)

def save_settings(self, settings):
    pass

@sloth_settings.route('/settings/themes', methods=['GET', 'POST'])
def theme_settings():
    config = current_app.config
    theme_folders = os.listdir(config["THEMES_PATH"])
    themes = [theme for theme in theme_folders if os.path.isfile(os.path.join(config["THEMES_PATH"], theme, "theme.json"))]

    return render_template('theme_settings.html')