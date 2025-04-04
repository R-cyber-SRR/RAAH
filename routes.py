import os
import uuid
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, send_from_directory, jsonify, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import app, db
from models import User, Student, Teacher, Module, Attendance, Grade, Notification
from forms import ModuleForm, GradeForm, AttendanceForm, NotificationForm, AIAssistantForm
from ai_assistant import text_to_speech, speech_to_text, speech_to_speech_translation, text_to_image, educational_assistant

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_student():
            return redirect(url_for('student_dashboard'))
        elif current_user.is_teacher():
            return redirect(url_for('teacher_dashboard'))
    return render_template('index.html')

# Student routes
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if not current_user.is_student():
        flash('Access denied. Student privileges required.', 'danger')
        return redirect(url_for('index'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    # Get recent grades
    recent_grades = Grade.query.filter_by(student_id=student.id).order_by(Grade.date.desc()).limit(5).all()
    
    # Get recent attendance
    recent_attendance = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.date.desc()).limit(5).all()
    
    # Get unread notifications
    unread_notifications = Notification.query.filter_by(student_id=student.id, read=False).count()
    
    # Get total modules available for the student's grade
    modules_count = Module.query.filter_by(grade_level=student.grade_level).count()
    
    return render_template('student/dashboard.html', 
                           student=student,
                           recent_grades=recent_grades,
                           recent_attendance=recent_attendance,
                           unread_notifications=unread_notifications,
                           modules_count=modules_count)

@app.route('/student/modules')
@login_required
def student_modules():
    if not current_user.is_student():
        flash('Access denied. Student privileges required.', 'danger')
        return redirect(url_for('index'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    # Get modules for the student's grade level
    modules = Module.query.filter_by(grade_level=student.grade_level).order_by(Module.created_at.desc()).all()
    
    return render_template('student/modules.html', modules=modules)

@app.route('/student/grades')
@login_required
def student_grades():
    if not current_user.is_student():
        flash('Access denied. Student privileges required.', 'danger')
        return redirect(url_for('index'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    # Get all grades for the student
    grades = Grade.query.filter_by(student_id=student.id).order_by(Grade.date.desc()).all()
    
    # Calculate average grade
    total_percentage = 0
    if grades:
        for grade in grades:
            total_percentage += (grade.score / grade.max_score) * 100
        average_grade = total_percentage / len(grades)
    else:
        average_grade = 0
    
    return render_template('student/grades.html', grades=grades, average_grade=average_grade)

@app.route('/student/attendance')
@login_required
def student_attendance():
    if not current_user.is_student():
        flash('Access denied. Student privileges required.', 'danger')
        return redirect(url_for('index'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    # Get all attendance records for the student
    attendance_records = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.date.desc()).all()
    
    # Calculate attendance statistics
    total_records = len(attendance_records)
    present_count = sum(1 for record in attendance_records if record.status == 'present')
    absent_count = sum(1 for record in attendance_records if record.status == 'absent')
    late_count = sum(1 for record in attendance_records if record.status == 'late')
    
    attendance_rate = (present_count / total_records * 100) if total_records > 0 else 0
    
    return render_template('student/attendance.html', 
                           attendance_records=attendance_records,
                           attendance_rate=attendance_rate,
                           present_count=present_count,
                           absent_count=absent_count,
                           late_count=late_count)

@app.route('/student/notifications')
@login_required
def student_notifications():
    if not current_user.is_student():
        flash('Access denied. Student privileges required.', 'danger')
        return redirect(url_for('index'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    # Get all notifications for the student
    notifications = Notification.query.filter_by(student_id=student.id).order_by(Notification.date.desc()).all()
    
    # Mark all notifications as read
    for notification in notifications:
        if not notification.read:
            notification.read = True
    
    db.session.commit()
    
    return render_template('student/notifications.html', notifications=notifications)

@app.route('/student/ai_assistant', methods=['GET', 'POST'])
@login_required
def student_ai_assistant():
    if not current_user.is_student():
        flash('Access denied. Student privileges required.', 'danger')
        return redirect(url_for('index'))
    
    form = AIAssistantForm()
    
    return render_template('student/ai_assistant.html', form=form)

# Teacher routes
@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if not current_user.is_teacher():
        flash('Access denied. Teacher privileges required.', 'danger')
        return redirect(url_for('index'))
    
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    
    # Get counts for dashboard
    module_count = Module.query.filter_by(teacher_id=teacher.id).count()
    student_count = Student.query.count()
    
    # Get recent modules
    recent_modules = Module.query.filter_by(teacher_id=teacher.id).order_by(Module.created_at.desc()).limit(5).all()
    
    return render_template('teacher/dashboard.html', 
                           teacher=teacher,
                           module_count=module_count,
                           student_count=student_count,
                           recent_modules=recent_modules)

@app.route('/teacher/modules', methods=['GET', 'POST'])
@login_required
def teacher_modules():
    if not current_user.is_teacher():
        flash('Access denied. Teacher privileges required.', 'danger')
        return redirect(url_for('index'))
    
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    form = ModuleForm()
    
    if form.validate_on_submit():
        # Handle file upload
        file_path = None
        if form.file.data:
            file = form.file.data
            filename = secure_filename(file.filename)
            # Add unique identifier to avoid overwriting
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
        
        # Create new module
        module = Module(
            title=form.title.data,
            description=form.description.data,
            file_path=file_path,
            teacher_id=teacher.id,
            grade_level=form.grade_level.data,
            subject=form.subject.data
        )
        
        db.session.add(module)
        db.session.commit()
        
        flash('Module uploaded successfully!', 'success')
        return redirect(url_for('teacher_modules'))
    
    # Get all modules created by the teacher
    modules = Module.query.filter_by(teacher_id=teacher.id).order_by(Module.created_at.desc()).all()
    
    return render_template('teacher/modules.html', form=form, modules=modules)

@app.route('/teacher/grades', methods=['GET', 'POST'])
@login_required
def teacher_grades():
    if not current_user.is_teacher():
        flash('Access denied. Teacher privileges required.', 'danger')
        return redirect(url_for('index'))
    
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    form = GradeForm()
    
    # Populate form choices
    form.module.choices = [(m.id, m.title) for m in Module.query.filter_by(teacher_id=teacher.id).all()]
    form.student.choices = [(s.id, f"{s.first_name} {s.last_name}") for s in Student.query.all()]
    
    if form.validate_on_submit():
        # Create new grade entry
        grade = Grade(
            score=form.score.data,
            max_score=form.max_score.data,
            comments=form.comments.data,
            student_id=form.student.data,
            module_id=form.module.data,
            date=datetime.utcnow().date()
        )
        
        db.session.add(grade)
        db.session.commit()
        
        # Create notification for the student
        module = Module.query.get(form.module.data)
        notification = Notification(
            title=f"New grade for {module.title}",
            message=f"You received a grade of {grade.score}/{grade.max_score} for {module.title}.",
            student_id=form.student.data,
            sender_id=teacher.id,
            date=datetime.utcnow()
        )
        
        db.session.add(notification)
        db.session.commit()
        
        flash('Grade submitted successfully!', 'success')
        return redirect(url_for('teacher_grades'))
    
    # Get all grades for modules created by the teacher
    grades = Grade.query.join(Module).filter(Module.teacher_id == teacher.id).order_by(Grade.date.desc()).all()
    
    return render_template('teacher/grades.html', form=form, grades=grades)

@app.route('/teacher/attendance', methods=['GET', 'POST'])
@login_required
def teacher_attendance():
    if not current_user.is_teacher():
        flash('Access denied. Teacher privileges required.', 'danger')
        return redirect(url_for('index'))
    
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    form = AttendanceForm()
    
    # Populate form choices
    form.student.choices = [(s.id, f"{s.first_name} {s.last_name}") for s in Student.query.all()]
    
    if form.validate_on_submit():
        # Check if attendance record already exists for this student and date
        existing_record = Attendance.query.filter_by(
            student_id=form.student.data,
            date=form.date.data
        ).first()
        
        if existing_record:
            # Update existing record
            existing_record.status = form.status.data
            existing_record.notes = form.notes.data
            existing_record.recorded_by = teacher.id
            flash('Attendance record updated!', 'success')
        else:
            # Create new attendance record
            attendance = Attendance(
                date=form.date.data,
                status=form.status.data,
                notes=form.notes.data,
                student_id=form.student.data,
                recorded_by=teacher.id
            )
            db.session.add(attendance)
            flash('Attendance recorded successfully!', 'success')
        
        db.session.commit()
        return redirect(url_for('teacher_attendance'))
    
    # Pre-fill date with today's date
    if not form.date.data:
        form.date.data = datetime.utcnow().date()
    
    # Get recent attendance records
    attendance_records = Attendance.query.filter_by(recorded_by=teacher.id).order_by(Attendance.date.desc()).limit(20).all()
    
    return render_template('teacher/attendance.html', form=form, attendance_records=attendance_records)

@app.route('/teacher/notifications', methods=['GET', 'POST'])
@login_required
def teacher_notifications():
    if not current_user.is_teacher():
        flash('Access denied. Teacher privileges required.', 'danger')
        return redirect(url_for('index'))
    
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    form = NotificationForm()
    
    # Populate form choices
    form.student.choices = [(s.id, f"{s.first_name} {s.last_name}") for s in Student.query.all()]
    
    if form.validate_on_submit():
        # Create new notification
        notification = Notification(
            title=form.title.data,
            message=form.message.data,
            student_id=form.student.data,
            sender_id=teacher.id,
            date=datetime.utcnow()
        )
        
        db.session.add(notification)
        db.session.commit()
        
        flash('Notification sent successfully!', 'success')
        return redirect(url_for('teacher_notifications'))
    
    # Get notifications sent by the teacher
    notifications = Notification.query.filter_by(sender_id=teacher.id).order_by(Notification.date.desc()).all()
    
    return render_template('teacher/notifications.html', form=form, notifications=notifications)

@app.route('/teacher/ai_assistant', methods=['GET', 'POST'])
@login_required
def teacher_ai_assistant():
    if not current_user.is_teacher():
        flash('Access denied. Teacher privileges required.', 'danger')
        return redirect(url_for('index'))
    
    form = AIAssistantForm()
    
    return render_template('teacher/ai_assistant.html', form=form)

# Shared routes
@app.route('/download/<path:filename>')
@login_required
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# AI Assistant API routes
@app.route('/api/ai/text_to_speech', methods=['POST'])
@login_required
def api_text_to_speech():
    data = request.json
    text = data.get('text')
    voice = data.get('voice', 'alloy')
    
    if not text:
        return jsonify({"error": "Text is required"}), 400
    
    result, status_code = text_to_speech(text, voice)
    return jsonify(result), status_code

@app.route('/api/ai/speech_to_text', methods=['POST'])
@login_required
def api_speech_to_text():
    if 'audio' not in request.files:
        return jsonify({"error": "Audio file is required"}), 400
    
    audio_file = request.files['audio']
    
    result, status_code = speech_to_text(audio_file)
    return jsonify(result), status_code

@app.route('/api/ai/speech_to_speech_translation', methods=['POST'])
@login_required
def api_speech_to_speech_translation():
    if 'audio' not in request.files:
        return jsonify({"error": "Audio file is required"}), 400
    
    audio_file = request.files['audio']
    target_language = request.form.get('target_language', 'English')
    
    result, status_code = speech_to_speech_translation(audio_file, target_language)
    return jsonify(result), status_code

@app.route('/api/ai/text_to_image', methods=['POST'])
@login_required
def api_text_to_image():
    data = request.json
    prompt = data.get('prompt')
    
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    
    result, status_code = text_to_image(prompt)
    return jsonify(result), status_code

@app.route('/api/ai/educational_assistant', methods=['POST'])
@login_required
def api_educational_assistant():
    data = request.json
    prompt = data.get('prompt')
    
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    
    role = 'student' if current_user.is_student() else 'teacher'
    result, status_code = educational_assistant(prompt, role)
    return jsonify(result), status_code
