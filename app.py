from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
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

    return {"output": output, "error": error}
