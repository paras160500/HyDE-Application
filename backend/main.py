#==========================================================================================
#                                   Import Statements
#==========================================================================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config import GROQ_MODEL, EMBEDDING_MODEL, PINECONE_INDEX,EMBEDDING_MODEL
from helper import get_index,embed_text,pinecone_search,generate_final_answer,generate_hypothetical_doc
from schemas import QueryRequest,CompareRequest,IngestRequest

#==========================================================================================
#                                      Init Statements
#==========================================================================================

app = FastAPI(
    title = "HyDE RAG API",
    description="Compare Standard vs HyDE Retrival Side-by-side",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

#==========================================================================================
#                                       Route Statements
#==========================================================================================

@app.get("/")
def root():
    return {
        "message" : "HyDe RAG API is running ✔️",
        "model" : GROQ_MODEL,
        "embedding" : EMBEDDING_MODEL,
        "endpoints" : {
            "POST /query/standard" : "Standard RAG - embed raw query",
            "POST /query/hyde" : "HyDE RAG - embed hypothetical doc",
            "POST /query/compare" : "Side-by-side comparision",
            "POST /ingest" : "Upsert documents into Pinecone",
            "Get /health" : "Health check "
        }
    }

@app.get("/health")
def health():
    try:
        status = get_index().describe_index_stats()
        return {
            "status" : "ok",
            "pinecone_index" : PINECONE_INDEX,
            "total_vectors" : status.get("total_vector_count" , 0),
            "embedding_model" : EMBEDDING_MODEL,
            "groq_model" : GROQ_MODEL
        }
    except Exception as e:
        raise HTTPException(status_code=503 , detail=str(e))


@app.post("/query/standard")
def standard_query(req : QueryRequest):
    """
        Standard RAG:
            1. Embed the raw user query
            2. Search Pinecone
            3. Generate answer 
    """
    query_vector = embed_text(req.query)
    docs = pinecone_search(query_vector , req.top_k , req.namespace)
    answer = generate_final_answer(req.query , docs)

    return {
        "method" : "standard",
        "query" : req.query,
        "retrieved_docs" : docs,
        "answer" : answer
    }


@app.post("/query/hyde")
def hyde_query(req : QueryRequest):
    """
        HyDE RAG:
            1. Grow generated a hypothetical document answer
            2. Embed that hypothetical doc(not the raw text query)
            3. Search Pinecone with richer embedding
            4. Generate final answer from real retrieved docs.
    """
    hypothetical_doc = generate_hypothetical_doc(req.query)
    hyde_vector = embed_text(hypothetical_doc)
    docs = pinecone_search(hyde_vector , req.top_k , req.namespace)
    answer = generate_final_answer(req.query , docs)

    return {
        "method" : "hyde",
        "query" : req.query,
        "hypothetical_doc" : hypothetical_doc,
        "retrieved_docs" : docs,
        "answer" : answer 
    }


@app.post("/query/compare")
def compare_query(req : CompareRequest):
    """
        Side by side comparision of Standard vs HyDE.
        The analysis.unique_to_hyde field shows that HyDE found that standard missed.
    """
    # Standard
    query_vector = embed_text(req.query)
    standard_docs = pinecone_search(query_vector , req.top_k , req.namespace)
    standard_anser = generate_final_answer(req.query , standard_docs)

    # HyDe
    hypothetical_doc = generate_hypothetical_doc(req.query)
    hyde_vector = embed_text(hypothetical_doc)
    hyde_docs = pinecone_search(hyde_vector , req.top_k , req.namespace)
    hyde_answer = generate_final_answer(req.query , hyde_docs)

    # Overlap
    std_ids = {d['id'] for d in standard_docs}
    hyde_ids = {d['id'] for d in hyde_docs}

    return {
        "query" : req.query,
        "standard" : {
            "retrieved_docs" : standard_docs,
            "answer" : standard_anser
        },
        "hyde" : {
            "hypothetical_doc" : hypothetical_doc,
            "retrieved_docs" : hyde_docs,
            "answer" : hyde_answer
        },
        "analysis" : {
            "overlap_count" : len(std_ids & hyde_ids),
            "overlapping_doc_ids" : list(std_ids & hyde_ids),
            "unique_to_standard": list(std_ids - hyde_ids),
            "unique_to_hyde" : list(hyde_ids - std_ids),                  # Main key insight
            "total_docs_compared" : req.top_k
        }
    }


@app.post("/ingest")
def ingest_documents(req: IngestRequest):
    """
        Embed and upsert the document into Pinecone.
        Payload : {"documents" : [{"id" : "..." , "text" : "..." , "metadata" : {...} }]}
    """
    if not req.documents:
        raise HTTPException(status_code=400 , detail="No documents provided.")

    vectors = [] 
    for doc in req.documents:
        if "id" not in doc or "text" not in doc:
            raise HTTPException(status_code=400 , detail="Each doc needs 'id' and 'text'")
        meta = {**doc.get("metadata" , {}) , "text" : doc['text']}
        vectors.append({
            "id" : doc['id'],
            "values" : embed_text(doc['text']),
            "metadata" : meta 
        })

    batch = 100 
    for i in range( 0 , len(vectors) , batch):
        get_index().upsert(vectors=vectors[i : i+batch] , namespace=req.namespace)

    return {
        "status" : "success",
        "upserted" : len(vectors),
        "namespace" : req.namespace or "default"
    }


