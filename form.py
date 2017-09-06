from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectMultipleField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class ProcessForm(FlaskForm):
    scene_id = StringField('Scene ID: ', validators=[DataRequired()], id='scene_id')

    atmo_source = SelectMultipleField('Atmosphere Data Source: ', choices=[('narr', 'NARR'), ('merra', 'MERRA')])

    buoy_id = SelectMultipleField('Buoy IDs: ', choices=[])
