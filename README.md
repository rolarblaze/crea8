# SellCrea8 API

## Overview

SellCrea8 is be a web application featuring a landing page, user onboarding, a dashboard for managing services, payment integration, appointments and calendar booking, project tracking, customer support, and additional "nice-to-have" features.

SellCrea8 aims to centralize creative and digital services into an affordable and user-friendly platform, supporting various business needs with high-quality, personalized solutions.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Database Local Setup (Development Environment)](#database-setup-development)
- [Database Setup (Heroku)](#database-setup-heroku)
- [Usage](#usage)
- [Contributing](#contributing)
- [Pull Request Template](#pull-request-template)

## Installation

1. Clone the repository to your local machine and navigate to the project directory. 

```bash
git clone https://github.com/sellmedia/Sellcrea8_Backend.git
```

2. Install python on your visual studio code or (your preferred code editor)

3. Create a virtual environment in your project folder using this command:

```bash
python -m venv venv 
```

4. Activate the virutal environment using this: 
**For Mac Users**:
```bash
source venv/bin/activate 
```

**For Windows Users**: 
- Activate the virtual environment using this (if you don't have a "bin" directory in your 'venv' folder listed in the file navigation area of your code editor):

```bash 
cd venv/scripts && activate
```
- Be sure to return to the root of your project file after this. You can use this command 

```bash
cd ../..
```

5. Install the project dependencies using the following command:
**For Mac Users**:

```bash
pip install -r requirements.txt
```

**For Windows Users**:
- Remove the 'uvloop' dependency from the requirements.txt file before running this command: 

```bash
pip install -r requirements.txt
```

- Then add the dependency back when you're done (since you'd be pushing this code to the repo and the repo includes it. The UVloop dependency is not required for Windows Users)


6. Make the appropriate configurations in your .env file following the configuration guide (#configuration)

## Configuration

Before running the SellCrea8 API application, make sure to configure the necessary environment variables. The following environment variables should be set with your specific values in development:

```bash
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin_password
ADMIN_SECRET_KEY=admin_secret_key
DATABASE_HOSTNAME=localhost
DATABASE_PORT=5432
DATABASE_PASSWORD=database_password
DATABASE_NAME=database_name
DATABASE_USERNAME=database_username
SECRET_KEY=your_secret_key
ALGORITHM=HS256

# Set the expiration time in minutes
ACCESS_TOKEN_EXPIRATION_TIME=15  # 15 minutes
REFRESH_TOKEN_EXPIRATION_TIME=86400 # 2 months 

# We might also consider using the Zoho mailing eventually. Set these for now 
ZOHO_SMTP_SENDER_EMAIL = admin@example.com
ZOHO_SMTP_USERNAME = admin@example.com
ZOHO_SMTP_OUTGOING_SERVER_NAME = admin@example.com
ZOHO_SMTP_PASSWORD = zoho_smtp_password
ZOHO_SMTP_PORT_WITH_SSL = ssl_port
ZOHO_SMTP_PORT_WITH_TLS = tsl_port
ZOHO_SMTP_REQUIRE_AUTHENTICATION = Yes

# The REMOTE_URL might not be of neccessity now, so use this default 
REMOTE_URL = 'http://127.0.0.1:8000'
PASSWORD_RESET_CODE_EXPIRATION_TIME=1440

ENDPOINT_URL = yourendpointurl
AWS_ACCESS_KEY_ID= yourawsaccesskeyid
AWS_SECRET_ACCESS_KEY = yourawssecretaccesskey

# The Termii Key will be set later on, use this as default for now
TERMII_API_KEY= yourtermiiapikey
TERMII_SMS_URL= yourtermiismsurl

PHONE_NUMBER_VERIFICATION_CODE_EXPIRATION_TIME = 60

INVITE_CODE_EXPIRATION_TIME = 2

# The Profile Photo and Cover Photo base url will be set as we continue development
# Use this for now 

PROFILE_PHOTO_BASE_URL = yourprofilephotobaseurl
COVER_PHOTO_BASE_URL = yourcoverphotobaseurl

SUPPORT_EMAIL = yoursupport@email.com
```

7. Before Setting Up The Database, run the application using this command: 

```bash
    uvicorn app.main:app --reload
```


## Database Local Setup (Development Environment)

### Step 1: Download and Install PostgreSQL
**Download PostgreSQL:** Go to the PostgreSQL download page(#https://www.postgresql.org/download/).
Select your operating system (Windows, macOS, Linux).
Download the installer and run it.

**Install PostgreSQL:** Follow the installation wizard instructions.
During the installation, you will be prompted to set a password for the postgres user. Remember this password as it will be used to connect to the database.

**Start PostgreSQL:** Ensure the PostgreSQL server is running. This can usually be managed via the PostgreSQL installation directory or through system services.


### Step 2: Download and Install pgAdmin
**Download pgAdmin:** Go to the pgAdmin download page. Select your operating system and download the installer.

**Install pgAdmin:** Run the installer and follow the installation wizard instructions.

**Start pgAdmin:** Launch pgAdmin from your applications menu.

### Step 3: Configure PostgreSQL in pgAdmin
**Open pgAdmin and create a new server:** Open pgAdmin and right-click on "Servers" in the Browser panel, then select "Create" > "Server...".
Enter a name for the server.

**Connection settings:** In the "Connection" tab, fill in the connection details:
Host name/address: localhost
Port: 5432
Username: postgres
Password: (the password you set during PostgreSQL installation)

**Save the server configuration:** Click "Save". You should now see the server listed under "Servers" in pgAdmin.

### Step 4: Apply Database Migrations From Your Terminal 
Open your code editor and run this script to apply the database migrations to your locally hosted database
**Note:** Ensure that your environment variables in your .env file contains the exact details you just set for your database in pgAdmin. i.e:
Host name/address: localhost
Port: 5432
Username: postgres
Password: (the password you set during PostgreSQL installation)

**script:**
```bash
    alembic upgrade head 
```
### Step 5: Run the application from the terminal
Type this command in your terminal to run the program 

```bash
    uvicorn app.main:app --reload
```




## Database Setup (Heroku)
If you are hosting the SellCrea8 API on Heroku with a Postgres database, follow these steps to set up the database. This part is typically for the DevOps person. 

### Step 1: Apply Migrations

Run the following command to apply database migrations:

```bash
heroku run alembic upgrade head --app your-heroku-app-name
```

## Usage
Follow the instructions below to utilize the API effectively.

### Documentation

Access the API documentation by navigating to the root endpoint with the forward slash in front of the URL containing "docs," as in `/docs`. Explore the provided endpoints and learn the endpoints available.

### Example

**Navigate to the documentation endpoint:**
```bash
https://the-api-url/docs
```
**or**
```bash
http://localhost:8000/docs
```

### Contributing
# SellCrea8 API Contribution Guidelines

We welcome contributions to enhance and improve the SellCrea8 API. Please follow the guidelines below for making contributions to the codebase.

### How to Contribute

1. **Clone the Repository:** Clone the repository to your local machine. Use the following command:

    ```bash
    git clone https://github.com/sellmedia/Sellcrea8_Backend.git
    ```

2. **Checkout Development Branch:** Navigate to the development branch to ensure you’re working on the latest codebase:

    ```bash
    git checkout development
    ```

3. **Create a Branch:** Create a new branch for your feature or bug fix. Use a descriptive name for your branch:

    ```bash
    git checkout -b feature/your-feature
    ```

Since this is a private repository and you might not know what feature you're contributing to unless directed by the Lead engineer, following the directive of the Lead Engineer, your branch will also be created on the repo and you can push your changes to your branch and make Pull Requests (PRs) against the development branch. The PR will be subejct to review.

**Hence, you can use this:**

    ```bash
    git checkout -b your_branch
    ```

4. **Make Changes:** Implement your changes or additions. Ensure that your code follows the project's coding style and conventions.

5. **Run Tests:** If applicable, run the tests to ensure your changes do not introduce new issues:
    **Example command for running tests**
    ```bash
    mypy --ignore-missing-imports --disable-error-code "annotation-unchecked" --disable-error-code "attr-defined" --disable-error-code "unused-ignore" --disable-error-code "var-annotated" --disable-error-code "arg-type" --disable-error-code "assignment" --disable-error-code "misc" --disable-error-code "valid-type"  --disable-error-code "call-arg" app
    ```

6. **Update Documentation:** If your changes affect the project's documentation, ensure it is updated accordingly.

7. **Commit Changes:** Commit your changes with a clear and concise commit message. Use present tense and follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

    ```bash
    git commit -m "feat: add new feature"
    ```

8. **Push Changes:** Push your changes to the repository on GitHub:

    ```bash
    git push origin your_branch
    ```

9. **Create a Pull Request:** Go to the repository on GitHub and create a pull request (PR) from your branch to the `development` branch. Provide a clear and detailed description of your changes.

10. **Code Review:** Your PR will be reviewed by project maintainers. Address any feedback or comments provided during the review.

### Pull Request Template

When submitting a pull request, use the following template (copy this template and make edits from the Description Title and make the appropriate edits with the contents):

## Copy From The Description Title Below
#### Note: For the checkboxes, put an uppercase "X" without the quotation marks in the square bracket (i.e [ ]) to mark the kind of change made. 

## Description

Provide a clear and concise description of the changes introduced by this pull request. You can clear all these typed here as this is just a template

## Related Issue

If this pull request is related to an existing issue, link the issue here. Also clear what is typed here as this is just a template.

## Type of Change

- [ ] Bug Fix
- [ ] New Feature
- [ ] Documentation Update
- [ ] Other (please specify)


## Checklist

- [ ] I have tested my changes.
- [ ] I have updated the documentation.
- [ ] My code follows the project's coding style.
- [ ] I have added/modified tests to cover my changes. 

## Screenshots (if applicable)

Provide any screenshots or visual representations of your changes (if applicable).
