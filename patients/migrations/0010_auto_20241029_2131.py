from datetime import date

from django.db import migrations


def clear_all_tables(apps, schema_editor):
    Patient = apps.get_model('patients', 'Patient')
    Geocode = apps.get_model('patients', 'Geocode')
    TreatmentRecord = apps.get_model('patients', 'TreatmentRecord')
    UserPatientAssignment = apps.get_model('patients', 'UserPatientAssignment')

    # Deleting all entries in each table
    UserPatientAssignment.objects.all().delete()
    TreatmentRecord.objects.all().delete()
    Patient.objects.all().delete()
    Geocode.objects.all().delete()

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
    Geocode = apps.get_model('patients', 'Geocode')

    # Retrieve geocodes
    geocodes = list(Geocode.objects.all())

    # Creating 10 example patients and assigning them to geocodes
    patients_data = [
        {'name': 'Josh Allen', 'address': '123 Elm St', 'date_of_birth': date(1980, 1, 1), 'height': 76.0, 'weight': 237.0, 'blood_group': 'O+', 'bed_id': 'B101', 'treatment_area': 'General Ward', 'geocode': geocodes[0]},
        {'name': 'James Cook', 'address': '456 Oak St', 'date_of_birth': date(1999, 9, 25), 'height': 70.0, 'weight': 190.0, 'blood_group': 'AB-', 'bed_id': 'B102', 'treatment_area': 'ICU', 'geocode': geocodes[1]},
        {'name': 'Keon Coleman', 'address': '789 Pine St', 'date_of_birth': date(2001, 3, 1), 'height': 74.0, 'weight': 210.0, 'blood_group': 'B+', 'bed_id': 'B103', 'treatment_area': 'Orthopedics', 'geocode': geocodes[2]},
        {'name': 'Dalton Kincaid', 'address': '321 Maple St', 'date_of_birth': date(1996, 10, 18), 'height': 76.0, 'weight': 246.0, 'blood_group': 'AB+', 'bed_id': 'B104', 'treatment_area': 'Pediatrics', 'geocode': geocodes[3]},
        {'name': 'Dawson Knox', 'address': '654 Cedar St', 'date_of_birth': date(1996, 11, 14), 'height': 76.0, 'weight': 254.0, 'blood_group': 'B-', 'bed_id': 'B105', 'treatment_area': 'General Ward', 'geocode': geocodes[4]},
        {'name': 'Dion Dawkins', 'address': '789 Birch St', 'date_of_birth': date(1994, 4, 26), 'height': 76.0, 'weight': 320.0, 'blood_group': 'A+', 'bed_id': 'B106', 'treatment_area': 'Cardiology', 'geocode': geocodes[0]},
        {'name': 'Damar Hamlin', 'address': '159 Spruce St', 'date_of_birth': date(1998, 3, 24), 'height': 72.0, 'weight': 200.0, 'blood_group': 'O-', 'bed_id': 'B107', 'treatment_area': 'Neurology', 'geocode': geocodes[1]},
        {'name': 'Taylor Rapp', 'address': '753 Aspen St', 'date_of_birth': date(1997, 12, 22), 'height': 72.0, 'weight': 208.0, 'blood_group': 'B-', 'bed_id': 'B108', 'treatment_area': 'General Ward', 'geocode': geocodes[2]},
        {'name': 'Ed Oliver', 'address': '951 Willow St', 'date_of_birth': date(1997, 12, 12), 'height': 73.0, 'weight': 287.0, 'blood_group': 'AB-', 'bed_id': 'B109', 'treatment_area': 'Pediatrics', 'geocode': geocodes[3]},
        {'name': 'Von Miller', 'address': '357 Oakwood St', 'date_of_birth': date(1989, 3, 26), 'height': 75.0, 'weight': 250.0, 'blood_group': 'A+', 'bed_id': 'B110', 'treatment_area': 'Orthopedics', 'geocode': geocodes[4]},
    ]

    for patient_data in patients_data:
        Patient.objects.create(**patient_data)

class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0009_auto_20241029_2127'),
    ]

    operations = [
        migrations.RunPython(clear_all_tables),
        migrations.RunPython(create_geocodes),
        migrations.RunPython(create_patients),
    ]
