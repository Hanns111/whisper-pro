# Whisper Pro 🎙️

Sistema profesional de transcripción de audio y video usando OpenAI Whisper, con soporte automático para GPU (CUDA) y CPU.

## 💻 Hardware del Sistema

**Nombre del dispositivo:** MSI Titan 18 HX A2XWJG  
**Procesador:** Intel(R) Core(TM) Ultra 9 285HX (2.80 GHz)  
**RAM instalada:** 64 GB  
**GPU:** NVIDIA GeForce RTX 5090 (24 GB VRAM)  
**Sistema operativo:** Windows 11 Home 64 bits  
**Arquitectura:** x64  

**Aclaración técnica:**  
- Este hardware permite ejecutar Whisper large-v3 a máxima precisión.
- **IMPORTANTE:** La RTX 5090 tiene compute capability sm_120, que no es compatible con la versión actual de PyTorch (solo soporta hasta sm_90). Por lo tanto, Whisper se ejecuta en CPU, lo cual es más lento pero funcional.
- **FFmpeg completo es obligatorio:** Se requiere una instalación completa de FFmpeg con `ffprobe` habilitado. La versión de SteelSeries GG no incluye `ffprobe` y no funcionará.

## 📋 Características

- ✅ **Detección automática de GPU**: Usa CUDA si está disponible, CPU en caso contrario
- ✅ **Múltiples modelos**: tiny, base, small, medium, large-v3
- ✅ **Formatos soportados**: MP3, WAV, M4A, OGG, MP4, AVI, MKV, MOV, etc.
- ✅ **Timestamps**: Genera transcripciones con marcas de tiempo
- ✅ **Múltiples formatos de salida**: TXT, JSON, SRT, VTT
- ✅ **Detección automática de idioma** o forzado (español, inglés, portugués, etc.)
- ✅ **Procesamiento por lotes**: Transcribe todos los archivos de una carpeta automáticamente
- ✅ **Logging completo**: Registra todo el proceso en archivos de log
- ✅ **Análisis avanzado de agresión verbal**: Detecta insultos, amenazas, descalificaciones, gaslighting, manipulación e invalidación
- ✅ **Detección de estrés vocal**: Analiza cambios en volumen y detecta voz elevada
- ✅ **Detección de agresión dirigida**: Identifica agresión específica hacia víctimas (Claudia, Juan Diego, José Carlos)
- ✅ **Informes unificados**: Genera informes completos en español e inglés con todos los análisis
- ✅ **Análisis de patrones de comportamiento**: ✅ **COMPLETADO** - 152 patrones identificados en 25 archivos, correlación entre caso histórico (Rikke) y caso actual (Claudia)
- ✅ **Análisis forense de PDFs**: Correlación de documentos históricos con transcripciones actuales según Straffeloven §243

## 🚀 Instalación en Windows 11

### 1. Instalar Python

