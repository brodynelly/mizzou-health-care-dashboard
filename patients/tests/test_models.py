from django.test import TestCase
from django.contrib.auth import get_user_model
from patients.models import Patient, TreatmentRecord
from accounts.models import Role
from datetime import date

CustomUser = get_user_model()

class PatientModelTests(TestCase):
    def setUp(self):
        # Create Roles
        self.nurse_role, _ = Role.objects.get_or_create(name='nurse')
        self.doctor_role, _ = Role.objects.get_or_create(name='doctor')

        # Create Users
        self.nurse = CustomUser.objects.create_user(
            username='nurse_joy',
            email='nurse@example.com',
            password='password123',
            first_name='Nurse',
            last_name='Joy',
            role=self.nurse_role
        )
        self.doctor = CustomUser.objects.create_user(
            username='doctor_who',
            email='doctor@example.com',
            password='password123',
            first_name='Doctor',
            last_name='Who',
            role=self.doctor_role
        )

        self.patient = Patient.objects.create(
            name="John Doe",
            address="123 Main St",
            date_of_birth=date(1990, 1, 1),
            height=70.0,
            weight=180.0,
            blood_group="O+",
            bed_id="B1",
            treatment_area="ICU"
        )

    def test_assign_nurse(self):
        self.patient.assign_nurse(self.nurse)
        self.assertEqual(self.patient.nurse_count, 1)
        self.assertTrue(TreatmentRecord.objects.filter(patient=self.patient, worker=self.nurse).exists())
        self.assertEqual(self.patient.state, Patient.NURSE_ASSIGNED)

    def test_assign_doctor_fails_without_nurse(self):
        with self.assertRaises(ValueError) as cm:
            self.patient.assign_doctor(self.doctor)
        self.assertIn("A doctor cannot be assigned unless at least one nurse is assigned", str(cm.exception))

    def test_assign_doctor_success(self):
        self.patient.assign_nurse(self.nurse)
        self.patient.assign_doctor(self.doctor)
        self.assertTrue(self.patient.doctor_assigned)
        self.assertEqual(self.patient.state, Patient.DOCTOR_ASSIGNED)

    def test_unassign_nurse(self):
        self.patient.assign_nurse(self.nurse)
        self.patient.unassign_nurse(self.nurse)
        self.assertEqual(self.patient.nurse_count, 0)
        self.assertEqual(self.patient.state, Patient.UNASSIGNED)

    def test_role_validation(self):
        # Try to assign doctor as nurse
        with self.assertRaises(ValueError):
            self.patient.assign_nurse(self.doctor)
