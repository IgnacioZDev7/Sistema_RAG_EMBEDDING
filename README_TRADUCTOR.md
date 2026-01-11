# 🌐 Traductor Médico RAG

## 📋 Descripción

Traductor médico especializado que utiliza RAG (Retrieval-Augmented Generation) para traducir frases médicas entre **Español**, **Aymara** y **Quechua**. 

El sistema busca en una base de conocimientos pre-validada (CSV) la frase más cercana médicamente, garantizando precisión y fidelidad en las traducciones médicas.

## 🎯 Características

- ✅ **Traducción bidireccional**: Español ↔ Aymara/Quechua
- ✅ **RAG con embeddings**: Búsqueda semántica inteligente
- ✅ **Base de conocimientos validada**: Solo usa frases pre-traducidas del CSV
- ✅ **Interfaz web moderna**: Streamlit
- ✅ **Precisión médica**: Prioriza fidelidad médica sobre similitud textual

## 📦 Requisitos

1. **Ollama instalado y corriendo**
   ```bash
   ollama serve
   ```

2. **Modelo de Ollama disponible**
   ```bash
   ollama pull llama3.2
   ```

3. **Entorno virtual con dependencias**
   - LangChain
   - Streamlit
   - ChromaDB
   - FastEmbed

## 🚀 Cómo Ejecutar

### Opción 1: Comando directo
```bash
streamlit run traductor_rag.py
```

### Opción 2: Con intérprete del entorno virtual
```bash
.venv/Scripts/python.exe -m streamlit run traductor_rag.py
```

### Opción 3: En Windows (Git Bash)
```bash
source .venv/Scripts/activate
streamlit run traductor_rag.py
```

## 🌐 Acceso

Una vez ejecutado, la aplicación estará disponible en:
- **URL local**: http://localhost:8501
- Se abrirá automáticamente en tu navegador

## 📖 Uso de la Interfaz

### 1. Carga Automática

**El sistema carga automáticamente al iniciar:**
- ✅ Detecta si existe `traducciones.csv` en el directorio raíz
- ✅ Carga el diccionario en memoria para acceso rápido
- ✅ Verifica si la base de datos vectorial existe
- ✅ Si la BD está vacía o no existe, la regenera automáticamente
- ✅ Muestra un mensaje de confirmación cuando todo está listo

**Carga Manual (Opcional):**
- Si necesitas recargar el CSV, usa el botón "📂 Cargar traducciones.csv (por defecto)" en el sidebar
- O sube un CSV personalizado usando el file uploader

### 2. Configurar Traducción

**Dirección de traducción:**
- **Español → Indígena**: Traduce del español a aymara o quechua
- **Indígena → Español**: Traduce de aymara/quechua al español

**Idioma objetivo:**
- Si traduces **Español → Indígena**: Selecciona "aymara" o "quechua"
- Si traduces **Indígena → Español**: Selecciona el idioma de origen (aymara o quechua)

### 3. Traducir

1. Escribe la frase a traducir en el área de texto
2. Haz clic en "🔄 Traducir"
3. El sistema buscará la frase más cercana en la base de conocimientos
4. Verás:
   - ✅ Frase original
   - 🌐 Traducción encontrada
   - ℹ️ Información adicional (ID, confianza, etc.)
   - 📚 Frases similares encontradas

## 📄 Formato del CSV

El CSV debe tener las siguientes columnas (separadas por punto y coma `;`):

```csv
id;categoria;español;aymara;quechua
1;comunicacion efectiva;¿Cómo te llamas?;¿Sutimax kunasa?;Imataq sutiyki?
2;sintomas;¿Te duele la cabeza?;¿P'iqix ustamti?;¿Umayki nananchu?
```

**Columnas requeridas:**
- `id`: Identificador único
- `categoria`: Categoría de la frase (ej: comunicación efectiva, síntomas, etc.)
- `español`: Frase en español
- `aymara`: Traducción en aymara
- `quechua`: Traducción en quechua

## 🔧 Configuración del Modelo

En el sidebar puedes configurar:

- **Modelo de Ollama**: Selecciona el modelo a usar (llama3.2 recomendado)
- **Temperatura**: Controla la creatividad (0.3 recomendado para traducción precisa)

## 📝 Ejemplos de Uso

