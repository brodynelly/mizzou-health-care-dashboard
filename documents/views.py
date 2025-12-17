import os

from dal import autocomplete
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DeleteView, DetailView, FormView, ListView, UpdateView
from xhtml2pdf import pisa

from .forms import (  # Import the custom form with Summernote widget
    DocumentFieldForm,
    DocumentForm,
    DocumentTypeForm,
)
from .models import Document, DocumentField, DocumentFieldValue, DocumentType, Drug


def generate_pdf(document):
    # Render the HTML content
    html_content = render_to_string('documents/document_pdf.html', {'document': document})

    # Define a path to save the PDF file
    pdf_directory = os.path.join(settings.MEDIA_ROOT, 'documents/pdfs')
    pdf_path = os.path.join(pdf_directory, f'{document.title}.pdf')

    # Create the directory if it doesn't exist
    if not os.path.exists(pdf_directory):
        os.makedirs(pdf_directory)

    # Create PDF
    with open(pdf_path, 'wb') as pdf_file:
        pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)

    # Check for errors
    if pisa_status.err:
        return None

    return pdf_path

def document_pdf_view(request, pk):
    # Get the document instance
    document = get_object_or_404(Document, pk=pk)

    # Check if the document has an uploaded PDF
    if document.is_uploaded_pdf and document.pdf_file and os.path.exists(document.pdf_file.path):
        # Serve the existing uploaded PDF file
        return FileResponse(open(document.pdf_file.path, 'rb'), content_type='application/pdf')

    # Check if the PDF has already been generated
    if document.pdf_file and not document.is_uploaded_pdf and os.path.exists(document.pdf_file.path):
        # Serve the existing generated PDF file
        return FileResponse(open(document.pdf_file.path, 'rb'), content_type='application/pdf')

    # If the PDF doesn't exist and it needs to be generated, generate it
    if not document.is_uploaded_pdf:
        pdf_path = generate_pdf(document)
        if pdf_path:
            # Correctly save the relative path of the PDF file
            document.pdf_file.name = os.path.relpath(pdf_path, settings.MEDIA_ROOT).replace('\\', '/')
            document.save()

            # Serve the generated PDF file
            return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')

    return HttpResponse('Error generating or retrieving PDF', content_type='text/plain')


@method_decorator(login_required, name='dispatch')
class DrugAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Get all drugs, possibly filtered by user input
        qs = Drug.objects.all()

        # If there's a search term, filter the queryset accordingly
        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs

    model = Document
    form_class = DocumentForm  # Use the custom form with Summernote
    template_name = 'documents/document_form.html'  # Template for document creation
    success_url = reverse_lazy('document_list')  # Redirect after successful creation

    def form_valid(self, form):
        form.instance.owner = self.request.user  # Set the document owner to the logged-in user

        # Ensure content is properly processed
        cleaned_content = form.cleaned_data.get('content', '')
        form.instance.content = cleaned_content

        return super().form_valid(form)

##DOCUMENT VIEWS
#----------------------------

# List View: List all documents owned or shared with the user
@method_decorator(login_required, name='dispatch')
class DocumentListView(ListView):
    model = Document
    template_name = 'documents/document_list.html'  # Template for listing documents
    context_object_name = 'documents'

    def get_paginate_by(self, queryset):
        items_per_page = self.request.GET.get('items_per_page', 20)

        try:
            # Convert the value to an integer, default to 6 if conversion fails
            return int(items_per_page)
        except ValueError:
            # If conversion fails, use the default value of 6
            return 20

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(patient__treated_by=self.request.user)

        # Search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(patient__name__icontains=query) |
                Q(document_type__name__icontains=query) |
                Q(owner__username__icontains=query)
            )

        # Filter by document type
        document_type_id = self.request.GET.get('filter')
        if document_type_id:
            queryset = queryset.filter(document_type_id=document_type_id)

        # Sort functionality
        sort_by = self.request.GET.get('sort')
        if sort_by == 'title':
            queryset = queryset.order_by('title')
        elif sort_by == 'patient':
            queryset = queryset.order_by('patient__name')
        elif sort_by == 'owner':
            queryset = queryset.order_by('owner__username')
        elif sort_by == 'document_type':
            queryset = queryset.order_by('document_type__name')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Include document types for filter options
        context['document_types'] = DocumentType.objects.all()

        # Keep the filter, sort, and items per page values for pagination links
        context['q'] = self.request.GET.get('q', '')
        context['filter'] = self.request.GET.get('filter', '')
        context['sort'] = self.request.GET.get('sort', 'title')
        context['items_per_page'] = self.request.GET.get('items_per_page', 6)

        return context

