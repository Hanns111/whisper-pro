"""
Módulo de transcripción usando OpenAI Whisper
Soporta GPU (CUDA) y CPU automáticamente
"""

import os
import torch
import whisper
from typing import Optional, Dict, Any
import logging


class WhisperTranscriber:
    """
    Clase para transcribir audio usando Whisper con soporte GPU/CPU
    """
    
    # Modelos disponibles ordenados por tamaño y precisión
    MODELOS_DISPONIBLES = {
        'tiny': 'tiny',
        'base': 'base',
        'small': 'small',
        'medium': 'medium',
        'large-v3': 'large-v3'
    }
    
    def __init__(self, modelo: str = 'base', dispositivo: Optional[str] = None):
        """
        Inicializa el transcriptor Whisper
        
        Args:
            modelo: Nombre del modelo a usar (tiny, base, small, medium, large-v3)
            dispositivo: Dispositivo forzado ('cuda' o 'cpu'). Si None, detecta automáticamente
        """
        self.modelo_nombre = modelo
        self.modelo = None
        self.logger = logging.getLogger(__name__)
        self.dispositivo = self._detectar_dispositivo(dispositivo)
        
        self._cargar_modelo()
    
    def _detectar_dispositivo(self, dispositivo_forzado: Optional[str] = None) -> str:
        """
        Detecta automáticamente si hay GPU disponible
        
        Args:
            dispositivo_forzado: Dispositivo forzado por el usuario
            
        Returns:
            'cuda' si hay GPU disponible, 'cpu' en caso contrario
        """
        if dispositivo_forzado:
            return dispositivo_forzado
        
        if torch.cuda.is_available():
            self.logger.info(f"GPU detectada: {torch.cuda.get_device_name(0)}")
            self.logger.info(f"Memoria GPU disponible: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
            return 'cuda'
        else:
            self.logger.info("No se detectó GPU, usando CPU")
            return 'cpu'
    
    def _cargar_modelo(self):
        """Carga el modelo Whisper en el dispositivo correspondiente"""
        try:
            self.logger.info(f"Cargando modelo '{self.modelo_nombre}' en {self.dispositivo}...")
            
            # Whisper detecta automáticamente el dispositivo según torch
            # pero podemos forzarlo moviendo el modelo después
            self.modelo = whisper.load_model(
                self.modelo_nombre,
                device=self.dispositivo
            )
            
            self.logger.info(f"Modelo '{self.modelo_nombre}' cargado exitosamente en {self.dispositivo}")
            
        except Exception as e:
            self.logger.error(f"Error al cargar el modelo: {str(e)}")
            raise
    
    def transcribir(
        self,
        ruta_audio: str,
        idioma: Optional[str] = None,
        task: str = 'transcribe',
        verbose: bool = False,
        fp16: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Transcribe un archivo de audio
        
        Args:
            ruta_audio: Ruta al archivo de audio
            idioma: Código de idioma (es, en, pt, etc.). None para detección automática
            task: 'transcribe' o 'translate' (traducir a inglés)
            verbose: Mostrar progreso detallado
            **kwargs: Argumentos adicionales para whisper.transcribe()
            
        Returns:
            Diccionario con la transcripción y metadatos
        """
        if not os.path.exists(ruta_audio):
            raise FileNotFoundError(f"El archivo no existe: {ruta_audio}")
        
        try:
            self.logger.info(f"Transcribiendo: {os.path.basename(ruta_audio)}")
            
            # Opciones de transcripción
            opciones = {
                'task': task,
                'verbose': verbose,
                'fp16': fp16,
                **kwargs
            }
            
            # Si se especifica idioma, forzarlo
            if idioma:
                opciones['language'] = idioma
                self.logger.info(f"Idioma forzado: {idioma}")
            else:
                self.logger.info("Detección automática de idioma")
            
            # Realizar transcripción
            resultado = self.modelo.transcribe(
                ruta_audio,
                **opciones
            )
            
            # Log del idioma detectado
            idioma_detectado = resultado.get('language', 'desconocido')
            self.logger.info(f"Idioma detectado: {idioma_detectado}")
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error al transcribir {ruta_audio}: {str(e)}")
            raise
    
    def obtener_info_modelo(self) -> Dict[str, Any]:
        """
        Obtiene información sobre el modelo y dispositivo actual
        
        Returns:
            Diccionario con información del modelo
        """
        info = {
            'modelo': self.modelo_nombre,
            'dispositivo': self.dispositivo,
            'gpu_disponible': torch.cuda.is_available()
        }
        
        if torch.cuda.is_available():
            info['gpu_nombre'] = torch.cuda.get_device_name(0)
            info['gpu_memoria_total_gb'] = torch.cuda.get_device_properties(0).total_memory / 1024**3
        
        return info