### Ejemplo 1: Español → Aymara
- **Dirección**: Español → Indígena
- **Idioma objetivo**: aymara
- **Frase**: "¿Te duele la cabeza?"
- **Resultado**: Busca la frase más cercana y devuelve la traducción en aymara

### Ejemplo 2: Quechua → Español
- **Dirección**: Indígena → Español
- **Idioma de origen**: quechua
- **Frase**: "¿Umayki nananchu?"
- **Resultado**: Busca la frase y devuelve la traducción en español

## 🎨 Características de la Interfaz

### Panel Lateral (Sidebar)
- **Estado de la Base de Datos**: Muestra si está cargada
- **Cargar Traducciones**: Upload o carga por defecto
- **Configuración del Modelo**: Selección de modelo y temperatura
- **Estadísticas**: Número de frases cargadas y por categoría

### Área Principal
- **Selector de Dirección**: Español ↔ Indígena
- **Selector de Idioma**: Aymara o Quechua
- **Área de Traducción**: Input y botones
- **Resultados**: Visualización estructurada de traducciones
- **Ejemplos**: Frases de ejemplo para probar

## ⚙️ Funcionamiento Técnico

### Flujo de Traducción

1. **Carga Automática**: Al iniciar, el sistema carga automáticamente `traducciones.csv`:
   - Crea un diccionario en memoria para acceso rápido (`st.session_state.traducciones`)
   - Genera embeddings vectoriales de todas las frases
   - Almacena en ChromaDB (`traducciones_db/`) para búsqueda semántica

2. **Búsqueda RAG**: Cuando el usuario ingresa una frase:
   - El retriever busca los 5 documentos más similares en el vector store
   - Estos documentos se pasan como contexto al modelo LLM

3. **Selección de ID**: El modelo (guiado por `prompt.txt`):
   - Analiza la frase del usuario
   - Compara con las frases en el contexto recuperado
   - Devuelve **solo el ID** de la frase más cercana médicamente (formato: `ID:6` o `ID:NONE`)

4. **Extracción y Búsqueda**: El sistema:
   - Extrae el ID de la respuesta del modelo
   - Busca ese ID en el diccionario cargado en memoria
   - Obtiene la traducción correcta según el idioma objetivo

5. **Visualización**: Muestra:
   - Frase original (del CSV)
   - Traducción (del CSV)
   - Información adicional (ID, categoría, etc.)

## 📂 Archivos del Proyecto

### Archivos Principales

- **`traductor_rag.py`**: Aplicación principal con Streamlit
  - Carga automática del CSV
  - Interfaz web completa
  - Sistema RAG con retriever y LLM
  - Debug integrado

- **`traducciones.csv`**: Base de conocimientos con frases traducidas
  - Formato: delimitador `;` (punto y coma)
  - Columnas: `id`, `categoria`, `español`, `aymara`, `quechua`
  - Se carga automáticamente al iniciar

- **`prompt.txt`**: Instrucciones estrictas para el modelo de Ollama
  - Define el comportamiento del modelo
  - Formato de respuesta: solo ID (ej: `ID:6`)
  - Prohibiciones: no traducir, no explicar, solo seleccionar ID

### Archivos Generados

- **`traducciones_db/`**: Base de datos vectorial de ChromaDB
  - Se crea automáticamente al cargar el CSV
  - Contiene embeddings de todas las frases
  - Se regenera si está vacía o corrupta

### Archivos de Configuración

- **`pyproject.toml`**: Configuración del proyecto
- **`requirements.txt`**: Dependencias del proyecto

## 🔍 Diferencias con app.py

| Característica | app.py | traductor_rag.py |
|---------------|--------|------------------|
| Fuente de datos | PDF | CSV |
| Propósito | Chat sobre documento | Traducción médica |
| Prompt | Hardcodeado | Desde `prompt.txt` |
| Output | Texto libre | Solo ID (ej: `ID:6`) |
| Idiomas | Español | Español, Aymara, Quechua |
| Retriever | `similarity_score_threshold` | `similarity` (siempre devuelve docs) |
| Carga | Manual | Automática al iniciar |
| Validación | No | Sí (solo frases del CSV) |

## 🐛 Solución de Problemas

### Error: "Ollama no está corriendo"
```bash
ollama serve
```
Asegúrate de que Ollama esté ejecutándose antes de iniciar Streamlit.

### Error: "Modelo no encontrado"
```bash
ollama pull llama3.2
```
O usa otro modelo disponible: `llama3.1`, `llama3`, `mistral`, etc.

