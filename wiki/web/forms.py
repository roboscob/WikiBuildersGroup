"""
    Forms
    ~~~~~
"""
from flask_login import current_user
from flask_wtf import Form
from wtforms import BooleanField, StringField
from wtforms import TextField
from wtforms import TextAreaField
from wtforms import PasswordField
from wtforms.validators import InputRequired, Length, DataRequired, EqualTo
from wtforms.validators import ValidationError

from wiki.core import clean_url
from wiki.web import current_wiki
from wiki.web import current_users


class URLForm(Form):
    url = TextField('', [InputRequired()])

    def validate_url(form, field):
        if current_wiki.exists(field.data):
            raise ValidationError('The URL "%s" exists already.' % field.data)

    def clean_url(self, url):
        return clean_url(url)


class SearchForm(Form):
    term = TextField('', [InputRequired()])
    ignore_case = BooleanField(
        description='Ignore Case',
        # FIXME: default is not correctly populated
        default=True)


class EditorForm(Form):
    title = TextField('', [InputRequired()])
    body = TextAreaField('', [InputRequired()])
    tags = TextField('')


class LoginForm(Form):
    name = TextField('', [InputRequired()])
    password = PasswordField('', [InputRequired()])

    def validate_name(form, field):
        user = current_users.get_user(field.data)
        if not user:
            raise ValidationError('This username does not exist.')

    def validate_password(form, field):
        user = current_users.get_user(form.name.data)
        if not user:
            return
        if not user.check_password(field.data):
            raise ValidationError('Username and password do not match.')


class RegisterForm(Form):
    username = StringField('Username', [DataRequired()])
    password = PasswordField('New Password', [
        DataRequired(),
        Length(min=4),
        EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password', [DataRequired()])
    full_name = StringField('Full Name', [DataRequired()])
    bio = TextAreaField('Bio.')

    def validate_username(form, field):
        user = current_users.get_user(field.data)
        if user:
            raise ValidationError('This username already exists')
        elif ' ' in field.data:  # Usernames with spaces would error in the URL
            raise ValidationError('Username cannot contain spaces')


class UnregisterForm(Form):
    username = StringField('', [DataRequired()])

    def validate_username(form, field):
        if field.data != current_user.get_id():
            raise ValidationError('You must type the username of the user you\'re unregistering')
