from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectMultipleField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class ProcessForm(FlaskForm):
    scene_id = StringField('Scene ID: ', validators=[DataRequired()])

    ee_user = StringField('USGS Username: ', validators=[DataRequired()])
    ee_pass = PasswordField('USGS Password: ', validators=[DataRequired()])

    atmo_source = SelectMultipleField('Atmosphere Data Source: ', choices=[('narr', 'NARR'), ('merra', 'MERRA')])