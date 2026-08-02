#==========================================================================================
#                                   Import Statements
#==========================================================================================

import os
import requests

API_URL = "http://localhost:8000"

#==========================================================================================
#                         Sample documents about RAG and embeddings
#==========================================================================================

SAMPLE_DOCS = [

    {
        "id": "doc_001",
        "text": (
            "Retrieval-Augmented Generation improves language model responses by allowing "
            "a system to search external information before producing an answer. Instead "
            "of depending only on knowledge stored inside model parameters, the system "
            "retrieves relevant passages from a connected collection of documents and "
            "uses those passages as additional context. This approach helps reduce "
            "incorrect answers and allows models to work with private or frequently "
            "updated information."
        ),
        "metadata": {"topic": "rag", "source": "overview"}
    },

    {
        "id": "doc_002",
        "text": (
            "A modern search pipeline can improve accuracy by converting both user "
            "questions and stored information into numerical representations. These "
            "representations capture meaning rather than only matching exact words. "
            "When a person asks a short question, the system searches for stored "
            "information with similar concepts and relationships in the vector space."
        ),
        "metadata": {"topic": "semantic_search", "source": "technical"}
    },

    {
        "id": "doc_003",
        "text": (
            "Some retrieval systems first create an imaginary answer passage before "
            "performing a search. The generated passage contains concepts that are "
            "likely to appear in the ideal answer. This longer representation is then "
            "converted into a vector and compared with stored documents, helping "
            "bridge the gap between short user questions and detailed knowledge sources."
        ),
        "metadata": {"topic": "advanced_retrieval", "source": "technical"}
    },

    {
        "id": "doc_004",
        "text": (
            "Vector databases are specialized storage systems designed for searching "
            "high-dimensional numerical representations. Instead of looking for exact "
            "text matches, they compare distances between vectors using techniques "
            "such as cosine similarity. These databases are commonly used in AI "
            "applications that need fast retrieval from large collections of data."
        ),
        "metadata": {"topic": "vector_database", "source": "overview"}
    },

    {
        "id": "doc_005",
        "text": (
            "The quality of information retrieval depends heavily on how documents "
            "are divided before indexing. Large passages may contain useful context "
            "but can include unrelated information. Very small passages may lose "
            "important surrounding details. Overlapping sections are often used so "
            "that important ideas are preserved across multiple segments."
        ),
        "metadata": {"topic": "chunking", "source": "best_practices"}
    },

    {
        "id": "doc_006",
        "text": (
            "A retrieval system can use two different models during searching. The "
            "first model quickly finds possible matches by comparing vector "
            "representations. A second model can then analyze the question and "
            "candidate documents together to decide which results are most relevant. "
            "This improves precision but requires additional computation."
        ),
        "metadata": {"topic": "reranking", "source": "advanced"}
    },

    {
        "id": "doc_007",
        "text": (
            "Traditional keyword-based search methods rely on matching words between "
            "a query and documents. Methods such as BM25 calculate importance based "
            "on word frequency and document statistics. Although effective for many "
            "applications, keyword search may fail when users describe an idea using "
            "different words than the documents."
        ),
        "metadata": {"topic": "bm25", "source": "retrieval"}
    },

    {
        "id": "doc_008",
        "text": (
            "Embedding models learn relationships between pieces of text by mapping "
            "them into numerical spaces. During training, examples with similar "
            "meaning are positioned closer together while unrelated examples are "
            "separated. These learned representations allow machines to compare "
            "concepts even when exact vocabulary is different."
        ),
        "metadata": {"topic": "embeddings", "source": "technical"}
    },

    {
        "id": "doc_009",
        "text": (
            "Query improvement techniques modify a user's original search request "
            "before retrieving information. The system may add related terms, "
            "rewrite the question, or generate additional context. These methods "
            "help when users provide incomplete questions that do not contain enough "
            "information for accurate searching."
        ),
        "metadata": {"topic": "query_expansion", "source": "retrieval"}
    },

    {
        "id": "doc_010",
        "text": (
            "Pinecone is a managed service that stores vector representations and "
            "provides fast similarity search capabilities. Applications can insert "
            "embeddings together with metadata and later retrieve the closest "
            "matching vectors. It is commonly used for building AI applications "
            "that require scalable information retrieval."
        ),
        "metadata": {"topic": "pinecone", "source": "database"}
    },

    {
        "id": "doc_011",
        "text": (
            "Large language models sometimes produce inaccurate information because "
            "they generate responses based on learned patterns rather than checking "
            "external facts. Connecting these models with trusted sources can improve "
            "reliability by providing additional evidence during response generation."
        ),
        "metadata": {"topic": "hallucination", "source": "llm"}
    },

    {
        "id": "doc_012",
        "text": (
            "Transformer models process language using attention mechanisms that allow "
            "the model to consider relationships between words across long sequences. "
            "These architectures power many modern language systems and are capable "
            "of understanding complex patterns in text."
        ),
        "metadata": {"topic": "transformers", "source": "deep_learning"}
    },

    {
        "id": "doc_013",
        "text": (
            "Convolutional neural networks are deep learning models mainly used for "
            "image processing tasks. They detect patterns such as edges, textures, "
            "and shapes through convolution operations. CNN architectures are widely "
            "used in object detection and image classification applications."
        ),
        "metadata": {"topic": "computer_vision", "source": "distractor"}
    },

    {
        "id": "doc_014",
        "text": (
            "Graphics processing units contain many parallel processing cores that "
            "allow them to perform large numbers of mathematical operations "
            "simultaneously. GPUs are frequently used for training neural networks "
            "because machine learning workloads involve massive matrix calculations."
        ),
        "metadata": {"topic": "hardware", "source": "distractor"}
    },

    {
        "id": "doc_015",
        "text": (
            "Reinforcement learning trains agents by allowing them to interact with "
            "an environment and receive rewards or penalties. Over time, the agent "
            "learns strategies that maximize expected rewards. This approach is "
            "different from systems that learn directly from fixed datasets."
        ),
        "metadata": {"topic": "reinforcement_learning", "source": "distractor"}
    },

    {
        "id": "doc_016",
        "text": (
            "Information retrieval systems can improve results by understanding the "
            "intent behind a user's request rather than focusing only on the exact "
            "terms entered. A person may describe a problem using everyday language "
            "while the relevant information may use technical terminology. Systems "
            "that understand concepts can connect these different expressions."
        ),
        "metadata": {"topic": "semantic_matching", "source": "retrieval"}
    },

    {
        "id": "doc_017",
        "text": (
            "A knowledge base allows an artificial intelligence application to access "
            "information outside its original training data. The stored information "
            "can contain company documents, manuals, research papers, or frequently "
            "updated records. Accessing this external source helps applications "
            "provide responses based on specific available information."
        ),
        "metadata": {"topic": "knowledge_base", "source": "rag"}
    },

    {
        "id": "doc_018",
        "text": (
            "Multi-query search improves retrieval by creating several alternative "
            "versions of a user's question. Each rewritten question explores a "
            "different possible interpretation of the original request. Combining "
            "results from multiple searches can increase the chance of finding "
            "useful information."
        ),
        "metadata": {"topic": "multi_query_retrieval", "source": "advanced"}
    },

    {
        "id": "doc_019",
        "text": (
            "Some AI systems compress retrieved information before sending it to a "
            "language model. Instead of providing every retrieved passage, the system "
            "selects the most important sentences and removes unnecessary details. "
            "This helps reduce context size while maintaining important evidence."
        ),
        "metadata": {"topic": "context_compression", "source": "optimization"}
    },

    {
        "id": "doc_020",
        "text": (
            "Approximate nearest neighbor algorithms allow large collections of "
            "vectors to be searched efficiently without comparing every possible "
            "item. These methods trade a small amount of exact accuracy for much "
            "faster search speed, making them useful for applications containing "
            "millions of stored representations."
        ),
        "metadata": {"topic": "ann_search", "source": "technical"}
    },

    {
        "id": "doc_021",
        "text": (
            "Different retrieval methods have different strengths. Statistical "
            "approaches are effective when important words appear directly in the "
            "query, while meaning-based approaches are useful when the same idea is "
            "expressed using different vocabulary. Combining multiple methods can "
            "provide stronger search performance."
        ),
        "metadata": {"topic": "hybrid_search", "source": "retrieval"}
    },

    {
        "id": "doc_022",
        "text": (
            "A language model can improve its response quality when it receives "
            "relevant evidence before generating text. The evidence acts as a source "
            "of guidance that helps the model stay aligned with available facts "
            "instead of relying only on patterns learned during training."
        ),
        "metadata": {"topic": "grounded_generation", "source": "llm"}
    },

    {
        "id": "doc_023",
        "text": (
            "Search evaluation requires measuring whether retrieved results are useful "
            "for answering user questions. Metrics such as precision, recall, and "
            "ranking quality help determine whether a retrieval system returns the "
            "right information and places important results near the top."
        ),
        "metadata": {"topic": "retrieval_evaluation", "source": "research"}
    },

    {
        "id": "doc_024",
        "text": (
            "A document store used by AI applications often contains metadata along "
            "with text content. Metadata can include dates, categories, authors, or "
            "permissions. Filtering with metadata before or during similarity search "
            "allows systems to retrieve more relevant information."
        ),
        "metadata": {"topic": "metadata_filtering", "source": "database"}
    },

    {
        "id": "doc_025",
        "text": (
            "Open-source vector search libraries allow developers to build retrieval "
            "systems without depending on a hosted service. These libraries provide "
            "indexing algorithms, similarity calculations, and tools for searching "
            "large collections of numerical representations."
        ),
        "metadata": {"topic": "faiss", "source": "vector_search"}
    },

    {
        "id": "doc_026",
        "text": (
            "Some applications combine exact matching with meaning-based retrieval. "
            "Exact matching helps locate specific names, numbers, and identifiers, "
            "while semantic retrieval helps discover related ideas. A combined "
            "approach can handle a wider range of user questions."
        ),
        "metadata": {"topic": "hybrid_retrieval", "source": "advanced"}
    },

    {
        "id": "doc_027",
        "text": (
            "Long documents create challenges because only a small portion usually "
            "contains the information needed for a particular question. Systems must "
            "identify relevant sections instead of passing entire documents to a "
            "language model, which improves efficiency and reduces irrelevant context."
        ),
        "metadata": {"topic": "long_context", "source": "optimization"}
    },

    {
        "id": "doc_028",
        "text": (
            "Large language models generate text by predicting likely sequences based "
            "on patterns learned from training examples. Although they can produce "
            "fluent answers, they may confidently generate incorrect details when "
            "they lack reliable information about a specific topic."
        ),
        "metadata": {"topic": "language_models", "source": "background"}
    },

    {
        "id": "doc_029",
        "text": (
            "Attention mechanisms allow neural networks to assign different importance "
            "to parts of an input sequence. This ability helps models capture "
            "relationships between distant words and understand complex language "
            "structures."
        ),
        "metadata": {"topic": "attention", "source": "deep_learning"}
    },

    {
        "id": "doc_030",
        "text": (
            "Generative AI applications often require a balance between response "
            "quality, speed, and cost. Improving retrieval accuracy may require "
            "additional computation, while faster systems may sacrifice some "
            "precision. Production systems optimize these trade-offs depending on "
            "their requirements."
        ),
        "metadata": {"topic": "production_ai", "source": "engineering"}
    }

]


def main():
    print("🚀 Ingesting documents into Pinecone via /ingest endpoint...")
    print(f"   API: {API_URL}")
    print(f"   Documents: {len(SAMPLE_DOCS)}\n")

    response = requests.post(
        f"{API_URL}/ingest",
        json={"documents": SAMPLE_DOCS, "namespace": ""}
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success! Upserted {result['upserted']} documents.")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    main()