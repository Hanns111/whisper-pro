# ✅ Checklist de Verificación

## Pre-ejecución

Antes de ejecutar transcripciones, verifica:

### Entorno
- [ ] Entorno conda `whisper-env` está activo
- [ ] Python 3.10.19 está disponible
- [ ] Pip instala en el entorno correcto

### Dependencias
- [ ] openai-whisper instalado
- [ ] torch con CUDA instalado y funcionando
- [ ] ffmpeg accesible desde PATH
- [ ] numpy, numba, tiktoken, tqdm instalados

### GPU
- [ ] CUDA disponible: `torch.cuda.is_available()` = True
- [ ] GPU detectada: RTX 5090
- [ ] Memoria GPU suficiente (>10 GB para large-v3)

### Estructura del Proyecto
- [ ] Carpeta `audios/` existe
- [ ] Carpeta `transcripciones/` existe
- [ ] Carpeta `logs/` existe
- [ ] Carpeta `src/` con todos los módulos
- [ ] Archivo `pipeline_transcripcion.py` existe

### Configuración
- [ ] Carpeta de origen configurada correctamente
- [ ] Modelo configurado (large-v3 recomendado)
- [ ] Dispositivo configurado (cuda)

### Archivos de Origen
- [ ] Carpeta de origen existe
- [ ] Archivos de audio están en la carpeta de origen
- [ ] Formatos soportados (.mp3, .wav, .m4a, etc.)

## Post-ejecución

Después de ejecutar, verifica:

### Resultados
- [ ] Archivos copiados a `audios/`
- [ ] Transcripciones generadas en `transcripciones/`
- [ ] Logs generados en `logs/`

### Archivos por Audio
- [ ] `*_transcripcion_es.txt` generado
- [ ] `*_traduccion_en.txt` generado
- [ ] `*_timestamps.txt` generado
- [ ] `*_analisis.json` generado

### Calidad
- [ ] Transcripciones tienen contenido
- [ ] Timestamps son correctos
- [ ] Análisis de violencia detecta patrones
- [ ] JSON tiene estructura correcta

### Logs
- [ ] Log file creado
- [ ] No hay errores críticos en logs
- [ ] Tiempos de procesamiento registrados

## Verificación de Hardware

- [ ] GPU RTX 5090 detectada
- [ ] 24 GB VRAM disponible
- [ ] CUDA 12.1 funcionando
- [ ] PyTorch con soporte CUDA

## Verificación de Software

- [ ] Windows 11 Home 64 bits
- [ ] Python 3.10.19
- [ ] Conda 24.1.2
- [ ] FFmpeg instalado

## Estado del Sistema

### Antes de Ejecutar
```powershell
# Ejecutar estos comandos y verificar salidas
conda info --envs
python --version
python -c "import torch; print(torch.cuda.is_available())"
ffmpeg -version
```

### Después de Ejecutar
```powershell
# Verificar resultados
Get-ChildItem transcripciones\ | Measure-Object
Get-ChildItem logs\ | Select-Object -Last 1
```

## Problemas Comunes

### Si CUDA no está disponible:
- [ ] Verificar instalación de drivers NVIDIA
- [ ] Reinstalar torch con CUDA: `pip install torch --index-url https://download.pytorch.org/whl/cu121`

### Si falta memoria GPU:
- [ ] Cerrar otras aplicaciones
- [ ] Usar modelo más pequeño (medium o small)
- [ ] Procesar archivos uno por uno

### Si no encuentra archivos:
- [ ] Verificar ruta de carpeta origen
- [ ] Verificar que los archivos existen
- [ ] Verificar permisos de lectura

---

**Fecha de verificación:** _______________
**Verificado por:** _______________
**Estado:** ☐ Listo / ☐ Pendiente





