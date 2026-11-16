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
