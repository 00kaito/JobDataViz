from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User
import json
import os

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    remember_me = BooleanField('Zapamiętaj mnie')
    submit = SubmitField('Zaloguj się')

class RegistrationForm(FlaskForm):
    first_name = StringField('Imię', validators=[
        DataRequired(), 
        Length(min=2, max=50, message='Imię musi mieć od 2 do 50 znaków')
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
    employment_category = SelectField('Branża/kategorie zatrudnienia, których statystyki najbardziej Cię interesują', validators=[DataRequired()])
    submit = SubmitField('Zarejestruj się')
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # Ustaw dostępne kategorie zatrudnienia
        self.employment_category.choices = self.get_employment_categories()
    
    def get_employment_categories(self):
        """Pobierz kategorie zatrudnienia IT"""
        categories = [
            ('', 'Wybierz kategorię'),
            ('Frontend', 'Frontend'),
            ('Backend', 'Backend'),
            ('FullStack', 'FullStack'),
            ('Data/AI', 'Data/AI'),
            ('Admin / Devops & Infra', 'Admin / Devops & Infra'),
            ('Security', 'Security'),
            ('QA & Testing', 'QA & Testing'),
            ('Architecture', 'Architecture'),
            ('PM / ERP & Business', 'PM / ERP & Business')
        ]
        return categories
    
    def validate_first_name(self, first_name):
        # Sprawdź czy imię zawiera tylko litery i spacje
        import re
        if not re.match("^[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ ]+$", first_name.data):
            raise ValidationError('Imię może zawierać tylko litery i spacje.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Ten adres email jest już zarejestrowany.')

class UserManagementForm(FlaskForm):
    first_name = StringField('Imię', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    employment_category = SelectField('Kategoria zatrudnienia', validators=[DataRequired()])
    role = SelectField('Rola', choices=[
        ('viewer', 'Przeglądający'),
        ('analyst', 'Analityk'),
        ('admin', 'Administrator')
    ], validators=[DataRequired()])
    is_active = BooleanField('Aktywny')
    submit = SubmitField('Zapisz zmiany')
    
    def __init__(self, *args, **kwargs):
        super(UserManagementForm, self).__init__(*args, **kwargs)
        # Ustaw dostępne kategorie zatrudnienia
        self.employment_category.choices = self.get_employment_categories()
    
    def get_employment_categories(self):
        """Pobierz kategorie zatrudnienia IT"""
        categories = [
            ('Frontend', 'Frontend'),
            ('Backend', 'Backend'),
            ('FullStack', 'FullStack'),
            ('Data/AI', 'Data/AI'),
            ('Admin / Devops & Infra', 'Admin / Devops & Infra'),
            ('Security', 'Security'),
            ('QA & Testing', 'QA & Testing'),
            ('Architecture', 'Architecture'),
            ('PM / ERP & Business', 'PM / ERP & Business')
        ]
        return categories