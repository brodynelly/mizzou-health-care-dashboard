from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .models import Geocode, Patient, TreatmentRecord

CustomUser = get_user_model()

#Create View
@method_decorator(login_required, name='dispatch')
class PatientCreateView(CreateView):
    model = Patient
    fields = ['name', 'address', 'date_of_birth', 'height', 'weight', 'blood_group', 'bed_id', 'treatment_area', 'geocode']
    template_name = 'patients/patient_form.html'
    success_url = reverse_lazy('patient_list')

# Read/List View with pagination, search, filter, and sort
@method_decorator(login_required, name='dispatch')
class PatientListView(ListView):
    model = Patient
    template_name = 'patients/patient_list.html'
    context_object_name = 'patients'

    def get_paginate_by(self, queryset):
        # Get the pagination setting from the request, default to 10 if not specified
        items_per_page = self.request.GET.get('items_per_page', '20')
        try:
            return int(items_per_page)
        except ValueError:
            return 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        sort_by = self.request.GET.get('sort', 'name')
        treatment_state = self.request.GET.get('treatment_state', '')


        # Search functionality
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(bed_id__icontains=search_query) |
                Q(treatment_area__icontains=search_query) |
                Q(geocode__name__icontains=search_query)
            )

        # Filter by treatment state if selected
        if treatment_state:
            queryset = queryset.filter(state=treatment_state)

        # Apply sorting
        if sort_by:
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['treatment_area_filter'] = self.request.GET.get('treatment_area', '')
        context['sort_by'] = self.request.GET.get('sort', 'name')
        context['items_per_page'] = self.request.GET.get('items_per_page', '10')
        return context


# Detail View
@method_decorator(login_required, name='dispatch')
class PatientDetailView(DetailView):
    model = Patient
    template_name = 'patients/patient_detail.html'
    context_object_name = 'patient'

# Update View
@method_decorator(login_required, name='dispatch')
class PatientUpdateView(UpdateView):
    model = Patient
    fields = ['name', 'address', 'date_of_birth', 'height', 'weight', 'blood_group', 'bed_id', 'treatment_area']
    template_name = 'patients/patient_form.html'
    success_url = reverse_lazy('patient_list')

# Delete View
@method_decorator(login_required, name='dispatch')
class PatientDeleteView(DeleteView):
    model = Patient
    template_name = 'patients/patient_confirm_delete.html'
    success_url = reverse_lazy('patient_list')

#Icare View aka View Patient by geocode
@method_decorator(login_required, name='dispatch')
class ICareBoardView(ListView):
    model = Patient
    template_name = 'patients/icare_board.html'
    context_object_name = 'patients'
    paginate_by = 10  # Default pagination value

    def get_paginate_by(self, queryset):
        # Get the pagination setting from the request, default to 10 if not specified or invalid
        items_per_page = self.request.GET.get('paginate_by', '10')
        try:
            return int(items_per_page)
        except (ValueError, TypeError):
            return self.paginate_by

    def get_queryset(self):
        geocode_id = self.kwargs.get('geocode_id')
        if geocode_id:
            geocode = get_object_or_404(Geocode, id=geocode_id)
        elif self.request.user.is_authenticated and self.request.user.primary_geocode:
            geocode = self.request.user.primary_geocode
        else:
            geocode = None

        self.geocode = geocode  # Store geocode for use in context

        if geocode:
            patients_queryset = geocode.patients.prefetch_related('treated_by').all()

            # Apply search filter if a query is provided
            search_query = self.request.GET.get('search', '')
            if search_query:
                patients_queryset = patients_queryset.filter(
                    Q(name__icontains=search_query) |
                    Q(treatment_area__icontains=search_query)
                )

            # Apply sorting
            sort_by = self.request.GET.get('sort', 'name')
            if sort_by in ['name', 'treatment_area', 'bed_id', 'date_of_birth']:
                patients_queryset = patients_queryset.order_by(sort_by)

            return patients_queryset
        else:
            return Patient.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Ensure each patient has full context with treatment details
        for patient in context['patients']:
            # Check if the current user is assigned to the patient
            treatment_records = TreatmentRecord.objects.filter(patient=patient)

            patient.is_assigned_to_user = False
            patient.assigned_workers = []

            for record in treatment_records:
                worker = record.worker
                if worker == user:
                    patient.is_assigned_to_user = True

                # Append worker details to assigned_workers
                patient.assigned_workers.append({
                    'name': worker.name,
                    'role': worker.role.name,
                    'is_user': worker == user
                })

            # Determine if the user can assign or unassign
            patient.can_assign = (
                (user.role.name == 'doctor' and not patient.doctor_assigned and patient.nurse_count > 0) or
                (user.role.name == 'nurse' and patient.nurse_count < 3 and not patient.is_assigned_to_user)
            )
            patient.can_unassign = patient.is_assigned_to_user

        context['geocode'] = self.geocode
        context['other_geocodes'] = Geocode.objects.exclude(id=self.geocode.id) if self.geocode else Geocode.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['sort_by'] = self.request.GET.get('sort', 'name')
        context['paginate_by'] = self.get_paginate_by(self.get_queryset())  # Add paginate_by to the context
        return context

    def post(self, request, *args, **kwargs):
        patient_id = request.POST.get('patient_id')
        action = request.POST.get('action')
        patient = get_object_or_404(Patient, id=patient_id)

        print(f"Post action: {action}, User: {request.user}, Patient ID: {patient_id}")

        try:
            if action == 'assign':
                if request.user.role.name == 'doctor':
                    # Assign the doctor only if not already assigned
                    if not patient.doctor_assigned:
                        patient.assign_doctor(request.user)
                    else:
                        messages.warning(request, f"{request.user.name} is already assigned as the doctor.")
                elif request.user.role.name == 'nurse':
                    # Assign the nurse only if under the limit
                    if patient.nurse_count < 3:
                        patient.assign_nurse(request.user)
                    else:
                        messages.warning(request, "Cannot assign more than 3 nurses to a patient.")

            elif action == 'unassign':
                if request.user.role.name == 'doctor':
                    patient.unassign_doctor(request.user)
                elif request.user.role.name == 'nurse':
                    patient.unassign_nurse(request.user)

        except ValueError as e:
            messages.error(request, f"Failed to assign/unassign: {str(e)}")

        referer = request.META.get('HTTP_REFERER', request.path)
        return redirect(referer)

