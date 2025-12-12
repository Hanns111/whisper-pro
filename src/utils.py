"""
Utilidades generales para el proyecto
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import logging


def crear_carpetas(*carpetas: str) -> None:
    """
    Crea carpetas si no existen
    
    Args:
        *carpetas: Rutas de carpetas a crear
    """
    for carpeta in carpetas:
        os.makedirs(carpeta, exist_ok=True)


def sanitizar_nombre(nombre: str, max_longitud: int = 200) -> str:
    """
    Sanitiza un nombre de archivo eliminando caracteres inválidos
    
    Args:
        nombre: Nombre a sanitizar
        max_longitud: Longitud máxima del nombre
        
    Returns:
        Nombre sanitizado
    """
    # Obtener nombre sin extensión
    nombre_base = Path(nombre).stem
    extension = Path(nombre).suffix
    
    # Reemplazar caracteres inválidos
    nombre_limpio = re.sub(r'[<>:"/\\|?*]', '_', nombre_base)
    
    # Eliminar espacios al inicio y final
    nombre_limpio = nombre_limpio.strip()
    
    # Reemplazar múltiples espacios/guiones bajos con uno solo
    nombre_limpio = re.sub(r'[\s_]+', '_', nombre_limpio)
    
    # Limitar longitud
    if len(nombre_limpio) > max_longitud:
        nombre_limpio = nombre_limpio[:max_longitud]
    
    # Si quedó vacío, usar nombre por defecto
    if not nombre_limpio:
        nombre_limpio = "archivo"
    
    return nombre_limpio + extension


def guardar_transcripcion(
    resultado: Dict[str, Any],
    ruta_audio: str,
    carpeta_destino: str,
    formato: str = 'txt'
) -> str:
    """
    Guarda una transcripción en un archivo
    
    Args:
        resultado: Resultado de la transcripción de Whisper
        ruta_audio: Ruta al archivo de audio original
        carpeta_destino: Carpeta donde guardar la transcripción
        formato: Formato de salida ('txt', 'json', 'srt', 'vtt')
        
    Returns:
        Ruta al archivo guardado
    """
    # Crear carpeta si no existe
    crear_carpetas(carpeta_destino)
    
    # Obtener nombre base del archivo de audio
    nombre_base = sanitizar_nombre(os.path.basename(ruta_audio))
    nombre_sin_extension = Path(nombre_base).stem
    
    # Generar nombre del archivo de salida
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_salida = f"{nombre_sin_extension}_{timestamp}"
    
    if formato == 'txt':
        ruta_salida = os.path.join(carpeta_destino, f"{nombre_salida}.txt")
        texto = resultado.get('text', '')
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            f.write(texto)
    
    elif formato == 'json':
        ruta_salida = os.path.join(carpeta_destino, f"{nombre_salida}.json")
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
    
    elif formato == 'srt':
        ruta_salida = os.path.join(carpeta_destino, f"{nombre_salida}.srt")
        srt_content = _generar_srt(resultado)
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            f.write(srt_content)
    
    elif formato == 'vtt':
        ruta_salida = os.path.join(carpeta_destino, f"{nombre_salida}.vtt")
        vtt_content = _generar_vtt(resultado)
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            f.write(vtt_content)
    
    else:
        raise ValueError(f"Formato no soportado: {formato}")
    
    return ruta_salida


def _generar_srt(resultado: Dict[str, Any]) -> str:
    """
    Genera contenido SRT a partir del resultado de Whisper
    
    Args:
        resultado: Resultado de la transcripción
        
    Returns:
        Contenido SRT como string
    """
    segments = resultado.get('segments', [])
    srt_lines = []
    
    for i, segment in enumerate(segments, 1):
        inicio = _formatear_tiempo_srt(segment.get('start', 0))
        fin = _formatear_tiempo_srt(segment.get('end', 0))
        texto = segment.get('text', '').strip()
        
        srt_lines.append(f"{i}\n{inicio} --> {fin}\n{texto}\n")
    
    return "\n".join(srt_lines)


def _generar_vtt(resultado: Dict[str, Any]) -> str:
    """
    Genera contenido VTT a partir del resultado de Whisper
    
    Args:
        resultado: Resultado de la transcripción
        
    Returns:
        Contenido VTT como string
    """
    vtt_lines = ["WEBVTT", ""]
    segments = resultado.get('segments', [])
    
    for segment in segments:
        inicio = _formatear_tiempo_vtt(segment.get('start', 0))
        fin = _formatear_tiempo_vtt(segment.get('end', 0))
        texto = segment.get('text', '').strip()
        
        vtt_lines.append(f"{inicio} --> {fin}")
        vtt_lines.append(texto)
        vtt_lines.append("")
    
    return "\n".join(vtt_lines)


def _formatear_tiempo_srt(segundos: float) -> str:
    """
    Formatea tiempo en formato SRT (HH:MM:SS,mmm)
    
    Args:
        segundos: Tiempo en segundos
        
    Returns:
        Tiempo formateado
    """
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    segs = int(segundos % 60)
    milisegundos = int((segundos % 1) * 1000)
    
    return f"{horas:02d}:{minutos:02d}:{segs:02d},{milisegundos:03d}"


def _formatear_tiempo_vtt(segundos: float) -> str:
    """
    Formatea tiempo en formato VTT (HH:MM:SS.mmm)
    
    Args:
        segundos: Tiempo en segundos
        
    Returns:
        Tiempo formateado
    """
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    segs = int(segundos % 60)
    milisegundos = int((segundos % 1) * 1000)
    
    return f"{horas:02d}:{minutos:02d}:{segs:02d}.{milisegundos:03d}"


def configurar_logging(
    carpeta_logs: str,
    nivel: int = logging.INFO,
    nombre_archivo: Optional[str] = None
) -> logging.Logger:
    """
    Configura el sistema de logging
    
    Args:
        carpeta_logs: Carpeta donde guardar los logs
        nivel: Nivel de logging (logging.INFO, logging.DEBUG, etc.)
        nombre_archivo: Nombre del archivo de log. Si None, usa timestamp
        
    Returns:
        Logger configurado
    """
    # Crear carpeta de logs
    crear_carpetas(carpeta_logs)
    
    # Nombre del archivo de log
    if nombre_archivo is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"transcripcion_{timestamp}.log"
    
    ruta_log = os.path.join(carpeta_logs, nombre_archivo)
    
    # Configurar formato
    formato = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para archivo
    file_handler = logging.FileHandler(ruta_log, encoding='utf-8')
    file_handler.setLevel(nivel)
    file_handler.setFormatter(formato)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(nivel)
    console_handler.setFormatter(formato)
    
    # Configurar logger raíz
    logger = logging.getLogger()
    logger.setLevel(nivel)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def obtener_tamaño_archivo(ruta: str) -> str:
    """
    Obtiene el tamaño de un archivo en formato legible
    
    Args:
        ruta: Ruta al archivo
        
    Returns:
        Tamaño formateado (ej: "1.5 MB")
    """
    if not os.path.exists(ruta):
        return "0 B"
    
    tamaño_bytes = os.path.getsize(ruta)
    
    for unidad in ['B', 'KB', 'MB', 'GB']:
        if tamaño_bytes < 1024.0:
            return f"{tamaño_bytes:.2f} {unidad}"
        tamaño_bytes /= 1024.0
    
    return f"{tamaño_bytes:.2f} TB"





