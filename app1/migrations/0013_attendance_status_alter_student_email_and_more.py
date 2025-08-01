# Generated by Django 5.0.7 on 2025-04-10 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0012_remove_student_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='status',
            field=models.CharField(choices=[('Present', 'Present'), ('Late', 'Late'), ('Absent', 'Absent')], default='Absent', max_length=10),
        ),
        migrations.AlterField(
            model_name='student',
            name='email',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name='student',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='student_images/'),
        ),
        migrations.AlterField(
            model_name='student',
            name='password',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='student',
            name='username',
            field=models.CharField(default='temp_username', max_length=50, unique=True),
            preserve_default=False,
        ),
    ]
