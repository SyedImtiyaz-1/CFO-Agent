from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import os
from app.utils.file_processor import FileProcessor
from fastapi.responses import JSONResponse

router = APIRouter()
file_processor = FileProcessor()

@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    results = []
    for file in files:
        try:
            result = await file_processor.process_upload(file)
            results.append({
                "filename": file.filename,
                "status": "processed",
                "data": result
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "message": f"Processed {len([r for r in results if r['status'] == 'processed'])} files successfully",
        "results": results
    }

@router.post("/analyze")
async def analyze_data(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    processed_data = []
    for file in files:
        try:
            result = await file_processor.process_upload(file)
            processed_data.append({
                "filename": file.filename,
                "data": result
            })
        except Exception as e:
            continue  # Skip files that can't be processed
    
    if not processed_data:
        raise HTTPException(status_code=400, detail="Could not process any of the provided files")
    
    # Combine data from all files (simple concatenation for demonstration)
    combined_data = {
        "columns": processed_data[0]["data"]["columns"],
        "data": [],
        "stats": {}
    }
    
    for item in processed_data:
        combined_data["data"].extend(item["data"])
        # Combine statistics (simple merge for demonstration)
        for col, stats in item["data"].get("stats", {}).items():
            if col not in combined_data["stats"]:
                combined_data["stats"][col] = stats
    
    return {
        "message": f"Analyzed data from {len(processed_data)} files",
        "total_rows": len(combined_data["data"]),
        "columns": combined_data["columns"],
        "stats": combined_data["stats"],
        "data": combined_data["data"]
    }
