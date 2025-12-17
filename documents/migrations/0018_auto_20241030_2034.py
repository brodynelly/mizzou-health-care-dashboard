import random
from datetime import datetime, timedelta

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0017_auto_20241028_1852'),
        ("patients", "0019_sample_data_creation"),
    ]

    def generate_sample_data(apps, schema_editor):
        Drug = apps.get_model('documents', 'Drug')
        DocumentType = apps.get_model('documents', 'DocumentType')
        DocumentField = apps.get_model('documents', 'DocumentField')
        Document = apps.get_model('documents', 'Document')
        DocumentFieldValue = apps.get_model('documents', 'DocumentFieldValue')
        CustomUser = apps.get_model('accounts', 'CustomUser')
        Patient = apps.get_model('patients', 'Patient')

        # Remove previous document types if id is not 1001
        DocumentType.objects.exclude(id=1001).delete()

        # Remove all previous drugs
        Drug.objects.all().delete()

        # Sample data for Drug
        drug_names = [
            'Aspirin', 'Ibuprofen', 'Paracetamol', 'Amoxicillin', 'Ciprofloxacin',
            'Metformin', 'Omeprazole', 'Atorvastatin', 'Simvastatin', 'Lisinopril',
            'Hydrochlorothiazide', 'Amlodipine', 'Metoprolol', 'Losartan', 'Furosemide',
            'Prednisone', 'Gabapentin', 'Cetirizine', 'Clindamycin', 'Azithromycin',
            'Levothyroxine', 'Albuterol', 'Fluoxetine', 'Sertraline', 'Citalopram',
            'Tamsulosin', 'Doxycycline', 'Ranitidine', 'Pantoprazole', 'Montelukast'
        ]
        drugs = [Drug.objects.create(name=name) for name in drug_names]

        # Sample data for DocumentType
        doc_type1 = DocumentType.objects.create(name='Medical Report')
        doc_type2 = DocumentType.objects.create(name='Prescription')
        doc_type3 = DocumentType.objects.create(name='Discharge Summary')
        doc_type4 = DocumentType.objects.create(name='Progress Note')

        # Sample data for DocumentField
        field1 = DocumentField.objects.create(document_type=doc_type1, name='Patient Name', field_type='text')
        field2 = DocumentField.objects.create(document_type=doc_type1, name='Date of Visit', field_type='date')
        field3 = DocumentField.objects.create(document_type=doc_type1, name='Diagnosis', field_type='text')
        field4 = DocumentField.objects.create(document_type=doc_type1, name='Treatment Plan', field_type='rich_text')
        field5 = DocumentField.objects.create(document_type=doc_type2, name='Prescribed Drug', field_type='drug')
        field6 = DocumentField.objects.create(document_type=doc_type2, name='Dosage', field_type='text')
        field7 = DocumentField.objects.create(document_type=doc_type3, name='Discharge Instructions', field_type='rich_text')
        field8 = DocumentField.objects.create(document_type=doc_type3, name='Follow-up Date', field_type='date')
        field9 = DocumentField.objects.create(document_type=doc_type4, name='Progress Notes', field_type='rich_text')
        field10 = DocumentField.objects.create(document_type=doc_type4, name='Next Appointment', field_type='date')

        # Sample data for Document
        users = list(CustomUser.objects.filter(role__name__in=['nurse', 'doctor']))
        nurses = [user for user in users if user.role.name == 'nurse']
        doctors = [user for user in users if user.role.name == 'doctor']
        patients = Patient.objects.all()  # Assuming there are 50 patients

        diagnoses = ['Flu', 'Cold', 'Stomach Ache', 'Migraine', 'Back Pain']
        treatment_plans = ['Rest and hydration', 'Take prescribed medication', 'Physical therapy', 'Increase fluid intake', 'Bed rest']
        discharge_instructions = ['Take rest for a week and avoid strenuous activities', 'Follow up with your primary care doctor', 'Continue prescribed medication for 5 days', 'Drink plenty of water', 'Avoid heavy lifting']
        progress_notes = ['Patient is recovering well, continue current treatment plan', 'Patient shows signs of improvement', 'No significant changes, follow the prescribed medication', 'Patient is experiencing mild side effects', 'Patient needs additional testing']

        for patient in patients:
            owner = random.choice(nurses + doctors)
            document1 = Document.objects.create(title=f'{patient.name} Medical Report', document_type=doc_type1, owner=owner, patient=patient)
            document2 = Document.objects.create(title=f'{patient.name} Prescription', document_type=doc_type2, owner=owner, patient=patient)
            document3 = Document.objects.create(title=f'{patient.name} Discharge Summary', document_type=doc_type3, owner=owner, patient=patient)
            document4 = Document.objects.create(title=f'{patient.name} Progress Note', document_type=doc_type4, owner=owner, patient=patient)

            # Sample data for DocumentFieldValue with randomness
            DocumentFieldValue.objects.create(document=document1, field=field1, value=patient.name)
            DocumentFieldValue.objects.create(document=document1, field=field2, value=(datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d'))
            DocumentFieldValue.objects.create(document=document1, field=field3, value=random.choice(diagnoses))
            DocumentFieldValue.objects.create(document=document1, field=field4, value=random.choice(treatment_plans))
            DocumentFieldValue.objects.create(document=document2, field=field5, value=random.choice(drugs).name)
            DocumentFieldValue.objects.create(document=document2, field=field6, value=f'{random.randint(100, 1000)}mg {random.choice(["once", "twice", "three times"])} daily')
            DocumentFieldValue.objects.create(document=document3, field=field7, value=random.choice(discharge_instructions))
            DocumentFieldValue.objects.create(document=document3, field=field8, value=(datetime.now() + timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'))
            DocumentFieldValue.objects.create(document=document4, field=field9, value=random.choice(progress_notes))
            DocumentFieldValue.objects.create(document=document4, field=field10, value=(datetime.now() + timedelta(days=random.randint(7, 60))).strftime('%Y-%m-%d'))

    operations = [
        migrations.RunPython(generate_sample_data),
    ]
