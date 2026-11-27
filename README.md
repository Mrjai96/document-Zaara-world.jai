# Zaara World — Company Management System

A Streamlit-based starter application for managing company operations. Includes dashboard, employee directory, departments, attendance, leave approvals, projects, tasks, clients, payroll register, finance, meetings, reports, activity logs, user management and settings.

## 1. Run locally

Requires Python 3.10 or newer.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown in the terminal (usually http://localhost:8501).

## 2. First login

On the first run, the app creates a starter administrator:

- Email: `admin@zaaraworld.com`
- Password: `ChangeMe123!`

**Immediately change this password** in Settings. For deployment, set environment variables / Streamlit secrets:
- `ZAARA_ADMIN_EMAIL`
- `ZAARA_ADMIN_PASSWORD`

These are used only when the database is first initialized. If the database already exists, changing them will not change the existing account password.

## 3. Deploy to Streamlit Community Cloud

1. Extract this ZIP.
2. Create a GitHub repository and upload all files and folders.
3. Go to https://share.streamlit.io/ and sign in with GitHub.
4. Choose **Create app**, select the repository and branch, and set the main file to `app.py`.
5. Deploy.
6. In app settings → **Secrets**, add:

```toml
ZAARA_ADMIN_EMAIL = "your-admin-email@example.com"
ZAARA_ADMIN_PASSWORD = "use-a-long-unique-password"
```

7. Restart/redeploy, then sign in and change the password.

## 4. Important deployment notes

This is a functional starter/MVP, not a fully audited enterprise ERP. It uses SQLite for simple setup. Streamlit Community Cloud's local filesystem is not guaranteed to be persistent across restarts or redeployments. For real company data and multiple concurrent users, migrate to managed PostgreSQL (for example, Supabase or Neon), configure persistent backups, and use a proper secrets manager.

Before production use:
- Enforce role-specific permissions on every page and database action (the starter includes basic role-aware user administration, not complete per-module authorization).
- Add audit logging for all sensitive changes.
- Add server-side validation, CSRF/session hardening as appropriate, rate limits and secure file storage.
- Configure payroll rules with a qualified accountant; statutory deductions vary by employee and jurisdiction.
- Review privacy, employment, tax and data-retention obligations.
- Do not store real salary, identity, bank, or other sensitive employee data until security and access controls have been reviewed.

## 5. Project structure

```text
zaara_world/
├── app.py
├── auth.py
├── database.py
├── ui.py
├── requirements.txt
├── README.md
└── .streamlit/
    └── config.toml
```

## 6. Data

The database file `zaara_world.db` is created automatically in the working directory. Back it up securely. Never commit the database, passwords, or Streamlit secrets to GitHub.
