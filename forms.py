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
    preferred_category = SelectField('Branża/kategoria zatrudnienia', validators=[DataRequired()])
    submit = SubmitField('Zarejestruj się')
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # Pobierz dostępne kategorie z pliku lub bazy danych
        self.preferred_category.choices = self.get_available_categories()
    
    def get_available_categories(self):
        """Pobierz dostępne kategorie zatrudnienia"""
        try:
            # Spróbuj pobrać kategorie z aplikacji Dash
            from flask import current_app
            if current_app:
                with current_app.app_context():
                    # Spróbuj pobrać dane z sesji lub cache
                    pass
        except Exception:
            pass
        
        # Domyślne kategorie jeśli brak danych
        default_categories = [
            ('', 'Wybierz kategorię'),
            ('IT', 'Informatyka / IT'),
            ('Finance', 'Finanse / Bankowość'),
            ('Marketing', 'Marketing / Reklama'),
            ('Sales', 'Sprzedaż'),
            ('HR', 'Zasoby Ludzkie'),
            ('Operations', 'Operacje / Logistyka'),
            ('Engineering', 'Inżynieria'),
            ('Healthcare', 'Ochrona Zdrowia'),
            ('Education', 'Edukacja'),
            ('Other', 'Inne')
        ]
        return default_categories
    
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
    username = StringField('Nazwa użytkownika', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Rola', choices=[
        ('viewer', 'Przeglądający'),
        ('analyst', 'Analityk'),
        ('admin', 'Administrator')
    ], validators=[DataRequired()])
    is_active = BooleanField('Aktywny')
    submit = SubmitField('Zapisz zmiany')