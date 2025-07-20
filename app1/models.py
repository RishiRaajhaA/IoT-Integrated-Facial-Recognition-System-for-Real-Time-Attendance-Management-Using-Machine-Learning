from django.db import models
from django.utils import timezone
from datetime import time as dt_time
import random


class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    roll_number = models.CharField(max_length=20, unique=True)
    student_class = models.CharField(max_length=10)

    # Updated: ensured non-null default username
    username = models.CharField(max_length=50, unique=True, null=False, default='temp_username')

    password = models.CharField(max_length=100)
    image = models.ImageField(upload_to='student_images/', blank=True, null=True)
    authorized = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.username == 'temp_username' or not self.username:
            while True:
                rand = str(random.randint(10000, 99999))
                if not Student.objects.filter(username=rand).exists():
                    self.username = rand
                    break
        if not self.password:
            self.password = "123"
        super().save(*args, **kwargs)


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Late', 'Late'),
        ('Absent', 'Absent'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)

    # ✅ Added status field to track attendance explicitly
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Absent')

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"

    def mark_checked_in(self):
        self.check_in_time = timezone.now()
        self._update_status()
        self.save()

    def mark_checked_out(self):
        if self.check_in_time:
            self.check_out_time = timezone.now()
            self.save()
        else:
            raise ValueError("Cannot mark check-out without check-in.")

    def calculate_duration(self):
        if self.check_in_time and self.check_out_time:
            duration = self.check_out_time - self.check_in_time
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        return None

    def _update_status(self):
        """Auto-update status based on check-in time."""
        if self.check_in_time:
            check_in = self.check_in_time.time()
            if check_in < dt_time(10, 50):
                self.status = 'Present'
            elif dt_time(10, 50) <= check_in < dt_time(11, 0):
                self.status = 'Late'
            else:
                self.status = 'Absent'
        else:
            self.status = 'Absent'

    def get_attendance_weight(self):
        """Return the weight for attendance percentage based on status."""
        return {
            'Present': 1.0,
            'Late': 0.75,
            'Absent': 0.0,
        }.get(self.status, 0.0)

    def save(self, *args, **kwargs):
        # Only set date if new object
        if not self.pk:
            self.date = timezone.now().date()

        # Always update status based on check-in
        self._update_status()
        super().save(*args, **kwargs)


class CameraConfiguration(models.Model):
    name = models.CharField(
        max_length=100, unique=True,
        help_text="Give a name to this camera configuration"
    )
    camera_source = models.CharField(
        max_length=255,
        help_text="Camera index (0 for default webcam or RTSP/HTTP URL for IP camera)"
    )
    threshold = models.FloatField(
        default=0.6,
        help_text="Face recognition confidence threshold"
    )

    def __str__(self):
        return self.name
