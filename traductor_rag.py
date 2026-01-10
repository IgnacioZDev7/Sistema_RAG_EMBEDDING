# Traductor Médico RAG - Español, Aymara y Quechua
import streamlit as st
import os
import csv
import json
import re
from pathlib import Path
from langchain_core.documents import Document

# Imports de LangChain
from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain

# Configuración de la página
st.set_page_config(
    page_title="Traductor Médico RAG",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🌐 Traductor Médico RAG")
st.markdown("**Traducción entre Español, Aymara y Quechua usando RAG**")
st.markdown("---")

# Inicializar el estado de la sesión
if "vector_store_loaded" not in st.session_state:
    st.session_state.vector_store_loaded = False
if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = None
if "traducciones" not in st.session_state:
    st.session_state.traducciones = {}

# Función para cargar CSV y convertirlo en documentos
def load_csv_as_documents(csv_path):
    """Carga el CSV de traducciones y lo convierte en documentos de LangChain"""
    documents = []
    traducciones_dict = {}
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig maneja el BOM automáticamente
            # Leer CSV con delimitador punto y coma
            reader = csv.DictReader(f, delimiter=';')
            
            for row in reader:
                # Obtener valores (manejar BOM si existe)
                id_frase = row.get('id', row.get('\ufeffid', '')).strip()  # Manejar BOM
                categoria = row.get('categoria', '').strip()
                español = row.get('español', '').strip()
                aymara = row.get('aymara', '').strip()
                quechua = row.get('quechua', '').strip()
                
                # Saltar filas vacías
                if not id_frase or not español:
                    continue
                
                # Guardar en diccionario para acceso rápido
                traducciones_dict[id_frase] = {
                    'id': id_frase,
                    'categoria': categoria,
                    'español': español,
                    'aymara': aymara,
                    'quechua': quechua
                }
                
                # Crear documento con formato optimizado para que el modelo vea claramente el ID
                # El formato debe ser muy claro para que el modelo pueda extraer el ID fácilmente
                contenido = f"ID:{id_frase}\nCategoría: {categoria}\nEspañol: {español}\nAymara: {aymara}\nQuechua: {quechua}"
                
                doc = Document(
                    page_content=contenido,
                    metadata={
                        'id': id_frase,
                        'categoria': categoria,
                        'español': español,
                        'aymara': aymara,
                        'quechua': quechua
                    }
                )
                documents.append(doc)
        
        # IMPORTANTE: Asignar el diccionario al session_state ANTES de retornar
        st.session_state.traducciones = traducciones_dict
        
        # Verificar que se cargó correctamente
        if not st.session_state.traducciones:
            raise ValueError("El diccionario está vacío después de cargar el CSV")
        
        return documents
    
    except Exception as e:
        st.error(f"Error al cargar CSV: {str(e)}")
        st.exception(e)
        # Asegurarse de que el diccionario esté vacío si hay error
        st.session_state.traducciones = {}
        return []

# Función para ingerir el CSV y crear la base vectorial
def ingest_csv(csv_path):
    """Procesa el CSV y crea la base de datos vectorial"""
    with st.spinner("Cargando traducciones desde CSV..."):
        documents = load_csv_as_documents(csv_path)
        
        if not documents:
            st.error("No se pudieron cargar documentos del CSV")
            return None
        
        st.info(f"✅ Cargadas {len(documents)} frases médicas")
        
        # Crear embeddings
        embedding = FastEmbedEmbeddings()
        
        # Crear vector store
        vector_store = Chroma.from_documents(
            documents=documents,
            embedding=embedding,
            persist_directory="./traducciones_db",
        )
        
        return vector_store

# Función para cargar el prompt desde archivo
def load_prompt_template(prompt_path):
    """Carga el template del prompt desde un archivo"""
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_text = f.read()
        return prompt_text
    except Exception as e:
        st.error(f"Error al cargar prompt: {str(e)}")
        return None

# Función para crear la cadena RAG de traducción
@st.cache_resource
def create_translation_rag_chain(model_name="llama3.2", temperature=0.3):
    """Crea la cadena RAG para traducción médica - Lógica simple como app.py"""
    local_llm = ChatOllama(
        model=model_name,
        temperature=temperature,  # Baja temperatura para respuestas más precisas
    )
    
    # Cargar prompt desde archivo
    prompt_path = "./prompt.txt"
    prompt_template_text = load_prompt_template(prompt_path)
    
    if not prompt_template_text:
        st.error("No se pudo cargar el prompt.txt")
        return None
    
    # Adaptar el prompt para LangChain:
    # Reemplazar {query} por {input} (LangChain usa {input})
    # Mantener {context} como está
    prompt_template_text = prompt_template_text.replace('{query}', '{input}')
    
    # Crear template - LangChain usa {input} y {context} por defecto
    prompt_template = PromptTemplate.from_template(prompt_template_text)
    
    # Cargar vector store
    embedding = FastEmbedEmbeddings()
    vector_store = Chroma(
        persist_directory="./traducciones_db",
        embedding_function=embedding
    )
    
    # Crear retriever - threshold más bajo para encontrar más coincidencias
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 10, "score_threshold": 0.1},  # Más documentos y threshold más bajo
    )
    
    # Crear cadena RAG - igual que app.py
    document_chain = create_stuff_documents_chain(local_llm, prompt_template)
    rag_chain = create_retrieval_chain(retriever, document_chain)
    
    return rag_chain

