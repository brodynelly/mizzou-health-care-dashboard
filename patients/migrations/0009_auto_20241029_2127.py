from datetime import date

from django.db import migrations


def clear_all_tables(apps, schema_editor):
    Patient = apps.get_model('patients', 'Patient')
    Geocode = apps.get_model('patients', 'Geocode')
    TreatmentRecord = apps.get_model('patients', 'TreatmentRecord')
    UserPatientAssignment = apps.get_model('patients', 'UserPatientAssignment')
    CustomUser = apps.get_model('accounts', 'CustomUser')

    # Deleting all entries in each table
    UserPatientAssignment.objects.all().delete()
    TreatmentRecord.objects.all().delete()
    Patient.objects.all().delete()
    Geocode.objects.all().delete()
    CustomUser.objects.all().delete()

def create_geocodes(apps, schema_editor):
    Geocode = apps.get_model('patients', 'Geocode')

    # Creating example geocodes
    geocodes_data = [
        {'name': 'North Region', 'description': 'Northern treatment area'},
        {'name': 'South Region', 'description': 'Southern treatment area'},
        {'name': 'East Region', 'description': 'Eastern treatment area'},
        {'name': 'West Region', 'description': 'Western treatment area'},
        {'name': 'Central Region', 'description': 'Central treatment area'},
    ]

    for geocode_data in geocodes_data:
        Geocode.objects.create(**geocode_data)

def create_patients(apps, schema_editor):
    Patient = apps.get_model('patients', 'Patient')

    # Creating 5 example patients
    patients_data = [
        {'name': 'John Doe', 'address': '123 Elm St', 'date_of_birth': date(1980, 1, 1), 'height': 70.0, 'weight': 180.0, 'blood_group': 'O+', 'bed_id': 'B101', 'treatment_area': 'General Ward'},
        {'name': 'Jane Smith', 'address': '456 Oak St', 'date_of_birth': date(1990, 2, 14), 'height': 65.0, 'weight': 150.0, 'blood_group': 'A-', 'bed_id': 'B102', 'treatment_area': 'ICU'},
        {'name': 'Mike Johnson', 'address': '789 Pine St', 'date_of_birth': date(1975, 3, 10), 'height': 72.0, 'weight': 200.0, 'blood_group': 'B+', 'bed_id': 'B103', 'treatment_area': 'Orthopedics'},
        {'name': 'Emily Brown', 'address': '321 Maple St', 'date_of_birth': date(2000, 5, 25), 'height': 62.0, 'weight': 130.0, 'blood_group': 'AB+', 'bed_id': 'B104', 'treatment_area': 'Pediatrics'},
        {'name': 'Sarah White', 'address': '654 Cedar St', 'date_of_birth': date(1985, 7, 7), 'height': 68.0, 'weight': 160.0, 'blood_group': 'B-', 'bed_id': 'B105', 'treatment_area': 'General Ward'},
    ]

    for patient_data in patients_data:
        Patient.objects.create(**patient_data)

class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0008_treatmentrecord_patient_treated_by'),
    ]

    operations = [
        migrations.RunPython(clear_all_tables),
        migrations.RunPython(create_geocodes),
        migrations.RunPython(create_patients),
    ]
