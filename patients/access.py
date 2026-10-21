from django.core.exceptions import PermissionDenied


def get_authorized_unit_id(user):
    if user.primary_geocode_id is None or getattr(user.role, "name", None) not in {
        "doctor",
        "nurse",
    }:
        raise PermissionDenied
    return user.primary_geocode_id
