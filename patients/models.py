import uuid

from django.db import models, transaction


class Patient(models.Model):
    UNASSIGNED = "unassigned"
    NURSE_ASSIGNED = "nurse_assigned"
    DOCTOR_ASSIGNED = "doctor_assigned"
    STATE_CHOICES = [
        (UNASSIGNED, "Unassigned"),
        (NURSE_ASSIGNED, "Nurse Assigned"),
        (DOCTOR_ASSIGNED, "Doctor Assigned"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    address = models.TextField()
    date_of_birth = models.DateField()  # Date of birth of the patient
    height = models.DecimalField(max_digits=5, decimal_places=2)  # Height in inches
    weight = models.DecimalField(max_digits=6, decimal_places=2)  # Weight in pounds
    blood_group = models.CharField(max_length=3)  # Example: "A+", "AB-"
    bed_id = models.CharField(max_length=50)  # Bed ID assigned to the patient
    treatment_area = models.CharField(max_length=100)  # Treatment unit or department
    geocode = models.ForeignKey(
        "Geocode",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patients",
    )

    treated_by = models.ManyToManyField(
        "accounts.CustomUser", through="TreatmentRecord", related_name="patients"
    )
    state = models.CharField(max_length=15, choices=STATE_CHOICES, default=UNASSIGNED)
    nurse_count = models.PositiveIntegerField(default=0)
    doctor_assigned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"

    def assign_nurse(self, nurse_user):
        if getattr(nurse_user.role, "name", None) != "nurse":
            raise ValueError("User must have role 'nurse' to be assigned as a nurse.")

        with transaction.atomic():
            patient = Patient.objects.select_for_update().get(pk=self.pk)
            self._assign_nurse_locked(patient, nurse_user)

    def _assign_nurse_locked(self, patient, nurse_user):
        if patient.nurse_count >= 3:
            raise ValueError("A patient can have no more than 3 nurses assigned.")

        if TreatmentRecord.objects.filter(patient=patient, worker=nurse_user).exists():
            raise ValueError(
                f"{nurse_user.name} is already assigned as a nurse to this patient."
            )

        TreatmentRecord.objects.create(patient=patient, worker=nurse_user)
        patient.nurse_count += 1
        patient.state = (
            self.DOCTOR_ASSIGNED if patient.doctor_assigned else self.NURSE_ASSIGNED
        )
        patient.save(update_fields=["nurse_count", "state"])
        self.nurse_count, self.state = patient.nurse_count, patient.state

    def assign_doctor(self, doctor_user):
        if getattr(doctor_user.role, "name", None) != "doctor":
            raise ValueError("User must have role 'doctor' to be assigned as a doctor.")

        with transaction.atomic():
            patient = Patient.objects.select_for_update().get(pk=self.pk)
            if TreatmentRecord.objects.filter(
                patient=patient, worker=doctor_user
            ).exists():
                raise ValueError(
                    f"{doctor_user.name} is already assigned as a doctor to this patient."
                )
            if patient.doctor_assigned:
                raise ValueError("A patient can have only one doctor assigned.")
            if patient.nurse_count == 0:
                raise ValueError(
                    "A doctor cannot be assigned unless at least one nurse is assigned."
                )
            TreatmentRecord.objects.create(patient=patient, worker=doctor_user)
            patient.doctor_assigned = True
            patient.state = self.DOCTOR_ASSIGNED
            patient.save(update_fields=["doctor_assigned", "state"])
            self.doctor_assigned, self.state = True, patient.state

    def unassign_nurse(self, nurse_user):
        if getattr(nurse_user.role, "name", None) != "nurse":
            raise ValueError("User must have role 'nurse' to be unassigned as a nurse.")

        with transaction.atomic():
            patient = Patient.objects.select_for_update().get(pk=self.pk)
            try:
                TreatmentRecord.objects.get(patient=patient, worker=nurse_user).delete()
            except TreatmentRecord.DoesNotExist:
                raise ValueError("This nurse is not assigned to the patient.")
            patient.nurse_count -= 1
            if patient.nurse_count == 0:
                patient.state = (
                    self.UNASSIGNED
                    if not patient.doctor_assigned
                    else self.DOCTOR_ASSIGNED
                )
            patient.save(update_fields=["nurse_count", "state"])
            self.nurse_count, self.state = patient.nurse_count, patient.state

    def unassign_doctor(self, doctor_user):
        if getattr(doctor_user.role, "name", None) != "doctor":
            raise ValueError(
                "User must have role 'doctor' to be unassigned as a doctor."
            )

        with transaction.atomic():
            patient = Patient.objects.select_for_update().get(pk=self.pk)
            try:
                TreatmentRecord.objects.get(
                    patient=patient, worker=doctor_user
                ).delete()
            except TreatmentRecord.DoesNotExist:
                raise ValueError("This doctor is not assigned to the patient.")
            patient.doctor_assigned = False
            patient.state = (
                self.NURSE_ASSIGNED if patient.nurse_count > 0 else self.UNASSIGNED
            )
            patient.save(update_fields=["doctor_assigned", "state"])
            self.doctor_assigned, self.state = False, patient.state


class TreatmentRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    worker = models.ForeignKey(
        "accounts.CustomUser", on_delete=models.CASCADE, blank=True, null=True
    )  # Renamed to 'worker'

    class Meta:
        unique_together = (
            "patient",
            "worker",
        )  # Ensure each worker is only assigned once per patient


class Geocode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return f"{self.name}"
