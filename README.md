# Django Project with Docker

This guide will help you set up and run the Django project using Docker and Docker Compose. Please follow the steps below to get started.

## PICTURES: 

<img width="1511" alt="image" src="https://github.com/user-attachments/assets/06b74985-378c-4dd2-8515-770670809478" />
<img width="1511" alt="image" src="https://github.com/user-attachments/assets/ae2733d1-3116-4d7d-b6b6-8ac2c95ca343" />
<img width="1511" alt="image" src="https://github.com/user-attachments/assets/468f9897-7297-42f1-be9a-0ed71b471509" />
<img width="1511" alt="image" src="https://github.com/user-attachments/assets/4f7696fd-9510-4fc5-93d3-190f70434e08" />
<img width="1511" alt="image" src="https://github.com/user-attachments/assets/84e5d6c9-70d3-44fd-b6d8-2d48264a3e38" />
<img width="1511" alt="image" src="https://github.com/user-attachments/assets/917b2764-cd3a-4e1b-ad1c-fbcc0f3417d0" />
<img width="1511" alt="image" src="https://github.com/user-attachments/assets/89691628-a70f-4d0f-b817-26ec13caaed1" />


## Prerequisites

- Ensure that you have [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed on your machine.
- If you do **not** have Docker installed, follow the instructions below to download and run Docker Desktop.

### Installing Docker Desktop

1. **Download Docker Desktop**
   - Visit the [Docker Desktop download page](https://www.docker.com/products/docker-desktop) and download the installer appropriate for your operating system (Windows, macOS, or Linux).

2. **Install Docker Desktop**
   - **Windows**: Double-click the downloaded installer and follow the on-screen instructions. You may be prompted to enable WSL 2 if not already enabled. Refer to [Docker’s WSL 2 installation guide](https://docs.docker.com/docker-for-windows/wsl/) for more details.
   - **macOS**: Open the downloaded `.dmg` file, drag the Docker icon to your Applications folder, and follow the on-screen instructions.
   - **Linux**: Installation instructions for your distribution can be found [here](https://docs.docker.com/desktop/install/linux-install/).

3. **Start Docker Desktop**
   - Once installed, open Docker Desktop from your Start menu (Windows) or Applications folder (macOS).
   - Ensure that Docker Desktop is running. You should see the Docker whale icon in your system tray or menu bar.
   - **Do not close Docker Desktop** while working with Docker containers, as it must be running in the background.
   - In the bottom-left corner of Docker Desktop, you should see an indicator confirming that the **Docker Engine is running**. If it is not running, start it manually from the Docker Desktop interface.

### Verify Docker Installation

- Open a terminal (Command Prompt, PowerShell, Terminal, etc.) and run the following command to verify Docker is installed correctly:


  ```sh
  docker --version
  ```

## Getting Started

1. **Download and Unzip the Project**
   - Download the zip file containing the project.
   - Unzip it to your desired location.

2. **Navigate to the Project Directory of the Django Project**
   - Open a terminal window and navigate to the directory where you unzipped the project.
   - It should be called ICareProject or something similar

   ```sh
   cd your_project_directory
   ```

3. **Build and Start the Docker Containers**
   - Run the following command to build and start the containers:

   ```sh
   docker-compose up --build
   ```

   - This will create and start the necessary services (e.g., web and database).

4. **Apply Migrations**
   - Once the containers are up and running, apply the database migrations:

   ```sh
   docker-compose exec web python manage.py migrate
   ```

5. **Access the Application**
   - Open your web browser and navigate to [http://localhost:8000](http://localhost:8000) to access the Django site.


## Project Important Notes

### User Information

#### Admin User
- **Email:** admin@mail.com  
- **Password:** admin  
- The admin user does not have assigned patients and cannot assign patients. The admin view is limited. To see the entire site functionality, use doctor and nurse accounts.

#### Nurse Users
- There are 5 nurses available for login.
  - **Email Format:** nurse1@mail.com (Replace the `1` with any number from `1-5` to log in with different nurse accounts.)
  - **Password:** password  

#### Doctor Users
- There are 2 doctors available for login.
  - **Email Format:** doctor1@mail.com (Replace the `1` with `1` or `2` to log in with different doctor accounts.)
  - **Password:** password  

### Adding Users
- To add a new user, you must be logged in with the admin account.
- Navigate to the **Admin Page**. There you can view the list of existing users. Click **Add** and follow the prompts to create a new user.

### Viewing Drug Autocomplete Functionality
- The drug autocomplete feature is accessible when editing or creating a **Prescription Type Document**.

### Document Palette Note
- The **Document Palette** only displays documents associated with the currently logged-in user's assigned patients.



## Stopping the Containers

- To stop the running containers, use the following command:

  ```sh
  docker-compose down
  ```

## Notes

- Make sure that no other services are using port 8000, as it is the default port for this Django application.
- If you need to change the port, you can modify the `docker-compose.yml` file accordingly.



# Understanding Django as an MVC Framework

Professor, I know you're used to grading projects built using the traditional MVC framework, especially in ASP.NET, so I thought it might be helpful to explain how Django fits into that structure in a way that maps to what you're familiar with. Django is often described as an "MTV" (Model-Template-View) framework, but it really maps quite closely to the MVC pattern that you know. I'll break it down step by step to make it easier to understand how to read Django code.

In a typical MVC framework like ASP.NET:

- **Model**: Represents the data and the business logic. It is responsible for querying the database, storing information, and ensuring data integrity.
- **View**: This part presents data to the user, often containing HTML and other presentational code.
- **Controller**: Acts as the intermediary between the Model and the View. It handles user input, processes requests, and updates the Model or View as needed.

In Django, these elements map slightly differently:

- **Model**: The Django **Model** works the same way as the Model in ASP.NET MVC. It defines the structure of your data, handles database interactions, and contains business logic. Django uses an ORM (Object-Relational Mapper) to interact with the database, which allows us to work with Python code instead of raw SQL.

- **View**: In Django, the **View** functions like the **Controller** in MVC. It handles the logic of responding to user requests, interacts with the Model to get or modify data, and decides what response to send back. Think of Django Views as the decision-making layer—similar to ASP.NET Controllers—managing user interactions and business logic.

- **Template**: The **Template** in Django corresponds to the **View** in ASP.NET MVC. This is where the presentation logic resides. Templates are used to render HTML and present data to the user, just like Razor Views in ASP.NET. This separation keeps the presentation code clean and distinct from the business logic.

### Summary of Django in MVC Terms

- **Model**: Defines the data structure and business rules (similar to the ASP.NET Model).
- **View (in Django)**: Functions like the Controller, handling logic, user input, and managing data (similar to ASP.NET Controllers).
- **Template**: Responsible for rendering the final output and presenting data to the user (similar to the ASP.NET View).

### Finding the Logic in This Project

In this project, I have organized the code into several apps: **accounts**, **documents**, and **patients**, along with the main **django\_project**. Here's how the MVC elements are implemented:

- **Model Logic**: Each app (accounts, documents, patients) has its own `models.py` file, which defines the data structure and business rules for that specific part of the application. For example, the **accounts** app has models related to user information, while the **patients** app has models for patient records.

- **View Logic**: The core logic, which handles user requests and interacts with models, is in the `views.py` files within each app. For example, in **documents/views.py**, you will see how requests for document-related actions are handled. This is similar to how Controllers in ASP.NET manage requests, pulling data from models and deciding how to respond.

- **Templates**: Each app also has its own folder for templates, like `accounts/templates/accounts/`, `documents/templates/documents/`, and `patients/templates/patients/`. Additionally, there is a main templates folder for common layouts, such as the base layout (`templates/base.html`). This is equivalent to having shared views in ASP.NET, where a common layout is used across multiple pages for consistency.

- **Static Files**: The static files (like CSS and JavaScript) are in a root-level `static/` folder. These are like the static content in ASP.NET, used for styling and adding interactive behavior to the pages.

- **URLs and Routing**: Django uses a `urls.py` file in each app to define URL patterns and map them to specific views. This is similar to routing in ASP.NET, where URLs are mapped to specific Controller actions. The main `urls.py` file in the project includes references to each app's `urls.py`, allowing the project to handle incoming requests appropriately.

The **base.html** template serves as the foundation for all pages, similar to a shared layout page in ASP.NET MVC. Each specific page template extends this base, ensuring consistency in the overall look and feel while still allowing for app-specific content.

### Understanding Class-Based Views (CBVs)

Django also provides **Class-Based Views (CBVs)**, which can be a bit different from what you might be used to in ASP.NET MVC. CBVs provide an object-oriented way to handle requests and make code more reusable compared to function-based views.

- **Inheritance**: CBVs inherit from Django's generic views like `ListView` or `DetailView`. For example, `ListView` is used to display a list of objects, similar to an ASP.NET Controller method that returns a list of items.

- **Attributes**: CBVs use attributes like `model`, `template_name`, or `context_object_name` to specify what data to use and how to render it. This is similar to using properties in ASP.NET to bind data to views.

- **Methods**: CBVs can override methods like `get()` or `post()` to handle requests, similar to how ASP.NET Controllers handle different HTTP verbs. The `get_context_data()` method is used to pass extra data to the template, like using `ViewBag` in ASP.NET.

Here’s an example:

```python
from django.views.generic import ListView
from .models import Document

class DocumentListView(ListView):
    model = Document
    template_name = 'documents/document_list.html'
    context_object_name = 'documents'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['extra_info'] = 'Some extra information'
        return context
```

In this example, `DocumentListView` inherits from `ListView` to display `Document` objects. The `template_name` specifies which HTML template to use, and `context_object_name` defines how the data will be referred to in the template. The `get_context_data()` method adds extra information to the context, similar to using `ViewBag` in ASP.NET.
