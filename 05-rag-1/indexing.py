from langchain_community.document_loaders import PyPDFLoader
from dotenv import load_dotenv
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

load_dotenv()

pdf_path = Path(__file__).parent / "nodejs.pdf"

loader = PyPDFLoader(file_path=pdf_path)
docs = loader.load()  # reads the pdf file

# chunking
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=400)

split_docs = text_splitter.split_documents(documents=docs)

# vectore embedding
embedding_model = OpenAIEmbeddings( 
    model="text-embedding-3-large"
)

# Using [embedding_model] create embeddings of [split_docs] and store in DB
vectore_store = QdrantVectorStore.from_documents(
    documents=split_docs,
    url="http://vector-db:6333",
    collection_name="learning_vectors",
    embedding=embedding_model
)

print("Indexing completed")
