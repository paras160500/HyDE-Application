#==========================================================================================
#                                   Import Statements
#==========================================================================================
from config import get_embedder,GROQ_MODEL,get_groq,get_index

#==========================================================================================
#                                   Logic Statements
#==========================================================================================

def embed_text(text : str) -> list[float]:
    """
        Embedding text using openai embedding model
        Args:
            text(str) : Text need to convert into embeddings 
        Returns:
            list[float] : That is embeddings
    """
    return get_embedder().embed_query(text)


def generate_hypothetical_doc(query : str) -> str:
    """
        First ask Groq to write a hypothetical document-style passage that
        would answer the query. Then its embeddings will align with real doc.
    """
    system_prompt = (
        "You are an expert in NLP,machine learning and REtrieval-Augmented Generation(RAG) Systems." 
        "Given a user question about AI/ML topics, write a detailed factual passage.(3-5 sentences)"
        "that directly answer the question as if extracted from a technical NLP research paper or documentation."
        "Write in third-person encyclopedic style.Do not say 'I' or 'Here is'."
        "Note: 'HyDE' referes tp Hypothetical Document Embedding, a RAG retrieval technique-"
        "not the Jekyll static site generator."
    )

    response = get_groq().chat.completions.create(
        model = GROQ_MODEL,
        messages = [
            {"role" : "system" , "content" : system_prompt},
            {"role" : "user" , "content" : query}
        ],
        max_tokens=250,
        temperature=0.3 
    )
    return response.choices[0].message.content.strip()


def pinecone_search(vector : list[float] , top_k : int , namespace : str) -> list[dict]:
    """
        Similarity search in Pinecone.
        Args:
            vector(list[float]) : Vector which need to be search in the database 
            top_k(int) : How many results we want from the pinecone 
            namespace(str) : Name of the namespace 
        Returns:
            list[dict] : Give the list of the dict having the retrivel context 
    """
    results = get_index().query(
        vector = vector ,
        top_k=5,
        include_metadata=True,
        namespace=namespace
    )

    return [
        {
            "id" : m["id"],
            "score" : round(m['score'] , 4),
            "text" : m['metadata'].get("text" , ""),
            "metadata" : {k : v for k, v in m['metadata'].items() if k!= "text"}
        }
        for m in results['matches']
    ]


def generate_final_answer(query : str , docs : list[dict]) -> str:
    """
        RAG Answer generation - uses retrived docs as context.
    """
    context = "\n\n".join(f"[Doc {i+1}] {d['text']}" for i , d in enumerate(docs))
    response = get_groq().chat.completions.create(
        model = GROQ_MODEL,
        messages=[
            {
                "role" : "system" ,
                "content" : (
                    "You are a helpful assistant.Answer the question using ONLY"
                    "the provided context documents. Be concise and accrate."
                )
            },
            {
                "role" : "user" , "content" : f"Context : \n{context}\n\nQuestion : {query}"
            }
        ],
        max_tokens=400,
        temperature=0.2 
    )
    return response.choices[0].message.content.strip()