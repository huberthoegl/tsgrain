from flask_wtf import FlaskForm, Form
from wtforms import StringField, IntegerField, BooleanField, SubmitField, FormField, DateTimeField, IntegerField, SelectField
from wtforms.validators import DataRequired


class SettingsForm(FlaskForm):
    # Anzahl_Tennisplätze = StringField('Anzahl Tennisplätze')
    max_zeit_manuell = StringField('Maximale Manuelle Beregnungsdauer')
    # max_zeit_auto_aus = StringField('Maximale Dauer beim Deaktivieren der Automatik')
    submit = SubmitField('OK')

class SetDateTimeForm(FlaskForm):
    date_new = StringField('Datum Start')
    time_new = StringField('Uhrzeit Start')
    submitdatetime = SubmitField('OK')

class InputForm(FlaskForm):
    date_start = StringField('Datum Start', validators=[DataRequired()])
    time_start =StringField('Uhrzeit Start', validators=[DataRequired()])
    time_dauer = StringField('Dauer der Beregnung pro Platz', validators=[DataRequired()])
    platz_1 = BooleanField('Platz 1')
    platz_2 = BooleanField('Platz 2')
    platz_3 = BooleanField('Platz 3')
    platz_4 = BooleanField('Platz 4')
    platz_5 = BooleanField('Platz 5')
    platz_6 = BooleanField('Platz 6')
    platz_7 = BooleanField('Platz 7')
    zyklus_zeit = StringField('Zyklus Zeit')
    submit = SubmitField('OK')

class StatusForm(FlaskForm):
   status_platz_1 = SubmitField('Platz 1')
   status_platz_2 = SubmitField('Platz 2')
   status_platz_3 = SubmitField('Platz 3')
   status_platz_4 = SubmitField('Platz 4')
   status_platz_5 = SubmitField('Platz 5')
   status_platz_6 = SubmitField('Platz 6')
   status_platz_7 = SubmitField('Platz 7')


