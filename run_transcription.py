"""
Script principal para transcribir todos los audios en la carpeta audios/
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
from src.analizador_agresion import AgresionAnalyzer
from src.detector_voz import VoiceStressDetector
from src.detector_victimas import VictimDetector
from src.analizador_forense_dk import AnalizadorForenseDK
from src.generador_informe_unico import GeneradorInformeUnico
import logging


def main():
    """Función principal"""
    
    # Configurar rutas
    # Ruta absoluta donde están los audios originales (NO se copian ni mueven)
    CARPETA_AUDIOS = r"C:\Users\hanns\Downloads\Audios-20251203T004026Z-1-001\Audios"
    
    # Ruta absoluta para transcripciones
    CARPETA_TRANSCRIPCIONES = r"C:\Users\hanns\Proyectos\whisper-pro\transcripciones"
    CARPETA_LOGS = 'logs'
    CARPETA_MODELOS = 'modelos'
    
    # Mostrar rutas por consola
    print(f"Usando carpeta de entrada: {CARPETA_AUDIOS}")
    print(f"Usando carpeta de salida: {CARPETA_TRANSCRIPCIONES}")
    
    # Crear carpetas necesarias (solo las de salida, no la de entrada)
    crear_carpetas(CARPETA_TRANSCRIPCIONES, CARPETA_LOGS, CARPETA_MODELOS)
    
    # Configurar logging
    logger = configurar_logging(CARPETA_LOGS)
    logger.info("=" * 60)
    logger.info("Iniciando proceso de transcripción")
    logger.info("=" * 60)
    
    # Configuración del transcriptor
    MODELO = os.getenv('WHISPER_MODEL', 'base')  # Puede cambiarse a: tiny, base, small, medium, large-v3
    IDIOMA = os.getenv('WHISPER_LANGUAGE', None)  # None = detección automática, o 'es', 'en', 'pt', etc.
    FORMATO_SALIDA = os.getenv('WHISPER_FORMAT', 'txt')  # txt, json, srt, vtt
    
    try:
        # Inicializar transcriptor
        logger.info(f"Configurando transcriptor con modelo: {MODELO}")
        transcriptor = WhisperTranscriber(modelo=MODELO)
        
        # Inicializar analizadores
        logger.info("Inicializando analizadores de agresión, voz, víctimas y análisis forense DK")
        analizador_agresion = AgresionAnalyzer()
        detector_voz = VoiceStressDetector()
        detector_victimas = VictimDetector()
        analizador_forense_dk = AnalizadorForenseDK()
        generador_informe = GeneradorInformeUnico()
        
        # Mostrar información del dispositivo
        info = transcriptor.obtener_info_modelo()
        logger.info(f"Dispositivo: {info['dispositivo']}")
        if info['gpu_disponible']:
            logger.info(f"GPU: {info.get('gpu_nombre', 'N/A')}")
            logger.info(f"Memoria GPU: {info.get('gpu_memoria_total_gb', 0):.2f} GB")
        
        # Cargar archivos de audio (LEER directamente, SIN copiar ni mover)
        logger.info(f"Buscando archivos de audio en: {CARPETA_AUDIOS}")
        logger.info("NOTA: Los archivos originales NO serán copiados ni modificados")
        loader = AudioLoader()
        archivos_audio = loader.cargar_carpeta(CARPETA_AUDIOS, recursivo=True)  # Búsqueda recursiva para encontrar todos
        
        if not archivos_audio:
            logger.warning(f"No se encontraron archivos de audio en {CARPETA_AUDIOS}")
            logger.info("Verifica que la carpeta existe y contiene archivos .mp3, .m4a, .wav, etc.")
            return
        
        # Filtrar solo .m4a y .mp3 como se solicitó
        archivos_audio = [f for f in archivos_audio if f.lower().endswith(('.m4a', '.mp3'))]
        
        if not archivos_audio:
            logger.warning(f"No se encontraron archivos .m4a o .mp3 en {CARPETA_AUDIOS}")
            return
        
        logger.info(f"Encontrados {len(archivos_audio)} archivo(s) .m4a/.mp3 para procesar")
        
        # Procesar cada archivo
        tiempo_inicio_total = time.time()
        exitosos = 0
        fallidos = 0
        
        for i, archivo_audio in enumerate(archivos_audio, 1):
            logger.info("-" * 60)
            logger.info(f"Procesando archivo {i}/{len(archivos_audio)}: {os.path.basename(archivo_audio)}")
            logger.info(f"Tamaño: {obtener_tamaño_archivo(archivo_audio)}")
            
            tiempo_inicio = time.time()
            
            try:
                # a) Transcribir audio
                logger.info("Paso 1/6: Transcribiendo audio...")
                resultado = transcriptor.transcribir(
                    archivo_audio,
                    idioma=IDIOMA,
                    verbose=False
                )
                
                # Guardar transcripción original (mantener funcionalidad original)
                ruta_guardada = guardar_transcripcion(
                    resultado,
                    archivo_audio,
                    CARPETA_TRANSCRIPCIONES,
                    formato=FORMATO_SALIDA
                )
                
                tiempo_transcripcion = time.time() - tiempo_inicio
                
                # Mostrar resumen básico
                texto = resultado.get('text', '')
                idioma_detectado = resultado.get('language', 'desconocido')
                duracion_audio = resultado.get('segments', [{}])[-1].get('end', 0) if resultado.get('segments') else 0
                
                logger.info(f"✓ Transcripción completada en {tiempo_transcripcion:.2f} segundos")
                logger.info(f"  Idioma detectado: {idioma_detectado}")
                logger.info(f"  Duración del audio: {duracion_audio:.2f} segundos")
                logger.info(f"  Caracteres transcritos: {len(texto)}")
                logger.info(f"  Guardado en: {ruta_guardada}")
                
                # b) Analizar agresión verbal
                logger.info("Paso 2/6: Analizando agresión verbal...")
                analisis_agresion = analizador_agresion.analizar_transcripcion(resultado)
                logger.info(f"  Detectadas {len(analisis_agresion)} instancias de agresión")
                
                # c) Analizar estrés vocal
                logger.info("Paso 3/6: Analizando estrés vocal...")
                analisis_voz = detector_voz.analizar_audio(
                    archivo_audio,
                    resultado.get('segments', [])
                )
                logger.info(f"  Detectados {len(analisis_voz)} momentos de voz elevada")
                
                # d) Analizar agresión dirigida a víctimas
                logger.info("Paso 4/6: Analizando agresión dirigida a víctimas...")
                analisis_victimas = detector_victimas.analizar_transcripcion(
                    resultado,
                    analisis_agresion
                )
                logger.info(f"  Detectadas {len(analisis_victimas)} instancias de agresión dirigida")
                
                # e) Análisis forense DK (Straffeloven §243)
                logger.info("Paso 5/6: Realizando análisis forense según legislación danesa...")
                analisis_forense_dk = analizador_forense_dk.analyser_transkription(resultado)
                logger.info(f"  Análisis forense completado: {analisis_forense_dk['risikoniveau']}")
                
                # f) Generar informe único consolidado
                logger.info("Paso 6/6: Generando informe único consolidado...")
                
                # Generar identificador único
                timestamp = int(time.time())
                identificador_unico = f"ID_{timestamp}_{os.path.splitext(os.path.basename(archivo_audio))[0]}"
                fecha_analisis = time.strftime('%Y-%m-%d %H:%M:%S')
                
                # Generar contenido del informe único
                contenido_informe = generador_informe.generar_informe(
                    nombre_archivo=os.path.basename(archivo_audio),
                    duracion_audio=duracion_audio,
                    fecha_analisis=fecha_analisis,
                    identificador_unico=identificador_unico,
                    resultado_whisper=resultado,
                    analisis_agresion=analisis_agresion,
                    analisis_voz=analisis_voz,
                    analisis_victimas=analisis_victimas,
                    analisis_forense_dk=analisis_forense_dk
                )
                
                # Guardar informe único
                ruta_informe_unico = generador_informe.guardar_informe(
                    contenido=contenido_informe,
                    nombre_archivo_audio=os.path.basename(archivo_audio),
                    carpeta_salida=CARPETA_TRANSCRIPCIONES
                )
                
                logger.info(f"✓ Informe único guardado: {os.path.basename(ruta_informe_unico)}")
                
                exitosos += 1
                
            except Exception as e:
                tiempo_transcripcion = time.time() - tiempo_inicio
                logger.error(f"✗ Error al transcribir {os.path.basename(archivo_audio)}: {str(e)}")
                logger.exception("Detalles del error:")
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
        
    except KeyboardInterrupt:
        logger.warning("\nProceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error fatal: {str(e)}")
        logger.exception("Detalles del error:")
        sys.exit(1)


if __name__ == '__main__':
    main()

