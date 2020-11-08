from flask_wtf import FlaskForm
from wtforms import SubmitField



class AddressForm(FlaskForm):
    submit = SubmitField('submit-button')