# Función para extraer ID de la respuesta del modelo
def extraer_id_respuesta(respuesta):
    """Extrae el ID de la respuesta del modelo que viene en formato ID:<numero> o ID:NONE"""
    respuesta_limpia = respuesta.strip()
    
    # Buscar patrón ID:<numero> o ID:NONE
    patron = r'ID:\s*(\d+|NONE)'
    match = re.search(patron, respuesta_limpia, re.IGNORECASE)
    
    if match:
        id_str = match.group(1).strip()
        if id_str.upper() == 'NONE':
            return None
        try:
            return str(id_str)  # Devolver como string para buscar en el dict
        except:
            return None
    
    # Si no encuentra el patrón, intentar buscar solo números
    numeros = re.findall(r'\d+', respuesta_limpia)
    if numeros:
        return str(numeros[0])  # Devolver el primer número encontrado
    
    return None

# Función para traducir usando RAG - Lógica simple como app.py
def translate_with_rag(query, direction, lang):
    """Traduce una frase usando RAG - Lógica simple"""
    if st.session_state.rag_chain is None:
        model_name = st.session_state.get("model_name", "llama3.2")
        temperature = st.session_state.get("temperature", 0.3)
        st.session_state.rag_chain = create_translation_rag_chain(model_name, temperature)
    
    # Invocar la cadena RAG con la query del usuario - igual que app.py
    result = st.session_state.rag_chain.invoke({
        "input": query
    })
    
    return result

# Cargar CSV automáticamente al inicio (igual que app.py carga el PDF)
# Ruta del CSV (equivalente a pdf_path en app.py)
csv_path = "./traducciones.csv"
db_path = "./traducciones_db"

# Verificar si la BD existe
db_exists = os.path.exists(db_path) and os.path.exists(f"{db_path}/chroma.sqlite3")

# Si el CSV existe, cargarlo siempre (igual que app.py siempre carga el PDF)
if os.path.exists(csv_path):
    # Cargar el diccionario del CSV (siempre, para tener acceso rápido)
    if not st.session_state.traducciones:
        try:
            documents = load_csv_as_documents(csv_path)
            if st.session_state.traducciones:
                st.success(f"✅ Diccionario cargado: {len(st.session_state.traducciones)} frases")
            else:
                st.error("❌ Error: El diccionario no se cargó correctamente")
        except Exception as e:
            st.error(f"❌ Error al cargar diccionario: {str(e)}")
            st.exception(e)
    
    # Si la BD no existe, crearla (igual que app.py crea la BD del PDF)
    if not db_exists:
        with st.spinner("🔄 Cargando traducciones y creando base de datos..."):
            try:
                ingest_csv(csv_path)
                st.session_state.vector_store_loaded = True
            except Exception as e:
                st.error(f"❌ Error al crear base de datos: {str(e)}")
                st.exception(e)
    else:
        # La BD ya existe, solo marcar como cargada
        st.session_state.vector_store_loaded = True
