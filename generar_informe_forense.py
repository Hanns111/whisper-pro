#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar informe forense técnico completo para inmigración
Correlaciona patrones del caso Rikke (PDFs) con caso Claudia (audios)
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("ADVERTENCIA: PyMuPDF no disponible. No se podrán leer PDFs.")

# Rutas
RUTA_PDFS = r"C:\Users\hanns\Downloads\AUDIOS\Procesos Lars (ex esposa)-20251203T004023Z-1-001\Procesos Lars (ex esposa)"
RUTA_TRANSCRIPCIONES_1 = r"C:\Users\hanns\Proyectos\whisper-pro\transcripciones\Audios de Lars -20251203T004029Z-1-001"
RUTA_TRANSCRIPCIONES_2 = r"C:\Users\hanns\Proyectos\whisper-pro\transcripciones\Audios-20251203T004026Z-1-001"
RUTA_PATRONES_JSON = r"C:\Users\hanns\Proyectos\whisper-pro\patrones_lars.json"
RUTA_SALIDA = r"C:\Users\hanns\Proyectos\whisper-pro"

def extraer_texto_pdf(ruta_pdf: str) -> Dict[str, Any]:
    """Extrae texto de un PDF"""
    if not PYMUPDF_AVAILABLE:
        return {'exito': False, 'error': 'PyMuPDF no disponible'}
    
    try:
        doc = fitz.open(ruta_pdf)
        texto_completo = []
        texto_por_pagina = []
        
        for num_pagina in range(len(doc)):
            pagina = doc.load_page(num_pagina)
            texto_pagina = pagina.get_text()
            texto_por_pagina.append({
                'pagina': num_pagina + 1,
                'texto': texto_pagina
            })
            texto_completo.append(texto_pagina)
        
        texto_unificado = '\n\n'.join(texto_completo)
        doc.close()
        
        return {
            'exito': True,
            'texto_completo': texto_unificado,
            'texto_por_pagina': texto_por_pagina,
            'num_paginas': len(texto_por_pagina)
        }
    except Exception as e:
        return {'exito': False, 'error': str(e)}

def buscar_patrones_en_pdf(texto: str, texto_por_pagina: List[Dict]) -> List[Dict]:
    """Busca patrones de comportamiento en texto del PDF"""
    patrones_encontrados = []
    
    # Patrones a buscar
    patrones = {
        'amenazas_autoridades': [
            r'report.*you|anmelde|rapportere',
            r'take.*children.*away|tage.*børn|quitar.*hijos',
            r'police.*come|politi.*kommer',
            r'lose.*children|miste.*børn|perder.*hijos'
        ],
        'manipulacion_financiera': [
            r'penge|money|dinero',
            r'trading|crypto',
            r'who.*pay|hvem.*betale|quién.*paga',
            r'don\'t have.*money|har ikke.*penge|no.*tengo.*dinero'
        ],
        'victimizacion': [
            r'jeg vil ikke leve|I don\'t want to live|no quiero vivir',
            r'jeg er så stresset|I am so stressed|estoy tan estresado',
            r'mit liv var roligt|my life was quiet|mi vida era tranquila'
        ],
        'criticas_hijos': [
            r'Kristian|Frederik',
            r'børnene|children|hijos',
            r'problemer med|problems with|problemas con'
        ],
        'culpabilizacion': [
            r'det er din skyld|it\'s your fault|es tu culpa',
            r'du er ansvarlig|you are responsible|eres responsable',
            r'du ødelægger|you are destroying|estás destruyendo'
        ],
        'amenazas_abandono': [
            r'jeg forlader|I will leave|me voy',
            r'jeg flytter væk|I am moving away|me estoy yendo'
        ]
    }
    
    for tipo_patron, regexes in patrones.items():
        for regex in regexes:
            for pagina_info in texto_por_pagina:
                pagina = pagina_info['pagina']
                texto_pagina = pagina_info['texto']
                matches = re.finditer(regex, texto_pagina, re.IGNORECASE)
                
                for match in matches:
                    contexto_inicio = max(0, match.start() - 100)
                    contexto_fin = min(len(texto_pagina), match.end() + 100)
                    contexto = texto_pagina[contexto_inicio:contexto_fin]
                    
                    patrones_encontrados.append({
                        'tipo': tipo_patron,
                        'pagina': pagina,
                        'texto': match.group(),
                        'contexto': contexto.strip()
                    })
    
    return patrones_encontrados

