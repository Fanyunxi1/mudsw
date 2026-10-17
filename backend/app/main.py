from fastapi import FastAPI, UploadFile, File, HTTPException, Request, status
from app.schemas import URLRequest, URLResponse, CSVResponse
from app.model import URLScannerModel
from app.utils import parse_csv, format_results
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import joblib, io, csv, traceback
# import feature_extraction
# from feature_extraction import colnames

app = FastAPI(title="LinkScanner API")

# 允许前端本地调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = URLScannerModel()
class URLRequest(BaseModel):
    url: str

@app.post("/api/detect_url", response_model=URLResponse)
async def detect_url(request: URLRequest):
    try:
        is_malicious = model.predict(request.url.strip())
        return URLResponse(url=request.url, isMalicious=is_malicious)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error during URL detection"
        )

@app.post("/api/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    print("🔔 /api/upload_csv 被调用")
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")

        content = await file.read()
        urls = parse_csv(content)  # 解析 URL 列
        preds = model.predict_batch(urls)
        results = format_results(urls, preds)  # [{'url': ..., 'isMalicious': True/False}, ...]

        # 写入内存中的 CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['URL', 'Malicious'])  # 表头
        for r in results:
            writer.writerow([r['url'], 'Yes' if r['isMalicious'] else 'No'])
        output.seek(0)

        return StreamingResponse(
            output,
            media_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename=results.csv'}
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Server error during CSV upload")