else:
    st.warning("⚠️ No se encontró traducciones.csv")

# Sidebar para configuración
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Verificar si la base de datos existe
    db_path = "./traducciones_db"
    db_exists = os.path.exists(db_path) and os.path.exists(f"{db_path}/chroma.sqlite3")
    
    if db_exists:
        st.success("✅ Base de datos cargada")
        st.session_state.vector_store_loaded = True
    else:
        st.warning("⚠️ Base de datos no encontrada")
        st.info("Carga el CSV de traducciones para crear la base de datos")
    
    st.markdown("---")
    
    # Cargar CSV
    st.subheader("📄 Cargar Traducciones")
    csv_file = st.file_uploader(
        "Sube el archivo CSV de traducciones",
        type=["csv"],
        help="Sube el CSV con las traducciones médicas"
    )
    
    if csv_file is not None:
        if st.button("🔄 Procesar CSV", type="primary"):
            with st.spinner("Procesando traducciones..."):
                # Guardar temporalmente
                temp_path = f"./temp_{csv_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(csv_file.getbuffer())
                
                try:
                    ingest_csv(temp_path)
                    os.remove(temp_path)
                    st.success("✅ Traducciones procesadas correctamente")
                    st.session_state.vector_store_loaded = True
                    st.session_state.rag_chain = None  # Resetear cadena
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
    
    # Botón para cargar CSV por defecto
    if st.button("📂 Cargar traducciones.csv (por defecto)"):
        csv_path = "./traducciones.csv"
        if os.path.exists(csv_path):
            try:
                ingest_csv(csv_path)
                st.success("✅ Traducciones cargadas")
                st.session_state.vector_store_loaded = True
                st.session_state.rag_chain = None
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        else:
            st.error("❌ No se encontró traducciones.csv")
    
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
        value=0.3,
        step=0.1,
        help="Baja temperatura = respuestas más precisas (recomendado para traducción)"
    )
    
    st.session_state.model_name = model_name
    st.session_state.temperature = temperature
    
    st.markdown("---")
    
    # Estadísticas
    if st.session_state.traducciones:
        st.subheader("📊 Estadísticas")
        st.write(f"**Frases cargadas:** {len(st.session_state.traducciones)}")
        
        # Contar por categoría
        categorias = {}
        for trad in st.session_state.traducciones.values():
            cat = trad.get('categoria', 'Sin categoría')
            categorias[cat] = categorias.get(cat, 0) + 1
        
        if categorias:
            st.write("**Por categoría:**")
            for cat, count in categorias.items():
                st.write(f"  • {cat}: {count}")

# Área principal de traducción
if not st.session_state.vector_store_loaded:
    st.info("👆 Por favor, carga el CSV de traducciones desde la barra lateral para comenzar")
    
    # Mostrar información sobre el formato esperado
    with st.expander("ℹ️ Información sobre el formato CSV"):
        st.markdown("""
        El CSV debe tener las siguientes columnas (separadas por punto y coma `;`):
        - `id`: Identificador único
        - `categoria`: Categoría de la frase (ej: comunicación efectiva, síntomas, etc.)
        - `español`: Frase en español
        - `aymara`: Traducción en aymara
        - `quechua`: Traducción en quechua
        """)
