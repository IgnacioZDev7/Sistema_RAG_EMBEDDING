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

### 1. Cargar Traducciones

**Opción A: Cargar CSV por defecto**
- Haz clic en "📂 Cargar traducciones.csv (por defecto)" en el sidebar
- El sistema cargará automáticamente `traducciones.csv`

**Opción B: Subir CSV personalizado**
- Usa el file uploader en el sidebar
- Sube tu archivo CSV con el formato correcto
- Haz clic en "🔄 Procesar CSV"

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

1. **Carga de CSV**: Convierte el CSV en documentos de LangChain
2. **Embeddings**: Crea embeddings vectoriales de todas las frases
3. **Vector Store**: Almacena en ChromaDB para búsqueda rápida
4. **RAG Chain**: Usa el prompt de `prompt.txt` para guiar la traducción
5. **Retrieval**: Busca las frases más similares semánticamente
6. **Generación**: El modelo selecciona la frase más cercana médicamente
7. **Respuesta JSON**: Devuelve resultado estructurado con la traducción

## 📂 Archivos del Proyecto

- `traductor_rag.py`: Aplicación principal con Streamlit
- `traducciones.csv`: Base de conocimientos con frases traducidas
- `prompt.txt`: Instrucciones para el modelo de Ollama
- `traducciones_db/`: Base de datos vectorial (se crea automáticamente)

## 🔍 Diferencias con app.py

| Característica | app.py | traductor_rag.py |
|---------------|--------|------------------|
| Fuente de datos | PDF | CSV |
| Propósito | Chat sobre documento | Traducción médica |
| Prompt | Hardcodeado | Desde prompt.txt |
| Output | Texto libre | JSON estructurado |
| Idiomas | Español | Español, Aymara, Quechua |

## 🐛 Solución de Problemas

### Error: "Ollama no está corriendo"
```bash
ollama serve
```

### Error: "Modelo no encontrado"
```bash
ollama pull llama3.2
```

### Error: "No se encontró traducciones.csv"
- Verifica que el archivo esté en el directorio raíz
- O usa el file uploader para subir tu CSV

### La traducción no encuentra resultados
- Verifica que la frase esté en el CSV
- Intenta con una frase similar
- Revisa que el CSV tenga el formato correcto

## 📚 Notas Importantes

- ⚠️ El sistema **NO traduce libremente**, solo usa frases del CSV
- ✅ Prioriza **fidelidad médica** sobre similitud textual
- 🔒 Garantiza que las traducciones sean **pre-validadas**
- 📊 Muestra **confianza** y **frases similares** encontradas

## 🎉 ¡Listo!

Tu traductor médico RAG está listo para usar. Asegúrate de tener:
1. ✅ Ollama corriendo
2. ✅ Modelo descargado (llama3.2)
3. ✅ CSV de traducciones cargado
4. ✅ Aplicación ejecutándose

---

**Powered by Ollama + LangChain + Streamlit**

