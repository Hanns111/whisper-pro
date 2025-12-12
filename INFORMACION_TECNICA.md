# 🔧 Información Técnica

## Especificaciones del Sistema

### Hardware
- **Dispositivo:** MSI Titan 18 HX A2XWJG
- **CPU:** Intel(R) Core(TM) Ultra 9 285HX (2.80 GHz)
- **RAM:** 64 GB
- **GPU:** NVIDIA GeForce RTX 5090 Laptop GPU (24 GB VRAM)
- **OS:** Windows 11 Home 64 bits
- **Arquitectura:** x64

### Software
- **Python:** 3.10.19
- **Conda:** 24.1.2
- **PyTorch:** 2.5.1+cu121
- **CUDA:** 12.1
- **Whisper:** 20250625

## Arquitectura del Proyecto

### Módulos Principales

#### `src/transcriber.py`
- Clase `WhisperTranscriber`
- Maneja carga de modelos
- Detección automática GPU/CPU
- Transcripción con parámetros configurables

#### `src/audio_loader.py`
- Clase `AudioLoader`
- Carga archivos individuales o carpetas
- Soporte para múltiples formatos
- Extracción de ZIP

#### `src/utils.py`
- Funciones auxiliares
- Sanitización de nombres
- Guardado de transcripciones (TXT, JSON, SRT, VTT)
- Sistema de logging

#### `src/violence_detector.py`
- Clase `ViolenceDetector`
- Detección de patrones de violencia
- Análisis de segmentos y transcripciones completas
- Identificación de víctimas mencionadas

#### `pipeline_transcripcion.py`
- Clase `PipelineTranscripcion`
- Orquesta todo el proceso
- Copia de archivos
- Transcripción y análisis
- Generación de resultados

## Modelos de Whisper

### Modelos Disponibles

| Modelo | Parámetros | Memoria GPU | Velocidad | Precisión |
|--------|-----------|-------------|-----------|-----------|
| tiny   | 39M       | ~1 GB       | Muy rápida | Baja      |
| base   | 74M       | ~1 GB       | Rápida    | Media     |
| small  | 244M      | ~2 GB       | Media     | Buena     |
| medium | 769M      | ~5 GB       | Lenta     | Muy buena |
| large-v3 | 1550M   | ~10 GB      | Muy lenta | Excelente |

### Modelo Configurado: large-v3

- **Razón:** Máxima precisión para análisis de violencia verbal
- **Requisitos:** GPU con al menos 10 GB VRAM (RTX 5090 tiene 24 GB)
- **Rendimiento:** ~1-2x tiempo real en GPU

## Configuración CUDA

### Versión CUDA
- **Instalada:** 12.1
- **PyTorch:** Compilado con CUDA 12.1
- **GPU:** RTX 5090 (sm_120) - Advertencia de compatibilidad menor, pero funcional

### Optimizaciones
- **FP16:** Habilitado (precisión de 16 bits, más rápido)
- **Device:** CUDA forzado
- **Memory Management:** Automático por PyTorch

## Formatos de Salida

### TXT (Texto Plano)
```
Texto completo sin formato
```

### Timestamps
```
[00:15] Primera frase transcrita
[00:32] Segunda frase transcrita
```

### JSON
```json
{
  "archivo": "audio.mp3",
  "speaker": "desconocido",
  "contiene_insultos": true,
  "victima_mencionada": ["Claudia"],
  "momentos_agresion": [
    {
      "texto": "...",
      "minuto_segundo": "02:15",
      "tipo": "insulto"
    }
  ]
}
```

## Detección de Violencia

### Patrones Detectados

1. **Insultos**
   - Palabras ofensivas directas
   - Groserías y términos despectivos

2. **Manipulación Emocional**
   - Frases que buscan generar culpa
   - Negación de emociones válidas

3. **Gaslighting**
   - Negación de eventos
   - Hacer dudar de la memoria/percepción

4. **Amenazas**
   - Implícitas o explícitas
   - Referencias a consecuencias

5. **Denigración**
   - Específica hacia Claudia
   - Combinación de nombre + insulto

### Víctimas Identificadas
- Claudia (variantes: claudia, clau)
- Juan Diego (variantes: juan diego, juan, diego)
- José Carlos (variantes: josé carlos, jose carlos, josé, jose, carlos)

## Rendimiento

### Tiempos Estimados (GPU RTX 5090)

| Modelo | Audio 1 min | Audio 10 min | Audio 60 min |
|--------|-------------|--------------|--------------|
| tiny   | ~5 seg      | ~30 seg      | ~3 min       |
| base   | ~10 seg     | ~1 min       | ~6 min       |
| small  | ~20 seg     | ~3 min       | ~15 min      |
| medium | ~40 seg     | ~6 min       | ~35 min      |
| large-v3 | ~1 min    | ~10 min      | ~60 min      |

### Factores que Afectan Velocidad
- Longitud del audio
- Calidad del audio
- Ruido de fondo
- Modelo seleccionado
- Uso de GPU vs CPU

## Logging

### Niveles de Log
- **INFO:** Operaciones normales
- **WARNING:** Advertencias (archivos no encontrados, etc.)
- **ERROR:** Errores en procesamiento
- **DEBUG:** Información detallada (no habilitado por defecto)

### Ubicación de Logs
- Carpeta: `logs/`
- Formato: `transcripcion_YYYYMMDD_HHMMSS.log`
- Codificación: UTF-8

## Limitaciones Conocidas

1. **GPU RTX 5090:** Advertencia de compatibilidad sm_120, pero funciona
2. **Modelo large-v3:** Requiere mucha memoria, puede fallar en audios muy largos
3. **Detección de violencia:** Basada en patrones, puede tener falsos positivos/negativos
4. **Idioma:** Optimizado para español, otros idiomas pueden tener menor precisión

## Mejoras Futuras

- [ ] Soporte para faster-whisper (más rápido)
- [ ] Detección de múltiples speakers
- [ ] Análisis de sentimiento
- [ ] Exportación a más formatos
- [ ] Interfaz gráfica

---

**Última actualización:** Diciembre 2025