# Detail View: View a single document
@method_decorator(login_required, name='dispatch')
class DocumentDetailView(DetailView):
    model = Document
    template_name = 'documents/document_detail.html'  # Template for viewing a document
# Update View: Edit an existing document
@method_decorator(login_required, name='dispatch')
class DocumentUpdateView(FormView):
    template_name = 'documents/document_form.html'
    success_url = reverse_lazy('document_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        document = Document.objects.get(pk=self.kwargs['pk'])
        kwargs['document_type'] = document.document_type

        # Set initial values for title, patient, and document fields
        kwargs['initial'] = {'title': document.title, 'patient': document.patient}

        # Populate initial values for the document fields
        for field_value in document.field_values.all():
            if field_value.field.field_type == 'drug':
                try:
                    # Set the initial value to the Drug instance if it's a drug field
                    kwargs['initial'][field_value.field.snake_case_name] = Drug.objects.get(name=field_value.value)
                except Drug.DoesNotExist:
                    kwargs['initial'][field_value.field.snake_case_name] = None
            else:
                kwargs['initial'][field_value.field.snake_case_name] = field_value.value

        # Populate the initial value for the PDF file if it was uploaded
        if document.is_uploaded_pdf and document.pdf_file:
            kwargs['initial']['pdf_file'] = document.pdf_file

        return kwargs

    def get_form(self):
        return DocumentForm(**self.get_form_kwargs())

    def form_valid(self, form):
        document = Document.objects.get(pk=self.kwargs['pk'])
        document.title = form.cleaned_data.get('title', 'Untitled Document')
        document.patient = form.cleaned_data.get('patient')  # Update the patient field

        # Update the PDF file if it has changed
        if 'pdf_file' in form.cleaned_data and form.cleaned_data['pdf_file']:
            document.pdf_file = form.cleaned_data['pdf_file']
            document.is_uploaded_pdf = True
        elif not form.cleaned_data.get('pdf_file'):
            # Handle the case where the PDF file is removed (optional)
            document.pdf_file = None
            document.is_uploaded_pdf = False

        document.save()

        # Update field values
        for field in document.document_type.fields.all():
            value = form.cleaned_data.get(field.snake_case_name, '')

            # Handle the case where the field is of type 'drug'
            if field.field_type == 'drug' and isinstance(value, Drug):
                value = value.name

            DocumentFieldValue.objects.update_or_create(
                document=document, field=field, defaults={'value': value}
            )

        return super().form_valid(form)


# Delete View: Delete an existing document
@method_decorator(login_required, name='dispatch')
class DocumentDeleteView(DeleteView):
    model = Document
    template_name = 'documents/document_confirm_delete.html'  # Template for confirming deletion
    success_url = reverse_lazy('document_list')

@method_decorator(login_required, name='dispatch')
class DocumentCreateView(FormView):
    template_name = 'documents/document_form.html'
    success_url = reverse_lazy('document_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        document_type = DocumentType.objects.get(pk=self.kwargs['document_type_pk'])
        kwargs['document_type'] = document_type
        return kwargs

    def get_form(self):
        return DocumentForm(**self.get_form_kwargs())

    def form_valid(self, form):
        document_type = DocumentType.objects.get(pk=self.kwargs['document_type_pk'])
        owner = self.request.user  # Assuming the user is logged in
        title = form.cleaned_data.get('title', 'Untitled Document')
        patient = form.cleaned_data.get('patient')  # Get the patient from the form
        pdf_file = form.cleaned_data.get('pdf_file')  # Get the uploaded PDF file if provided

        if not patient:
            # If patient is required, raise an error
            form.add_error('patient', 'Patient is required.')
            return self.form_invalid(form)

        if pdf_file:
            # Log to confirm we are in the branch that uploads a PDF
            print("Creating document with uploaded PDF.")

            # Create a new document instance but do not save it to the database yet
            document = Document(
                document_type=document_type,
                owner=owner,
                title=title,
                patient=patient
            )

            # Assign the uploaded PDF file
            document.pdf_file = pdf_file

            # Explicitly set the is_uploaded_pdf flag
            document.is_uploaded_pdf = True

            # Save the document instance to commit changes to the database
            document.save()

            # Log to verify the value after saving
            print(f"Document ID: {document.id}, is_uploaded_pdf: {document.is_uploaded_pdf}")
        else:
            # Log to confirm that no PDF was uploaded
            print("No PDF uploaded, creating document to generate PDF later.")

            # Create a document without an uploaded PDF
            document = Document.objects.create(
                document_type=document_type,
                owner=owner,
                title=title,
                patient=patient
            )

            # Create document field values based on the form data
            for field in document_type.fields.all():
                value = form.cleaned_data.get(field.snake_case_name)
                DocumentFieldValue.objects.create(document=document, field=field, value=value or '')

        # Log to ensure document was saved with the correct values
        print(f"Final Document State -> ID: {document.id}, is_uploaded_pdf: {document.is_uploaded_pdf}")

        return super().form_valid(form)

    # View to select a DocumentType before creating a Document



##DOCUMENT TYPES
#-----------------------------

@method_decorator(login_required, name='dispatch')
class DocumentTypeSelectView(ListView):
    model = DocumentType
    template_name = 'documents/document_type/document_type_select.html'
    context_object_name = 'document_types'

    def post(self, request, *args, **kwargs):
        document_type_id = request.POST.get('document_type')
        if document_type_id:
            return HttpResponseRedirect(reverse_lazy('document_create', kwargs={'document_type_pk': document_type_id}))
        return super().get(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class DocumentTypeCreateView(FormView):
    template_name = 'documents/document_type/document_type_create.html'
    form_class = DocumentTypeForm
    success_url = reverse_lazy('document_type_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_form'] = DocumentFieldForm()
        context['fields'] = self.request.session.get('document_fields', [])
        return context

    def form_valid(self, form):
        document_type = form.save()
        fields = self.request.session.get('document_fields', [])
        for field_data in fields:
            DocumentField.objects.create(
                document_type=document_type,
                name=field_data['name'],
                field_type=field_data['field_type']
            )
        # Clear session after saving fields
        self.request.session['document_fields'] = []
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        if 'add_field' in request.POST:
            field_form = DocumentFieldForm(request.POST)
            if field_form.is_valid():
                # Store the field data in session
                fields = request.session.get('document_fields', [])
                fields.append({
                    'name': field_form.cleaned_data['name'],
                    'field_type': field_form.cleaned_data['field_type']
                })
                request.session['document_fields'] = fields
            return redirect('document_type_create')
        elif 'remove_field' in request.POST:
            field_index = int(request.POST.get('remove_field'))
            fields = request.session.get('document_fields', [])
            if 0 <= field_index < len(fields):
                del fields[field_index]
                request.session['document_fields'] = fields
            return redirect('document_type_create')
        return super().post(request, *args, **kwargs)


#List View
@method_decorator(login_required, name='dispatch')
class DocumentTypeListView(ListView):
    model = DocumentType
    template_name = 'documents/document_type/document_type_list.html'
    context_object_name = 'document_types'

# Delete View
@method_decorator(login_required, name='dispatch')
class DocumentTypeDeleteView(DeleteView):
    model = DocumentType
    template_name = 'documents/document_type/document_type_confirm_delete.html'
    success_url = reverse_lazy('document_type_list')

# Update View
@method_decorator(login_required, name='dispatch')
class DocumentTypeUpdateView(UpdateView):
    model = DocumentType
    form_class = DocumentTypeForm
    template_name = 'documents/document_type/document_type_create.html'
    success_url = reverse_lazy('document_type_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_form'] = DocumentFieldForm()
        context['fields'] = self.object.fields.all()
        return context

    def post(self, request, *args, **kwargs):
        if 'add_field' in request.POST:
            field_form = DocumentFieldForm(request.POST)
            if field_form.is_valid():
                DocumentField.objects.create(
                    document_type=self.get_object(),
                    name=field_form.cleaned_data['name'],
                    field_type=field_form.cleaned_data['field_type']
                )
            return redirect('document_type_update', pk=self.get_object().pk)
        elif 'remove_field' in request.POST:
            field_id = int(request.POST.get('remove_field'))
            DocumentField.objects.filter(id=field_id, document_type=self.get_object()).delete()
            return redirect('document_type_update', pk=self.get_object().pk)
        return super().post(request, *args, **kwargs)
