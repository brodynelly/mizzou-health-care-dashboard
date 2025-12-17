from dal import autocomplete
from django import forms
from django_summernote.widgets import SummernoteWidget

from .models import Document, DocumentField, DocumentType, Drug


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'patient', 'pdf_file']

    def __init__(self, *args, **kwargs):
        document_type = kwargs.pop('document_type')
        super(DocumentForm, self).__init__(*args, **kwargs)

        if document_type.id != 1001:
            self.fields.pop('pdf_file', None)

        # Add fields based on DocumentType fields
        for field in document_type.fields.all():
            if field.field_type == 'text':
                self.fields[field.snake_case_name] = forms.CharField(label=field.name, required=False)
            elif field.field_type == 'number':
                self.fields[field.snake_case_name] = forms.IntegerField(label=field.name, required=False)
            elif field.field_type == 'date':
                self.fields[field.snake_case_name] = forms.DateField(label=field.name, required=False, widget=forms.DateInput(attrs={'type': 'date'}))
            elif field.field_type == 'rich_text':
                self.fields[field.snake_case_name] = forms.CharField(label=field.name, widget=SummernoteWidget(), required=False)
            elif field.field_type == 'drug':
                # Instantiate DrugModelForm and add the field
                self.fields[field.snake_case_name] = forms.ModelChoiceField(
                    label=field.name,
                    queryset=Drug.objects.all(),
                    widget=autocomplete.ModelSelect2(
                        url='drug_autocomplete',
                    ),
                    required=False
                )

class DocumentTypeForm(forms.ModelForm):
    class Meta:
        model = DocumentType
        fields = ['name']

# Form to add fields to DocumentType
class DocumentFieldForm(forms.ModelForm):
    class Meta:
        model = DocumentField
        fields = ['name', 'field_type']
