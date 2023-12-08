import re
import subprocess
from pathlib import Path

from fastapi import FastAPI
from fastapi import Form
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel


def get_itag(output: str):
# Split the output into lines
    lines = output.split("\n")

# Initialize variables to store the maximum abr and corresponding itag
    max_abr = 0
    max_abr_itag = None

# Iterate through the lines
    for line in lines:
        if "mime_type=\"audio/mp4\"" in line:
            # Extract abr value using regular expression
            abr_match = re.search(r'abr="(\d+)kbps"', line)
            if abr_match:
                current_abr = int(abr_match.group(1))
                # Update max_abr and max_abr_itag if current_abr is greater
                if current_abr > max_abr:
                    max_abr = current_abr
                    max_abr_itag_match = re.search(r'itag="(\d+)"', line)
                    if max_abr_itag_match:
                        max_abr_itag = max_abr_itag_match.group(1)

# Print the result
    print(f"Max abr: {max_abr}")
    print(f"Corresponding itag: {max_abr_itag}")
    return max_abr_itag

app = FastAPI()

class DownloadRequest(BaseModel):
    link: str

class InferenceRequest(BaseModel):
    filename: str

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
                <form id="fileForm" hx-post="/submit" hx-target="#result" class="space-y-4">
                    <div>
                        <label for="yt_link" class="block text-sm font-medium text-gray-700">Enter YouTube Link:</label>
                        <input type="text" id="yt_link" name="yt_link" class="mt-1 p-2 w-full border rounded-md">
                    </div>
                    <div>
                        <button type="submit" class="w-full bg-blue-500 text-white p-2 rounded-md">Submit</button>
                    </div>
                </form>
        </div>

        <!-- Display result here -->
        <div id="result" hx-target="#result"></div>

        <script>
            // Optional: Add htmx script initialization
            htmx.on("htmx:configRequest", function (event) {
                // You can modify the request before it's sent, if needed
                console.log("Configuring htmx request:", event.detail.xhr);
            });

            function submitForm() {
                // Optional: Add logic before the form submission
                console.log("Before form submission");

                // Submit the form using htmx
                htmx.submit("#fileForm");

                // Optional: Add logic after the form submission
                console.log("After form submission");
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/submit")
async def submit_form(yt_link: str = Form(...)):
    # Run the subprocess command and capture the output
    try:
        # Use subprocess.PIPE to capture the output
        result = subprocess.run(
            f"pipx run pytube {yt_link} --list",
            shell=True,
            check=True,
            text=True,  # Capture output as text
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Access the captured output
        output = result.stdout

        # Now you can parse the output as needed
        # print(f"Captured output: {output}")

        # Parse the output and find the max abr and corresponding itag
        # ... (use the parsing logic from the previous example)
        itag = get_itag(output)

        result = subprocess.run(
            f"pipx run pytube {yt_link} --itag {itag}",
            shell=True,
            check=True,
            text=True,  # Capture output as text
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Return a response
        return {"message": f"Processing {yt_link}", "captured_output": output}
    except subprocess.CalledProcessError as e:
        # If the subprocess command returns a non-zero exit code
        error_message = f"Error running subprocess: {e.returncode}, {e.stderr}"
        print(error_message)
        return {"error": error_message}

# Additional route for serving the htmx library (optional)
@app.get("/htmx.js")
async def get_htmx():
    return FileResponse("static/htmx.js")

@app.post("/run_inference")
async def run_inference(data: InferenceRequest):
    filename = data.filename
    inference_script = "python inference.py"

    # Run the inference script
    try:
        subprocess.run(f"{inference_script} --input {filename}", shell=True, check=True)
        return {"message": f"Inference completed for {filename}"}
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Error running inference script")

@app.post("/run_ffmpeg")
async def run_ffmpeg(data: InferenceRequest):
    filename = data.filename
    instruments_wav = f"{filename}_instruments.wav"
    instruments_mp3 = f"{filename}_instruments.mp3"

    # Run ffmpeg command to convert wav to mp3
    try:
        subprocess.run(f"ffmpeg -i {instruments_wav} {instruments_mp3}", shell=True, check=True)
        return {"message": f"FFmpeg conversion completed for {filename}"}
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Error running ffmpeg command")


@app.post("/youget")
async def youget(data: DownloadRequest):
    # Run ffmpeg command to convert wav to mp3
    try:
        r = subprocess.run(f"pipx run pytube {data.link} --list", shell=True, check=True)
        # TODO: parse the output and find the highest quality audio itag
        itag = get_itag(r)
        subprocess.run(f"pipx run pytube {data.link} --itag {itag}", shell=True, check=True)
        return {"message": "File downloaded"}
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Error running ffmpeg command")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
