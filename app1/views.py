import os
import cv2
import numpy as np
import torch
import paho.mqtt.client as mqtt
from facenet_pytorch import InceptionResnetV1, MTCNN
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import Student, Attendance, CameraConfiguration
from django.core.files.base import ContentFile
from datetime import datetime, timedelta
from django.utils import timezone
import pygame  # Import pygame for playing sounds
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
import threading
import time
import base64
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Student
from datetime import datetime
from django.shortcuts import render, redirect
from .models import Attendance
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
import calendar
from datetime import time as dt_time
from datetime import date# if you need time object from datetime
from calendar import monthrange
from datetime import timedelta
from django.db.models import Count
from .models import Attendance, Student
from django.utils.timezone import localtime
# from datetime import time
# from datetime import time as dt_time
# import time


def landing_page(request):
    return render(request, 'home1.html')  # Shown first when accessing "/"

def redirect_to_login(request):
    return redirect('admin_login') 

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:  # Ensuring it's an admin
            login(request, user)
            return redirect('home')  # Redirect to dashboard/home.html
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials or not admin.'})
    return render(request, 'login.html')  # Show login form

@login_required
def home(request):
    return render(request, 'home.html')

def student_register(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        roll_number = request.POST['roll_number']
        student_class = request.POST['student_class']
        username = request.POST['username']
        password = request.POST['password']

        # Process the base64 image data
        image_data = request.POST['image_data']
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        image_file = ContentFile(base64.b64decode(imgstr), name=f'{username}_photo.{ext}')

        # Save student object
        Student.objects.create(
            name=name,
            email=email,
            roll_number=roll_number,
            student_class=student_class,
            username=username,
            password=password,
            image=image_file,
        )

        # Redirect to student login page
        return redirect('student_login')  # Make sure this matches your URL name

    return render(request, 'student_register.html')

def student_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            student = Student.objects.get(username=username, password=password)
            if not student.authorized:
                messages.error(request, "Your account has not been authorized by the admin yet.")
                return render(request, 'student_login.html')

            # ✅ Set session key for logged-in student
            request.session['student_username'] = student.username
            print("✅ Logged in student username set in session:", request.session.get('student_username'))

            return redirect('student_dashboard')

        except Student.DoesNotExist:
            messages.error(request, "Invalid username or password.")
            return render(request, 'student_login.html')

    return render(request, 'student_login.html')
def student_logout(request):
    request.session.flush()  # Clears session
    return redirect('student_login')

def build_calendar(current_date, late_dates, absent_dates, present_dates):
    year = current_date.year
    month = current_date.month

    _, num_days = monthrange(year, month)

    calendar_weeks = []
    week = []

    for day in range(1, num_days + 1):
        current_day = date(year, month, day)

        # Fill initial empty slots (Mon=0, ..., Sun=6)
        if len(week) == 0 and current_day.weekday() != 0:
            for _ in range(current_day.weekday()):
                week.append({'day': '', 'status': ''})

        # Determine status
        if current_day in absent_dates:
            status = 'absent'
        elif current_day in late_dates:
            status = 'late'
        elif current_day in present_dates:
            status = 'present'
        elif current_day > date.today():
            status = 'future'
        else:
            status = ''

        week.append({'day': day, 'status': status})

        if len(week) == 7:
            calendar_weeks.append(week)
            week = []

    if week:
        while len(week) < 7:
            week.append({'day': '', 'status': ''})
        calendar_weeks.append(week)

    return calendar_weeks

def student_dashboard(request):
    username = request.session.get('student_username')
    
    if not username:
        return render(request, 'error.html', {'message': 'User not logged in'})

    try:
        student = Student.objects.get(username=username)
    except Student.DoesNotExist:
        return render(request, 'error.html', {'message': 'Student not found'})

    attendance_records = Attendance.objects.filter(student=student).order_by('-date')

    total_present = 0
    total_late = 0
    total_absent = 0
    attendance_score = 0.0

    present_dates = set()
    late_dates = set()
    absent_dates = set()

    for record in attendance_records:
        print(f"Date: {record.date} | Check-in: {record.check_in_time} | Status: {getattr(record, 'status', 'Unknown')}")
        record_date = record.date
        print(record.date)
        check_in_datetime = record.check_in_time

        if check_in_datetime:
            check_in = localtime(check_in_datetime).time()
            print(check_in)

            if check_in < dt_time(10, 50):
                total_present += 1
                print("added in present days")
                attendance_score += 1.0
                record.status = "Present"
                present_dates.add(record_date)

            elif dt_time(10, 50) <= check_in < dt_time(11, 0):
                total_late += 1
                print("added in late days")
                attendance_score += 0.75
                record.status = "Late"
                late_dates.add(record_date)

            else:  # Check-in after 11:00 AM
                total_absent += 1
                print("added in absent days")
                record.status = "Absent"
                absent_dates.add(record_date)
        else:
            total_absent += 1
            record.status = "Absent"
            absent_dates.add(record_date)

    total_days = total_present + total_late + total_absent
    attendance_percentage = round((attendance_score / total_days) * 100, 1) if total_days > 0 else 0.0

    # For monthly calendar (you can adjust the current month as needed)
    current_date = date.today()
    calendar_weeks = build_calendar(current_date, late_dates, absent_dates, present_dates)

    context = {
        'student': student,
        'attendance_records': attendance_records,
        'total_present': total_present,
        'total_late': total_late,
        'total_absent': total_absent,
        'attendance_percentage': attendance_percentage,
        'calendar_weeks': calendar_weeks,
        'trend_dates': [str(r.date) for r in attendance_records[:7]][::-1],
        'trend_present': [
            1 if r.status == 'Present' else 0 for r in attendance_records[:7]
        ][::-1],
    }

    return render(request, 'student_dashboard.html', context)
MQTT_BROKER = "localhost"
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_RECOGNIZED = "face/recognized"
MQTT_TOPIC_UPDATE = "face/update"

# MQTT client setup
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Callback for when a message is received
def on_message(client, userdata, msg):
    print(f"Message received on topic {msg.topic}: {msg.payload.decode()}")
    if msg.topic == MQTT_TOPIC_UPDATE:
        encode_uploaded_images()  # Refresh encodings when there's an update

client.on_message = on_message
client.subscribe(MQTT_TOPIC_UPDATE)
client.loop_start()

# Initialize MTCNN and InceptionResnetV1
mtcnn = MTCNN(keep_all=True)
resnet = InceptionResnetV1(pretrained='vggface2').eval()

# Function to detect and encode faces
def detect_and_encode(image):
    with torch.no_grad():
        boxes, _ = mtcnn.detect(image)
        if boxes is not None:
            faces = []
            for box in boxes:
                face = image[int(box[1]):int(box[3]), int(box[0]):int(box[2])]
                if face.size == 0:
                    continue
                face = cv2.resize(face, (160, 160))
                face = np.transpose(face, (2, 0, 1)).astype(np.float32) / 255.0
                face_tensor = torch.tensor(face).unsqueeze(0)
                encoding = resnet(face_tensor).detach().numpy().flatten()
                faces.append(encoding)
            return faces
    return []

# Function to encode uploaded images
def encode_uploaded_images():
    known_face_encodings = []
    known_face_names = []

    # Fetch only authorized images
    uploaded_images = Student.objects.filter(authorized=True)

    for student in uploaded_images:
        image_path = os.path.join(settings.MEDIA_ROOT, str(student.image))
        known_image = cv2.imread(image_path)
        known_image_rgb = cv2.cvtColor(known_image, cv2.COLOR_BGR2RGB)
        encodings = detect_and_encode(known_image_rgb)
        if encodings:
            known_face_encodings.extend(encodings)
            known_face_names.append(student.name)

    return known_face_encodings, known_face_names

# Function to recognize faces
def recognize_faces(known_encodings, known_names, test_encodings, threshold=0.6):
    recognized_names = []
    for test_encoding in test_encodings:
        distances = np.linalg.norm(known_encodings - test_encoding, axis=1)
        min_distance_idx = np.argmin(distances)
        if distances[min_distance_idx] < threshold:
            recognized_names.append(known_names[min_distance_idx])
        else:
            recognized_names.append('Not Recognized')
    return recognized_names

# View for capturing student information and image
def capture_student(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        roll_number = request.POST.get('roll_number')
        student_class = request.POST.get('student_class')
        image_data = request.POST.get('image_data')

        # Decode the base64 image data
        if image_data:
            header, encoded = image_data.split(',', 1)
            image_file = ContentFile(base64.b64decode(encoded), name=f"{name}.jpg")

            student = Student(
                name=name,
                email=email,
                roll_number=roll_number,
                student_class=student_class,
                image=image_file,
                authorized=False  # Default to False during registration
            )
            student.save()

            return redirect('selfie_success')  # Redirect to a success page

    return render(request, 'capture_student.html')


# Success view after capturing student information and image
def selfie_success(request):
    return render(request, 'selfie_success.html')
# This views for capturing studen faces and recognize
def capture_and_recognize(request):
    stop_events = []
    camera_threads = []
    camera_windows = []
    error_messages = []

    def process_frame(cam_config, stop_event):
        cap = None
        window_created = False
        try:
            if cam_config.camera_source.isdigit():
                cap = cv2.VideoCapture(int(cam_config.camera_source))
            else:
                cap = cv2.VideoCapture(cam_config.camera_source)

            if not cap.isOpened():
                raise Exception(f"Unable to access camera {cam_config.name}.")

            threshold = cam_config.threshold
            pygame.mixer.init()
            success_sound = pygame.mixer.Sound('app1/suc.wav')

            window_name = f'Face Recognition - {cam_config.name}'
            camera_windows.append(window_name)

            while not stop_event.is_set():
                ret, frame = cap.read()
                if not ret:
                    print(f"Failed to capture frame for camera: {cam_config.name}")
                    break

                # Improve brightness for low-light situations
                frame = cv2.convertScaleAbs(frame, alpha=1.5, beta=30)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Get bounding boxes
                boxes, _ = mtcnn.detect(frame_rgb)

                if boxes is not None:
                    test_face_encodings = detect_and_encode(frame_rgb)
                    known_face_encodings, known_face_names = encode_uploaded_images()

                    if known_face_encodings and test_face_encodings:
                        names = recognize_faces(
                            np.array(known_face_encodings),
                            known_face_names,
                            test_face_encodings,
                            threshold
                        )

                        for name, box in zip(names, boxes):
                            if box is not None:
                                x1, y1, x2, y2 = map(int, box)
                                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                cv2.putText(frame, name, (x1, y1 - 10),
                                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

                                if name != 'Not Recognized':
                                    students = Student.objects.filter(name=name)
                                    if students.exists():
                                        student = students.first()
                                        attendance, created = Attendance.objects.get_or_create(
                                            student=student, date=datetime.now().date())

                                        if created:
                                            attendance.mark_checked_in()
                                            success_sound.play()
                                            client.publish(MQTT_TOPIC_RECOGNIZED, f"{name} checked in")
                                        else:
                                            if attendance.check_in_time and not attendance.check_out_time:
                                                if timezone.now() >= attendance.check_in_time + timedelta(seconds=60):
                                                    attendance.mark_checked_out()
                                                    success_sound.play()
                                                    client.publish(MQTT_TOPIC_RECOGNIZED, f"{name} checked out")

                if not window_created:
                    cv2.namedWindow(window_name)
                    window_created = True

                cv2.imshow(window_name, frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    stop_event.set()
                    break

        except Exception as e:
            print(f"Error in thread for {cam_config.name}: {e}")
            error_messages.append(str(e))
        finally:
            if cap is not None:
                cap.release()
            if window_created:
                cv2.destroyWindow(window_name)

    try:
        cam_configs = CameraConfiguration.objects.all()
        if not cam_configs.exists():
            raise Exception("No camera configurations found.")

        for cam_config in cam_configs:
            stop_event = threading.Event()
            stop_events.append(stop_event)

            camera_thread = threading.Thread(target=process_frame, args=(cam_config, stop_event))
            camera_threads.append(camera_thread)
            camera_thread.start()

        while any(thread.is_alive() for thread in camera_threads):
            time.sleep(1)

    except Exception as e:
        error_messages.append(str(e))
    finally:
        for stop_event in stop_events:
            stop_event.set()
        for window in camera_windows:
            if cv2.getWindowProperty(window, cv2.WND_PROP_VISIBLE) >= 1:
                cv2.destroyWindow(window)

    if error_messages:
        full_error_message = "\n".join(error_messages)
        return render(request, 'error.html', {'error_message': full_error_message})

    return redirect('student_attendance_list')

#this is for showing Attendance list
def student_attendance_list(request):
    # Get the search query and date filter from the request
    search_query = request.GET.get('search', '')
    date_filter = request.GET.get('attendance_date', '')

    # Get all students
    students = Student.objects.all()

    # Filter students based on the search query
    if search_query:
        students = students.filter(name__icontains=search_query)

    # Prepare the attendance data
    student_attendance_data = []

    for student in students:
        # Get the attendance records for each student, filtering by attendance date if provided
        attendance_records = Attendance.objects.filter(student=student)

        if date_filter:
            # Assuming date_filter is in the format YYYY-MM-DD
            attendance_records = attendance_records.filter(date=date_filter)

        attendance_records = attendance_records.order_by('date')
        
        student_attendance_data.append({
            'student': student,
            'attendance_records': attendance_records
        })

    context = {
        'student_attendance_data': student_attendance_data,
        'search_query': search_query,  # Pass the search query to the template
        'date_filter': date_filter       # Pass the date filter to the template
    }
    return render(request, 'student_attendance_list.html', context)


def home(request):
    total_students = Student.objects.count()
    total_attendance = Attendance.objects.count()
    total_check_ins = Attendance.objects.filter(check_in_time__isnull=False).count()
    total_check_outs = Attendance.objects.filter(check_out_time__isnull=False).count()
    total_cameras = CameraConfiguration.objects.count()

    context = {
        'total_students': total_students,
        'total_attendance': total_attendance,
        'total_check_ins': total_check_ins,
        'total_check_outs': total_check_outs,
        'total_cameras': total_cameras,
    }
    return render(request, 'home.html', context)


# Custom user pass test for admin access
def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def student_list(request):
    students = Student.objects.all()
    return render(request, 'student_list.html', {'students': students})

@login_required
@user_passes_test(is_admin)
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'student_detail.html', {'student': student})

@login_required
@user_passes_test(is_admin)
def student_authorize(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        authorized = request.POST.get('authorized', False)
        student.authorized = bool(authorized)
        student.save()
        return redirect('student-detail', pk=pk)
    
    return render(request, 'student_authorize.html', {'student': student})

# This views is for Deleting student
@login_required
@user_passes_test(is_admin)
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted successfully.')
        return redirect('student-list')  # Redirect to the student list after deletion
    
    return render(request, 'student_delete_confirm.html', {'student': student})


# View function for user login
def user_login(request):
    # Check if the request method is POST, indicating a form submission
    if request.method == 'POST':
        # Retrieve username and password from the submitted form data
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user using the provided credentials
        user = authenticate(request, username=username, password=password)

        # Check if the user was successfully authenticated
        if user is not None:
            # Log the user in by creating a session
            login(request, user)
            # Redirect the user to the student list page after successful login
            return redirect('home')  # Replace 'student-list' with your desired redirect URL after login
        else:
            # If authentication fails, display an error message
            messages.error(request, 'Invalid username or password.')

    # Render the login template for GET requests or if authentication fails
    return render(request, 'login.html')


# This is for user logout
def user_logout(request):
    logout(request)
    return redirect('login')  # Replace 'login' with your desired redirect URL after logout

# Function to handle the creation of a new camera configuration
@login_required
@user_passes_test(is_admin)
def camera_config_create(request):
    # Check if the request method is POST, indicating form submission
    if request.method == "POST":
        # Retrieve form data from the request
        name = request.POST.get('name')
        camera_source = request.POST.get('camera_source')
        threshold = request.POST.get('threshold')

        try:
            # Save the data to the database using the CameraConfiguration model
            CameraConfiguration.objects.create(
                name=name,
                camera_source=camera_source,
                threshold=threshold,
            )
            # Redirect to the list of camera configurations after successful creation
            return redirect('camera_config_list')

        except IntegrityError:
            # Handle the case where a configuration with the same name already exists
            messages.error(request, "A configuration with this name already exists.")
            # Render the form again to allow user to correct the error
            return render(request, 'camera_config_form.html')

    # Render the camera configuration form for GET requests
    return render(request, 'camera_config_form.html')


# READ: Function to list all camera configurations
@login_required
@user_passes_test(is_admin)
def camera_config_list(request):
    # Retrieve all CameraConfiguration objects from the database
    configs = CameraConfiguration.objects.all()
    # Render the list template with the retrieved configurations
    return render(request, 'camera_config_list.html', {'configs': configs})


# UPDATE: Function to edit an existing camera configuration
@login_required
@user_passes_test(is_admin)
def camera_config_update(request, pk):
    # Retrieve the specific configuration by primary key or return a 404 error if not found
    config = get_object_or_404(CameraConfiguration, pk=pk)

    # Check if the request method is POST, indicating form submission
    if request.method == "POST":
        # Update the configuration fields with data from the form
        config.name = request.POST.get('name')
        config.camera_source = request.POST.get('camera_source')
        config.threshold = request.POST.get('threshold')
        config.success_sound_path = request.POST.get('success_sound_path')

        # Save the changes to the database
        config.save()  

        # Redirect to the list page after successful update
        return redirect('camera_config_list')  
    
    # Render the configuration form with the current configuration data for GET requests
    return render(request, 'camera_config_form.html', {'config': config})


# DELETE: Function to delete a camera configuration
@login_required
@user_passes_test(is_admin)
def camera_config_delete(request, pk):
    # Retrieve the specific configuration by primary key or return a 404 error if not found
    config = get_object_or_404(CameraConfiguration, pk=pk)

    # Check if the request method is POST, indicating confirmation of deletion
    if request.method == "POST":
        # Delete the record from the database
        config.delete()  
        # Redirect to the list of camera configurations after deletion
        return redirect('camera_config_list')

    # Render the delete confirmation template with the configuration data
    return render(request, 'camera_config_delete.html', {'config': config})
