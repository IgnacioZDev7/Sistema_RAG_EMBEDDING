# Aplicación RAG con Streamlit
import streamlit as st
import os
from pathlib import Path

# Imports de LangChain
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain

# Configuración de la página
st.set_page_config(
    page_title="RAG con Ollama",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🤖 Sistema RAG Local con Ollama")
st.markdown("---")

# Inicializar el estado de la sesión
if "messages" not in st.session_state:
    st.session_state.messages = []
if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = None
if "db_loaded" not in st.session_state:
    st.session_state.db_loaded = False

# Sidebar para configuración
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Verificar si la base de datos existe
    db_path = "./local_knowledge_db"
    db_exists = os.path.exists(db_path) and os.path.exists(f"{db_path}/chroma.sqlite3")
    
    if db_exists:
        st.success("✅ Base de datos cargada")
        st.session_state.db_loaded = True
    else:
        st.warning("⚠️ Base de datos no encontrada")
        st.info("Carga un documento PDF para crear la base de datos")
    
    st.markdown("---")
    
    # Cargar nuevo documento
    st.subheader("📄 Cargar Documento")
    uploaded_file = st.file_uploader(
        "Sube un archivo PDF",
        type=["pdf"],
        help="Sube un PDF para procesarlo y crear la base de conocimientos"
    )
    
    if uploaded_file is not None:
        if st.button("🔄 Procesar Documento", type="primary"):
            with st.spinner("Procesando documento..."):
                # Guardar el archivo temporalmente
                temp_path = f"./temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                try:
                    # Procesar el documento
                    ingest_document(temp_path)
                    
                    # Limpiar archivo temporal
                    os.remove(temp_path)
                    
                    st.success("✅ Documento procesado correctamente")
                    st.session_state.db_loaded = True
                    st.session_state.rag_chain = None  # Resetear la cadena
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al procesar: {str(e)}")
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
    
    st.markdown("---")
    
    # Configuración del modelo
    st.subheader("🧠 Configuración del Modelo")
    model_name = st.selectbox(
        "Modelo de Ollama",
        ["llama3.2", "llama3.1", "llama3", "mistral", "neural-chat"],
        index=0,
        help="Selecciona el modelo de Ollama a usar"
    )
    
    temperature = st.slider(
        "Temperatura",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Controla la creatividad de las respuestas"
    )
    
    st.session_state.model_name = model_name
    st.session_state.temperature = temperature

# Función para ingerir documento
def ingest_document(pdf_path):
    """Procesa un PDF y crea la base de datos vectorial"""
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1024,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(pages)
    
    embedding = FastEmbedEmbeddings()
    
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
        persist_directory="./local_knowledge_db",
    )
    
    return vector_store

# Función para crear la cadena RAG
@st.cache_resource
def create_local_rag_chain(model_name="llama3.2", temperature=0.7):
    """Crea la cadena RAG para interactuar con el documento"""
    local_llm = ChatOllama(
        model=model_name,
        temperature=temperature,
    )
    
    prompt_template = PromptTemplate.from_template(
        """
        Eres un asistente inteligente y experto.
        Responde basándote en el contexto proporcionado de los documentos.
        
        Si no encuentras la información en el contexto, dilo claramente.
        Siempre menciona en qué parte del documento viene tu respuesta.
        
        Contexto de los documentos:
        {context}
        
        Pregunta del usuario: 
        {input}
        
        Respuesta detallada:
        """
    )
    
    embedding = FastEmbedEmbeddings()
    vector_store = Chroma(
        persist_directory="./local_knowledge_db",
        embedding_function=embedding
    )
    
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 3, "score_threshold": 0.5},
    )
    
    document_chain = create_stuff_documents_chain(local_llm, prompt_template)
    rag_chain = create_retrieval_chain(retriever, document_chain)
    
    return rag_chain

# Función para obtener respuesta
def get_response(question):
    """Obtiene la respuesta del sistema RAG"""
    if st.session_state.rag_chain is None:
        model_name = st.session_state.get("model_name", "llama3.2")
        temperature = st.session_state.get("temperature", 0.7)
        st.session_state.rag_chain = create_local_rag_chain(model_name, temperature)
    
    result = st.session_state.rag_chain.invoke({"input": question})
    return result

# Área principal de chat
if not st.session_state.db_loaded:
    st.info("👆 Por favor, carga un documento PDF desde la barra lateral para comenzar")
else:
    # Inicializar la cadena RAG si no está inicializada
    if st.session_state.rag_chain is None:
        with st.spinner("🔄 Inicializando sistema RAG..."):
            model_name = st.session_state.get("model_name", "llama3.2")
            temperature = st.session_state.get("temperature", 0.7)
            st.session_state.rag_chain = create_local_rag_chain(model_name, temperature)
    
    # Mostrar historial de mensajes
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message:
                with st.expander("📚 Fuentes consultadas"):
                    for i, doc in enumerate(message["sources"], 1):
                        page = doc.metadata.get('page', '?')
                        st.write(f"{i}. Página {page} del documento")
    
    # Input del usuario
    if prompt := st.chat_input("Escribe tu pregunta sobre el documento..."):
        # Agregar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Obtener respuesta
        with st.chat_message("assistant"):
            with st.spinner("🤔 Pensando..."):
                try:
                    result = get_response(prompt)
                    answer = result['answer']
                    sources = result.get('context', [])
                    
                    st.markdown(answer)
                    
                    # Mostrar fuentes
                    if sources:
                        with st.expander("📚 Fuentes consultadas"):
                            for i, doc in enumerate(sources, 1):
                                page = doc.metadata.get('page', '?')
                                st.write(f"{i}. Página {page} del documento")
                    
                    # Guardar en historial
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
    
    # Botón para limpiar historial
    if st.session_state.messages:
        if st.button("🗑️ Limpiar conversación"):
            st.session_state.messages = []
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Powered by Ollama + LangChain + Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)

