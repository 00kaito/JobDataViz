from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Hasło', validators=[DataRequired()])
    remember_me = BooleanField('Zapamiętaj mnie')
    submit = SubmitField('Zaloguj się')

class RegistrationForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[
        DataRequired(), 
        Length(min=4, max=20)
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Hasło', validators=[
        DataRequired(), 
        Length(min=6, message='Hasło musi mieć co najmniej 6 znaków')
    ])
    password2 = PasswordField('Powtórz hasło', validators=[
        DataRequired(), 
        EqualTo('password', message='Hasła muszą być identyczne')
    ])
    submit = SubmitField('Zarejestruj się')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Ta nazwa użytkownika jest już zajęta.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Ten adres email jest już zarejestrowany.')

class UserManagementForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Rola', choices=[
        ('viewer', 'Przeglądający'),
        ('analyst', 'Analityk'),
        ('admin', 'Administrator')
    ], validators=[DataRequired()])
    is_active = BooleanField('Aktywny')
    submit = SubmitField('Zapisz zmiany')