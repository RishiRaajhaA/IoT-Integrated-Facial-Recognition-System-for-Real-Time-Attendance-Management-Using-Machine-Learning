from django.http import JsonResponse
from django.urls import path
from . import views

# MQTT placeholder views
def mqtt_test(request):
    return JsonResponse({"message": "MQTT test endpoint is working!"})

def mqtt_receive(request):
    return JsonResponse({"message": "MQTT message received successfully!"})

urlpatterns = [
    path('', views.landing_page, name='landing_page'),  # Landing page (home1.html)
    path('login/', views.login_view, name='admin_login'),
    path('logout/', views.user_logout, name='logout'),
    path('home/', views.home, name='home'),

    # Student capture and recognition
    path('capture/', views.capture_student, name='capture_student'),
    path('success/', views.selfie_success, name='selfie_success'),
    path('capture-and-recognize/', views.capture_and_recognize, name='capture_and_recognize'),

    # Student management
    path('students/', views.student_list, name='student-list'),
    path('students/<int:pk>/', views.student_detail, name='student-detail'),
    path('students/<int:pk>/authorize/', views.student_authorize, name='student-authorize'),
    path('students/<int:pk>/delete/', views.student_delete, name='student-delete'),
    path('students/attendance/', views.student_attendance_list, name='student_attendance_list'),

    # Camera configuration
    path('camera-config/', views.camera_config_create, name='camera_config_create'),
    path('camera-config/list/', views.camera_config_list, name='camera_config_list'),
    path('camera-config/update/<int:pk>/', views.camera_config_update, name='camera_config_update'),
    path('camera-config/delete/<int:pk>/', views.camera_config_delete, name='camera_config_delete'),
    path('student/login/', views.student_login, name='student_login'),
    path('student/register/', views.student_register, name='student_register'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/logout/', views.student_logout, name='student_logout'),


    # MQTT endpoints
    path('mqtt/test/', mqtt_test, name='mqtt_test'),
    path('mqtt/receive/', mqtt_receive, name='mqtt_receive'),
]
