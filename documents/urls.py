from django.urls import path

from .views import (
    DocumentCreateView,
    DocumentDeleteView,
    DocumentDetailView,
    DocumentListView,
    DocumentTypeCreateView,
    DocumentTypeDeleteView,
    DocumentTypeListView,
    DocumentTypeSelectView,
    DocumentTypeUpdateView,
    DocumentUpdateView,
    DrugAutocompleteView,
    document_pdf_view,
)

urlpatterns = [
    path('documents/', DocumentListView.as_view(), name='document_list'),  # List all documents
    path('documents/type/select/', DocumentTypeSelectView.as_view(), name='document_type_select'),
    path('documents/type/<int:document_type_pk>/create/', DocumentCreateView.as_view(), name='document_create'),
    path('documents/<uuid:pk>/', DocumentDetailView.as_view(), name='document_detail'),  # View a specific document
    path('documents/<uuid:pk>/edit/', DocumentUpdateView.as_view(), name='document_edit'),  # Edit a specific document
    path('documents/<uuid:pk>/delete/', DocumentDeleteView.as_view(), name='document_delete'),  # Delete a specific document
    path('documents/<uuid:pk>/pdf/', document_pdf_view, name='document_pdf'),
    path('document_type/create/', DocumentTypeCreateView.as_view(), name='document_type_create'),
    path('document_type/<int:pk>/update/', DocumentTypeUpdateView.as_view(), name='document_type_update'),
    path('document_type/<int:pk>/delete/', DocumentTypeDeleteView.as_view(), name='document_type_delete'),
    path('document_type/list/', DocumentTypeListView.as_view(), name='document_type_list'),
    path('drug_autocomplete/', DrugAutocompleteView.as_view(), name="drug_autocomplete" ),
]
