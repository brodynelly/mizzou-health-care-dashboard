# Django Project with Docker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![CI](https://github.com/brodynelly/mizzou-health-care-dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/brodynelly/mizzou-health-care-dashboard/actions/workflows/ci.yml) ![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)

This guide will help you set up and run the Django project using Docker and Docker Compose. Please follow the steps below to get started.

## Project Structure

This project follows a standard Django structure with some quality of life improvements:

- **Apps**: `accounts`, `documents`, `pages`, `patients` (kebab-case naming for repositories, snake_case for python modules)
- **Configuration**: `django_project` (snake_case)
- **Environment**: Managed via `.env` file (see `env.example`)
- **Linting/Formatting**: Uses `ruff` for fast Python linting and formatting.
- **CI**: GitHub Actions workflow for automated testing and linting.

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

1. **Clone the Repository**
   ```sh
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Setup Environment Variables**
   - Create a `.env` file in the root directory based on the `env.example` (if provided) or use the defaults:
     ```
     DJANGO_SECRET_KEY=your-secret-key
     DEBUG=True
     DATABASE_URL=postgres://postgres:postgres@db:5432/postgres
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

## Development

### Linting and Formatting
This project uses `ruff` for linting and formatting.
- To check for issues: `ruff check .`
- To format code: `ruff format .`

### Running Tests
To run tests locally using the Docker container:
```sh
docker-compose exec web python manage.py test
```

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
