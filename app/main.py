from fastapi import FastAPI, UploadFile, File, HTTPException
from app import analyzer
from app.database import init_db, insert_logs, delete_file
from app.parser import parse_lines
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


init_db()

app = FastAPI(title="Log File Analyzer")


@app.get("/")
def home():
    return FileResponse("static/index.html")


app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/files")
def get_files():
    return analyzer.list_files()


@app.get("/stats/levels")
def stats_levels(source_file: str | None = None):
    return analyzer.count_by_level(source_file)


@app.get("/stats/top-errors")
def stats_errors():
    return analyzer.top_errors()


@app.get("/stats/errors-per-hour")
def stats_errors_per_hour():
    return analyzer.errors_per_hour()

@app.get("/logs")
def get_logs(level: str | None = None, keyword: str | None = None, limit: int = 50):
    return analyzer.search_logs(level, keyword, limit)

@app.post("/upload")
async def upload_log(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8", errors="replace")

    lines = text.splitlines()
    entries = parse_lines(lines)

    if not entries:
        raise HTTPException(status_code=400, detail="No valid log lines found in this file")

    saved = insert_logs(entries, file.filename)
    return {
        "filename": file.filename,
        "saved": saved,
        "skipped": len(lines) - saved,
    }

@app.delete("/files/{source_file}")
def remove_file(source_file: str):
    deleted = delete_file(source_file)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="File not found")
    return {"source_file": source_file, "deleted": deleted}