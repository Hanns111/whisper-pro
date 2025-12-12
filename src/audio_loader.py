"""
Módulo para cargar y procesar archivos de audio
Soporta archivos individuales, carpetas y ZIP
"""

import os
import zipfile
from pathlib import Path
from typing import List, Optional
import logging


class AudioLoader:
    """
    Clase para cargar archivos de audio desde diferentes fuentes
    """
    
    # Formatos de audio soportados
    FORMATOS_AUDIO = {'.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac'}
    
    # Formatos de video soportados (de los que se puede extraer audio)
    FORMATOS_VIDEO = {'.mp4', '.avi', '.mkv', '.mov', '.webm', '.flv', '.m4v'}
    
    # Todos los formatos soportados
    FORMATOS_SOPORTADOS = FORMATOS_AUDIO | FORMATOS_VIDEO
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def es_audio_valido(self, ruta_archivo: str) -> bool:
        """
        Verifica si un archivo es un audio/video válido
        
        Args:
            ruta_archivo: Ruta al archivo
            
        Returns:
            True si el archivo es válido, False en caso contrario
        """
        extension = Path(ruta_archivo).suffix.lower()
        return extension in self.FORMATOS_SOPORTADOS
    
    def cargar_archivo(self, ruta_archivo: str) -> Optional[str]:
        """
        Carga un archivo de audio individual
        
        Args:
            ruta_archivo: Ruta al archivo de audio
            
        Returns:
            Ruta al archivo si es válido, None en caso contrario
        """
        if not os.path.exists(ruta_archivo):
            self.logger.warning(f"Archivo no encontrado: {ruta_archivo}")
            return None
        
        if not os.path.isfile(ruta_archivo):
            self.logger.warning(f"No es un archivo: {ruta_archivo}")
            return None
        
        if not self.es_audio_valido(ruta_archivo):
            self.logger.warning(f"Formato no soportado: {ruta_archivo}")
            return None
        
        return ruta_archivo
    
    def cargar_carpeta(self, ruta_carpeta: str, recursivo: bool = False) -> List[str]:
        """
        Carga todos los archivos de audio de una carpeta
        
        Args:
            ruta_carpeta: Ruta a la carpeta
            recursivo: Si True, busca en subcarpetas también
            
        Returns:
            Lista de rutas a archivos de audio válidos
        """
        if not os.path.exists(ruta_carpeta):
            self.logger.warning(f"Carpeta no encontrada: {ruta_carpeta}")
            return []
        
        if not os.path.isdir(ruta_carpeta):
            self.logger.warning(f"No es una carpeta: {ruta_carpeta}")
            return []
        
        archivos_encontrados = []
        
        if recursivo:
            # Búsqueda recursiva
            for raiz, directorios, archivos in os.walk(ruta_carpeta):
                for archivo in archivos:
                    ruta_completa = os.path.join(raiz, archivo)
                    if self.es_audio_valido(ruta_completa):
                        archivos_encontrados.append(ruta_completa)
        else:
            # Solo archivos en la carpeta raíz
            for archivo in os.listdir(ruta_carpeta):
                ruta_completa = os.path.join(ruta_carpeta, archivo)
                if os.path.isfile(ruta_completa) and self.es_audio_valido(ruta_completa):
                    archivos_encontrados.append(ruta_completa)
        
        self.logger.info(f"Encontrados {len(archivos_encontrados)} archivos de audio en {ruta_carpeta}")
        return archivos_encontrados
    
    def extraer_zip(self, ruta_zip: str, carpeta_destino: Optional[str] = None) -> List[str]:
        """
        Extrae archivos de audio de un archivo ZIP
        
        Args:
            ruta_zip: Ruta al archivo ZIP
            carpeta_destino: Carpeta donde extraer. Si None, usa la misma carpeta del ZIP
            
        Returns:
            Lista de rutas a archivos de audio extraídos
        """
        if not os.path.exists(ruta_zip):
            self.logger.warning(f"Archivo ZIP no encontrado: {ruta_zip}")
            return []
        
        if not zipfile.is_zipfile(ruta_zip):
            self.logger.warning(f"No es un archivo ZIP válido: {ruta_zip}")
            return []
        
        try:
            # Determinar carpeta de destino
            if carpeta_destino is None:
                carpeta_destino = os.path.join(
                    os.path.dirname(ruta_zip),
                    os.path.splitext(os.path.basename(ruta_zip))[0]
                )
            
            # Crear carpeta de destino si no existe
            os.makedirs(carpeta_destino, exist_ok=True)
            
            archivos_extraidos = []
            
            with zipfile.ZipFile(ruta_zip, 'r') as zip_ref:
                # Listar archivos en el ZIP
                archivos_zip = zip_ref.namelist()
                
                for archivo_zip in archivos_zip:
                    # Verificar que no sea una carpeta
                    if archivo_zip.endswith('/'):
                        continue
                    
                    # Verificar formato
                    if not self.es_audio_valido(archivo_zip):
                        continue
                    
                    # Extraer archivo
                    try:
                        ruta_destino = os.path.join(carpeta_destino, os.path.basename(archivo_zip))
                        zip_ref.extract(archivo_zip, carpeta_destino)
                        
                        # Si el archivo estaba en una subcarpeta, moverlo a la raíz
                        if os.path.dirname(archivo_zip):
                            ruta_original = os.path.join(carpeta_destino, archivo_zip)
                            if os.path.exists(ruta_original) and ruta_original != ruta_destino:
                                os.rename(ruta_original, ruta_destino)
                        
                        if os.path.exists(ruta_destino):
                            archivos_extraidos.append(ruta_destino)
                            self.logger.info(f"Extraído: {os.path.basename(archivo_zip)}")
                    
                    except Exception as e:
                        self.logger.warning(f"Error al extraer {archivo_zip}: {str(e)}")
                        continue
            
            self.logger.info(f"Extraídos {len(archivos_extraidos)} archivos de audio del ZIP")
            return archivos_extraidos
            
        except zipfile.BadZipFile:
            self.logger.error(f"Archivo ZIP corrupto: {ruta_zip}")
            return []
        except Exception as e:
            self.logger.error(f"Error al procesar ZIP {ruta_zip}: {str(e)}")
            return []
    
    def cargar(self, ruta: str, recursivo: bool = False, extraer_zip: bool = True) -> List[str]:
        """
        Carga archivos de audio desde una ruta (archivo, carpeta o ZIP)
        
        Args:
            ruta: Ruta al archivo, carpeta o ZIP
            recursivo: Si True, busca en subcarpetas (solo para carpetas)
            extraer_zip: Si True, extrae archivos de ZIP automáticamente
            
        Returns:
            Lista de rutas a archivos de audio
        """
        if not os.path.exists(ruta):
            self.logger.warning(f"Ruta no encontrada: {ruta}")
            return []
        
        # Si es un archivo ZIP
        if zipfile.is_zipfile(ruta) and extraer_zip:
            return self.extraer_zip(ruta)
        
        # Si es un archivo individual
        if os.path.isfile(ruta):
            archivo = self.cargar_archivo(ruta)
            return [archivo] if archivo else []
        
        # Si es una carpeta
        if os.path.isdir(ruta):
            return self.cargar_carpeta(ruta, recursivo)
        
        return []





