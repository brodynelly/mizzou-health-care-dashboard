from django.db import migrations


def create_users(apps, schema_editor):
    # Get models through the migration system
    User = apps.get_model("accounts", "CustomUser")
    Role = apps.get_model("accounts", "Role")
    Geocode = apps.get_model("patients", "Geocode")

    # Delete all users first
    User.objects.all().delete()

    # Create roles if they do not exist
    roles = ["doctor", "nurse", "admin"]
    role_objects = {}
    for role_name in roles:
        role, created = Role.objects.get_or_create(name=role_name)
        role_objects[role_name] = role

    # Get geocodes
    geocodes = list(Geocode.objects.all())

    # Helper function to get a geocode
    def get_geocode(index):
        return geocodes[index % len(geocodes)] if geocodes else None

    # Create admin user with admin role
    primary_geocode = get_geocode(0) if geocodes else None
    User.objects.create_superuser(
        email="admin@mail.com",
        password="admin",
        first_name="Admin",
        last_name="User",
        username="admin",
        profession="Admin",
        role=role_objects["admin"],  # Assign admin role explicitly
        primary_geocode=primary_geocode,
    )

    # Create other users
    users_data = [
        {
            "username": "nurse1",
            "email": "nurse1@mail.com",
            "first_name": "Nurse",
            "last_name": "One",
            "profession": "Nurse",
            "role": role_objects["nurse"],
            "geocode_index": 0,
        },
        {
            "username": "nurse2",
            "email": "nurse2@mail.com",
            "first_name": "Nurse",
            "last_name": "Two",
            "profession": "Nurse",
            "role": role_objects["nurse"],
            "geocode_index": 1,
        },
        {
            "username": "nurse3",
            "email": "nurse3@mail.com",
            "first_name": "Nurse",
            "last_name": "Three",
            "profession": "Nurse",
            "role": role_objects["nurse"],
            "geocode_index": 2,
        },
        {
            "username": "nurse4",
            "email": "nurse4@mail.com",
            "first_name": "Nurse",
            "last_name": "Four",
            "profession": "Nurse",
            "role": role_objects["nurse"],
            "geocode_index": 5,
        },
        {
            "username": "nurse5",
            "email": "nurse5@mail.com",
            "first_name": "Nurse",
            "last_name": "Five",
            "profession": "Nurse",
            "role": role_objects["nurse"],
            "geocode_index": 6,
        },

        {
            "username": "doctor1",
            "email": "doctor1@mail.com",
            "first_name": "Doctor",
            "last_name": "One",
            "profession": "Doctor",
            "role": role_objects["doctor"],
            "geocode_index": 3,
        },
        {
            "username": "doctor2",
            "email": "doctor2@mail.com",
            "first_name": "Doctor",
            "last_name": "Two",
            "profession": "Doctor",
            "role": role_objects["doctor"],
            "geocode_index": 4,
        },
    ]

    for user_data in users_data:
        User.objects.create_user(
            username=user_data["username"],
            email=user_data["email"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            profession=user_data["profession"],
            role=user_data["role"],
            primary_geocode=get_geocode(user_data["geocode_index"]),
            password="password",
        )


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0010_auto_20241029_2136"),
    ]

    operations = [
        migrations.RunPython(create_users),
    ]
