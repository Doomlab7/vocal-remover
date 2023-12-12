import subprocess
from pathlib import Path

from fastapi import FastAPI
from fastapi import Form
from fastapi import Request
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app_functions import DownloadRequest
from app_functions import InferenceRequest
from app_functions import get_itag as _get_itag
from app_functions import run_ffmpeg as _run_ffmpeg
from app_functions import run_inference as _run_inference
from app_functions import youget as _youget


def get_itag(output: str):
    return _get_itag(output)

app = FastAPI()

# Mount the "static" directory to serve static files (e.g., the HTML file)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Use Jinja2Templates for rendering HTML templates
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")  # Use Path to get correct absolute path

# Route to serve the HTML page
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        <title>File Processing App</title>
        <!-- Include htmx script -->
        <script defer src="https://unpkg.com/htmx.org@1.7.0/dist/htmx.js"></script>
    </head>
    <body class="bg-gray-200 flex items-center justify-center h-screen">
        <div class="bg-white p-8 rounded shadow-md w-96">
            <h1 class="text-2xl font-semibold mb-4">File Processing App</h1>
            <!-- Add htmx attributes to the form -->
                <form id="fileForm" hx-post="/submit" hx-target="#result" hx-swap="outerHTML" hx-vals=".">
                    <div>
                        <label for="yt_link" class="block text-sm font-medium text-gray-700">Enter YouTube Link:</label>
                        <input type="text" id="yt_link" name="yt_link" class="mt-1 p-2 w-full border rounded-md">
                    </div>
                    <div>
                        <button type="submit" class="w-full bg-blue-500 text-white p-2 rounded-md">Submit</button>
                    </div>
                </form>
        </div>

<!-- Include htmx script -->
<script src="https://unpkg.com/htmx.org@1.7.0/dist/htmx.js"></script>

<script>
    async function submitForm() {
        const ytLink = document.getElementById('yt_link').value;

        try {
            // Display a loading message or spinner
            document.getElementById('result').innerHTML = 'Processing...';

            // Use HTMX to submit the form asynchronously
            const response = await htmx.ajax('/submit', 'post', { yt_link });

            // Extract relevant information from the response
            const message = response.message || 'Request processed successfully';

            // Display the message in the result div
            document.getElementById('result').innerHTML = message;

            // Clear the input field
            document.getElementById('yt_link').value = '';
        } catch (error) {
            // Handle errors if needed
            console.error('Error:', error);

            // Display an error message in the result div
            document.getElementById('result').innerHTML = 'Error processing the request. Please try again.';
        }
    }
</script>

        <!-- Display result here -->
        <div id="result" hx-target="#result"></div>

        <script>
            // Optional: Add htmx script initialization
            htmx.on("htmx:configRequest", function (event) {
                // You can modify the request before it's sent, if needed
                console.log("Configuring htmx request:", event.detail.xhr);
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/submit")
async def submit_form(yt_link: str = Form(...)):
    try:
        result = subprocess.run(
            f"pipx run pytube {yt_link} --list",
            shell=True,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        output = result.stdout
        itag = get_itag(output)

        result = subprocess.run(
            f"pipx run pytube {yt_link} --itag {itag}",
            shell=True,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        response_data = {"message": f"Processing {yt_link}", "captured_output": output}

        # Returning JSONResponse to handle the response in a more controlled manner
        return JSONResponse(content=response_data, status_code=200)

    except subprocess.CalledProcessError as e:
        error_message = f"Error running subprocess: {e.returncode}, {e.stderr}"
        print(error_message)

        # Returning an error response
        return JSONResponse(content={"error": error_message}, status_code=500)


# Additional route for serving the htmx library (optional)
@app.get("/htmx.js")
async def get_htmx():
    return FileResponse("static/htmx.js")

@app.post("/run_inference")
async def run_inference(data: InferenceRequest):
    _run_inference(data)
@app.post("/run_ffmpeg")
async def run_ffmpeg(data: InferenceRequest):
    _run_ffmpeg(data)

@app.post("/youget")
async def youget(data: DownloadRequest):
    _youget(data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