def cargar_transcripciones() -> List[Dict]:
    """Carga todas las transcripciones de audio"""
    transcripciones = []
    
    for ruta_base in [RUTA_TRANSCRIPCIONES_1, RUTA_TRANSCRIPCIONES_2]:
        if not os.path.exists(ruta_base):
            continue
        
        for root, dirs, files in os.walk(ruta_base):
            for file in files:
                if file.endswith('_INFORME_UNICO.txt'):
                    ruta_completa = os.path.join(root, file)
                    try:
                        with open(ruta_completa, 'r', encoding='utf-8') as f:
                            contenido = f.read()
                        
                        # Extraer transcripción con timestamps
                        segmentos = []
                        patron_timestamp = r'\[(\d{2}):(\d{2})\]\s+(.+?)(?=\n\[|\n\n|$)'
                        matches = re.finditer(patron_timestamp, contenido, re.MULTILINE | re.DOTALL)
                        
                        for match in matches:
                            minutos = int(match.group(1))
                            segundos = int(match.group(2))
                            texto = match.group(3).strip()
                            tiempo_total = minutos * 60 + segundos
                            
                            segmentos.append({
                                'start': tiempo_total,
                                'timestamp': f"{minutos:02d}:{segundos:02d}",
                                'text': texto
                            })
                        
                        if segmentos:
                            transcripciones.append({
                                'archivo': file,
                                'ruta': ruta_completa,
                                'segmentos': segmentos,
                                'texto_completo': '\n'.join([s['text'] for s in segmentos])
                            })
                    except Exception as e:
                        print(f"Error leyendo {file}: {e}")
    
    return transcripciones

def correlacionar_patrones(patrones_pdf: List[Dict], transcripciones: List[Dict]) -> List[Dict]:
    """Correlaciona patrones del PDF con transcripciones"""
    correlaciones = []
    
    for patron_pdf in patrones_pdf:
        tipo_patron = patron_pdf['tipo']
        texto_patron = patron_pdf['texto'].lower()
        
        # Buscar en transcripciones
        for transcripcion in transcripciones:
            for segmento in transcripcion['segmentos']:
                texto_segmento = segmento['text'].lower()
                
                # Buscar similitudes
                palabras_clave_patron = set(re.findall(r'\w+', texto_patron))
                palabras_clave_segmento = set(re.findall(r'\w+', texto_segmento))
                
                if palabras_clave_patron and palabras_clave_segmento:
                    palabras_comunes = palabras_clave_patron.intersection(palabras_clave_segmento)
                    similitud = len(palabras_comunes) / len(palabras_clave_patron.union(palabras_clave_segmento))
                    
                    if similitud > 0.2:  # Umbral mínimo
                        correlaciones.append({
                            'patron_pdf': patron_pdf,
                            'archivo_audio': transcripcion['archivo'],
                            'timestamp': segmento['timestamp'],
                            'texto_audio': segmento['text'],
                            'similitud': similitud
                        })
    
    return correlaciones

if __name__ == '__main__':
    print("=" * 80)
    print("GENERADOR DE INFORME FORENSE TÉCNICO PARA INMIGRACIÓN")
    print("=" * 80)
    print("\nIniciando proceso...")
    
    # Cargar datos de patrones existentes
    print("\n1. Cargando análisis previo de patrones...")
    if os.path.exists(RUTA_PATRONES_JSON):
        with open(RUTA_PATRONES_JSON, 'r', encoding='utf-8') as f:
            datos_patrones = json.load(f)
        print(f"   ✓ Cargados datos de {datos_patrones['total_archivos']} archivos")
    else:
        datos_patrones = {}
        print("   ⚠ No se encontró archivo de patrones")
    
    # Cargar transcripciones
    print("\n2. Cargando transcripciones de audio...")
    transcripciones = cargar_transcripciones()
    print(f"   ✓ Cargadas {len(transcripciones)} transcripciones")
    
    # Leer PDFs clave
    print("\n3. Leyendo PDFs del caso Rikke...")
    pdfs_procesados = []
    
    if PYMUPDF_AVAILABLE and os.path.exists(RUTA_PDFS):
        pdfs_clave = [
            'bitácora de Lars.pdf',
            'Processkrift.PDF.pdf',
            'familieretshuset sag børn rikke.pdf',
            'Sagsøgtes påstandsdokument.PDF.pdf'
        ]
        
        for nombre_pdf in pdfs_clave:
            ruta_pdf = os.path.join(RUTA_PDFS, nombre_pdf)
            if os.path.exists(ruta_pdf):
                print(f"   Procesando: {nombre_pdf}")
                resultado = extraer_texto_pdf(ruta_pdf)
                if resultado['exito']:
                    patrones = buscar_patrones_en_pdf(
                        resultado['texto_completo'],
                        resultado['texto_por_pagina']
                    )
                    pdfs_procesados.append({
                        'nombre': nombre_pdf,
                        'patrones': patrones,
                        'num_paginas': resultado['num_paginas']
                    })
                    print(f"      ✓ {len(patrones)} patrones encontrados")
    else:
        print("   ⚠ PyMuPDF no disponible o carpeta no existe")
        print("   Continuando con datos de patrones existentes...")
    
    print("\n" + "=" * 80)
    print("PROCESO COMPLETADO")
    print("=" * 80)
    print(f"\nPDFs procesados: {len(pdfs_procesados)}")
    print(f"Transcripciones cargadas: {len(transcripciones)}")
    print(f"Total patrones en JSON: {sum(len(v) if isinstance(v, dict) else 0 for v in datos_patrones.get('estadisticas', {}).values())}")
    
    print("\nAhora se generarán los informes...")



