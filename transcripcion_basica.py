"""
Script simple para transcripción básica de audio a texto
Funcionalidad original del proyecto - Sin análisis adicionales
"""

import os
import sys
import time
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.transcriber import WhisperTranscriber
from src.audio_loader import AudioLoader
from src.utils import (
    crear_carpetas,
    guardar_transcripcion,
    configurar_logging,
    obtener_tamaño_archivo
)
import logging


def main():
    """Función principal - Solo transcripción básica"""
    
    # Configurar rutas
    # Puedes cambiar esta ruta a tu carpeta de audios
    CARPETA_AUDIOS = r"C:\Users\hanns\Proyectos\whisper-pro\audios"
    
    # Ruta para transcripciones
    CARPETA_TRANSCRIPCIONES = r"C:\Users\hanns\Proyectos\whisper-pro\transcripciones"
    CARPETA_LOGS = 'logs'
    CARPETA_MODELOS = 'modelos'
    
    # Mostrar rutas por consola
    print(f"📁 Carpeta de entrada: {CARPETA_AUDIOS}")
    print(f"📁 Carpeta de salida: {CARPETA_TRANSCRIPCIONES}")
    print()
    
    # Crear carpetas necesarias
    crear_carpetas(CARPETA_TRANSCRIPCIONES, CARPETA_LOGS, CARPETA_MODELOS)
    
    # Configurar logging
    logger = configurar_logging(CARPETA_LOGS)
    logger.info("=" * 60)
    logger.info("Transcripción Básica - Sin Análisis Adicionales")
    logger.info("=" * 60)
    
    # Configuración del transcriptor
    MODELO = os.getenv('WHISPER_MODEL', 'base')  # tiny, base, small, medium, large-v3
    IDIOMA = os.getenv('WHISPER_LANGUAGE', None)  # None = detección automática, o 'es', 'en', 'pt', etc.
    FORMATO_SALIDA = os.getenv('WHISPER_FORMAT', 'txt')  # txt, json, srt, vtt
    
    print(f"⚙️  Modelo: {MODELO}")
    print(f"⚙️  Idioma: {IDIOMA if IDIOMA else 'Detección automática'}")
    print(f"⚙️  Formato: {FORMATO_SALIDA}")
    print()
    
    try:
        # Inicializar transcriptor
        logger.info(f"Configurando transcriptor con modelo: {MODELO}")
        transcriptor = WhisperTranscriber(modelo=MODELO)
        
        # Mostrar información del dispositivo
        info = transcriptor.obtener_info_modelo()
        logger.info(f"Dispositivo: {info['dispositivo']}")
        if info['gpu_disponible']:
            logger.info(f"GPU: {info.get('gpu_nombre', 'N/A')}")
            logger.info(f"Memoria GPU: {info.get('gpu_memoria_total_gb', 0):.2f} GB")
        
        print(f"💻 Dispositivo: {info['dispositivo']}")
        if info['gpu_disponible']:
            print(f"🎮 GPU: {info.get('gpu_nombre', 'N/A')}")
        print()
        
        # Cargar archivos de audio
        logger.info(f"Buscando archivos de audio en: {CARPETA_AUDIOS}")
        loader = AudioLoader()
        archivos_audio = loader.cargar_carpeta(CARPETA_AUDIOS, recursivo=True)
        
        if not archivos_audio:
            logger.warning(f"No se encontraron archivos de audio en {CARPETA_AUDIOS}")
            print(f"❌ No se encontraron archivos de audio en: {CARPETA_AUDIOS}")
            print("   Verifica que la carpeta existe y contiene archivos de audio.")
            return
        
        # Filtrar formatos comunes
        formatos_soportados = ('.mp3', '.m4a', '.wav', '.ogg', '.flac', '.mp4', '.avi', '.mkv', '.mov')
        archivos_audio = [f for f in archivos_audio if f.lower().endswith(formatos_soportados)]
        
        if not archivos_audio:
            logger.warning(f"No se encontraron archivos de audio soportados en {CARPETA_AUDIOS}")
            print(f"❌ No se encontraron archivos de audio soportados.")
            print(f"   Formatos soportados: {', '.join(formatos_soportados)}")
            return
        
        logger.info(f"Encontrados {len(archivos_audio)} archivo(s) para procesar")
        print(f"📊 Encontrados {len(archivos_audio)} archivo(s) para procesar")
        print()
        
        # Procesar cada archivo
        tiempo_inicio_total = time.time()
        exitosos = 0
        fallidos = 0
        
        for i, archivo_audio in enumerate(archivos_audio, 1):
            logger.info("-" * 60)
            logger.info(f"Procesando archivo {i}/{len(archivos_audio)}: {os.path.basename(archivo_audio)}")
            logger.info(f"Tamaño: {obtener_tamaño_archivo(archivo_audio)}")
            
            print(f"[{i}/{len(archivos_audio)}] {os.path.basename(archivo_audio)}")
            
            tiempo_inicio = time.time()
            
            try:
                # Transcribir audio
                logger.info("Transcribiendo audio...")
                resultado = transcriptor.transcribir(
                    archivo_audio,
                    idioma=IDIOMA,
                    verbose=False
                )
                
                # Guardar transcripción
                ruta_guardada = guardar_transcripcion(
                    resultado,
                    archivo_audio,
                    CARPETA_TRANSCRIPCIONES,
                    formato=FORMATO_SALIDA
                )
                
                tiempo_transcripcion = time.time() - tiempo_inicio
                
                # Mostrar resumen
                texto = resultado.get('text', '')
                idioma_detectado = resultado.get('language', 'desconocido')
                duracion_audio = resultado.get('segments', [{}])[-1].get('end', 0) if resultado.get('segments') else 0
                
                logger.info(f"✓ Transcripción completada en {tiempo_transcripcion:.2f} segundos")
                logger.info(f"  Idioma detectado: {idioma_detectado}")
                logger.info(f"  Duración del audio: {duracion_audio:.2f} segundos")
                logger.info(f"  Caracteres transcritos: {len(texto)}")
                logger.info(f"  Guardado en: {ruta_guardada}")
                
                print(f"  ✅ Completado en {tiempo_transcripcion:.1f}s")
                print(f"  📝 Idioma: {idioma_detectado} | Duración: {duracion_audio:.1f}s | Caracteres: {len(texto)}")
                print(f"  💾 Guardado: {os.path.basename(ruta_guardada)}")
                print()
                
                exitosos += 1
                
            except Exception as e:
                tiempo_transcripcion = time.time() - tiempo_inicio
                logger.error(f"✗ Error al transcribir {os.path.basename(archivo_audio)}: {str(e)}")
                logger.exception("Detalles del error:")
                print(f"  ❌ Error: {str(e)}")
                print()
                fallidos += 1
        
        # Resumen final
        tiempo_total = time.time() - tiempo_inicio_total
        logger.info("=" * 60)
        logger.info("Proceso de transcripción finalizado")
        logger.info(f"Total de archivos: {len(archivos_audio)}")
        logger.info(f"Exitosos: {exitosos}")
        logger.info(f"Fallidos: {fallidos}")
        logger.info(f"Tiempo total: {tiempo_total:.2f} segundos ({tiempo_total/60:.2f} minutos)")
        if exitosos > 0:
            logger.info(f"Tiempo promedio por archivo: {tiempo_total/exitosos:.2f} segundos")
        logger.info("=" * 60)
        
        print("=" * 60)
        print("✅ Proceso completado")
        print(f"   Total: {len(archivos_audio)} | Exitosos: {exitosos} | Fallidos: {fallidos}")
        print(f"   Tiempo total: {tiempo_total/60:.1f} minutos")
        if exitosos > 0:
            print(f"   Tiempo promedio: {tiempo_total/exitosos:.1f} segundos por archivo")
        print("=" * 60)
        
    except KeyboardInterrupt:
        logger.warning("\nProceso interrumpido por el usuario")
        print("\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error fatal: {str(e)}")
        logger.exception("Detalles del error:")
        print(f"\n❌ Error fatal: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()

