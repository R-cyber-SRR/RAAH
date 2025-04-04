from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, DateField, FloatField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('student', 'Student'), ('teacher', 'Teacher')], validators=[DataRequired()])
    grade_level = SelectField('Grade Level', choices=[
        ('', 'Select Grade Level'),
        ('1', 'Grade 1'),
        ('2', 'Grade 2'),
        ('3', 'Grade 3'),
        ('4', 'Grade 4'),
        ('5', 'Grade 5'),
        ('6', 'Grade 6'),
        ('7', 'Grade 7'),
        ('8', 'Grade 8'),
        ('9', 'Grade 9'),
        ('10', 'Grade 10'),
        ('11', 'Grade 11'),
        ('12', 'Grade 12')
    ])
    department = SelectField('Department', choices=[
        ('', 'Select Department'),
        ('mathematics', 'Mathematics'),
        ('science', 'Science'),
        ('language', 'Language Arts'),
        ('social_studies', 'Social Studies'),
        ('arts', 'Arts'),
        ('physical_education', 'Physical Education'),
        ('technology', 'Technology'),
        ('other', 'Other')
    ])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class ModuleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=128)])
    description = TextAreaField('Description')
    file = FileField('Upload File')
    grade_level = SelectField('Grade Level', choices=[
        ('', 'Select Grade Level'),
        ('1', 'Grade 1'),
        ('2', 'Grade 2'),
        ('3', 'Grade 3'),
        ('4', 'Grade 4'),
        ('5', 'Grade 5'),
        ('6', 'Grade 6'),
        ('7', 'Grade 7'),
        ('8', 'Grade 8'),
        ('9', 'Grade 9'),
        ('10', 'Grade 10'),
        ('11', 'Grade 11'),
        ('12', 'Grade 12')
    ])
    subject = SelectField('Subject', choices=[
        ('', 'Select Subject'),
        ('mathematics', 'Mathematics'),
        ('science', 'Science'),
        ('language', 'Language Arts'),
        ('social_studies', 'Social Studies'),
        ('arts', 'Arts'),
        ('physical_education', 'Physical Education'),
        ('technology', 'Technology'),
        ('other', 'Other')
    ])
    submit = SubmitField('Upload Module')

class GradeForm(FlaskForm):
    student = SelectField('Student', coerce=int, validators=[DataRequired()])
    module = SelectField('Module', coerce=int, validators=[DataRequired()])
    score = FloatField('Score', validators=[DataRequired()])
    max_score = FloatField('Maximum Score', validators=[DataRequired()])
    comments = TextAreaField('Comments')
    submit = SubmitField('Submit Grade')

class AttendanceForm(FlaskForm):
    student = SelectField('Student', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Record Attendance')

class NotificationForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=128)])
    message = TextAreaField('Message', validators=[DataRequired()])
    student = SelectField('Student', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Send Notification')

class AIAssistantForm(FlaskForm):
    prompt = TextAreaField('Your Question', validators=[DataRequired()])
    submit = SubmitField('Ask AI Assistant')
