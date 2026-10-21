from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Role
from documents.forms import DocumentForm
from documents.models import Document, DocumentType
from documents.views import _authorized_patients
from patients.models import Geocode, Patient, TreatmentRecord


class DocumentAccessTests(TestCase):
    def setUp(self):
        self.role, _ = Role.objects.get_or_create(name="nurse")
        self.unit = Geocode.objects.create(name="Test unit", description="Synthetic")
        self.other_unit = Geocode.objects.create(
            name="Other test unit", description="Synthetic"
        )
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="assigned_nurse",
            email="assigned@example.com",
            password="test-only-password",
            role=self.role,
            primary_geocode=self.unit,
        )
        self.other_user = user_model.objects.create_user(
            username="other_nurse",
            email="other@example.com",
            password="test-only-password",
            role=self.role,
            primary_geocode=self.other_unit,
        )
        self.patient = self._patient("Synthetic patient", self.unit)
        self.other_patient = self._patient("Other synthetic patient", self.other_unit)
        TreatmentRecord.objects.create(patient=self.patient, worker=self.user)
        TreatmentRecord.objects.create(
            patient=self.other_patient, worker=self.other_user
        )
        self.document_type = DocumentType.objects.create(name="Synthetic note")
        self.document = Document.objects.create(
            title="Synthetic document",
            document_type=self.document_type,
            owner=self.other_user,
            patient=self.other_patient,
        )
        self.client.force_login(self.user)

    @staticmethod
    def _patient(name, unit):
        return Patient.objects.create(
            name=name,
            address="Synthetic address",
            date_of_birth=date(1990, 1, 1),
            height=70,
            weight=180,
            blood_group="O+",
            bed_id="TEST",
            treatment_area="Test unit",
            geocode=unit,
        )

    def test_document_detail_update_delete_and_pdf_are_scoped(self):
        routes = (
            ("document_detail", (self.document.pk,)),
            ("document_edit", (self.document.pk,)),
            ("document_delete", (self.document.pk,)),
            ("document_pdf", (self.document.pk,)),
        )
        for route_name, args in routes:
            with self.subTest(route=route_name):
                response = self.client.get(reverse(route_name, args=args))
                self.assertEqual(response.status_code, 404)

    def test_document_form_excludes_patients_outside_assigned_unit_scope(self):
        form = DocumentForm(
            data={
                "title": "Attempted cross-unit note",
                "patient": self.other_patient.pk,
            },
            document_type=self.document_type,
            patient_queryset=_authorized_patients(self.user),
        )
        self.assertFalse(form.is_valid())
        self.assertIn("patient", form.errors)
