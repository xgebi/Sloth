from flask import render_template, request, flash, redirect, url_for, current_app
import psycopg2

from app.administration.settings import settings as sloth_settings

@sloth_settings.route('/settings', methods=['GET', 'POST'])
def settings():
    #import pdb; pdb.set_trace()

    config = current_app.config
    con = psycopg2.connect("dbname='"+config["DATABASE_NAME"]+"' user='"+config["DATABASE_USER"]+"' host='"+config["DATABASE_URL"]+"' password='"+config["DATABASE_PASSWORD"]+"'")
    cur = con.cursor()

    items = []

    try:            
        cur.execute(
            "SELECT settings_name, display_name, settings_value FROM sloth_settings WHERE section_id = 'main'"
        )
        items = cur.fetchall()
    except Exception:
        print("Expection thrown")
        return render_template('settings.html')

    print(items)
    # TODO fetch settings from database
    return render_template('settings.html')

def save_settings(self, settings):
    pass

@sloth_settings.route('/settings/themes', methods=['GET', 'POST'])
def theme_settings():
    # TODO fetch theme settings
    # TODO fetch list of themes
    return render_template('theme_settings.html')