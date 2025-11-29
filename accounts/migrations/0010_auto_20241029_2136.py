from django.contrib.auth import get_user_model
from django.db import migrations


def create_superuser(apps, schema_editor):
    User = get_user_model()
    Geocode = apps.get_model('patients', 'Geocode')
    primary_geocode = Geocode.objects.first()

    if not User.objects.filter(email='admin@mail.com').exists():
        User.objects.create_superuser(
            email='admin@mail.com',
            password='admin',
            first_name='Admin',
            last_name='User',
            username='admin',
            profession='',
            role='admin',
            primary_geocode_id=primary_geocode.id if primary_geocode else None
        )


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0009_auto_20241027_1853'),  # Replace with actual app name and previous migration file name
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]
