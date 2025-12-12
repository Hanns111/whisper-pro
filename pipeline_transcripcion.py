"""
Pipeline avanzado de transcripción con detección de violencia verbal
Procesa audios desde carpeta de origen, los copia y transcribe con análisis completo
"""

import os
import sys
import shutil
import time
import json
from pathlib import Path
from typing import List, Dict, Any

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.transcriber import WhisperTranscriber
from src.audio_loader import AudioLoader
from src.utils import crear_carpetas, sanitizar_nombre, configurar_logging, obtener_tamaño_archivo
from src.violence_detector import ViolenceDetector
import logging


class PipelineTranscripcion:
    """
    Pipeline completo para transcripción con análisis de violencia
    """
    
    def __init__(
        self,
        carpeta_origen: str,
        carpeta_audios: str = 'audios',
        carpeta_transcripciones: str = 'transcripciones',
        carpeta_logs: str = 'logs',
        modelo: str = 'large-v3',
        dispositivo: str = 'cuda',
        fp16: bool = True
    ):
        """
        Inicializa el pipeline
        
        Args:
            carpeta_origen: Carpeta de donde copiar los audios
            carpeta_audios: Carpeta donde copiar los audios
            carpeta_transcripciones: Carpeta donde guardar transcripciones
            carpeta_logs: Carpeta donde guardar logs
            modelo: Modelo de Whisper a usar
            dispositivo: 'cuda' o 'cpu'
            fp16: Usar precisión de 16 bits (más rápido en GPU)
        """
        self.carpeta_origen = carpeta_origen
        self.carpeta_audios = carpeta_audios
        self.carpeta_transcripciones = carpeta_transcripciones
        self.carpeta_logs = carpeta_logs
        
        # Crear carpetas necesarias
        crear_carpetas(carpeta_audios, carpeta_transcripciones, carpeta_logs)
        
        # Configurar logging
        self.logger = configurar_logging(carpeta_logs, nivel=logging.INFO)
        self.logger.info("=" * 80)
        self.logger.info("Iniciando Pipeline de Transcripción Avanzado")
        self.logger.info("=" * 80)
        
        # Inicializar componentes
        self.logger.info(f"Inicializando transcriptor con modelo: {modelo}")
        # Si dispositivo es None, dejar que WhisperTranscriber detecte automáticamente
        dispositivo_transcriber = dispositivo if dispositivo else None
        self.transcriptor = WhisperTranscriber(
            modelo=modelo,
            dispositivo=dispositivo_transcriber
        )
        
        # Mostrar información del dispositivo
        info = self.transcriptor.obtener_info_modelo()
        self.logger.info(f"Dispositivo: {info['dispositivo']}")
        if info['gpu_disponible']:
            self.logger.info(f"GPU: {info.get('gpu_nombre', 'N/A')}")
            self.logger.info(f"Memoria GPU: {info.get('gpu_memoria_total_gb', 0):.2f} GB")
        
        self.audio_loader = AudioLoader()
        self.detector_violencia = ViolenceDetector()
        
        self.modelo = modelo
        self.dispositivo = dispositivo
        self.fp16 = fp16
    
    def copiar_audios_desde_origen(self) -> List[str]:
        """
        Copia archivos de audio desde la carpeta de origen a audios/
        
        Returns:
            Lista de rutas a archivos copiados
        """
        if not os.path.exists(self.carpeta_origen):
            self.logger.warning(f"Carpeta de origen no existe: {self.carpeta_origen}")
            return []
        
        self.logger.info(f"Buscando audios en: {self.carpeta_origen}")
        archivos_origen = self.audio_loader.cargar_carpeta(self.carpeta_origen, recursivo=True)
        
        if not archivos_origen:
            self.logger.warning(f"No se encontraron archivos de audio en {self.carpeta_origen}")
            return []
        
        self.logger.info(f"Encontrados {len(archivos_origen)} archivo(s) en origen")
        
        archivos_copiados = []
        
        for archivo_origen in archivos_origen:
            nombre_archivo = os.path.basename(archivo_origen)
            nombre_sanitizado = sanitizar_nombre(nombre_archivo)
            ruta_destino = os.path.join(self.carpeta_audios, nombre_sanitizado)
            
            # Si el archivo ya existe, agregar timestamp
            if os.path.exists(ruta_destino):
                nombre_base = Path(nombre_sanitizado).stem
                extension = Path(nombre_sanitizado).suffix
                timestamp = int(time.time())
                nombre_sanitizado = f"{nombre_base}_{timestamp}{extension}"
                ruta_destino = os.path.join(self.carpeta_audios, nombre_sanitizado)
            
            try:
                shutil.copy2(archivo_origen, ruta_destino)
                archivos_copiados.append(ruta_destino)
                self.logger.info(f"Copiado: {nombre_archivo} -> {nombre_sanitizado}")
            except Exception as e:
                self.logger.error(f"Error al copiar {archivo_origen}: {str(e)}")
        
        self.logger.info(f"Total de archivos copiados: {len(archivos_copiados)}")
        return archivos_copiados
    
    def transcribir_archivo(
        self,
        ruta_audio: str
    ) -> Dict[str, Any]:
        """
        Transcribe un archivo con traducción y análisis
        
        Args:
            ruta_audio: Ruta al archivo de audio
            
        Returns:
            Diccionario con transcripción, traducción y análisis
        """
        nombre_archivo = os.path.basename(ruta_audio)
        self.logger.info("-" * 80)
        self.logger.info(f"Procesando: {nombre_archivo}")
        self.logger.info(f"Tamaño: {obtener_tamaño_archivo(ruta_audio)}")
        
        tiempo_inicio = time.time()
        
        try:
            # Transcripción en español
            self.logger.info("Transcribiendo en español...")
            resultado_es = self.transcriptor.transcribir(
                ruta_audio,
                idioma='es',
                task='transcribe',
                fp16=self.fp16,
                verbose=False
            )
            
            # Traducción al inglés
            self.logger.info("Traduciendo al inglés...")
            resultado_en = self.transcriptor.transcribir(
                ruta_audio,
                idioma='es',
                task='translate',
                fp16=self.fp16,
                verbose=False
            )
            
            # Análisis de violencia
            self.logger.info("Analizando violencia verbal...")
            analisis = self.detector_violencia.analizar_transcripcion_completa(resultado_es)
            
            tiempo_procesamiento = time.time() - tiempo_inicio
            
            self.logger.info(f"✓ Procesamiento completado en {tiempo_procesamiento:.2f} segundos")
            self.logger.info(f"  Momentos de agresión detectados: {analisis['total_momentos_agresion']}")
            self.logger.info(f"  Víctimas mencionadas: {', '.join(analisis['victima_mencionada']) if analisis['victima_mencionada'] else 'Ninguna'}")
            
            return {
                'archivo': nombre_archivo,
                'transcripcion_es': resultado_es,
                'traduccion_en': resultado_en,
                'analisis': analisis,
                'tiempo_procesamiento': tiempo_procesamiento
            }
            
        except Exception as e:
            self.logger.error(f"✗ Error al procesar {nombre_archivo}: {str(e)}")
            self.logger.exception("Detalles del error:")
            raise
    
    def guardar_resultados(
        self,
        resultado: Dict[str, Any],
        ruta_audio: str
    ) -> Dict[str, str]:
        """
        Guarda todos los resultados de la transcripción
        
        Args:
            resultado: Resultado del procesamiento
            ruta_audio: Ruta al archivo de audio original
            
        Returns:
            Diccionario con rutas de archivos guardados
        """
        nombre_base = Path(sanitizar_nombre(os.path.basename(ruta_audio))).stem
        timestamp = int(time.time())
        prefijo = f"{nombre_base}_{timestamp}"
        
        archivos_guardados = {}
        
        # 1. Transcripción en español (texto limpio)
        ruta_txt_es = os.path.join(self.carpeta_transcripciones, f"{prefijo}_transcripcion_es.txt")
        with open(ruta_txt_es, 'w', encoding='utf-8') as f:
            f.write(resultado['transcripcion_es']['text'])
        archivos_guardados['transcripcion_es'] = ruta_txt_es
        
        # 2. Traducción al inglés
        ruta_txt_en = os.path.join(self.carpeta_transcripciones, f"{prefijo}_traduccion_en.txt")
        with open(ruta_txt_en, 'w', encoding='utf-8') as f:
            f.write(resultado['traduccion_en']['text'])
        archivos_guardados['traduccion_en'] = ruta_txt_en
        
        # 3. Archivo .txt con timestamps por frase
        ruta_timestamps = os.path.join(self.carpeta_transcripciones, f"{prefijo}_timestamps.txt")
        with open(ruta_timestamps, 'w', encoding='utf-8') as f:
            for segmento in resultado['transcripcion_es'].get('segments', []):
                inicio = self._formatear_tiempo(segmento.get('start', 0))
                texto = segmento.get('text', '').strip()
                f.write(f"[{inicio}] {texto}\n")
        archivos_guardados['timestamps'] = ruta_timestamps
        
        # 4. Archivo JSON completo
        json_data = {
            'archivo': resultado['archivo'],
            'speaker': 'desconocido',
            'contiene_insultos': resultado['analisis']['contiene_insultos'],
            'victima_mencionada': resultado['analisis']['victima_mencionada'],
            'momentos_agresion': resultado['analisis']['momentos_agresion']
        }
        
        ruta_json = os.path.join(self.carpeta_transcripciones, f"{prefijo}_analisis.json")
        with open(ruta_json, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        archivos_guardados['json'] = ruta_json
        
        return archivos_guardados
    
    def _formatear_tiempo(self, segundos: float) -> str:
        """Formatea tiempo en formato MM:SS"""
        minutos = int(segundos // 60)
        segs = int(segundos % 60)
        return f"{minutos:02d}:{segs:02d}"
    
    def ejecutar(self):
        """Ejecuta el pipeline completo"""
        try:
            # 1. Copiar audios desde origen
            archivos = self.copiar_audios_desde_origen()
            
            if not archivos:
                self.logger.warning("No hay archivos para procesar")
                return
            
            # 2. Procesar cada archivo
            tiempo_inicio_total = time.time()
            exitosos = 0
            fallidos = 0
            
            for archivo in archivos:
                try:
                    resultado = self.transcribir_archivo(archivo)
                    archivos_guardados = self.guardar_resultados(resultado, archivo)
                    
                    self.logger.info(f"Archivos guardados:")
                    for tipo, ruta in archivos_guardados.items():
                        self.logger.info(f"  - {tipo}: {os.path.basename(ruta)}")
                    
                    exitosos += 1
                    
                except Exception as e:
                    self.logger.error(f"Error al procesar {archivo}: {str(e)}")
                    fallidos += 1
            
            # Resumen final
            tiempo_total = time.time() - tiempo_inicio_total
            self.logger.info("=" * 80)
            self.logger.info("Pipeline completado")
            self.logger.info(f"Total de archivos: {len(archivos)}")
            self.logger.info(f"Exitosos: {exitosos}")
            self.logger.info(f"Fallidos: {fallidos}")
            self.logger.info(f"Tiempo total: {tiempo_total:.2f} segundos ({tiempo_total/60:.2f} minutos)")
            if exitosos > 0:
                self.logger.info(f"Tiempo promedio por archivo: {tiempo_total/exitosos:.2f} segundos")
            self.logger.info("=" * 80)
            
        except KeyboardInterrupt:
            self.logger.warning("\nPipeline interrumpido por el usuario")
        except Exception as e:
            self.logger.error(f"Error fatal: {str(e)}")
            self.logger.exception("Detalles del error:")


def main():
    """Función principal"""
    # Configuración
    CARPETA_ORIGEN = r"C:\Users\hanns\Downloads\Audios de Lars -20251203T004029Z-1-001\Audios de Lars"
    CARPETA_AUDIOS = 'audios'
    CARPETA_TRANSCRIPCIONES = 'transcripciones'
    CARPETA_LOGS = 'logs'
    MODELO = 'large-v3'
    # RTX 5090 (sm_120) no es compatible con PyTorch actual, usar CPU
    # DISPOSITIVO = 'cuda'  # Deshabilitado temporalmente
    DISPOSITIVO = 'cpu'  # Forzar CPU hasta que PyTorch soporte RTX 5090
    FP16 = False  # FP16 requiere CUDA, deshabilitado en CPU
    
    # Crear y ejecutar pipeline
    pipeline = PipelineTranscripcion(
        carpeta_origen=CARPETA_ORIGEN,
        carpeta_audios=CARPETA_AUDIOS,
        carpeta_transcripciones=CARPETA_TRANSCRIPCIONES,
        carpeta_logs=CARPETA_LOGS,
        modelo=MODELO,
        dispositivo=DISPOSITIVO,
        fp16=FP16
    )
    
    pipeline.ejecutar()


if __name__ == '__main__':
    main()

