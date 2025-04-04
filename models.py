from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student', 'teacher', 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with the student profile
    student = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')
    
    # Relationship with the teacher profile
    teacher = db.relationship('Teacher', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_student(self):
        return self.role == 'student'
    
    def is_teacher(self):
        return self.role == 'teacher'
    
    def is_admin(self):
        return self.role == 'admin'
    
    def __repr__(self):
        return f'<User {self.username}>'

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    date_of_birth = db.Column(db.Date)
    admission_date = db.Column(db.Date, default=datetime.utcnow)
    grade_level = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Relationships
    attendances = db.relationship('Attendance', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    grades = db.relationship('Grade', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Student {self.first_name} {self.last_name}>'

class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    date_of_birth = db.Column(db.Date)
    hire_date = db.Column(db.Date, default=datetime.utcnow)
    department = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Relationships
    modules = db.relationship('Module', backref='teacher', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Teacher {self.first_name} {self.last_name}>'

class Module(db.Model):
    __tablename__ = 'modules'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    grade_level = db.Column(db.String(20))  # To filter modules by grade level
    subject = db.Column(db.String(64))
    
    # Grades associated with this module
    grades = db.relationship('Grade', backref='module', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Module {self.title}>'

class Attendance(db.Model):
    __tablename__ = 'attendances'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False)  # 'present', 'absent', 'late'
    notes = db.Column(db.Text)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    recorded_by = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    
    # Add relationship to teacher
    teacher = db.relationship('Teacher', backref='recorded_attendances', foreign_keys=[recorded_by])
    
    def __repr__(self):
        return f'<Attendance {self.student_id} {self.date} {self.status}>'

class Grade(db.Model):
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Float, nullable=False)
    max_score = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    comments = db.Column(db.Text)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    
    def __repr__(self):
        return f'<Grade {self.student_id} {self.module_id} {self.score}/{self.max_score}>'

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    
    # Add relationship to teacher (sender)
    sender = db.relationship('Teacher', backref='sent_notifications', foreign_keys=[sender_id])
    
    def __repr__(self):
        return f'<Notification {self.id} {self.title}>'
