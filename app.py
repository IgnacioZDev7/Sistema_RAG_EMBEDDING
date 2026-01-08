# Imports actualizados para LangChain 1.x
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain

# primer paso
# procesamiento del pdf y contrsucción de la base vectorial
def ingest_document(pdf_path):
    print("Cargando documento...")

    loader = PyPDFLoader(pdf_path)
    pages = loader.load_and_split()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1024,
        chunk_overlap = 100,
        length_function = len,
        add_start_index = True,
    )
    chunks = text_splitter.split_documents(pages)

    print(f"Convertimos {len(pages)} páginas en {len(chunks)} pedazos inteligentes")

    embedding = FastEmbedEmbeddings()

    vector_store = Chroma.from_documents(
        documents = chunks,
        embedding = embedding,
        persist_directory = "./local_knowledge_db",
    )

    print("La IA local ya conoce el documento")
    return vector_store


# segundo paso
# crear la cadena RAG para interactuar con el documento

def create_local_rag_chain():
    local_llm = ChatOllama(
        model = "llama3.2",
        temperature = 0.7,
    )

    prompt_template = PromptTemplate.from_template(
        """
        Eres un asistente inteligente y experto.
        Responde basándote en el contexto proporcionado de los documentos.


        Si no encuentras la información en el contexto, dilo claramente.
        Siempre menciona en que parte del documento viene tu respuesta.

        Contexto de los documentos:
        {context}

        Pregunta del usuario: 
        {input}

        Respuesta detallada:
        """
    )

    embedding = FastEmbedEmbeddings()
    vector_store = Chroma(
        persist_directory = "./local_knowledge_db",
        embedding_function = embedding
    )

    retriever = vector_store.as_retriever(
        search_type = "similarity_score_threshold",
        search_kwargs = {"k":3, "score_threshold": 0.5},
    )

    document_chain = create_stuff_documents_chain(local_llm, prompt_template)
    rag_chain = create_retrieval_chain(retriever, document_chain)

    return rag_chain

# tercer paso
# interactuar con la IA local y el documento cargado

def chat_with_document(question):
    chain = create_local_rag_chain()

    print(f"\n Pregunta sobre el documento: {question}")
    print("Buscando en la base de conocimientos...")

    result = chain.invoke({"input": question})

    print(f"\n Respuesta: \n {result['answer']}")
    print("\n Fuentes consultadas:")

    for i, doc in enumerate(result['context'], 1):
        print(f" {i}. Página {doc.metadata.get('page', '?')} del documento")

    return result

# cuarto paso
# sistema completo con interacción

def main():
    print("Iniciando el sistema RAG local...")

    #ruta del documento (modificable)
    pdf_path = "T-4223.pdf"
    ingest_document(pdf_path)

    print("\n Ya puedes conversar y preguntar sobre tu documento")
    print("Escribe 'salir' para finalizar la conversación")

    while True:
        question = input("\n Pregunta: ")
        if question.lower() == "salir":
            break
        chat_with_document(question)
    print("Hasta luego!")

# ejecutar el sistema
if __name__ == "__main__":
    main()