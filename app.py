from fastapi import FastAPI, Request
import os
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse, Response
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request, Depends
import subprocess
from fastapi import Form

app = FastAPI()

# Mount the static folder for CSS files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates configuration
templates = Jinja2Templates(directory="templates")

# Assuming you have a function to get a FastAPI request instance, if not you can remove it.
def get_request(request: Request):
    return request

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/error/", response_class=HTMLResponse)
async def error_page(request: Request):
    return templates.TemplateResponse("error_page.html", {"request": request})


from fastapi import Request

@app.post("/submit_link/", response_class=HTMLResponse)
async def submit_link(link: str = Form(...), request: Request = None):
    try:
        if link is None:
            raise ValueError("Link is missing")

        # Replace "your_script.py" with the actual name of your Python script
        result = subprocess.run(["python", "downloader/main.py", link], capture_output=True, text=True)
        if result.returncode != 0:
            raise ValueError("Error running Python script")
        output = result.stdout
        error = result.stderr
        breakpoint()
    except Exception as e:
        output = None
        error = str(e)

    # You can customize the reroute URL based on the result of your script
    reroute_url = os.environ.get("REROUTE_URL") if not error else "/error"

    # Use inline HTML and client-side JavaScript for redirection
    return HTMLResponse(content=f"""
        <html>
            <head>
                <title>FastAPI Submission Box</title>
            </head>
            <body>
                <script>
                    window.location.href = '{reroute_url}';
                </script>
            </body>
        </html>
    """, status_code=200, media_type="text/html")
