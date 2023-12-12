from fastapi import FastAPI, Request
import os
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import subprocess
from fastapi import Form

app = FastAPI()

# Mount the static folder for CSS files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates configuration
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/submit_link/")
async def submit_link(link: str = Form(...)):
    # Run your Python script with the provided link as input
    try:
        # Replace "your_script.py" with the actual name of your Python script
        result = subprocess.run(["python", "downloader/main.py", link], capture_output=True, text=True)
        output = result.stdout
        error = result.stderr
    except Exception as e:
        output = None
        error = str(e)

 # You can customize the redirect URL based on the result of your script
    reroute_url = os.environ.get("REROUTE_URL") if not error else "/error"

    return HTMLResponse(content=f"""
        <html>
            <head>
                <title>FastAPI Submission Box</title>
                <link rel="stylesheet" href="{{ url_for('static', path='styles.css') }}">
            </head>
            <body>
                <script>
                    window.location.href = '{reroute_url}';
                </script>
            </body>
        </html>
    """, status_code=200, media_type="text/html")
