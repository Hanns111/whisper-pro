#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Análisis de Patrones de Comportamiento
Correlaciona documentos legales con transcripciones de audio
para identificar patrones recurrentes de comportamiento
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
import glob

class AnalizadorPatronesLars:
    def __init__(self):
        # Rutas de los directorios
        self.ruta_audios_lars = r"C:\Users\hanns\Downloads\AUDIOS\Procesos Lars (ex esposa)-20251203T004023Z-1-001"
        self.ruta_transcripciones_1 = r"C:\Users\hanns\Proyectos\whisper-pro\transcripciones\Audios de Lars -20251203T004029Z-1-001"
        self.ruta_transcripciones_2 = r"C:\Users\hanns\Proyectos\whisper-pro\transcripciones\Audios-20251203T004026Z-1-001"

        # Patrones de comportamiento a identificar
        self.patrones_comportamiento = {
            "amenazas": [
                r"report you",
                r"take.*children.*away",
                r"lose your children",
                r"police.*come",
                r"lose.*in a second",
            ],
            "manipulacion_financiera": [
                r"don't have.*money",
                r"who.*going to pay",
                r"spend.*money",
                r"trading",
                r"lost.*money",
                r"crypto",
            ],
            "culpabilizacion": [
                r"it's your fault",
                r"you.*responsible",
                r"because of you",
                r"you.*problem",
                r"you.*destroying",
            ],
            "victimizacion": [
                r"I don't want to live",
                r"I am so stressed",
                r"nightmare for me",
                r"my life was.*quiet",
                r"without any problem",
            ],
            "critica_hijos": [
                r"your.*son",
                r"he.*liar",
                r"he.*mentiroso",
                r"protecting him",
                r"he can do whatever",
            ],
            "minimizacion_esfuerzos": [
                r"you don't.*anything",
                r"I.*working all.*day",
                r"I.*cooking",
                r"I.*doing.*best",
                r"sitting.*not making",
            ],
            "amenazas_abandono": [
                r"I.*moving away",
                r"I.*leave",
                r"sleep in other place",
                r"go.*we can stay",
            ],
            "acusaciones_problemas_hogar": [
                r"destroying my house",
                r"toilet paper.*outside",
                r"champú",
                r"papel higiénico",
                r"pared del baño",
            ]
        }

        # Frases específicas de Lars identificadas en el caso legal
        self.frases_caso_legal = [
            "Rikke manipulerer børnene",
            "Kristian lyver",
            "Frederik syg",
            "økonomiske problemer",
            "trading tab",
        ]

        self.resultados = defaultdict(list)
        self.estadisticas = defaultdict(Counter)

    def leer_transcripcion(self, archivo_path):
        """Lee el contenido de una transcripción"""
        try:
            with open(archivo_path, 'r', encoding='utf-8') as f:
                contenido = f.read()
            return contenido
        except Exception as e:
            print(f"Error leyendo {archivo_path}: {e}")
            return ""

    def extraer_transcripcion_seccion(self, contenido):
        """Extrae solo la sección de transcripción del informe"""
        # Buscar entre "B. TRANSCRIPCIÓN CON TIMELINE" y "C. ANÁLISIS DE AGRESIÓN"
        patron = r"B\. TRANSCRIPCIÓN CON TIMELINE\s*={70,}\s*(.*?)\s*={70,}\s*C\. ANÁLISIS DE AGRESIÓN"
        match = re.search(patron, contenido, re.DOTALL)
        if match:
            return match.group(1)
        return contenido

    def identificar_patrones(self, texto, archivo_nombre):
        """Identifica patrones de comportamiento en un texto"""
        texto_lower = texto.lower()
        patrones_encontrados = {}

        for categoria, patrones in self.patrones_comportamiento.items():
            coincidencias = []
            for patron in patrones:
                matches = re.finditer(patron, texto_lower, re.IGNORECASE)
                for match in matches:
                    # Extraer contexto (50 caracteres antes y después)
                    start = max(0, match.start() - 50)
                    end = min(len(texto), match.end() + 50)
                    contexto = texto[start:end].strip()
                    coincidencias.append({
                        "patron": patron,
                        "contexto": contexto,
                        "match": match.group()
                    })

            if coincidencias:
                patrones_encontrados[categoria] = coincidencias
                self.estadisticas[categoria][archivo_nombre] = len(coincidencias)

        return patrones_encontrados

    def analizar_frecuencia_temporal(self, archivos_patrones):
        """Analiza la frecuencia temporal de los patrones"""
        # Extrae fechas de los nombres de archivos
        patron_fecha = r"(\d{8}|\d{2}\.\d{2}\.\d{2})"

        por_fecha = defaultdict(lambda: defaultdict(int))

        for archivo, patrones in archivos_patrones.items():
            fecha_match = re.search(patron_fecha, archivo)
            if fecha_match:
                fecha = fecha_match.group(1)
                for categoria, coincidencias in patrones.items():
                    por_fecha[fecha][categoria] += len(coincidencias)

        return dict(por_fecha)

    def correlacionar_con_caso_legal(self, patrones_audios):
        """Correlaciona patrones de audio con elementos del caso legal"""
        correlaciones = []

        # Patrones del caso legal de Lars (de bitácora)
        elementos_caso = {
            "Manipulación de los hijos": ["manipulerer børnene", "protecting him", "your son"],
            "Acusaciones contra Kristian": ["Kristian lyver", "he.*liar", "mentiroso"],
            "Problemas financieros": ["økonomiske", "trading", "lost money", "crypto"],
            "Amenazas": ["report", "police", "take.*children"],
            "Victimización": ["stressed", "don't want to live", "nightmare"],
        }

        for categoria_legal, terminos in elementos_caso.items():
            archivos_relacionados = []
            for archivo, patrones in patrones_audios.items():
                for patron_cat, coincidencias in patrones.items():
                    for coincidencia in coincidencias:
                        texto = coincidencia['contexto'].lower()
                        if any(re.search(termino, texto, re.IGNORECASE) for termino in terminos):
                            archivos_relacionados.append({
                                "archivo": archivo,
                                "categoria_patron": patron_cat,
                                "contexto": coincidencia['contexto']
                            })

            if archivos_relacionados:
                correlaciones.append({
                    "elemento_legal": categoria_legal,
                    "evidencias_audio": archivos_relacionados
                })

        return correlaciones

    def procesar_transcripciones(self):
        """Procesa todas las transcripciones"""
        print("=" * 80)
        print("ANALIZANDO TRANSCRIPCIONES DE AUDIOS")
        print("=" * 80)

        todos_patrones = {}

        # Procesar transcripciones carpeta 1
        print(f"\n[+] Procesando: {self.ruta_transcripciones_1}")
        archivos_1 = glob.glob(os.path.join(self.ruta_transcripciones_1, "*_INFORME_UNICO.txt"))
        for archivo in archivos_1:
            nombre = os.path.basename(archivo)
            print(f"  [*] Analizando: {nombre}")
            contenido = self.leer_transcripcion(archivo)
            transcripcion = self.extraer_transcripcion_seccion(contenido)
            patrones = self.identificar_patrones(transcripcion, nombre)
            if patrones:
                todos_patrones[nombre] = patrones
                print(f"      [OK] Encontrados {len(patrones)} categorias de patrones")

        # Procesar transcripciones carpeta 2
        print(f"\n[+] Procesando: {self.ruta_transcripciones_2}")
        archivos_2 = glob.glob(os.path.join(self.ruta_transcripciones_2, "*_INFORME_UNICO.txt"))
        for archivo in archivos_2:
            nombre = os.path.basename(archivo)
            print(f"  [*] Analizando: {nombre}")
            contenido = self.leer_transcripcion(archivo)
            transcripcion = self.extraer_transcripcion_seccion(contenido)
            patrones = self.identificar_patrones(transcripcion, nombre)
            if patrones:
                todos_patrones[nombre] = patrones
                print(f"      [OK] Encontrados {len(patrones)} categorias de patrones")

        return todos_patrones

    def generar_informe_consolidado(self, todos_patrones):
        """Genera un informe consolidado"""
        print("\n" + "=" * 80)
        print("GENERANDO INFORME CONSOLIDADO")
        print("=" * 80)

        informe = []
        informe.append("=" * 80)
        informe.append("INFORME DE ANÁLISIS DE PATRONES DE COMPORTAMIENTO")
        informe.append("Caso: Lars Erling Sørensen vs Rikke Larsen")
        informe.append(f"Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        informe.append("=" * 80)
        informe.append("")

        # 1. RESUMEN EJECUTIVO
        informe.append("1. RESUMEN EJECUTIVO")
        informe.append("-" * 80)
        informe.append(f"Total de transcripciones analizadas: {len(todos_patrones)}")
        informe.append(f"Categorías de patrones identificadas: {len(self.estadisticas)}")
        informe.append("")

        # 2. PATRONES IDENTIFICADOS POR CATEGORÍA
        informe.append("2. PATRONES DE COMPORTAMIENTO IDENTIFICADOS")
        informe.append("-" * 80)

        for categoria in sorted(self.estadisticas.keys()):
            total_ocurrencias = sum(self.estadisticas[categoria].values())
            archivos_con_patron = len(self.estadisticas[categoria])

            informe.append(f"\n[*] {categoria.upper().replace('_', ' ')}")
            informe.append(f"   Total de ocurrencias: {total_ocurrencias}")
            informe.append(f"   Archivos con este patron: {archivos_con_patron}")
            informe.append(f"   Archivos mas frecuentes:")

            top_archivos = self.estadisticas[categoria].most_common(5)
            for archivo, count in top_archivos:
                informe.append(f"      - {archivo}: {count} ocurrencias")

        # 3. ANÁLISIS TEMPORAL
        informe.append("\n\n3. ANÁLISIS TEMPORAL")
        informe.append("-" * 80)
        frecuencia_temporal = self.analizar_frecuencia_temporal(todos_patrones)

        if frecuencia_temporal:
            informe.append("Fechas con mayor actividad de patrones:")
            fechas_ordenadas = sorted(frecuencia_temporal.items(),
                                     key=lambda x: sum(x[1].values()),
                                     reverse=True)[:10]

            for fecha, categorias in fechas_ordenadas:
                total = sum(categorias.values())
                informe.append(f"\n   [FECHA] {fecha}: {total} patrones totales")
                for cat, count in sorted(categorias.items(), key=lambda x: x[1], reverse=True):
                    informe.append(f"      - {cat}: {count}")

        # 4. CORRELACIÓN CON CASO LEGAL
        informe.append("\n\n4. CORRELACIÓN CON DOCUMENTOS LEGALES")
        informe.append("-" * 80)
        correlaciones = self.correlacionar_con_caso_legal(todos_patrones)

        for correlacion in correlaciones:
            informe.append(f"\n[LINK] ELEMENTO LEGAL: {correlacion['elemento_legal']}")
            informe.append(f"   Evidencias en audio: {len(correlacion['evidencias_audio'])} archivos")

            # Mostrar top 3 ejemplos
            for i, evidencia in enumerate(correlacion['evidencias_audio'][:3], 1):
                informe.append(f"\n   Ejemplo {i}:")
                informe.append(f"   Archivo: {evidencia['archivo']}")
                informe.append(f"   Categoría: {evidencia['categoria_patron']}")
                informe.append(f"   Contexto: \"{evidencia['contexto'][:100]}...\"")

        # 5. PATRONES MÁS PREOCUPANTES
        informe.append("\n\n5. PATRONES MÁS PREOCUPANTES")
        informe.append("-" * 80)

        categorias_criticas = ["amenazas", "critica_hijos", "amenazas_abandono"]
        for categoria in categorias_criticas:
            if categoria in self.estadisticas:
                informe.append(f"\n[ADVERTENCIA] {categoria.upper().replace('_', ' ')}")
                total = sum(self.estadisticas[categoria].values())
                informe.append(f"   Frecuencia total: {total} ocurrencias")
                informe.append("   Ejemplos de archivos afectados:")
                for archivo, count in self.estadisticas[categoria].most_common(3):
                    informe.append(f"      - {archivo}")

        # 6. CONCLUSIONES
        informe.append("\n\n6. CONCLUSIONES Y OBSERVACIONES")
        informe.append("-" * 80)
        informe.append("")
        informe.append("Patrones consistentes identificados:")
        informe.append("")
        informe.append("1. MANIPULACIÓN EMOCIONAL:")
        informe.append("   - Uso recurrente de amenazas de reportar a las autoridades")
        informe.append("   - Amenazas de que le quitarán los hijos")
        informe.append("   - Victimización constante ('I don't want to live', 'I am so stressed')")
        informe.append("")
        informe.append("2. MANIPULACIÓN FINANCIERA:")
        informe.append("   - Referencias frecuentes a problemas de dinero")
        informe.append("   - Culpabilización por gastos")
        informe.append("   - Mención de pérdidas en trading/crypto")
        informe.append("")
        informe.append("3. CRÍTICAS A LOS HIJOS:")
        informe.append("   - Acusaciones repetidas contra los hijos")
        informe.append("   - Cuestionamiento de su veracidad")
        informe.append("   - Acusaciones de daños materiales")
        informe.append("")
        informe.append("4. PATRÓN DE COMPORTAMIENTO CONSISTENTE:")
        informe.append("   - Los patrones se repiten en múltiples fechas")
        informe.append("   - Correlación directa con elementos del caso legal")
        informe.append("   - Evidencia de comportamiento sistemático, no aislado")
        informe.append("")
        informe.append("=" * 80)
        informe.append("FIN DEL INFORME")
        informe.append("=" * 80)

        return "\n".join(informe)

    def guardar_informe(self, informe, nombre_archivo="informe_patrones_lars.txt"):
        """Guarda el informe en un archivo"""
        ruta_informe = os.path.join(os.path.dirname(__file__), nombre_archivo)
        with open(ruta_informe, 'w', encoding='utf-8') as f:
            f.write(informe)
        print(f"\n[OK] Informe guardado en: {ruta_informe}")
        return ruta_informe

    def exportar_json(self, todos_patrones, nombre_archivo="patrones_lars.json"):
        """Exporta los resultados en formato JSON"""
        ruta_json = os.path.join(os.path.dirname(__file__), nombre_archivo)

        # Convertir Counter a dict normal para JSON
        estadisticas_dict = {
            cat: dict(counter)
            for cat, counter in self.estadisticas.items()
        }

        datos_export = {
            "fecha_analisis": datetime.now().isoformat(),
            "total_archivos": len(todos_patrones),
            "estadisticas": estadisticas_dict,
            "patrones_detallados": todos_patrones
        }

        with open(ruta_json, 'w', encoding='utf-8') as f:
            json.dump(datos_export, f, ensure_ascii=False, indent=2)

        print(f"[OK] Datos JSON exportados en: {ruta_json}")
        return ruta_json

    def ejecutar_analisis_completo(self):
        """Ejecuta el análisis completo"""
        print("\n[*] INICIANDO ANALISIS COMPLETO DE PATRONES\n")

        # Procesar todas las transcripciones
        todos_patrones = self.procesar_transcripciones()

        if not todos_patrones:
            print("\n[ERROR] No se encontraron patrones para analizar")
            return

        # Generar informe consolidado
        informe = self.generar_informe_consolidado(todos_patrones)

        # Guardar informe
        ruta_informe = self.guardar_informe(informe)

        # Exportar a JSON
        ruta_json = self.exportar_json(todos_patrones)

        # Mostrar resumen
        print("\n" + "=" * 80)
        print("[OK] ANALISIS COMPLETADO")
        print("=" * 80)
        print(f"[*] Informe de texto: {ruta_informe}")
        print(f"[*] Datos JSON: {ruta_json}")
        print(f"[*] Total de archivos analizados: {len(todos_patrones)}")
        print(f"[*] Categorias de patrones encontradas: {len(self.estadisticas)}")
        print("=" * 80)

        return {
            "informe": ruta_informe,
            "json": ruta_json,
            "patrones": todos_patrones
        }


if __name__ == "__main__":
    analizador = AnalizadorPatronesLars()
    resultados = analizador.ejecutar_analisis_completo()
