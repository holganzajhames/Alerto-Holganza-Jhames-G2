# Alerto · Account Feature

Alerto is a campus safety project. This phase implements the account flows using Django templates, Django authentication, and PostgreSQL.

| Role | How to create it | Dashboard |
| --- | --- | --- |
| Student | Register through the site | Contact details and profile shortcuts |
| Administrator | Run Django's `createsuperuser` command | Registered student count and administrator profile shortcuts |

Students and administrators receive HTTP 403 if they try to open the other role's dashboard. Profile links always use the signed-in account. Sign in with your username and password.

## Run locally on Windows

1. Install Python 3.10 or newer and PostgreSQL. In pgAdmin, create a database named `alerto`.
2. Open Command Prompt in this project folder and run:

   ```bat
   py -m venv venv
   venv\Scripts\activate.bat
   python -m pip install -r requirements.txt
   copy .env.example .env
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

3. Open `.env`, paste the generated key into `DJANGO_SECRET_KEY`, and fill in your PostgreSQL password. If using Supabase, enter the PostgreSQL connection details from its **Connect** panel. Use a direct or session-pooler connection and set `POSTGRES_SSLMODE=require`. Quote values if they contain spaces or special characters.
4. Apply migrations, create the administrator, and start Django:

   ```bat
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

5. Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/). Register a student account with a different username and email from the administrator.

On macOS or Linux, use `python3 -m venv venv`, `source venv/bin/activate`, and `cp .env.example .env` for the corresponding setup commands.

## Verify the account flows

Run `python manage.py test` against a local PostgreSQL account with permission to create a test database. For a manual demo, register a student, sign in, edit the profile, and sign out. Sign in as administrator and check the student count. While signed in under each role, try opening the other role's dashboard URL from the table below.

| Page | URL |
| --- | --- |
| Student dashboard | `/dashboard/student/` |
| Administrator dashboard | `/dashboard/admin/` |
| My profile | `/profile/` |
| Edit profile | `/profile/edit/` |

## Publish and submit

Create an empty public GitHub repository named `Alerto-Lastname-Firstname-Section`, replacing each placeholder with your class submission details. From this project folder, run:

```sh
git log --oneline
git remote add origin https://github.com/YOUR-USERNAME/Alerto-Lastname-Firstname-Section.git
git push -u origin main
```

Open the repository link in an incognito window, then paste it into the [submission form](https://forms.gle/RmYMff8sL2Dp6pZ86).

## PD2 Core feature

Alerto lets students report campus incidents and lets authorized staff manually review each report. The Student dashboard links to **Submit an SOS report** and **My SOS reports**. Students can create, view, edit, and delete their own unverified reports. The Administrator dashboard links to **Review reports**, where staff can confirm or dismiss an unverified report once. A confirmed report creates one notification record for future delivery. Reviewed reports are read-only.

Each SOS report belongs to a student, and each review belongs to a reviewer and one report. PostgreSQL stores submissions, paired GPS coordinates when available, and final decisions. GPS is optional and approximate. If permission is declined or unavailable, enter a campus location manually. This increment covers reporting and review. Device push and the incident map are planned for a later increment.

### Upgrade an existing Alerto setup on Windows

In the VS Code PowerShell terminal, from the repository folder:

```powershell
git switch main
git pull --ff-only origin main
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8001
```

Keep your existing local `.env`. For Supabase, copy the Session pooler connection details into the corresponding `POSTGRES_*` settings and use `POSTGRES_SSLMODE=require`. Open [Alerto](http://127.0.0.1:8001/) and sign in.

### Demo accounts

To create the report's demo accounts, use an isolated disposable PostgreSQL database with `DJANGO_DEBUG=True`, apply migrations, then run:

```powershell
.\venv\Scripts\python.exe manage.py seed_pd2_demo --confirm-demo-database
```

| Dashboard | Username |
| --- | --- |
| Student | `pd2_student` |
| Administrator | `pd2_reviewer` |

The command prints a newly generated password for each new account in your own terminal. Save them privately if you need to reuse them.

For a private setup, register a student through the form and create an administrator with `createsuperuser`. Use fresh passwords on a shared or deployed database. To demonstrate validation, submit with a blank campus location or input only one GPS coordinate. Run the regression suite with `python manage.py test` against PostgreSQL with permission to create a test database.
