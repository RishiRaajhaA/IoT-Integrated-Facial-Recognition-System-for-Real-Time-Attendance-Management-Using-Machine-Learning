from django.db import migrations, models
import random

def assign_roll_numbers_and_usernames(apps, schema_editor):
    Student = apps.get_model('app1', 'Student')
    for idx, student in enumerate(Student.objects.all(), start=1001):
        student.roll_number = f"ROLL{idx}"
        student.username = f"user{random.randint(10000, 99999)}"
        student.password = "123"
        student.save()

class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0010_remove_cameraconfiguration_success_sound_path'),
    ]

    operations = [
        # Add fields without unique constraints first
        migrations.AddField(
            model_name='student',
            name='password',
            field=models.CharField(default='123', max_length=100),
        ),
        migrations.AddField(
            model_name='student',
            name='roll_number',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='username',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),

        # Populate data safely
        migrations.RunPython(assign_roll_numbers_and_usernames),

        # Now apply uniqueness after values have been assigned
        migrations.AlterField(
            model_name='student',
            name='roll_number',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='username',
            field=models.CharField(blank=True, max_length=10, null=True, unique=True),
        ),

        migrations.AlterField(
            model_name='student',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='student',
            name='student_class',
            field=models.CharField(max_length=10),
        ),
    ]
