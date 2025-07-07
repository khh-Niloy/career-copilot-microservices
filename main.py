from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import fitz  # PyMuPDF
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urlparse


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],  # allow all for now (you can restrict later)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Career Copilot : PDF Parser Service is running at 9000"}

def extract_name_from_url(url: str) -> str:
    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")  # linkedin.com
    domain_name = domain.split(".")[0]  # linkedin, github, etc.

    # GitHub repo or fallback
    if "github.com" in domain:
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) >= 2:
            return f"{path_parts[-1]} GitHub"
        return "GitHub"

    # Hosted site (vercel / firebase)
    elif "vercel.app" in domain or "web.app" in domain:
        subdomain = domain.split(".")[0]
        return f"{subdomain} Live Site"

    # Other: generic platform name
    return domain_name.capitalize()

@app.post("/api/pdf/extract")
async def extract_pdf(pdf: UploadFile = File(...)):
    if pdf.content_type != "application/pdf":
        return {"error": "Only PDFs are accepted"}

    content = await pdf.read()
    doc = fitz.open(stream=content, filetype="pdf")

    full_text = ""
    all_links = []

    for page in doc:
        full_text += page.get_text()
        for link in page.get_links():
            if "uri" in link:
                all_links.append(link["uri"])

    # Remove duplicates
    unique_links = list(set(all_links))

    # Clean and label
    extracted_links = []
    for url in unique_links:
        name = extract_name_from_url(url)
        extracted_links.append({"name": name, "url": url})

    return JSONResponse(content={"text": full_text, "links": extracted_links})