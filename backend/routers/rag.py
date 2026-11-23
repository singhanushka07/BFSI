import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db, User, UploadedDocument
from auth.jwt_handler import get_current_user
from rag.pipeline import ingest_pdf, query_collection, list_collections, delete_collection
from pydantic import BaseModel

router = APIRouter(prefix="/api/rag", tags=["RAG Pipeline"])

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class QueryRequest(BaseModel):
    collection: str
    query: str
    n_results: int = 5


@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    company: str = Form("Unknown"),
    doc_type: str = Form("annual_report"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    safe_name = f"{current_user.id}_{company.replace(' ', '_')}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    collection_name = f"user_{current_user.id}_{company.replace(' ', '_').lower()}"

    try:
        chunks_added = ingest_pdf(
            file_path,
            collection_name,
            metadata={"company": company, "doc_type": doc_type, "user_id": str(current_user.id)},
        )
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"PDF ingestion failed: {str(e)}")

    doc = UploadedDocument(
        user_id=current_user.id,
        filename=file.filename,
        company=company,
        doc_type=doc_type,
        chroma_collection=collection_name,
        pages=chunks_added,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "message": "PDF uploaded and indexed successfully",
        "collection": collection_name,
        "chunks_indexed": chunks_added,
        "doc_id": doc.id,
    }


@router.post("/query")
def query_rag(request: QueryRequest, current_user: User = Depends(get_current_user)):
    results = query_collection(request.collection, request.query, request.n_results)
    return {
        "query": request.query,
        "collection": request.collection,
        "results": results,
        "count": len(results),
    }


@router.get("/documents")
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    docs = db.query(UploadedDocument).filter(UploadedDocument.user_id == current_user.id).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "company": d.company,
            "doc_type": d.doc_type,
            "collection": d.chroma_collection,
            "pages": d.pages,
            "uploaded_at": d.uploaded_at.isoformat(),
        }
        for d in docs
    ]


@router.delete("/documents/{doc_id}")
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = db.query(UploadedDocument).filter(
        UploadedDocument.id == doc_id, UploadedDocument.user_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    delete_collection(doc.chroma_collection)
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted"}
