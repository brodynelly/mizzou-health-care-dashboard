import random
from datetime import date

from django.db import migrations

UNASSIGNED = 'unassigned'
NURSE_ASSIGNED = 'nurse_assigned'
DOCTOR_ASSIGNED = 'doctor_assigned'
STATE_CHOICES = [
    (UNASSIGNED, 'Unassigned'),
    (NURSE_ASSIGNED, 'Nurse Assigned'),
    (DOCTOR_ASSIGNED, 'Doctor Assigned'),
]

def assign_nurse_to_patient(apps, schema_editor, patient_id, nurse_user_id):
    Patient = apps.get_model("patients", "Patient")
    TreatmentRecord = apps.get_model("patients", "TreatmentRecord")
    CustomUser = apps.get_model("accounts", "CustomUser")

    patient = Patient.objects.get(id=patient_id)
    nurse_user = CustomUser.objects.get(id=nurse_user_id)

    if nurse_user.role.name != "nurse":
        raise ValueError("User must have role 'nurse' to be assigned as a nurse.")

    if patient.nurse_count >= 3:
        raise ValueError("A patient can have no more than 3 nurses assigned.")

    if TreatmentRecord.objects.filter(patient=patient, worker=nurse_user).exists():
        raise ValueError(
            f"{nurse_user.name} is already assigned as a nurse to this patient."
        )

    # Create the TreatmentRecord for the nurse
    TreatmentRecord.objects.create(patient=patient, worker=nurse_user)
    patient.nurse_count += 1
    patient.state = NURSE_ASSIGNED
    patient.save()

