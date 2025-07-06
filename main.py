from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import fitz  # PyMuPDF

app = FastAPI()

@app.get("/")
def root():
    return {"message": "PDF Parser Service is running"}

@app.post("/extract")
async def extract_pdf(pdf: UploadFile = File(...)):
    content = await pdf.read()
    doc = fitz.open(stream=content, filetype="pdf")

    full_text = ""
    links = []

    for i, page in enumerate(doc):
        full_text += page.get_text()
        for link in page.get_links():
            if "uri" in link:
                url = link["uri"]
                # Simple naming heuristic example:
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
