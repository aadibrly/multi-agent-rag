from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from app.config import settings

def get_embeddings()-> OpenAIEmbeddings:
    """Return cloud hosted NVIDIA Embeddings vida Openai-compatablitiy Endpoint"""
    embeddings= OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        api_key=settings.NVIDIA_API_KEY,
        base_url="https://integrate.api.nvidia.com/v1"
    )
    return embeddings

def get_vectorstore(bot_id:str="default")-> Chroma:
    """return a Chroma db collection isolation for a specific bot"""
    vectors = Chroma(collection_name=f"bot_{bot_id}",
                     embedding_function=get_embeddings,
                     persist_directory=settings.CHROMA_PERSIST_DIR)
    return vectors

def injest_file(file_path:str, bot_id:str = 'default')-> int:
    """Load a PDF, DOCX, or TXT file, split into chunks, and store in ChromaDB."""

    path = Path(file_path) #we can acces path suffex prefix name etcc when convert to a Path object
    ext = path.suffix.lower()

    if ext == '.pdf':
        loader = PyPDFLoader(str(path))
    if ext == '.docx':
        loader = Docx2txtLoader(str(path))
    if ext in {".txt", ".md"}:
        loader = TextLoader(str(path), encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    #loading the documents
    raw_docs = loader.load()
    #splitting the docs
    splitter =  RecursiveCharacterTextSplitter(chunk_size = 800, chunk_overlap = 150)

    chunks = splitter.split_documents(raw_docs)

    #adding extras to metadata
    for i, chunk in enumerate(chunks):
        chunk.metadata['source'] = path.name
        chunk.metadata['bot_id'] = bot_id
        chunk.metadata['chunk_id'] = i

    vector_store = get_vectorstore(bot_id)
    vector_store.add_documents(chunks)
    return len(chunks)
     