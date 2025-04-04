from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app import db
from models import User, Student, Teacher
from forms import LoginForm, RegisterForm

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_student():
            return redirect(url_for('student_dashboard'))
        elif current_user.is_teacher():
            return redirect(url_for('teacher_dashboard'))
        else:
            return redirect(url_for('index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            
            if user.is_student():
                return redirect(next_page or url_for('student_dashboard'))
            elif user.is_teacher():
                return redirect(next_page or url_for('teacher_dashboard'))
            else:
                return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'danger')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists', 'danger')
            return render_template('register.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        
        # Add user to database
        db.session.add(user)
        db.session.commit()
        
        # Create profile based on role
        if user.is_student():
            student = Student(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                user_id=user.id,
                grade_level=form.grade_level.data if hasattr(form, 'grade_level') else None
            )
            db.session.add(student)
        elif user.is_teacher():
            teacher = Teacher(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                user_id=user.id,
                department=form.department.data if hasattr(form, 'department') else None
            )
            db.session.add(teacher)
        
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))
