import uuid

from django.db import models


class Patient(models.Model):
    UNASSIGNED = 'unassigned'
    NURSE_ASSIGNED = 'nurse_assigned'
    DOCTOR_ASSIGNED = 'doctor_assigned'
    STATE_CHOICES = [
        (UNASSIGNED, 'Unassigned'),
        (NURSE_ASSIGNED, 'Nurse Assigned'),
        (DOCTOR_ASSIGNED, 'Doctor Assigned'),
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
    geocode = models.ForeignKey('Geocode', on_delete=models.SET_NULL, null=True, blank=True, related_name='patients')


    treated_by = models.ManyToManyField("accounts.CustomUser", through='TreatmentRecord', related_name='patients')
    state = models.CharField(max_length=15, choices=STATE_CHOICES, default=UNASSIGNED)
    nurse_count = models.PositiveIntegerField(default=0)
    doctor_assigned = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.name}"

    def assign_nurse(self, nurse_user):
        if nurse_user.role.name != 'nurse':
            raise ValueError("User must have role 'nurse' to be assigned as a nurse.")

        if self.nurse_count >= 3:
            raise ValueError("A patient can have no more than 3 nurses assigned.")

        if TreatmentRecord.objects.filter(patient=self, worker=nurse_user).exists():
            raise ValueError(f"{nurse_user.name} is already assigned as a nurse to this patient.")

        # Create the TreatmentRecord for the nurse
        TreatmentRecord.objects.create(patient=self, worker=nurse_user)
        self.nurse_count += 1
        self.state = self.DOCTOR_ASSIGNED if self.doctor_assigned else self.NURSE_ASSIGNED
        self.save()

    def assign_doctor(self, doctor_user):
        if doctor_user.role.name != 'doctor':
            raise ValueError("User must have role 'doctor' to be assigned as a doctor.")

        if TreatmentRecord.objects.filter(patient=self, worker=doctor_user).exists():
            raise ValueError(f"{doctor_user.name} is already assigned as a doctor to this patient.")

        if self.doctor_assigned:
            raise ValueError("A patient can have only one doctor assigned.")

        if self.nurse_count == 0:
            raise ValueError("A doctor cannot be assigned unless at least one nurse is assigned.")

        # Create the TreatmentRecord for the doctor
        TreatmentRecord.objects.create(patient=self, worker=doctor_user)
        self.doctor_assigned = True
        self.state = self.DOCTOR_ASSIGNED
        self.save()

    def unassign_nurse(self, nurse_user):
        if nurse_user.role.name != 'nurse':
            raise ValueError("User must have role 'nurse' to be unassigned as a nurse.")

        try:
            record = TreatmentRecord.objects.get(patient=self, worker=nurse_user)
            record.delete()
            self.nurse_count -= 1
            if self.nurse_count == 0:
                self.state = self.UNASSIGNED if not self.doctor_assigned else self.DOCTOR_ASSIGNED
            self.save()
        except TreatmentRecord.DoesNotExist:
            raise ValueError("This nurse is not assigned to the patient.")

    def unassign_doctor(self, doctor_user):
        if doctor_user.role.name != 'doctor':
            raise ValueError("User must have role 'doctor' to be unassigned as a doctor.")

        try:
            record = TreatmentRecord.objects.get(patient=self, worker=doctor_user)
            record.delete()
            self.doctor_assigned = False
            self.state = self.NURSE_ASSIGNED if self.nurse_count > 0 else self.UNASSIGNED
            self.save()
        except TreatmentRecord.DoesNotExist:
            raise ValueError("This doctor is not assigned to the patient.")




class TreatmentRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    worker = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE, blank=True, null=True)  # Renamed to 'worker'

    class Meta:
        unique_together = ('patient', 'worker')  # Ensure each worker is only assigned once per patient

class Geocode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return f"{self.name}"
