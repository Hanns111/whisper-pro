# 📝 Instrucciones para Hans

## Configuración del Sistema

### Entorno Conda

El proyecto usa el entorno conda `whisper-env` con Python 3.10.19.

**Activar entorno:**
```powershell
conda activate whisper-env
```

**Verificar que está activo:**
```powershell
conda info --envs
# Debe mostrar whisper-env con asterisco (*)
```

### Dependencias Instaladas

- ✅ openai-whisper (20250625)
- ✅ torch (2.5.1+cu121) con soporte CUDA
- ✅ ffmpeg-python
- ✅ numpy, numba, tiktoken, tqdm

**Verificar CUDA:**
```powershell
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0))"
```

## Uso del Sistema

### Opción 1: Transcripción Básica

Para transcribir archivos que ya están en `audios/`:

```powershell
python run_transcription.py
```

**Configuración:**
- Modelo: `base` (puede cambiarse en el script)
- Idioma: Detección automática
- Formato salida: `txt`

### Opción 2: Pipeline Avanzado

Para procesar audios desde la carpeta de origen con análisis completo:

```powershell
python pipeline_transcripcion.py
```

**Este pipeline:**
1. Copia automáticamente audios desde:
   `C:\Users\hanns\Downloads\Audios de Lars -20251203T004029Z-1-001\Audios de Lars`
2. Los copia a `audios/`
3. Transcribe con modelo `large-v3` en GPU
4. Genera:
   - Transcripción en español (texto limpio)
   - Traducción al inglés
   - Archivo con timestamps por frase
   - JSON con análisis de violencia

## Estructura de Salida

Cada archivo procesado genera:

1. `{nombre}_{timestamp}_transcripcion_es.txt`
   - Texto completo en español

2. `{nombre}_{timestamp}_traduccion_en.txt`
   - Traducción completa al inglés

3. `{nombre}_{timestamp}_timestamps.txt`
   - Texto con timestamps por frase: `[MM:SS] texto`

4. `{nombre}_{timestamp}_analisis.json`
   - Análisis completo con:
     - Contiene insultos: true/false
     - Víctimas mencionadas: []
     - Momentos de agresión: []

## Análisis de Violencia Verbal

El sistema detecta automáticamente:

- **Insultos**: Palabras ofensivas y groserías
- **Manipulación emocional**: Frases que buscan controlar emocionalmente
- **Gaslighting**: Negación de la realidad, hacer dudar
- **Amenazas**: Frases que implican daño o consecuencias
- **Denigración**: Específicamente hacia Claudia
- **Menciones**: Detecta cuando se menciona a Claudia, Juan Diego o José Carlos

## Configuración Avanzada

### Cambiar Modelo

Edita `pipeline_transcripcion.py`:
```python
MODELO = 'large-v3'  # Cambiar a: tiny, base, small, medium, large-v3
```

### Cambiar Carpeta de Origen

Edita `pipeline_transcripcion.py`:
```python
CARPETA_ORIGEN = r"ruta\a\tu\carpeta"
```

### Usar CPU en lugar de GPU

Edita `pipeline_transcripcion.py`:
```python
DISPOSITIVO = 'cpu'
```

## Solución de Problemas

### Error: "CUDA out of memory"
- El modelo `large-v3` requiere mucha memoria
- Cierra otras aplicaciones que usen GPU
- Considera usar `medium` o `small`

### Error: "Carpeta de origen no existe"
- Verifica la ruta en `pipeline_transcripcion.py`
- Asegúrate de que la carpeta existe

### Transcripciones lentas
- Verifica que CUDA esté funcionando
- El modelo `large-v3` es el más lento pero más preciso
- Para velocidad, usa `base` o `small`

## Logs

Todos los procesos se registran en `logs/`:
- Fecha y hora de cada operación
- Errores y advertencias
- Tiempos de procesamiento
- Estadísticas finales

## Próximos Pasos

1. Revisa la configuración en `pipeline_transcripcion.py`
2. Verifica que la carpeta de origen existe
3. Ejecuta el pipeline cuando estés listo
4. Revisa los resultados en `transcripciones/`

---

**Nota:** El sistema está configurado pero NO ejecutará transcripciones hasta que lo ordenes explícitamente.