@method_decorator(login_required, name='dispatch')
class MyBoardView(ListView):
    model = Patient
    template_name = 'patients/my_board.html'
    context_object_name = 'patients'

    def get_paginate_by(self, queryset):
        # Get the pagination setting from the request, default to 10 if not specified or invalid
        items_per_page = self.request.GET.get('paginate_by', '10')
        try:
            return int(items_per_page)
        except (ValueError, TypeError):
            return 10

    def get_queryset(self):
            user = self.request.user  # Access the current user

            if user.is_authenticated:
                # Retrieve all patients assigned to the current user through TreatmentRecord
                assigned_patients = Patient.objects.filter(
                    treatmentrecord__worker=user).distinct()  # Use distinct() to avoid duplicates
                # Apply search filter if a query is provided
                search_query = self.request.GET.get('search', '')
                if search_query:
                    assigned_patients = assigned_patients.filter(
                        Q(name__icontains=search_query) |
                        Q(treatment_area__icontains=search_query)
                    )

                # Apply sorting
                sort_by = self.request.GET.get('sort', 'name')
                if sort_by in ['name', 'treatment_area', 'bed_id', 'date_of_birth']:
                    assigned_patients = assigned_patients.order_by(sort_by)

                return assigned_patients.distinct()  # Use distinct() to avoid duplicates
            else:
                return Patient.objects.none()  # Return an empty queryset if user is not authenticated

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['sort_by'] = self.request.GET.get('sort', 'name')
        context['paginate_by'] = self.request.GET.get('paginate_by', '10')  # Add paginate_by to the context
        return context

    def post(self, request, *args, **kwargs):
        # Get the patient ID from the form data
        patient_id = request.POST.get('patient_id')
        patient = get_object_or_404(Patient, id=patient_id)
        user = request.user

        try:
            # Unassign the doctor if the user is a doctor
            if user.role.name == 'doctor':
                patient.unassign_doctor(user)
                messages.success(request, f"{user.name} has been unassigned as the doctor for {patient.name}.")

            # Unassign the nurse if the user is a nurse
            elif user.role.name == 'nurse':
                patient.unassign_nurse(user)
                messages.success(request, f"{user.name} has been unassigned as a nurse for {patient.name}.")

        except ValueError as e:
            messages.error(request, f"Failed to unassign: {str(e)}")
        # Redirect back to the referring URL to preserve query parameters
        referer = request.META.get('HTTP_REFERER', request.path)
        return redirect(referer)
