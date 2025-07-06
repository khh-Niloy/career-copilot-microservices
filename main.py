from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import fitz  # PyMuPDF
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # allow all for now (you can restrict later)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Career Copilot : PDF Parser Service is running at 9000"}

@app.post("/api/pdf/extract")
async def extract_pdf(pdf: UploadFile = File(...)):

    if pdf.content_type != "application/pdf":
        return {"error": "Only PDFs are accepted"}

    content = await pdf.read()
    doc = fitz.open(stream=content, filetype="pdf")

    full_text = ""
    links = []

    for i, page in enumerate(doc):
        full_text += page.get_text()
        for link in page.get_links():
            if "uri" in link:
                url = link["uri"]
                if "github.com" in url:
                    name = "GitHub"
                elif "linkedin.com" in url:
                    name = "LinkedIn"
                elif "vercel.app" in url or "web.app" in url:
                    name = "Live Site"
                elif "codeforces.com" in url:
                    name = "Codeforces"
                else:
                    name = "Other"

                links.append({"page": i + 1, "name": name, "url": url})

    return JSONResponse(content={"text": full_text, "links": links})
