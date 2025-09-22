import os
import pandas as pd
import PyPDF2
import docx2txt
from fastapi import UploadFile, HTTPException
from typing import List, Dict, Any, Optional
import tempfile
import shutil

class FileProcessor:
    def __init__(self):
        self.allowed_extensions = {'.csv', '.xlsx', '.xls', '.pdf', '.docx'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB

    async def process_upload(self, file: UploadFile) -> Dict[str, Any]:
        # Validate file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in self.allowed_extensions:
            raise HTTPException(status_code=400, detail=f"File type {file_extension} not allowed")

        # Validate file size
        file.file.seek(0, 2)  # Go to end of file
        file_size = file.file.tell()
        file.file.seek(0)  # Reset file pointer

        if file_size > self.max_file_size:
            raise HTTPException(status_code=400, detail="File too large")

        # Process file based on extension
        try:
            if file_extension == '.csv':
                return await self._process_csv(file)
            elif file_extension in ['.xlsx', '.xls']:
                return await self._process_excel(file)
            elif file_extension == '.pdf':
                return await self._process_pdf(file)
            elif file_extension == '.docx':
                return await self._process_docx(file)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

    async def _process_csv(self, file: UploadFile) -> Dict[str, Any]:
        df = pd.read_csv(file.file)
        return self._dataframe_to_dict(df)

    async def _process_excel(self, file: UploadFile) -> Dict[str, Any]:
        df = pd.read_excel(file.file)
        return self._dataframe_to_dict(df)

    async def _process_pdf(self, file: UploadFile) -> Dict[str, Any]:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        try:
            with open(tmp_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n\n"
            
            # Create a simple dataframe with the extracted text
            data = {"Page": [i+1 for i in range(len(reader.pages))],
                   "Content": [page.extract_text() for page in reader.pages]}
            df = pd.DataFrame(data)
            return self._dataframe_to_dict(df)
        finally:
            os.unlink(tmp_path)

    async def _process_docx(self, file: UploadFile) -> Dict[str, Any]:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        try:
            text = docx2txt.process(tmp_path)
            # Create a simple dataframe with the extracted text
            data = {"Content": [text]}
            df = pd.DataFrame(data)
            return self._dataframe_to_dict(df)
        finally:
            os.unlink(tmp_path)

    def _dataframe_to_dict(self, df: pd.DataFrame) -> Dict[str, Any]:
        # Convert DataFrame to a list of dictionaries
        data = df.where(pd.notnull(df), None).to_dict('records')
        
        # Get column names and types
        columns = [{
            'name': col,
            'type': str(df[col].dtype)
        } for col in df.columns]
        
        # Basic statistics for numeric columns
        stats = {}
        for col in df.select_dtypes(include=['number']).columns:
            stats[col] = {
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'mean': float(df[col].mean()),
                'median': float(df[col].median()),
                'std': float(df[col].std())
            }
        
        return {
            'columns': columns,
            'data': data,
            'stats': stats,
            'total_rows': len(df)
        }
