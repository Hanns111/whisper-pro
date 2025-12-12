# ⚡ Comandos Rápidos

## Activación del Entorno

```powershell
conda activate whisper-env
```

## Verificación del Sistema

```powershell
# Verificar Python
python --version

# Verificar CUDA
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0))"

# Verificar Whisper
pip show openai-whisper

# Verificar FFmpeg
ffmpeg -version
```

## Transcripción Básica

```powershell
# Transcribir archivos en audios/
python run_transcription.py
```

## Pipeline Avanzado

```powershell
# Procesar desde carpeta origen con análisis completo
python pipeline_transcripcion.py
```

## Gestión de Archivos

```powershell
# Ver archivos en audios/
Get-ChildItem audios\

# Ver transcripciones generadas
Get-ChildItem transcripciones\

# Ver logs
Get-ChildItem logs\
```

## Configuración Rápida

### Cambiar Modelo (en pipeline_transcripcion.py)
```python
MODELO = 'base'  # tiny, base, small, medium, large-v3
```

### Cambiar Dispositivo (en pipeline_transcripcion.py)
```python
DISPOSITIVO = 'cpu'  # 'cuda' o 'cpu'
```

### Cambiar Carpeta Origen (en pipeline_transcripcion.py)
```python
CARPETA_ORIGEN = r"ruta\completa\a\tu\carpeta"
```

## Limpieza

```powershell
# Limpiar archivos copiados (mantener originales)
Remove-Item audios\* -Force

# Limpiar transcripciones
Remove-Item transcripciones\* -Force

# Limpiar logs antiguos
Remove-Item logs\*.log -Force
```

## Información del Sistema

```powershell
# Información de conda
conda info

# Entornos disponibles
conda info --envs

# Paquetes instalados
conda list

# Información de GPU
nvidia-smi
```

## Solución Rápida de Problemas

```powershell
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall

# Verificar espacio en disco
Get-PSDrive C

# Ver procesos usando GPU
nvidia-smi
```

---

**Nota:** Todos los comandos asumen que estás en el directorio del proyecto:
`C:\Users\hanns\Proyectos\whisper-pro`





