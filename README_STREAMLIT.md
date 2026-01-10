# 🚀 Guía de Uso - Aplicación RAG con Streamlit

## 📋 Requisitos Previos

1. **Ollama instalado y corriendo**
   - Asegúrate de tener Ollama instalado
   - El modelo `llama3.2` debe estar disponible
   - Para verificar: `ollama list`

2. **Entorno virtual activado**
   - El entorno virtual `.venv` debe estar configurado
   - Streamlit ya está instalado

## 🎯 Cómo Ejecutar

### Opción 1: Ejecutar directamente

```bash
streamlit run streamlit_app.py
```

### Opción 2: Con el intérprete del entorno virtual

```bash
.venv/Scripts/python.exe -m streamlit run streamlit_app.py
```

### Opción 3: En Windows (Git Bash)

```bash
source .venv/Scripts/activate
streamlit run streamlit_app.py
```

## 🌐 Acceso

Una vez ejecutado, la aplicación estará disponible en:
- **URL local**: http://localhost:8501
- Se abrirá automáticamente en tu navegador

## 📖 Características

### ✅ Funcionalidades Implementadas

1. **Carga de Documentos PDF**
   - Sube PDFs desde la interfaz web
   - Procesamiento automático del documento
   - Creación de base de datos vectorial

2. **Chat Interactivo**
   - Interfaz de chat moderna
   - Historial de conversación
   - Respuestas basadas en el documento

3. **Configuración Flexible**
   - Selección de modelo de Ollama
   - Ajuste de temperatura
   - Visualización de fuentes consultadas

4. **Gestión Inteligente**
   - Detecta si la base de datos ya existe
   - No reprocesa documentos innecesariamente
   - Caché de la cadena RAG para mejor rendimiento

## 🎨 Uso de la Interfaz

### Panel Lateral (Sidebar)

- **Estado de la Base de Datos**: Muestra si está cargada
- **Cargar Documento**: Sube y procesa nuevos PDFs
- **Configuración del Modelo**: 
  - Selecciona el modelo de Ollama
  - Ajusta la temperatura (0.0 = conservador, 1.0 = creativo)

### Área Principal

- **Chat**: Escribe tus preguntas sobre el documento
- **Historial**: Ve todas las preguntas y respuestas anteriores
- **Fuentes**: Expande para ver las páginas consultadas

## 🔧 Solución de Problemas

### Error: "Ollama no está corriendo"
```bash
# Inicia Ollama
ollama serve
```

### Error: "Modelo no encontrado"
```bash
# Descarga el modelo
ollama pull llama3.2
```

### La aplicación no se abre
- Verifica que el puerto 8501 no esté en uso
- Revisa que Streamlit esté instalado: `streamlit --version`

## 📝 Notas

- La base de datos se guarda en `./local_knowledge_db/`
- Si ya tienes una base de datos, no necesitas recargar el documento
- El historial de chat se mantiene durante la sesión
- Usa "Limpiar conversación" para reiniciar el chat

## 🆚 Diferencias con app.py (Consola)

| Característica | app.py (Consola) | streamlit_app.py (Web) |
|---------------|------------------|------------------------|
| Interfaz | Terminal | Navegador Web |
| Carga de PDFs | Ruta hardcodeada | Upload desde web |
| Historial | No persistente | Persistente en sesión |
| Configuración | Código | Interfaz gráfica |
| Fuentes | Texto plano | Expandible |

## 🎉 ¡Listo!

Tu aplicación RAG ahora tiene una interfaz web moderna y fácil de usar.