def assign_doctor_to_patient(apps, schema_editor, patient_id, doctor_user_id):
    Patient = apps.get_model("patients", "Patient")
    TreatmentRecord = apps.get_model("patients", "TreatmentRecord")
    CustomUser = apps.get_model("accounts", "CustomUser")

    patient = Patient.objects.get(id=patient_id)
    doctor_user = CustomUser.objects.get(id=doctor_user_id)

    if doctor_user.role.name != "doctor":
        raise ValueError("User must have role 'doctor' to be assigned as a doctor.")

    if TreatmentRecord.objects.filter(patient=patient, worker=doctor_user).exists():
        raise ValueError(
            f"{doctor_user.name} is already assigned as a doctor to this patient."
        )

    if patient.doctor_assigned:
        raise ValueError("A patient can have only one doctor assigned.")

    if patient.nurse_count == 0:
        raise ValueError(
            "A doctor cannot be assigned unless at least one nurse is assigned."
        )

    # Create the TreatmentRecord for the doctor
    TreatmentRecord.objects.create(patient=patient, worker=doctor_user)
    patient.doctor_assigned = True
    patient.state = DOCTOR_ASSIGNED
    patient.save()


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

    # Create sample Geocodes
    geocode_1 = Geocode.objects.create(
        name="Celestial Heights",
        description="A high-altitude region known for its stunning views of the night sky",
    )
    geocode_2 = Geocode.objects.create(
        name="Mystic Falls",
        description="A serene location with cascading waterfalls and dense forests",
    )
    geocode_3 = Geocode.objects.create(
        name="Thunder Plains",
        description="A vast open plain that experiences frequent thunderstorms",
    )

    geocodes = [geocode_1, geocode_2, geocode_3]

    # Helper function to get a geocode
    def get_geocode(index):
        return geocodes[index % len(geocodes)] if geocodes else None

    # Create admin user with admin role
    primary_geocode = get_geocode(0)
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
            "geocode_index": 1,
        },
        {
            "username": "nurse5",
            "email": "nurse5@mail.com",
            "first_name": "Nurse",
            "last_name": "Five",
            "profession": "Nurse",
            "role": role_objects["nurse"],
            "geocode_index": 0,
        },
        {
            "username": "doctor1",
            "email": "doctor1@mail.com",
            "first_name": "Doctor",
            "last_name": "One",
            "profession": "Doctor",
            "role": role_objects["doctor"],
            "geocode_index": 2,
        },
        {
            "username": "doctor2",
            "email": "doctor2@mail.com",
            "first_name": "Doctor",
            "last_name": "Two",
            "profession": "Doctor",
            "role": role_objects["doctor"],
            "geocode_index": 1,
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
    return users_data


def create_sample_data(apps, schema_editor):
    # Delete all existing data
    CustomUser = apps.get_model("accounts", "CustomUser")
    Patient = apps.get_model("patients", "Patient")
    Geocode = apps.get_model("patients", "Geocode")
    TreatmentRecord = apps.get_model("patients", "TreatmentRecord")

    CustomUser.objects.all().delete()
    Patient.objects.all().delete()
    Geocode.objects.all().delete()
    TreatmentRecord.objects.all().delete()

    # Create users first
    users_data = create_users(apps, schema_editor)

    # Get geocodes
    geocode_1 = Geocode.objects.get(name="Celestial Heights")
    geocode_2 = Geocode.objects.get(name="Mystic Falls")
    geocode_3 = Geocode.objects.get(name="Thunder Plains")

    patients = [
        Patient.objects.create(
            name="Patrick Mahomes",
            address="1 Arrowhead Dr, West Columbia City, MO",
            date_of_birth=date(1995, 9, 17),
            height=75.0,
            weight=230.0,
            blood_group="A+",
            bed_id="B101",
            treatment_area="Cardiology",
            geocode=geocode_1,
        ),
        Patient.objects.create(
            name="Tom Brady",
            address="2 Buccaneer Way, West Columbia City, MO",
            date_of_birth=date(1977, 8, 3),
            height=76.0,
            weight=225.0,
            blood_group="B-",
            bed_id="B102",
            treatment_area="Neurology",
            geocode=geocode_2,
        ),
        Patient.objects.create(
            name="Aaron Rodgers",
            address="3 Lambeau Field Rd, West Columbia City, MO",
            date_of_birth=date(1983, 12, 2),
            height=74.0,
            weight=220.0,
            blood_group="O+",
            bed_id="B103",
            treatment_area="Oncology",
            geocode=geocode_3,
        ),
        Patient.objects.create(
            name="Josh Allen",
            address="4 Bills Dr, West Columbia City, MO",
            date_of_birth=date(1996, 5, 21),
            height=77.0,
            weight=237.0,
            blood_group="AB-",
            bed_id="B104",
            treatment_area="Orthopedics",
            geocode=geocode_1,
        ),
        Patient.objects.create(
            name="Lamar Jackson",
            address="5 Ravens Roost, West Columbia City, MO",
            date_of_birth=date(1997, 1, 7),
            height=74.0,
            weight=212.0,
            blood_group="A-",
            bed_id="B105",
            treatment_area="Gastroenterology",
            geocode=geocode_2,
        ),
        Patient.objects.create(
            name="Russell Wilson",
            address="6 Broncos Blvd, West Columbia City, MO",
            date_of_birth=date(1988, 11, 29),
            height=71.0,
            weight=215.0,
            blood_group="B+",
            bed_id="B106",
            treatment_area="Cardiology",
            geocode=geocode_3,
        ),
        Patient.objects.create(
            name="Dak Prescott",
            address="7 Cowboys Way, West Columbia City, MO",
            date_of_birth=date(1993, 7, 29),
            height=74.0,
            weight=238.0,
            blood_group="A+",
            bed_id="B107",
            treatment_area="Neurology",
            geocode=geocode_1,
        ),
        Patient.objects.create(
            name="Drew Brees",
            address="8 Saints Dr, West Columbia City, MO",
            date_of_birth=date(1979, 1, 15),
            height=72.0,
            weight=209.0,
            blood_group="B-",
            bed_id="B108",
            treatment_area="Oncology",
            geocode=geocode_2,
        ),
        Patient.objects.create(
            name="Kyler Murray",
            address="9 Cardinals Nest, West Columbia City, MO",
            date_of_birth=date(1997, 8, 7),
            height=70.0,
            weight=207.0,
            blood_group="O+",
            bed_id="B109",
            treatment_area="Orthopedics",
            geocode=geocode_3,
        ),
        Patient.objects.create(
            name="Matthew Stafford",
            address="10 Lions Den, West Columbia City, MO",
            date_of_birth=date(1988, 2, 7),
            height=75.0,
            weight=231.0,
            blood_group="AB-",
            bed_id="B110",
            treatment_area="Gastroenterology",
            geocode=geocode_1,
        ),
        Patient.objects.create(
            name="Justin Herbert",
            address="11 Chargers Lane, West Columbia City, MO",
            date_of_birth=date(1998, 3, 10),
            height=78.0,
            weight=236.0,
            blood_group="A+",
            bed_id="B111",
            treatment_area="Cardiology",
            geocode=geocode_2,
        ),
        Patient.objects.create(
            name="Derek Carr",
            address="12 Raiders Rd, West Columbia City, MO",
            date_of_birth=date(1991, 3, 28),
            height=75.0,
            weight=210.0,
            blood_group="B-",
            bed_id="B112",
            treatment_area="Neurology",
            geocode=geocode_3,
        ),
        Patient.objects.create(
            name="Deshaun Watson",
            address="13 Texans Blvd, West Columbia City, MO",
            date_of_birth=date(1995, 9, 14),
            height=74.0,
            weight=215.0,
            blood_group="O+",
            bed_id="B113",
            treatment_area="Oncology",
            geocode=geocode_1,
        ),
        Patient.objects.create(
            name="Baker Mayfield",
            address="14 Browns Way, West Columbia City, MO",
            date_of_birth=date(1995, 4, 14),
            height=73.0,
            weight=215.0,
            blood_group="AB-",
            bed_id="B114",
            treatment_area="Orthopedics",
            geocode=geocode_2,
        ),
        Patient.objects.create(
            name="Kirk Cousins",
            address="15 Vikings Dr, West Columbia City, MO",
            date_of_birth=date(1988, 8, 19),
            height=75.0,
            weight=202.0,
            blood_group="A-",
            bed_id="B115",
            treatment_area="Gastroenterology",
            geocode=geocode_3,
        ),
        Patient.objects.create(
            name="Jared Goff",
            address="16 Rams Blvd, West Columbia City, MO",
            date_of_birth=date(1994, 10, 14),
            height=76.0,
            weight=217.0,
            blood_group="B+",
            bed_id="B116",
            treatment_area="Cardiology",
            geocode=geocode_1,
        ),
        Patient.objects.create(
            name="Tua Tagovailoa",
            address="17 Dolphins Ave, West Columbia City, MO",
            date_of_birth=date(1998, 3, 2),
            height=73.0,
            weight=217.0,
            blood_group="A+",
            bed_id="B117",
            treatment_area="Neurology",
            geocode=geocode_2,
        ),
        Patient.objects.create(
            name="Joe Burrow",
            address="18 Bengals Blvd, West Columbia City, MO",
            date_of_birth=date(1996, 12, 10),
            height=76.0,
            weight=221.0,
            blood_group="B-",
            bed_id="B118",
            treatment_area="Oncology",
            geocode=geocode_3,
        ),
        Patient.objects.create(
            name="Mac Jones",
            address="19 Patriots Path, West Columbia City, MO",
            date_of_birth=date(1998, 9, 5),
            height=75.0,
            weight=214.0,
            blood_group="O+",
            bed_id="B119",
            treatment_area="Orthopedics",
            geocode=geocode_1,
        ),
        Patient.objects.create(
            name="Ryan Tannehill",
            address="20 Titans Trail, West Columbia City, MO",
            date_of_birth=date(1988, 7, 27),
            height=76.0,
            weight=217.0,
            blood_group="AB-",
            bed_id="B120",
            treatment_area="Gastroenterology",
            geocode=geocode_2,
        ),
        Patient.objects.create(
            name="Ben Roethlisberger",
            address="21 Steelers St, West Columbia City, MO",
            date_of_birth=date(1982, 3, 2),
            height=77.0,
            weight=240.0,
            blood_group="A-",
            bed_id="B121",
            treatment_area="Cardiology",
            geocode=geocode_3,
        ),
        Patient.objects.create(
            name="Cam Newton",
            address="22 Panthers Pl, West Columbia City, MO",
            date_of_birth=date(1989, 5, 11),
            height=77.0,
            weight=245.0,
            blood_group="B+",
            bed_id="B122",
            treatment_area="Neurology",
            geocode=geocode_1,
        ),
        Patient.objects.create(
            name="Carson Wentz",
            address="23 Commanders Ct, West Columbia City, MO",
            date_of_birth=date(1992, 12, 30),
            height=77.0,
            weight=237.0,
            blood_group="A+",
            bed_id="B123",
            treatment_area="Oncology",
            geocode=geocode_2,
        ),
        Patient.objects.create(
            name="Philip Rivers",
            address="24 Chargers Legacy, West Columbia City, MO",
            date_of_birth=date(1981, 12, 8),
            height=77.0,
            weight=228.0,
            blood_group="B-",
            bed_id="B124",
            treatment_area="Orthopedics",
            geocode=geocode_3,
        ),
        Patient.objects.create(
            name="Jameis Winston",
            address="25 Buccaneers Blvd, West Columbia City, MO",
            date_of_birth=date(1994, 1, 6),
            height=76.0,
            weight=231.0,
            blood_group="O+",
            bed_id="B125",
            treatment_area="Gastroenterology",
            geocode=geocode_1,
        ),
        Patient.objects.create(
            name="Trevor Lawrence",
            address="26 Jaguars Den, West Columbia City, MO",
            date_of_birth=date(1999, 10, 6),
            height=78.0,
            weight=220.0,
            blood_group="AB-",
            bed_id="B126",
            treatment_area="Cardiology",
            geocode=geocode_2,
        ),
        Patient.objects.create(
            name="Andy Dalton",
            address="27 Bears Ave, West Columbia City, MO",
            date_of_birth=date(1987, 10, 29),
            height=74.0,
            weight=219.0,
            blood_group="A-",
            bed_id="B127",
            treatment_area="Neurology",
            geocode=geocode_3,
        ),
        Patient.objects.create(
            name="Marcus Mariota",
            address="28 Falcons Flight, West Columbia City, MO",
            date_of_birth=date(1993, 10, 30),
            height=76.0,
            weight=222.0,
            blood_group="B+",
            bed_id="B128",
            treatment_area="Oncology",
            geocode=geocode_1,
        ),
        Patient.objects.create(
            name="Jimmy Garoppolo",
            address="29 49ers Rd, West Columbia City, MO",
            date_of_birth=date(1991, 11, 2),
            height=75.0,
            weight=225.0,
            blood_group="A+",
            bed_id="B129",
            treatment_area="Orthopedics",
            geocode=geocode_2,
        ),
        Patient.objects.create(
            name="Matt Ryan",
            address="30 Colts Dr, West Columbia City, MO",
            date_of_birth=date(1985, 5, 17),
            height=76.0,
            weight=220.0,
            blood_group="B-",
            bed_id="B130",
            treatment_area="Gastroenterology",
            geocode=geocode_3,
        ),
        Patient.objects.create(
            name="Justin Fields",
            address="31 Bears Den, West Columbia City, MO",
            date_of_birth=date(1999, 3, 5),
            height=75.0,
            weight=227.0,
            blood_group="O+",
            bed_id="B131",
            treatment_area="Cardiology",
            geocode=geocode_1,
        ),
        Patient.objects.create(
            name="Zach Wilson",
            address="32 Jets Run, West Columbia City, MO",
            date_of_birth=date(1999, 8, 3),
            height=74.0,
            weight=214.0,
            blood_group="AB-",
            bed_id="B132",
            treatment_area="Neurology",
            geocode=geocode_2,
        ),
        Patient.objects.create(
            name="Teddy Bridgewater",
            address="33 Dolphins Cove, West Columbia City, MO",
            date_of_birth=date(1992, 11, 10),
            height=74.0,
            weight=215.0,
            blood_group="A-",
            bed_id="B133",
            treatment_area="Oncology",
            geocode=geocode_3,
        ),
        Patient.objects.create(
            name="Daniel Jones",
            address="34 Giants Grove, West Columbia City, MO",
            date_of_birth=date(1997, 5, 27),
            height=77.0,
            weight=230.0,
            blood_group="B+",
            bed_id="B134",
            treatment_area="Orthopedics",
            geocode=geocode_1,
        ),
        Patient.objects.create(
            name="Taylor Heinicke",
            address="35 Commanders Court, West Columbia City, MO",
            date_of_birth=date(1993, 3, 15),
            height=73.0,
            weight=210.0,
            blood_group="A+",
            bed_id="B135",
            treatment_area="Gastroenterology",
            geocode=geocode_2,
        ),
        Patient.objects.create(
            name="Davis Mills",
            address="36 Texans Trail, West Columbia City, MO",
            date_of_birth=date(1998, 10, 21),
            height=76.0,
            weight=225.0,
            blood_group="B-",
            bed_id="B136",
            treatment_area="Cardiology",
            geocode=geocode_3,
        ),
        Patient.objects.create(
            name="Sam Darnold",
            address="37 Panthers Pride, West Columbia City, MO",
            date_of_birth=date(1997, 6, 5),
            height=75.0,
            weight=225.0,
            blood_group="O+",
            bed_id="B137",
            treatment_area="Neurology",
            geocode=geocode_1,
        ),
        Patient.objects.create(
            name="Geno Smith",
            address="38 Seahawks Nest, West Columbia City, MO",
            date_of_birth=date(1990, 10, 10),
            height=75.0,
            weight=221.0,
            blood_group="AB-",
            bed_id="B138",
            treatment_area="Oncology",
            geocode=geocode_2,
        ),
        Patient.objects.create(
            name="Jordan Love",
            address="39 Packers Pride, West Columbia City, MO",
            date_of_birth=date(1998, 11, 2),
            height=76.0,
            weight=224.0,
            blood_group="A-",
            bed_id="B139",
            treatment_area="Orthopedics",
            geocode=geocode_3,
        ),
        Patient.objects.create(
            name="Trey Lance",
            address="40 49ers Blvd, West Columbia City, MO",
            date_of_birth=date(2000, 5, 9),
            height=76.0,
            weight=224.0,
            blood_group="B+",
            bed_id="B140",
            treatment_area="Gastroenterology",
            geocode=geocode_1,
        ),
        Patient.objects.create(
            name="Nick Foles",
            address="41 Colts Path, West Columbia City, MO",
            date_of_birth=date(1989, 1, 20),
            height=78.0,
            weight=243.0,
            blood_group="A+",
            bed_id="B141",
            treatment_area="Cardiology",
            geocode=geocode_2,
        ),
        Patient.objects.create(
            name="Colt McCoy",
            address="42 Cardinals Ave, West Columbia City, MO",
            date_of_birth=date(1986, 9, 5),
            height=73.0,
            weight=212.0,
            blood_group="B-",
            bed_id="B142",
            treatment_area="Neurology",
            geocode=geocode_3,
        ),
        Patient.objects.create(
            name="Joe Flacco",
            address="43 Ravens Rd, West Columbia City, MO",
            date_of_birth=date(1985, 1, 16),
            height=78.0,
            weight=245.0,
            blood_group="O+",
            bed_id="B143",
            treatment_area="Oncology",
            geocode=geocode_1,
        ),
        Patient.objects.create(
            name="Mason Rudolph",
            address="44 Steelers Street, West Columbia City, MO",
            date_of_birth=date(1995, 7, 17),
            height=77.0,
            weight=235.0,
            blood_group="AB-",
            bed_id="B144",
            treatment_area="Orthopedics",
            geocode=geocode_2,
        ),
        Patient.objects.create(
            name="Case Keenum",
            address="45 Bills Blvd, West Columbia City, MO",
            date_of_birth=date(1988, 2, 17),
            height=73.0,
            weight=215.0,
            blood_group="A-",
            bed_id="B145",
            treatment_area="Gastroenterology",
            geocode=geocode_3,
        ),
        Patient.objects.create(
            name="Tyrod Taylor",
            address="46 Giants Grove, West Columbia City, MO",
            date_of_birth=date(1989, 8, 3),
            height=73.0,
            weight=217.0,
            blood_group="B+",
            bed_id="B146",
            treatment_area="Cardiology",
            geocode=geocode_1,
        ),
        Patient.objects.create(
            name="Chase Daniel",
            address="47 Chargers Lane, West Columbia City, MO",
            date_of_birth=date(1986, 10, 7),
            height=72.0,
            weight=225.0,
            blood_group="A+",
            bed_id="B147",
            treatment_area="Neurology",
            geocode=geocode_2,
        ),
        Patient.objects.create(
            name="PJ Walker",
            address="48 Panthers Pride, West Columbia City, MO",
            date_of_birth=date(1995, 2, 26),
            height=71.0,
            weight=210.0,
            blood_group="B-",
            bed_id="B148",
            treatment_area="Oncology",
            geocode=geocode_3,
        ),
        Patient.objects.create(
            name="CJ Beathard",
            address="49 Jaguars Blvd, West Columbia City, MO",
            date_of_birth=date(1993, 11, 16),
            height=74.0,
            weight=215.0,
            blood_group="O+",
            bed_id="B149",
            treatment_area="Orthopedics",
            geocode=geocode_1,
        ),
        Patient.objects.create(
            name="Nate Sudfeld",
            address="50 Lions Path, West Columbia City, MO",
            date_of_birth=date(1993, 10, 7),
            height=76.0,
            weight=227.0,
            blood_group="AB-",
            bed_id="B150",
            treatment_area="Gastroenterology",
            geocode=geocode_2,
        ),
    ]

    # Get users for assignment
    nurse_1 = CustomUser.objects.get(username="nurse1")
    nurse_2 = CustomUser.objects.get(username="nurse2")
    nurse_3 = CustomUser.objects.get(username="nurse3")
    nurse_4 = CustomUser.objects.get(username="nurse4")
    nurse_5 = CustomUser.objects.get(username="nurse5")
    doctor_1 = CustomUser.objects.get(username="doctor1")
    doctor_2 = CustomUser.objects.get(username="doctor2")

    nurses = [nurse_1, nurse_2, nurse_3, nurse_4, nurse_5]

    # Assign nurses to patients assign_doctor_to_patient(apps, schema_editor, patient_id, doctor_user_id)
    for i, patient in enumerate(patients):
        if i < 12:  # 25% of patients get 1 nurse
            assign_nurse_to_patient(
                apps, schema_editor, patient.id, random.choice(nurses).id
            )
        elif i < 24:  # Next 25% get 2 nurses
            selected_nurses = random.sample(nurses, 2)
            for nurse in selected_nurses:
                assign_nurse_to_patient(apps, schema_editor, patient.id, nurse.id)
        elif i < 36:  # Next 25% get 3 nurses
            selected_nurses = random.sample(nurses, 3)
            for nurse in selected_nurses:
                assign_nurse_to_patient(apps, schema_editor, patient.id, nurse.id)
        # Last 25% get no nurse

    # Assign doctors to patients with at least one nurse
    for patient in patients[:36]:  # Patients with at least one nurse assigned
        if random.choice([True, False]):  # 50% chance to assign a doctor
            assign_doctor_to_patient(
                apps, schema_editor, patient.id, random.choice([doctor_1, doctor_2]).id
            )


class Migration(migrations.Migration):

    dependencies = [
        ("patients", "0018_patient_doctor_assigned_patient_nurse_count_and_more"),
        ("accounts", "0011_auto_20241029_2354"),
    ]

    operations = [
        migrations.RunPython(create_sample_data),
    ]
