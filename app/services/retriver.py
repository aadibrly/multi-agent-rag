import requests
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi #scoring algorithem
from app.config import settings
from app.services.ingestion import get_vectorstore

def rerak_with_nvidia(query:str, docs: list[Document], top_n: int=4)-> list[Document]:
    """Use NVIDIA NIM cloud reranker API to score query-document pairs form the below function."""

    if not docs:
        return []

    url = ""
    header = {
        "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
        "Content-Type": "application/json",
          } #check nvidia build page for header if this broken arhh and this shit is passed as teh metadata on http request

    payload = {
        "model": settings.RERANKER_MODEL,
        "query": {"text": query},
        "passages": [{"text": d.page_content} for d in docs],
        } # if i wonder again wtf is this i got this from the same build page this shit choose the model

    try:
        #so if this try aint work we will retuns the top_n docs whcih get from the below function
        response = requests.post(url, headers=header, json=payload, timeout=10)
        response.raise_for_status() #if the response is not 200 then again the one will execute

        ranking = response.json().get("response", [])
                #None for me : if i wonder again how the response will looks like thein this is it 
                # responses =  {
                # "rankings": [
                #     {
                #     "index": 2,
                #     "logit": 4.828125
                #     },
                #     {
                #     "index": 0,
                #     "logit": 1.1044921875
                #     },.............
        sorted_index = [r['index'] for r in ranking[:top_n]]   
        return [docs[i] for i in sorted_index]
    
    except Exception:
        return docs[:top_n]

def hybrid_retriver(query: str, bot_id: str='default', top_k: int=4)-> list[dict]:
    vectorizer = get_vectorstore(bot_id)

    #doing a similarity search (no fancy words)
    dense_doc = vectorizer.similarity_search(query, k=10)

    #BM25 search 
    ## getting stored vectors
    stored = vectorizer.get(include=("documents", "metadatas"))
    all_text = stored.get("documents") or [] 
    all_metas = stored.get("metadatas") or [] 

    if not all_text:
        return []

    tokenised_corpus = [text.lower().split() for text in all_text]       
                    # tokenized_corpus = [
                    # ["the", "laptop", "has", "32gb", "ddr5", "ram"],   Chunk 0's tokens
                    # ["battery", "backup", "is", "8", "hours"],         Chunk 1's tokens
                    # ["rtx", "3050", "gpu", "has", "4gb", "vram"]       Chunk 2's tokens
                    # ] this is how this thing looks like after all_text get tokenized

    bm25_obj = BM25Okapi(tokenised_corpus)
    #getting scores with the tokenised and query
    query_clan = query.lower().split()
    score = bm25_obj.get_scores(query_clan)

    iterable = range(len(score)) 
    top_bm25 = sorted(iterable, key= lambda i: score[i], reverse=True)

    #converting the sorted datas into Document object also removes the ones with score less than 0
    sparese_docs = [
        Document(page_content=all_text[i], metadata=all_metas[i])
                     for i in top_bm25 if score[i] > 0
                     ]

    # reciprocal function

    rrf_scores: dict[str, float] = {}
    doc_map: dict[str, Document] = {}

    for rank, doc in enumerate(dense_doc):
        key = doc.page_content
        doc_map[key] = doc 
        rrf_scores[key] = rrf_scores.get(key, 0.0) + 1.0 / (60 + rank + 1)

    for rank, doc in enumerate(sparese_docs):
        key = doc.page_content
        doc_map[key] = doc
        rrf_scores[key] = rrf_scores.get(key, 0.0) + 1.0 / (60 + rank + 1)

    funsed_docs = [
        doc_map[k] for k in sorted(rrf_scores, key= rrf_scores.get, reverse=True)[:10] 
    ]

    #cloud cross encoder reranking
    final_docs = rerak_with_nvidia(query, funsed_docs, top_n=top_k)

    return [
        {
            "content" : d.page_content,
            "source" : d.metadata.get("source", "unknown"),
            "page": d.metadata.get("page", 0),

        } 
        
        for d in final_docs
    ]


