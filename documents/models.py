import re

# Create your models here.
import uuid

from django.db import models


class Drug(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class DocumentType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class DocumentField(models.Model):
    FIELD_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('rich_text', 'Rich Text'),
        ('drug', 'Drug'),  # New field type for drug autocomplete

    ]
    @property
    def snake_case_name(self):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', self.name.replace(' ', '_')).lower()

    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=50, choices=FIELD_TYPES)

    def __str__(self):
        return f"{self.name} ({self.field_type})"

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE, default="1")
    owner = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='documents', null= True, blank= True)  # Add patient field
    creation_date = models.DateTimeField(auto_now_add=True)  # Add creation date
    pdf_file = models.FileField(upload_to='documents/pdfs/', null=True, blank=True)  # New field for PDF storage
    is_uploaded_pdf = models.BooleanField(default=False)  # Flag to indicate if this is an uploaded PDF without fields



    def __str__(self):
        return self.title

class DocumentFieldValue(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='field_values')
    field = models.ForeignKey(DocumentField, on_delete=models.CASCADE)
    value = models.TextField()

    def __str__(self):
        return f"{self.field.name}: {self.value}"
