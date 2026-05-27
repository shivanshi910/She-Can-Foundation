# She Can Foundation - Simple Webpage

Open `index.html` in your browser to view the page.

Files:

- index.html — main page with NGO name, about, image, button, footer, and form
- styles.css — styling and responsive rules
- script.js — handles form submission and dark mode toggle

Backend (optional): a simple Flask backend is provided in the `server` folder.
To enable API storage, authentication and the admin panel, run the backend.

Quick start (Windows PowerShell):

```powershell
cd "c:\Users\shivi\OneDrive\Desktop\she1"
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r server\requirements.txt
python server\init_db.py
python server\app.py
```

Then open `http://localhost:5501` for the site (served by the Flask backend) and
`http://localhost:5501/admin.html` for the admin panel.

Default admin credentials: username `admin` password `password` (change immediately).

Environment and security notes:

- Use `FLASK_SECRET` environment variable to set a strong Flask secret key before running the backend.
- You can set the initial admin password with `ADMIN_PASS` when running `init_db.py` (recommended).

Example (PowerShell):

```powershell
$env:FLASK_SECRET = 'a-very-strong-secret'
$env:ADMIN_PASS = 'choose-a-strong-password'
python server\init_db.py
python server\app.py
```

No build steps required. Just open the HTML file in any modern browser.
