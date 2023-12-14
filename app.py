import asyncio
import logging
import os
import queue
from dataclasses import dataclass

from fastapi import BackgroundTasks
from fastapi import FastAPI
from fastapi import Form
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

logging.basicConfig(filename="app.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

@dataclass
class Args:
    link: str

app = FastAPI()

# Mount the static folder for CSS files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates configuration
templates = Jinja2Templates(directory="templates")

# Define a global queue for logging records
logging_queue = queue.Queue()

def log_to_queue(record):
    logging.info(record)
    logging_queue.put_nowait(record)

async def run_subprocess_and_capture_output(link):
    process = await asyncio.create_subprocess_shell(
        f"python downloader.py {link}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    while True:
        stdout_data = await process.stdout.read(100)
        stderr_data = await process.stderr.read(100)

        if not stdout_data and not stderr_data:
            break

        if stdout_data:
            log_to_queue(f"stdout: {stdout_data.decode()}")
        if stderr_data:
            log_to_queue(f"stderr: {stderr_data.decode()}")

    return_code = await process.wait()
    log_to_queue(f"Subprocess finished with return code: {return_code}")

# Assuming you have a function to get a FastAPI request instance, if not you can remove it.
def get_request(request: Request):
    return request

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/error/", response_class=HTMLResponse)
async def error_page(request: Request):
    return templates.TemplateResponse("error_page.html", {"request": request})


# Assuming you have a BackgroundTasks instance in your FastAPI app
background_tasks = BackgroundTasks()

def call_downloader_main(args):
    from download_yt_split_upload import main
    return main(args)

async def run_main_in_background(args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, call_downloader_main, args)

@app.post("/submit_link/", response_class=HTMLResponse)
async def submit_link(link: str = Form(...), request: Request = None):
    error = None
    try:
        if link is None:
            raise ValueError("Link is missing")

        args = Args(link=link)

        # Use the BackgroundTasks to add the run_main_in_background to the background tasks
        # background_tasks.add_task(run_main_in_background, a)

        from download_yt_split_upload import main
        main(args)

    except Exception as e:
        error = str(e)

    # You can customize the reroute URL based on the result of your script
    reroute_url = os.environ.get("REROUTE_URL") if not error else "/error"

    # Use inline HTML and client-side JavaScript for redirection
    return HTMLResponse(content=f"""
        <html>
            <head>
                <title>Download Convert Upload</title>
            </head>
            <body>
                <script>
                    window.location.href = '{reroute_url}';
                </script>
            </body>
        </html>
    """, status_code=200, media_type="text/html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
