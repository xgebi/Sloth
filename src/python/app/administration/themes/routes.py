from flask import render_template, request, flash, redirect, url_for, current_app, abort
import psycopg2
import os
import json

from app.administration.themes import themes as themes