1. Descarga Python 3.10 o superior desde [python.org](https://www.python.org/downloads/)
2. Durante la instalación, **marca la casilla "Add Python to PATH"**
3. Verifica la instalación abriendo PowerShell y ejecutando:
   ```powershell
   python --version
   ```

### 2. Instalar FFmpeg

FFmpeg es necesario para procesar archivos de audio y video.

**Opción A: Usando Chocolatey (recomendado)**
```powershell
# Si no tienes Chocolatey, instálalo primero desde https://chocolatey.org/install
choco install ffmpeg
```

**Opción B: Instalación manual**
1. Descarga FFmpeg desde [ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extrae el archivo ZIP
3. Agrega la carpeta `bin` de FFmpeg al PATH del sistema:
   - Abre "Variables de entorno" en Windows
   - Edita la variable "Path"
   - Agrega la ruta completa a la carpeta `bin` de FFmpeg (ej: `C:\ffmpeg\bin`)
4. Reinicia PowerShell y verifica:
   ```powershell
   ffmpeg -version
   ```

### 3. Instalar PyTorch (con soporte GPU opcional)

**Para CPU solamente:**
```powershell
pip install torch torchvision torchaudio
```

**Para GPU con CUDA 11.8:**
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Para GPU con CUDA 12.1:**
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**Verificar instalación de CUDA:**
```powershell
python -c "import torch; print('CUDA disponible:', torch.cuda.is_available())"
```

### 4. Instalar dependencias del proyecto

Navega a la carpeta del proyecto y ejecuta:

```powershell
cd C:\Users\hanns\Proyectos\whisper-pro
pip install -r requirements.txt
```

## 📁 Estructura del Proyecto

```
whisper-pro/
│── src/
│     ├── transcriber.py          # Clase principal de transcripción
│     ├── audio_loader.py         # Carga de archivos de audio
│     ├── utils.py                # Utilidades (carpetas, logs, etc.)
│     ├── violence_detector.py    # Detector básico de violencia (legacy)
│     ├── analizador_agresion.py  # Analizador avanzado de agresión verbal
│     ├── detector_voz.py         # Detector de estrés vocal y voz elevada
│     ├── detector_victimas.py    # Detector de agresión dirigida a víctimas
│     ├── analizador_forense_dk.py # Analizador forense según Straffeloven §243
│     ├── analizador_pdf_forense.py # Analizador forense de PDFs con correlación
│     └── __init__.py
│
│── modelos/                      # Modelos de Whisper (se descargan automáticamente)
│── transcripciones/              # Aquí se guardan TODAS las transcripciones e informes
│── logs/                         # Archivos de log
│
│── requirements.txt
│── run_transcription.py          # Script principal con análisis completo
│── run_pdf_analysis.py          # Script para análisis forense de PDFs
│── analizar_patrones_lars.py     # Script de análisis de patrones (ejecutado)
│── pipeline_transcripcion.py     # Pipeline avanzado (legacy)
│
│── # Archivos de análisis de patrones (COMPLETADO)
│── informe_patrones_lars.txt     # Informe inicial de patrones
│── patrones_lars.json            # Datos estructurados de patrones
│
│── # Documentación para informe forense
│── COPIAR_ESTE_PROMPT_EN_CURSOR.txt ⭐ # Prompt principal para Cursor IDE
│── README_CASO_CLAUDIA.md        # Documentación completa del caso
│── INSTRUCCIONES_USO.md          # Guía para usar Cursor
│── PROMPT_INFORME_FORENSE_INMIGRACION.md # Versión técnica del prompt
│── PROMPTS_PARA_CURSOR.md        # 10 prompts adicionales
│
│── README.md                     # Este archivo
```

**Rutas configuradas:**
- **Entrada (solo lectura)**: `C:\Users\hanns\Downloads\Audios de Lars -20251203T004029Z-1-001\Audios de Lars`
- **Salida**: `C:\Users\hanns\Proyectos\whisper-pro\transcripciones\`
- **Logs**: `C:\Users\hanns\Proyectos\whisper-pro\logs\`

## 🎯 Uso

### Uso básico

1. **Los archivos de audio se leen directamente** desde:
   ```
   C:\Users\hanns\Downloads\Audios de Lars -20251203T004029Z-1-001\Audios de Lars
   ```
   - **IMPORTANTE**: Los archivos originales NO se copian ni se modifican
   - El sistema lee directamente desde esta ubicación
   - Formatos procesados: `.m4a`, `.mp3` (búsqueda recursiva)

2. **Ejecuta el script de transcripción con análisis completo**:
   ```powershell
   python run_transcription.py
   ```

3. **Encuentra los resultados** en la carpeta:
   ```
   C:\Users\hanns\Proyectos\whisper-pro\transcripciones\
   ```
   
   Se generan los siguientes archivos por cada audio:
   - Transcripciones originales (`.txt`, `.json`, `.srt`, `.vtt`)
   - Análisis de agresión verbal (`*_analisis_agresion.json`, `*_analisis_agresion_es.txt`)
   - Análisis de estrés vocal (`*_analisis_voz.json`, `*_analisis_voz_es.txt`)
   - Análisis de víctimas (`*_analisis_victimas.json`, `*_analisis_victimas_es.txt`)
   - Análisis forense danés (`*_forensisk_analyse_dk.json`, `*_forensisk_analyse_dk.txt`)
   - **Informe completo unificado** (`*_informe_completo.json`, `*_informe_es.txt`, `*_informe_en.txt`)

### Configuración avanzada

Puedes modificar el modelo y otros parámetros editando `run_transcription.py` o usando variables de entorno:

```powershell
# Usar modelo más grande (más preciso pero más lento)
$env:WHISPER_MODEL="medium"
python run_transcription.py

# Forzar idioma español
$env:WHISPER_LANGUAGE="es"
python run_transcription.py

# Generar subtítulos SRT
$env:WHISPER_FORMAT="srt"
python run_transcription.py
```

### Modelos disponibles

- `tiny`: Más rápido, menos preciso
- `base`: Balance velocidad/precisión (recomendado para empezar)
- `small`: Mejor precisión
- `medium`: Alta precisión
- `large-v3`: Máxima precisión (requiere más memoria)

### Formatos de salida

- `txt`: Texto plano simple
- `json`: JSON completo con metadatos y timestamps
- `srt`: Subtítulos SRT
- `vtt`: Subtítulos WebVTT

## 📄 ANÁLISIS DE PDFs (EVIDENCIA LEGAL)

### Descripción

El proyecto incluye un módulo completo para análisis forense de documentos PDF oficiales (psicólogos, autoridades danesas, etc.). El análisis se realiza según criterios legales de Straffeloven §243 sobre violencia psicológica.

### ⚠️ ESTRATEGIA FORENSE IMPORTANTE

**CONTEXTO DE LOS PDFs:**
- Los PDFs analizados son sobre la **EX ESPOSA del abusador** y sus **HIJOS BIOLÓGICOS** que lo rechazan
- Estos documentos muestran **PATRONES DE COMPORTAMIENTO HISTÓRICOS** del abusador
- Los PDFs contienen argumentos que el abusador está enfrentando por patrones repetitivos

**CONTEXTO DE LOS AUDIOS:**
- Las grabaciones de audio son sobre **Claudia** (víctima actual) y sus hijos
- Los audios documentan situaciones con **Juan Diego** (17 años, autismo) y **José Carlos** (15 años, TDAH)
- Estos audios muestran **PATRONES DE COMPORTAMIENTO ACTUALES** del abusador

**OBJETIVO DE LA CORRELACIÓN:**
- Demostrar que el abusador **REPITE los mismos patrones** de comportamiento
- Establecer un **patrón consistente** de violencia psicológica a través del tiempo
- Proporcionar evidencia forense de que los patrones detectados en los PDFs (con ex esposa/hijos biológicos) están siendo **REPETIDOS** en los audios actuales (con Claudia y sus hijos)
- Esta correlación fortalece la evidencia legal según Straffeloven §243

### Características

- ✅ **Extracción de texto**: Usa PyMuPDF (fitz) para extraer texto de PDFs digitales
- ✅ **Detección de patrones**: Identifica gaslighting, coerción económica, amenazas, invalidación, manipulación emocional, control psicológico, aislamiento, humillación y chantaje emocional
- ✅ **Correlación con audios**: Correlaciona patrones históricos (PDFs sobre ex esposa/hijos biológicos) con patrones actuales (audios sobre Claudia y sus hijos)
- ✅ **Detección de víctimas en audios**: Identifica menciones a Claudia, Juan Diego y José Carlos en las transcripciones de audio
- ✅ **Detección de contradicciones**: Encuentra contradicciones internas y cambios bruscos de actitud
- ✅ **Clasificación legal danesa**: Evalúa según Straffeloven §243 con niveles de riesgo (lav, moderat, høj, kritisk)
- ✅ **Informes forenses correlacionales**: Genera informes profesionales que demuestran patrones repetitivos de comportamiento

### Instalación de Dependencias

```powershell
pip install PyMuPDF
```

### Uso

1. **Configurar la carpeta de PDFs** en `run_pdf_analysis.py`:
   ```python
   CARPETA_PDFS = r'C:\Users\hanns\Downloads\PDFs de Lars'
   ```

2. **Ejecutar el análisis**:
   ```powershell
   python run_pdf_analysis.py
   ```

3. **Encontrar los informes** en la carpeta `transcripciones/`:
   - Cada PDF genera un archivo: `{nombre_pdf}_PDF_CORRELACIONAL.txt`
   - Los informes muestran claramente las correlaciones entre patrones históricos (PDFs) y patrones actuales (audios)

### Estructura del Informe PDF Correlacional

Cada informe incluye:
- **A. CABECERA**: Nombre, fecha, hash SHA256, tamaño
- **A.1. CONTEXTO FORENSE**: Explicación de la estrategia de correlación (PDFs históricos vs audios actuales)
- **B. TEXTO EXTRAÍDO**: Contenido completo del PDF (original + traducciones)
- **C. ANÁLISIS DE AGRESIÓN (ES)**: Detecciones con citas textuales y **correlaciones con audios actuales**
- **D. ANÁLISIS FORENSE DK (§243)**: Clasificación legal y nivel de riesgo
- **E. RESUMEN FORENSE**: Explicación para abogado o Familienretshuset
- **F. IMPLICACIONES JURÍDICAS**: Análisis del patrón repetitivo y relevancia legal

### Notas Importantes

- ⚠️ **NO se copian ni modifican** los archivos PDF originales
- ⚠️ **NO requiere OCR**: Solo funciona con PDFs digitales (texto seleccionable)
- ⚠️ **NO instala pytesseract**: Solo usa PyMuPDF

## 🔍 ANÁLISIS DE PATRONES DE COMPORTAMIENTO (COMPLETADO)

### ✅ Trabajo Completado

Se ha realizado un análisis forense completo de patrones de comportamiento que correlaciona documentos legales históricos (caso Rikke Larsen - ex esposa) con transcripciones de audio actuales (caso Claudia).

### 📊 Hallazgos Principales

**Análisis realizado:**
- ✅ **25 archivos de transcripción** procesados automáticamente
- ✅ **152 ocurrencias** de patrones identificadas y documentadas
- ✅ **8 categorías** de comportamiento abusivo detectadas

**Patrones identificados (por frecuencia):**
1. **Manipulación financiera**: 50 ocurrencias
   - Referencias a dinero, pagos, trading, pérdidas financieras
   - Control económico como herramienta de manipulación

2. **Minimización de esfuerzos**: 43 ocurrencias
   - Desvalorización del trabajo y esfuerzos de Claudia
   - Invalidación de contribuciones

3. **Culpabilización**: 19 ocurrencias
   - Atribución de responsabilidad y culpa
   - "It's your fault", "You are responsible"

4. **Victimización**: 14 ocurrencias
   - Auto-victimización para manipular emocionalmente
   - "I don't want to live", "I am so stressed"

5. **Amenazas de abandono**: 10 ocurrencias
   - Amenazas de dejar o abandonar
   - Manipulación mediante miedo al abandono

6. **Críticas a los hijos**: 8 ocurrencias ⚠️
   - Críticas dirigidas a Juan Diego (TEA) y José Carlos (TDAH)
   - Uso de las condiciones de los niños para manipular

7. **Amenazas con autoridades**: 5 ocurrencias ⚠️
   - Amenazas de reportar a autoridades
   - Amenazas de quitar custodia de los hijos

8. **Acusaciones problemas hogar**: 3 ocurrencias
   - Acusaciones sobre problemas en el hogar

### ⚠️ Puntos Más Graves Identificados

**Archivo crítico:** `241125_Lars_amenaza_Alcohol_y_reporte...`

**Amenazas documentadas con timestamps exactos:**
- `[02:21]`: "I will report you"
- `[04:04]`: "They will take your children away from you"
- `[05:36]`: "You will lose your children in a second"

**Día más crítico:** 27 de octubre 2024
- 31 patrones detectados en un solo día
- 23 referencias a manipulación financiera
- Múltiples referencias a trading y pérdidas de dinero

### 📁 Archivos Generados

**Análisis automatizado:**
- `analizar_patrones_lars.py` - Script de análisis (ya ejecutado)
- `informe_patrones_lars.txt` - Informe inicial con estadísticas
- `patrones_lars.json` - Datos estructurados para análisis

**Documentación para generar informe forense:**
- `COPIAR_ESTE_PROMPT_EN_CURSOR.txt` ⭐ **ARCHIVO PRINCIPAL**
  - Prompt optimizado listo para usar en Cursor IDE
  - Genera informe forense técnico completo (20-40 páginas)
  - Incluye correlaciones entre caso Rikke y caso Claudia
  
- `README_CASO_CLAUDIA.md` - Resumen completo del caso
- `INSTRUCCIONES_USO.md` - Guía paso a paso para usar Cursor
- `PROMPT_INFORME_FORENSE_INMIGRACION.md` - Versión técnica detallada
- `PROMPTS_PARA_CURSOR.md` - 10 prompts adicionales para análisis

### 🚀 Cómo Generar el Informe Forense Completo

**3 pasos simples:**

1. **Abre Cursor IDE**
2. **Abre el archivo:** `COPIAR_ESTE_PROMPT_EN_CURSOR.txt`
3. **Copia TODO** (Ctrl+A, Ctrl+C) y pégalo en Cursor Chat

**Cursor generará automáticamente:**
- `informe_forense_inmigracion.md` (20-40 páginas)
  - Correlaciones completas entre caso Rikke y caso Claudia
  - Citas exactas: PDFs (páginas) + Audios (timestamps)
  - Análisis técnico de cada patrón
  - Conclusiones forenses

- `correlaciones_master.csv` (Tabla Excel)
  - Todas las correlaciones en formato tabla
  - Filtrable y ordenable
  - Para referencias rápidas

- `resumen_ejecutivo_2_paginas.md`
  - Resumen ejecutivo para presentación rápida

### ✨ Fortalezas del Caso

✅ **Patrón sistemático demostrado** - Lars hizo lo mismo con Rikke (documentado legalmente en Dinamarca)

✅ **10+ años de consistencia** - Mismo comportamiento con dos parejas diferentes

✅ **152 evidencias documentadas** - Cada una con timestamp exacto

✅ **Análisis objetivo** - Script automatizado, no opiniones

✅ **Respaldo legal internacional** - Caso oficial en Dinamarca

### 📖 Más Información

Para detalles completos del caso, análisis detallado y instrucciones paso a paso, consulta:
- `README_CASO_CLAUDIA.md` - Documentación completa del caso
- `INSTRUCCIONES_USO.md` - Cómo usar Cursor para generar el informe

## 📊 Módulos de Análisis

### Analizador de Agresión Verbal (`analizador_agresion.py`)

Detecta y clasifica diferentes tipos de agresión verbal:
- **Insultos**: Palabras ofensivas y groserías
- **Amenazas**: Frases que implican daño o consecuencias
- **Descalificaciones**: Frases que menosprecian o desvalorizan
- **Gaslighting**: Negación de la realidad, hacer dudar
- **Manipulación emocional**: Frases que buscan controlar emocionalmente
- **Invalidación**: Minimizar o negar sentimientos válidos

**Salida**: Lista de detecciones con timestamps, tipo, severidad (baja/media/alta) y frase completa.

### Detector de Estrés Vocal (`detector_voz.py`)

Analiza características acústicas del audio:
- **Aumento de volumen**: Detecta cambios > 10 dB sobre el promedio
- **Picos bruscos**: Identifica momentos de voz elevada
- **Análisis acústico**: Usa librosa para análisis de señal (opcional)

**Requisito**: Para análisis completo, instala librosa: `pip install librosa`

**Salida**: Lista de momentos con voz elevada, incluyendo cambio en dB y timestamps.

### Detector de Víctimas (`detector_victimas.py`)

Identifica agresión dirigida específicamente a víctimas:
- **Víctimas monitoreadas**: Claudia, Juan Diego, José Carlos
- **Tipos de agresión dirigida**:
  - Insulto dirigido
  - Amenaza dirigida
  - Invalidación dirigida
  - Manipulación dirigida
  - Burla dirigida
  - Presión emocional dirigida
  - Órdenes hostiles

**Salida**: Lista de detecciones agrupadas por víctima, con tipo, severidad y frase.

## 📝 Ejemplo de uso programático

```python
from src.transcriber import WhisperTranscriber
from src.analizador_agresion import AgresionAnalyzer
from src.detector_voz import VoiceStressDetector
from src.detector_victimas import VictimDetector

# Inicializar componentes
transcriptor = WhisperTranscriber(modelo='base')
analizador = AgresionAnalyzer()
detector_voz = VoiceStressDetector()
detector_victimas = VictimDetector()

# Transcribir
resultado = transcriptor.transcribir('audios/mi_audio.mp3', idioma='es')

# Analizar
agresion = analizador.analizar_transcripcion(resultado)
voz = detector_voz.analizar_audio('audios/mi_audio.mp3', resultado.get('segments', []))
victimas = detector_victimas.analizar_transcripcion(resultado, agresion)
```

## 📖 Cómo Interpretar los Informes

### Informe Completo (`*_informe_completo.json`)

Contiene toda la información estructurada:
- **transcripcion**: Texto completo, idioma, duración
- **analisis_agresion**: Lista de todas las agresiones detectadas
- **analisis_voz**: Momentos de voz elevada con cambios en dB
- **analisis_victimas**: Agresión dirigida agrupada por víctima

### Informe en Texto (`*_informe_es.txt` / `*_informe_en.txt`)

Versión legible del informe completo con:
1. **Transcripción completa** del audio
2. **Análisis de agresión** con timestamps y severidad
3. **Análisis de voz** con cambios en volumen
4. **Análisis de víctimas** agrupado por persona

### Severidad de Agresión

- **Alta**: Amenazas directas, insultos graves, órdenes hostiles
- **Media**: Manipulación, invalidación, descalificaciones
- **Baja**: Burla, mención sin agresión específica

## 🔧 Solución de problemas

### Error: "ffmpeg not found" o "ffprobe not found"
- **CRÍTICO**: Se requiere FFmpeg completo con `ffprobe` habilitado
- La versión de SteelSeries GG NO funciona (no incluye ffprobe)
- Instala FFmpeg completo:
  ```powershell
  choco install ffmpeg
  ```
  O descarga desde https://ffmpeg.org/download.html y agrega al PATH

### Error: "CUDA error: no kernel image is available"
- **Esperado**: La RTX 5090 (sm_120) no es compatible con PyTorch actual
- **Solución**: El sistema automáticamente usa CPU como fallback
- El procesamiento será más lento pero funcional

### Error: "librosa not available" en análisis de voz
- El análisis de voz requiere librosa para análisis acústico completo
- Instala: `pip install librosa`
- Sin librosa, el análisis de voz retornará lista vacía

### Transcripciones lentas
- **Normal en CPU**: Sin GPU, el procesamiento es más lento
- Usa un modelo más pequeño (tiny, base, small) para mayor velocidad
- El modelo `large-v3` en CPU puede tomar 1-2 horas para audios largos

### Modelo no se descarga
- Verifica tu conexión a internet
- Los modelos se descargan automáticamente la primera vez
- Se guardan en la carpeta `modelos/` o en el caché de Whisper

## 📄 Licencia

Este proyecto utiliza OpenAI Whisper, que está bajo la licencia MIT.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request.

---

**Desarrollado con ❤️ usando OpenAI Whisper**