else:
    # Inicializar cadena RAG si no está inicializada
    if st.session_state.rag_chain is None:
        with st.spinner("🔄 Inicializando sistema de traducción RAG..."):
            model_name = st.session_state.get("model_name", "llama3.2")
            temperature = st.session_state.get("temperature", 0.3)
            st.session_state.rag_chain = create_translation_rag_chain(model_name, temperature)
    
    # Selector de dirección de traducción
    col1, col2 = st.columns(2)
    
    with col1:
        direction = st.radio(
            "📤 Dirección de traducción",
            ["espanol_a_indigena", "indigena_a_espanol"],
            format_func=lambda x: "Español → Indígena" if x == "espanol_a_indigena" else "Indígena → Español",
            help="Selecciona la dirección de la traducción"
        )
    
    with col2:
        if direction == "espanol_a_indigena":
            lang = st.selectbox(
                "🌍 Idioma objetivo",
                ["aymara", "quechua"],
                help="Selecciona el idioma indígena objetivo"
            )
        else:
            lang = st.selectbox(
                "🌍 Idioma de origen",
                ["aymara", "quechua"],
                help="Selecciona el idioma indígena de origen"
            )
    
    st.markdown("---")
    
    # Área de entrada de texto
    st.subheader("💬 Traducción")
    
    # Input de texto
    texto_input = st.text_area(
        "Escribe la frase a traducir:",
        height=100,
        placeholder="Ejemplo: ¿Te duele la cabeza?",
        help="Escribe la frase que deseas traducir"
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        traducir_btn = st.button("🔄 Traducir", type="primary", use_container_width=True)
    
    with col2:
        if st.button("🗑️ Limpiar", use_container_width=True):
            texto_input = ""
            st.rerun()
    
    # Procesar traducción - Lógica simple como app.py
    if traducir_btn and texto_input.strip():
        with st.spinner("🔍 Buscando traducción en la base de conocimientos..."):
            try:
                # Invocar RAG - igual que app.py
                result = translate_with_rag(texto_input, direction, lang)
                respuesta = result.get('answer', '')
                
                # Extraer ID de la respuesta del modelo (formato: ID:<numero> o ID:NONE)
                id_encontrado = extraer_id_respuesta(respuesta)
                
                # Buscar la traducción en el diccionario usando el ID
                traduccion_data = None
                
                if id_encontrado and id_encontrado in st.session_state.traducciones:
                    # Encontramos el ID, obtener los datos del diccionario
                    trad_data = st.session_state.traducciones[id_encontrado]
                    español_original = trad_data.get('español', '').strip()
                    aymara = trad_data.get('aymara', '').strip()
                    quechua = trad_data.get('quechua', '').strip()
                    
                    # Determinar la traducción según direction y lang
                    if direction == "espanol_a_indigena":
                        if lang == "aymara" and aymara:
                            traduccion_data = {
                                'id_encontrado': id_encontrado,
                                'frase_origen': español_original,
                                'traduccion': aymara,
                                'idioma_origen': 'espanol',
                                'idioma_destino': 'aymara',
                                'audio_ref': f"audio_{id_encontrado}"
                            }
                        elif lang == "quechua" and quechua:
                            traduccion_data = {
                                'id_encontrado': id_encontrado,
                                'frase_origen': español_original,
                                'traduccion': quechua,
                                'idioma_origen': 'espanol',
                                'idioma_destino': 'quechua',
                                'audio_ref': f"audio_{id_encontrado}"
                            }
                    else:  # indigena_a_espanol
                        if lang == "aymara" and aymara:
                            traduccion_data = {
                                'id_encontrado': id_encontrado,
                                'frase_origen': aymara,
                                'traduccion': español_original,
                                'idioma_origen': 'aymara',
                                'idioma_destino': 'espanol',
                                'audio_ref': f"audio_{id_encontrado}"
                            }
                        elif lang == "quechua" and quechua:
                            traduccion_data = {
                                'id_encontrado': id_encontrado,
                                'frase_origen': quechua,
                                'traduccion': español_original,
                                'idioma_origen': 'quechua',
                                'idioma_destino': 'espanol',
                                'audio_ref': f"audio_{id_encontrado}"
                            }
                
                # Mostrar resultado
                if traduccion_data:
                    st.success("✅ Traducción encontrada")
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.markdown("### 📝 Frase Original")
                        st.info(traduccion_data['frase_origen'])
                        st.caption(f"Idioma: {traduccion_data['idioma_origen']}")
                    
                    with col_b:
                        st.markdown("### 🌐 Traducción")
                        st.success(traduccion_data['traduccion'])
                        st.caption(f"Idioma: {traduccion_data['idioma_destino']}")
                    
                    # Información adicional
                    with st.expander("ℹ️ Información adicional"):
                        st.write(f"**ID en CSV:** {traduccion_data['id_encontrado']}")
                        st.write(f"**Categoría:** {trad_data.get('categoria', 'N/A')}")
                        if traduccion_data.get('audio_ref'):
                            st.write(f"**Referencia de audio:** {traduccion_data['audio_ref']}")
                    
                    # Mostrar contexto recuperado (opcional, para debug)
                    if result.get('context'):
                        with st.expander("📚 Contexto recuperado", expanded=False):
                            for i, doc in enumerate(result['context'], 1):
                                metadata = doc.metadata
                                st.write(f"**{i}.** ID: {metadata.get('id', '?')} - {metadata.get('categoria', '?')}")
                                st.caption(f"Español: {metadata.get('español', 'N/A')}")
                else:
                    # No se encontró traducción
                    st.error("❌ No se encontró una traducción para esta frase")
                    
                    # Debug detallado
                    with st.expander("🔍 Debug - Respuesta del modelo", expanded=True):
                        st.write("**Respuesta completa del modelo:**")
                        st.text_area("", respuesta, height=150, key="debug_respuesta")
                        st.write(f"**ID extraído:** `{id_encontrado if id_encontrado else 'None'}`")
                        
                        if id_encontrado:
                            st.write(f"**¿ID existe en diccionario?** {id_encontrado in st.session_state.traducciones if st.session_state.traducciones else 'N/A'}")
                            if st.session_state.traducciones:
                                st.write(f"**IDs disponibles en diccionario:** {list(st.session_state.traducciones.keys())[:10]}...")
                                st.write(f"**Buscando ID '{id_encontrado}' (tipo: {type(id_encontrado).__name__})**")
                                st.write(f"**IDs en diccionario (primeros 10):** {[str(k) for k in list(st.session_state.traducciones.keys())[:10]]}")
                            else:
                                st.error("⚠️ El diccionario de traducciones NO está cargado. Recarga el CSV desde el sidebar.")
                    
                    # Mostrar contexto recuperado
                    if result.get('context'):
                        with st.expander("📚 Contexto recuperado por RAG", expanded=True):
                            st.write(f"**Total documentos recuperados:** {len(result['context'])}")
                            for i, doc in enumerate(result['context'], 1):
                                metadata = doc.metadata
                                st.write(f"**{i}.** ID: `{metadata.get('id', '?')}` - {metadata.get('categoria', '?')}")
                                st.caption(f"Español: {metadata.get('español', 'N/A')}")
                                if lang == "aymara":
                                    st.caption(f"Aymara: {metadata.get('aymara', 'N/A')}")
                                elif lang == "quechua":
                                    st.caption(f"Quechua: {metadata.get('quechua', 'N/A')}")
                                st.write("---")
                    else:
                        st.warning("⚠️ No se recuperó ningún contexto del vector store")
            
            except Exception as e:
                st.error(f"❌ Error al traducir: {str(e)}")
                st.exception(e)
    
    elif traducir_btn:
        st.warning("⚠️ Por favor, escribe una frase para traducir")
    
    st.markdown("---")
    
    # Ejemplos de uso
    with st.expander("💡 Ejemplos de frases para traducir"):
        st.markdown("""
        **Comunicación efectiva:**
        - ¿Cómo te llamas?
        - ¿Cuántos años tienes?
        - ¿Comprendiste todo?
        
        **Síntomas:**
        - ¿Te duele la cabeza?
        - ¿Tienes fiebre?
        - ¿Estás tosiendo?
        
        **Antecedentes:**
        - ¿Fumas?
        - ¿Tomas bebidas alcohólicas?
        - ¿Tomas medicamentos?
        """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Powered by Ollama + LangChain + Streamlit | Traductor Médico RAG</p>
    </div>
    """,
    unsafe_allow_html=True
)

