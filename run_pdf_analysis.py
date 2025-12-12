"""
Script principal para análisis forense de documentos PDF
Procesa PDFs y genera informes forenses según Straffeloven §243
"""

import os
import sys
import time
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.analizador_pdf_forense import AnalizadorPDFForense
from src.utils import crear_carpetas, configurar_logging
import logging


def main():
    """Función principal"""
    
    # ============================================================
    # CONFIGURACIÓN DE RUTAS
    # ============================================================
    # Carpeta donde están los PDFs históricos (NO se copian ni mueven)
    CARPETA_PDFS = r'C:\Users\hanns\Downloads\PDFs de Lars'
    
    # Carpetas de audios/videos para correlación (3 carpetas distintas)
    CARPETAS_AUDIOS = [
        r'C:\Users\hanns\Downloads\Audios de Lars -20251203T004029Z-1-001\Audios de Lars',
        r'C:\Users\hanns\Proyectos\whisper-pro\audios',  # Si existe
        r'C:\Users\hanns\Downloads\Audios'  # Si existe
    ]
    
    # Carpeta donde se guardan los informes y transcripciones
    CARPETA_TRANSCRIPCIONES = r'C:\Users\hanns\Proyectos\whisper-pro\transcripciones'
    CARPETA_LOGS = 'logs'
    
    # Crear carpetas necesarias
    crear_carpetas(CARPETA_TRANSCRIPCIONES, CARPETA_LOGS)
    
    # Configurar logging
    logger = configurar_logging(CARPETA_LOGS, nombre_archivo="pdf_analysis.log")
    logger.info("=" * 60)
    logger.info("Iniciando análisis forense de PDFs")
    logger.info("=" * 60)
    
    try:
        # Verificar que PyMuPDF esté disponible
        try:
            import fitz
            logger.info("PyMuPDF disponible")
        except ImportError:
            logger.error("PyMuPDF no está instalado. Instala con: pip install PyMuPDF")
            return
        
        # Inicializar analizador con carpetas de audios para correlación
        logger.info("Inicializando analizador forense de PDFs...")
        analizador = AnalizadorPDFForense(carpetas_audios=CARPETAS_AUDIOS)
        
        # Cargar transcripciones de audio para correlación
        logger.info("Cargando transcripciones de audio para correlación...")
        transcripciones = analizador.cargar_transcripciones_audio(CARPETA_TRANSCRIPCIONES)
        logger.info(f"  Cargadas {len(transcripciones)} transcripciones de audio")
        
        # Buscar archivos PDF
        logger.info(f"Buscando archivos PDF en: {CARPETA_PDFS}")
        logger.info("NOTA: Los archivos originales NO serán copiados ni modificados")
        
        if not os.path.exists(CARPETA_PDFS):
            logger.warning(f"La carpeta no existe: {CARPETA_PDFS}")
            logger.info("Verifica que la ruta sea correcta")
            return
        
        # Obtener lista de PDFs
        archivos_pdf = []
        for root, dirs, files in os.walk(CARPETA_PDFS):
            for file in files:
                if file.lower().endswith('.pdf'):
                    ruta_completa = os.path.join(root, file)
                    archivos_pdf.append(ruta_completa)
        
        if not archivos_pdf:
            logger.warning(f"No se encontraron archivos PDF en {CARPETA_PDFS}")
            logger.info("Coloca archivos PDF en la carpeta especificada")
            return
        
        logger.info(f"Encontrados {len(archivos_pdf)} archivo(s) PDF para procesar")
        
        # Procesar cada PDF
        tiempo_inicio_total = time.time()
        exitosos = 0
        fallidos = 0
        
        for i, archivo_pdf in enumerate(archivos_pdf, 1):
            logger.info("-" * 60)
            logger.info(f"Procesando PDF {i}/{len(archivos_pdf)}: {os.path.basename(archivo_pdf)}")
            
            tamaño_archivo = os.path.getsize(archivo_pdf)
            tamaño_mb = tamaño_archivo / (1024 * 1024)
            logger.info(f"Tamaño: {tamaño_mb:.2f} MB")
            
            tiempo_inicio = time.time()
            
            try:
                # Paso 1: Extraer texto
                logger.info("Paso 1/5: Extrayendo texto del PDF...")
                texto_extraido = analizador.extraer_texto_pdf(archivo_pdf)
                
                if not texto_extraido.get('exito', False):
                    logger.error(f"Error al extraer texto: {texto_extraido.get('error', 'Error desconocido')}")
                    fallidos += 1
                    continue
                
                texto_completo = texto_extraido.get('texto_completo', '')
                texto_por_pagina = texto_extraido.get('texto_por_pagina', [])
                num_paginas = texto_extraido.get('num_paginas', 0)
                logger.info(f"  Texto extraído: {len(texto_completo)} caracteres de {num_paginas} páginas")
                
                # Paso 2: Detectar agresión (con número de página y traducciones)
                logger.info("Paso 2/7: Detectando patrones de agresión psicológica...")
                detecciones_agresion = analizador.detectar_agresion(texto_completo, texto_por_pagina)
                logger.info(f"  Detectadas {len(detecciones_agresion)} instancias de agresión")
                
                # Paso 3: Detectar menciones a víctimas
                logger.info("Paso 3/7: Detectando menciones a víctimas...")
                menciones_victimas = analizador.detectar_menciones_victimas(texto_completo)
                total_menciones = sum(len(m) for m in menciones_victimas.values())
                logger.info(f"  Detectadas {total_menciones} menciones a víctimas")
                
                # Paso 4: Detectar contradicciones
                logger.info("Paso 4/7: Detectando contradicciones internas...")
                contradicciones = analizador.detectar_contradicciones(texto_completo)
                logger.info(f"  Detectadas {len(contradicciones)} posibles contradicciones")
                
                # Paso 5: Clasificación legal danesa
                logger.info("Paso 5/7: Realizando clasificación legal danesa (§243)...")
                clasificacion_legal = analizador.clasificar_legal_dk(texto_completo, detecciones_agresion)
                risikoniveau = clasificacion_legal.get('risikoniveau', 'lav')
                logger.info(f"  Clasificación completada: Nivel de riesgo {risikoniveau.upper()}")
                
                # Paso 6: Correlacionar con audios
                logger.info("Paso 6/7: Correlacionando agresiones con transcripciones de audio...")
                detecciones_correlacionadas = analizador.correlacionar_con_audios(detecciones_agresion, transcripciones)
                total_correlaciones = sum(len(det.get('correlaciones', [])) for det in detecciones_correlacionadas)
                logger.info(f"  Encontradas {total_correlaciones} correlaciones con audios/videos")
                
                # Paso 7: Calcular agravantes legales
                logger.info("Paso 7/7: Calculando agravantes legales por menores vulnerables...")
                agravantes_legales = analizador.calcular_agravantes_legales(detecciones_correlacionadas, menciones_victimas)
                nivel_final = agravantes_legales.get('nivel_riesgo_final', 'LAV')
                logger.info(f"  Nivel de riesgo final (con agravantes): {nivel_final}")
                
                # Generar informe correlacional
                logger.info("Generando informe correlacional...")
                nombre_pdf = os.path.basename(archivo_pdf)
                contenido_informe = analizador.generar_informe_correlacional(
                    nombre_pdf=nombre_pdf,
                    ruta_pdf=archivo_pdf,
                    texto_extraido=texto_extraido,
                    detecciones_agresion=detecciones_correlacionadas,
                    menciones_victimas=menciones_victimas,
                    contradicciones=contradicciones,
                    clasificacion_legal=clasificacion_legal,
                    agravantes_legales=agravantes_legales,
                    transcripciones=transcripciones
                )
                
                # Guardar informe
                nombre_base = os.path.splitext(nombre_pdf)[0]
                nombre_base = nombre_base.replace(' ', '_').replace('/', '_').replace('\\', '_')
                nombre_archivo_informe = f"{nombre_base}_PDF_CORRELACIONAL.txt"
                ruta_informe = os.path.join(CARPETA_TRANSCRIPCIONES, nombre_archivo_informe)
                
                os.makedirs(CARPETA_TRANSCRIPCIONES, exist_ok=True)
                with open(ruta_informe, 'w', encoding='utf-8') as f:
                    f.write(contenido_informe)
                
                tiempo_procesamiento = time.time() - tiempo_inicio
                logger.info(f"✓ Informe guardado: {nombre_archivo_informe}")
                logger.info(f"  Tiempo de procesamiento: {tiempo_procesamiento:.2f} segundos")
                
                exitosos += 1
                
            except Exception as e:
                tiempo_procesamiento = time.time() - tiempo_inicio
                logger.error(f"✗ Error al procesar {os.path.basename(archivo_pdf)}: {str(e)}")
                logger.exception("Detalles del error:")
                fallidos += 1
        
        # Resumen final
        tiempo_total = time.time() - tiempo_inicio_total
        logger.info("=" * 60)
        logger.info("Proceso de análisis forense finalizado")
        logger.info(f"Total de archivos: {len(archivos_pdf)}")
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

