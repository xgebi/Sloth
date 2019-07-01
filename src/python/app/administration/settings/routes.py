from flask import render_template, request, flash, redirect, url_for, current_app

from app.administration.settings import settings as sloth_settings

@sloth_settings.route('/settings', methods=['GET', 'POST'])
def settings():
    # TODO fetch settings from database
    return render_template('settings.html')

@sloth_settings.route('/settings/themes', methods=['GET', 'POST'])
def theme_settings():
    # TODO fetch theme settings
    # TODO fetch list of themes
    return render_template('theme_settings.html')