### Error: "No se encontró traducciones.csv"
- Verifica que el archivo esté en el directorio raíz del proyecto
- El archivo debe llamarse exactamente `traducciones.csv`
- O usa el file uploader en el sidebar para subir tu CSV

### Error: "El diccionario de traducciones NO está cargado"
- El CSV se carga automáticamente al iniciar
- Si aparece este error, recarga el CSV desde el sidebar
- Verifica que el CSV tenga el formato correcto (delimitador `;`)

### Error: "No se recuperó ningún contexto"
- La base de datos vectorial puede estar vacía
- El sistema detecta esto automáticamente y regenera la BD
- Si persiste, elimina la carpeta `traducciones_db/` y reinicia Streamlit

### La traducción devuelve IDs incorrectos
- Verifica que la base de datos tenga documentos (no esté vacía)
- Revisa el debug expandido para ver qué contexto se está recuperando
- Asegúrate de que el modelo esté recibiendo contexto del retriever

### El modelo devuelve siempre el mismo ID
- Esto indica que el retriever no está funcionando correctamente
- Verifica que la BD tenga documentos cargados
- Revisa los mensajes de debug para ver qué contexto se recupera

## 📚 Notas Importantes

### Características del Sistema

- ⚠️ **NO traduce libremente**: Solo usa frases que existen en el CSV
- ✅ **Prioriza fidelidad médica**: Usa similitud semántica para encontrar frases equivalentes
- 🔒 **Traducciones pre-validadas**: Todas las traducciones provienen del CSV validado
- 📊 **Debug integrado**: Expanders para ver la respuesta del modelo y el contexto recuperado
- 🔄 **Carga automática**: El CSV y la BD se cargan automáticamente al iniciar
- 🛡️ **Manejo de BOM**: El sistema maneja automáticamente archivos CSV con BOM (Byte Order Mark)

### Formato del Prompt

El sistema usa `prompt.txt` que instruye al modelo a:
1. Analizar la consulta del usuario
2. Comparar con las frases en el contexto (recuperadas por RAG)
3. Devolver **solo el ID** de la frase más cercana (formato: `ID:6` o `ID:NONE`)
4. **NO traducir**, **NO explicar**, solo devolver el ID

### Estructura de Datos

- **Diccionario en memoria**: `st.session_state.traducciones` - acceso rápido por ID
- **Vector Store**: ChromaDB con embeddings para búsqueda semántica
- **Documentos LangChain**: Cada fila del CSV se convierte en un Document con metadata

## 🎉 ¡Listo!

Tu traductor médico RAG está listo para usar. Asegúrate de tener:

1. ✅ **Ollama corriendo**: `ollama serve`
2. ✅ **Modelo descargado**: `ollama pull llama3.2`
3. ✅ **CSV de traducciones**: `traducciones.csv` en el directorio raíz
4. ✅ **Aplicación ejecutándose**: `streamlit run traductor_rag.py`

## 🔄 Flujo Completo del Sistema

```
Usuario ingresa frase
    ↓
Retriever busca documentos similares (RAG)
    ↓
Modelo recibe contexto + frase del usuario
    ↓
Modelo devuelve ID (ej: "ID:6")
    ↓
Sistema extrae ID y busca en diccionario
    ↓
Muestra traducción correcta del CSV
```

## 📝 Ejemplos de Frases para Probar

- **Comunicación efectiva**: "¿Cómo te llamas?", "¿Cuántos años tienes?", "¿Comprendiste todo?"
- **Síntomas**: "¿Te duele la cabeza?", "¿Tienes fiebre?", "¿Estás tosiendo?"
- **Antecedentes**: "¿Fumas?", "¿Tomas bebidas alcohólicas?", "¿Tomas medicamentos?"

## 🎯 Características Técnicas Implementadas

- ✅ Carga automática del CSV al iniciar
- ✅ Manejo de BOM en archivos CSV
- ✅ Verificación y regeneración automática de BD vacía
- ✅ Retriever con `similarity` (siempre devuelve documentos)
- ✅ Extracción robusta de ID con regex
- ✅ Debug expandible para troubleshooting
- ✅ Validación de traducciones contra CSV
- ✅ Interfaz responsive con Streamlit

---

**Powered by Ollama + LangChain + Streamlit | Traductor Médico RAG**

*Última actualización: Enero 2025*

