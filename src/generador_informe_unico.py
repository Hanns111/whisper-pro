"""
Generador de informe único consolidado
Genera un único archivo TXT con toda la información del análisis
"""

import os
import time
from typing import Dict, List, Any
from datetime import datetime
import logging


class GeneradorInformeUnico:
    """
    Clase para generar un informe único consolidado en formato TXT
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def _formatear_tiempo(self, segundos: float) -> str:
        """Formatea tiempo en formato MM:SS"""
        minutos = int(segundos // 60)
        segs = int(segundos % 60)
        return f"{minutos:02d}:{segs:02d}"
    
    def _formatear_duracion(self, segundos: float) -> str:
        """Formatea duración en formato legible"""
        horas = int(segundos // 3600)
        minutos = int((segundos % 3600) // 60)
        segs = int(segundos % 60)
        
        if horas > 0:
            return f"{horas}h {minutos}m {segs}s"
        elif minutos > 0:
            return f"{minutos}m {segs}s"
        else:
            return f"{segs}s"
    
    def generar_informe(
        self,
        nombre_archivo: str,
        duracion_audio: float,
        fecha_analisis: str,
        identificador_unico: str,
        resultado_whisper: Dict[str, Any],
        analisis_agresion: List[Dict[str, Any]],
        analisis_voz: List[Dict[str, Any]],
        analisis_victimas: List[Dict[str, Any]],
        analisis_forense_dk: Dict[str, Any]
    ) -> str:
        """
        Genera el informe único completo en formato texto
        
        Returns:
            Contenido completo del informe como string
        """
        lineas = []
        
        # ============================================================
        # A. CABECERA
        # ============================================================
        lineas.append("=" * 80 + "\n")
        lineas.append("INFORME ÚNICO DE ANÁLISIS FORENSE\n")
        lineas.append("=" * 80 + "\n\n")
        
        lineas.append("INFORMACIÓN DEL ARCHIVO\n")
        lineas.append("-" * 80 + "\n")
        lineas.append(f"Nombre del archivo: {nombre_archivo}\n")
        lineas.append(f"Duración: {self._formatear_duracion(duracion_audio)} ({duracion_audio:.2f} segundos)\n")
        lineas.append(f"Fecha del análisis: {fecha_analisis}\n")
        lineas.append(f"Identificador único: {identificador_unico}\n")
        lineas.append(f"Idioma detectado: {resultado_whisper.get('language', 'desconocido')}\n")
        lineas.append("\n" + "=" * 80 + "\n\n")
        
        # ============================================================
        # B. TRANSCRIPCIÓN CON TIMELINE
        # ============================================================
        lineas.append("B. TRANSCRIPCIÓN CON TIMELINE\n")
        lineas.append("=" * 80 + "\n\n")
        
        segments = resultado_whisper.get('segments', [])
        if segments:
            for segment in segments:
                inicio = segment.get('start', 0)
                texto = segment.get('text', '').strip()
                if texto:
                    tiempo_str = self._formatear_tiempo(inicio)
                    lineas.append(f"[{tiempo_str}] {texto}\n")
        else:
            # Si no hay segmentos, usar el texto completo
            texto_completo = resultado_whisper.get('text', '')
            if texto_completo:
                lineas.append(f"[00:00] {texto_completo}\n")
        
        lineas.append("\n" + "=" * 80 + "\n\n")
        
        # ============================================================
        # C. ANÁLISIS DE AGRESIÓN (ES)
        # ============================================================
        lineas.append("C. ANÁLISIS DE AGRESIÓN (ES)\n")
        lineas.append("=" * 80 + "\n\n")
        
        if not analisis_agresion:
            lineas.append("No se detectaron instancias de agresión verbal.\n\n")
        else:
            # Agrupar por tipo
            por_tipo = {}
            for ag in analisis_agresion:
                tipo = ag.get('tipo', 'desconocido')
                if tipo not in por_tipo:
                    por_tipo[tipo] = []
                por_tipo[tipo].append(ag)
            
            # Escribir por categorías
            categorias = {
                'insulto': 'INSULTOS',
                'amenaza': 'AMENAZAS',
                'descalificación': 'DESCALIFICACIONES',
                'gaslighting': 'GASLIGHTING',
                'manipulación emocional': 'MANIPULACIÓN EMOCIONAL',
                'invalidación': 'INVALIDACIÓN',
                'control económico': 'CONTROL ECONÓMICO'
            }
            
            for tipo_key, titulo in categorias.items():
                if tipo_key in por_tipo:
                    lineas.append(f"\n{titulo} ({len(por_tipo[tipo_key])} detecciones):\n")
                    lineas.append("-" * 80 + "\n")
                    for ag in por_tipo[tipo_key]:
                        inicio_str = self._formatear_tiempo(ag['inicio'])
                        fin_str = self._formatear_tiempo(ag['fin'])
                        severidad = ag.get('severidad', 'media')
                        frase = ag.get('frase', '')
                        lineas.append(f"[{inicio_str} - {fin_str}] Severidad: {severidad.upper()}\n")
                        lineas.append(f"  {frase}\n\n")
        
        lineas.append("\n" + "=" * 80 + "\n\n")
        
        # ============================================================
        # D. ANÁLISIS DE VOZ / ESTRÉS (ES)
        # ============================================================
        lineas.append("D. ANÁLISIS DE VOZ / ESTRÉS (ES)\n")
        lineas.append("=" * 80 + "\n\n")
        
        if not analisis_voz:
            lineas.append("No se detectaron momentos de voz elevada o estrés acústico.\n\n")
        else:
            # Agrupar por tipo
            por_tipo_voz = {}
            for voz in analisis_voz:
                tipo = voz.get('tipo', 'voz elevada')
                if tipo not in por_tipo_voz:
                    por_tipo_voz[tipo] = []
                por_tipo_voz[tipo].append(voz)
            
            lineas.append("DETECCIÓN DE PICOS DE VOLUMEN:\n")
            lineas.append("-" * 80 + "\n")
            for voz in analisis_voz:
                inicio_str = self._formatear_tiempo(voz['inicio'])
                fin_str = self._formatear_tiempo(voz['fin'])
                db_change = voz.get('db_change', 0)
                lineas.append(f"[{inicio_str} - {fin_str}] Aumento de volumen: {db_change:.2f} dB\n")
            
            lineas.append("\nCAMBIOS BRUSCOS DE TONO:\n")
            lineas.append("-" * 80 + "\n")
            # Si hay información de tono en el análisis
            cambios_tono = [v for v in analisis_voz if v.get('tipo') == 'cambio_tono']
            if cambios_tono:
                for cambio in cambios_tono:
                    inicio_str = self._formatear_tiempo(cambio['inicio'])
                    fin_str = self._formatear_tiempo(cambio['fin'])
                    lineas.append(f"[{inicio_str} - {fin_str}] Cambio brusco de tono detectado\n")
            else:
                lineas.append("No se detectaron cambios bruscos de tono.\n")
            
            lineas.append("\nVOZ ELEVADA:\n")
            lineas.append("-" * 80 + "\n")
            voz_elevada = [v for v in analisis_voz if 'elevada' in v.get('tipo', '').lower()]
            if voz_elevada:
                for voz in voz_elevada:
                    inicio_str = self._formatear_tiempo(voz['inicio'])
                    fin_str = self._formatear_tiempo(voz['fin'])
                    db_change = voz.get('db_change', 0)
                    lineas.append(f"[{inicio_str} - {fin_str}] Voz elevada detectada (+{db_change:.2f} dB)\n")
            else:
                lineas.append("No se detectaron momentos de voz elevada.\n")
            
            lineas.append("\nESTRÉS ACÚSTICO:\n")
            lineas.append("-" * 80 + "\n")
            lineas.append(f"Total de momentos de estrés detectados: {len(analisis_voz)}\n")
            if analisis_voz:
                db_promedio = sum(v.get('db_change', 0) for v in analisis_voz) / len(analisis_voz)
                lineas.append(f"Cambio promedio de volumen: {db_promedio:.2f} dB\n")
        
        lineas.append("\n" + "=" * 80 + "\n\n")
        
        # ============================================================
        # E. ANÁLISIS DE VÍCTIMAS (ES)
        # ============================================================
        lineas.append("E. ANÁLISIS DE VÍCTIMAS (ES)\n")
        lineas.append("=" * 80 + "\n\n")
        
        if not analisis_victimas:
            lineas.append("No se detectaron agresiones dirigidas a víctimas específicas.\n\n")
        else:
            # Agrupar por víctima
            por_victima = {}
            for det in analisis_victimas:
                victima = det.get('victima', 'Desconocida')
                if victima not in por_victima:
                    por_victima[victima] = []
                por_victima[victima].append(det)
            
            # Escribir por víctima
            for victima, dets in por_victima.items():
                lineas.append(f"\nAGRESIÓN HACIA {victima.upper()} ({len(dets)} detecciones):\n")
                lineas.append("-" * 80 + "\n")
                
                # Agrupar por tipo de agresión
                por_tipo_victima = {}
                for det in dets:
                    tipo = det.get('tipo', 'desconocido')
                    if tipo not in por_tipo_victima:
                        por_tipo_victima[tipo] = []
                    por_tipo_victima[tipo].append(det)
                
                for tipo, dets_tipo in por_tipo_victima.items():
                    lineas.append(f"\n  Tipo: {tipo.upper()} ({len(dets_tipo)} instancias)\n")
                    for det in dets_tipo:
                        inicio_str = self._formatear_tiempo(det['inicio'])
                        fin_str = self._formatear_tiempo(det['fin'])
                        severidad = det.get('severidad', 'media')
                        frase = det.get('frase', '')
                        lineas.append(f"    [{inicio_str} - {fin_str}] Severidad: {severidad.upper()}\n")
                        lineas.append(f"      {frase}\n\n")
        
        lineas.append("\n" + "=" * 80 + "\n\n")
        
        # ============================================================
        # F. ANÁLISIS FORENSE LEGAL DANÉS (§243)
        # ============================================================
        lineas.append("F. ANÁLISIS FORENSE LEGAL DANÉS (§243)\n")
        lineas.append("=" * 80 + "\n\n")
        
        # Clasificación bajo §243
        juridisk_klassifikation = analisis_forense_dk.get('juridisk_klassifikation', {})
        lineas.append("CLASIFICACIÓN BAJO STRAFFELOVEN §243:\n")
        lineas.append("-" * 80 + "\n")
        
        vurdering = juridisk_klassifikation.get('vurdering', '')
        if vurdering:
            lineas.append(f"{vurdering}\n\n")
        
        # Criterios detectados
        kriterier_opfyldt = juridisk_klassifikation.get('kriterier_opfyldt', [])
        if kriterier_opfyldt:
            lineas.append("Criterios detectados:\n")
            for kriterium in kriterier_opfyldt:
                lineas.append(f"  - {kriterium}\n")
            lineas.append("\n")
        
        # Nivel de riesgo (puede venir como string completo o solo nivel)
        risikoniveau_raw = analisis_forense_dk.get('risikoniveau', 'Lav risiko')
        # Extraer solo el nivel si viene como "Lav risiko", "Moderat risiko", etc.
        if isinstance(risikoniveau_raw, str) and ' ' in risikoniveau_raw:
            risikoniveau = risikoniveau_raw.split()[0].lower()
        else:
            risikoniveau = str(risikoniveau_raw).lower()
        
        lineas.append(f"NIVEL DE RIESGO: {risikoniveau.upper()}\n")
        lineas.append("-" * 80 + "\n")
        
        if risikoniveau == 'lav':
            lineas.append("Riesgo bajo: Pocas indicaciones de violencia psicológica.\n\n")
        elif risikoniveau == 'moderat':
            lineas.append("Riesgo moderado: Se detectaron algunos indicadores de violencia psicológica.\n\n")
        elif risikoniveau == 'høj':
            lineas.append("Riesgo alto: Se detectaron múltiples indicadores de violencia psicológica.\n\n")
        elif risikoniveau == 'kritisk':
            lineas.append("Riesgo crítico: Se detectaron indicadores graves y repetidos de violencia psicológica.\n\n")
        else:
            lineas.append(f"Riesgo evaluado: {risikoniveau_raw}\n\n")
        
        # Evidencia textual con timestamps
        tidsbegivenheder = analisis_forense_dk.get('tidsbegivenheder', [])
        if tidsbegivenheder:
            lineas.append("EVIDENCIA TEXTUAL CON TIMESTAMPS:\n")
            lineas.append("-" * 80 + "\n")
            for evento in tidsbegivenheder:
                tidsstempel = evento.get('tidsstempel', '00:00')
                tekst = evento.get('tekst', '')
                typer = evento.get('typer', [])
                if tekst:
                    tipos_str = ', '.join(typer) if typer else ''
                    if tipos_str:
                        lineas.append(f"[{tidsstempel}] {tipos_str}: {tekst}\n")
                    else:
                        lineas.append(f"[{tidsstempel}] {tekst}\n")
            lineas.append("\n")
        
        lineas.append("\n" + "=" * 80 + "\n\n")
        
        # ============================================================
        # G. INFORME UNIFICADO (ES)
        # ============================================================
        lineas.append("G. INFORME UNIFICADO (ES)\n")
        lineas.append("=" * 80 + "\n\n")
        
        lineas.append("RESUMEN NARRATIVO COMPLETO:\n")
        lineas.append("-" * 80 + "\n\n")
        
        # Resumen narrativo
        total_agresiones = len(analisis_agresion)
        total_voz = len(analisis_voz)
        total_victimas = len(analisis_victimas)
        
        lineas.append(f"El análisis del archivo '{nombre_archivo}' revela lo siguiente:\n\n")
        
        lineas.append(f"TRANSCRIPCIÓN: Se transcribió un audio de {self._formatear_duracion(duracion_audio)} ")
        lineas.append(f"en el idioma {resultado_whisper.get('language', 'desconocido')}.\n\n")
        
        if total_agresiones > 0:
            lineas.append(f"ANÁLISIS DE AGRESIÓN: Se detectaron {total_agresiones} instancias de agresión verbal, ")
            lineas.append("incluyendo insultos, amenazas, descalificaciones, gaslighting, manipulación emocional, ")
            lineas.append("invalidación y control económico.\n\n")
        else:
            lineas.append("ANÁLISIS DE AGRESIÓN: No se detectaron instancias de agresión verbal en el audio.\n\n")
        
        if total_voz > 0:
            lineas.append(f"ANÁLISIS DE VOZ: Se detectaron {total_voz} momentos de voz elevada o estrés acústico, ")
            lineas.append("indicando posibles picos de volumen y cambios bruscos de tono.\n\n")
        else:
            lineas.append("ANÁLISIS DE VOZ: No se detectaron momentos significativos de voz elevada o estrés acústico.\n\n")
        
        if total_victimas > 0:
            lineas.append(f"ANÁLISIS DE VÍCTIMAS: Se detectaron {total_victimas} instancias de agresión dirigida ")
            lineas.append("específicamente hacia víctimas identificadas (Claudia, Juan Diego, José Carlos).\n\n")
        else:
            lineas.append("ANÁLISIS DE VÍCTIMAS: No se detectaron agresiones dirigidas a víctimas específicas.\n\n")
        
        lineas.append("ANÁLISIS FORENSE LEGAL DANÉS: ")
        lineas.append(f"Según la evaluación bajo Straffeloven §243, el nivel de riesgo es {risikoniveau.upper()}. ")
        if vurdering:
            lineas.append(f"{vurdering}\n\n")
        else:
            lineas.append("Se realizó una evaluación completa de los criterios legales.\n\n")
        
        lineas.append("\nEXPLICACIÓN CLARA Y ENTENDIBLE:\n")
        lineas.append("-" * 80 + "\n\n")
        
        lineas.append("Este informe consolida todos los análisis realizados sobre el audio. ")
        lineas.append("La transcripción proporciona el contenido textual completo con referencias temporales precisas. ")
        lineas.append("El análisis de agresión identifica patrones verbales que pueden constituir violencia psicológica. ")
        lineas.append("El análisis de voz detecta cambios acústicos que pueden indicar estrés o agresividad. ")
        lineas.append("El análisis de víctimas identifica agresiones dirigidas específicamente a personas identificadas. ")
        lineas.append("Finalmente, el análisis forense legal danés evalúa el contenido según los criterios de ")
        lineas.append("Straffeloven §243 sobre violencia psicológica.\n\n")
        
        lineas.append("\nCONCLUSIONES:\n")
        lineas.append("-" * 80 + "\n\n")
        
        # Conclusiones basadas en los análisis
        conclusiones = []
        
        if total_agresiones > 0:
            conclusiones.append(f"Se identificaron {total_agresiones} instancias de agresión verbal que requieren atención.")
        
        if total_voz > 0:
            conclusiones.append(f"Se detectaron {total_voz} momentos de voz elevada que pueden indicar estrés o agresividad.")
        
        if total_victimas > 0:
            conclusiones.append(f"Se identificaron {total_victimas} agresiones dirigidas a víctimas específicas.")
        
        if risikoniveau in ['høj', 'kritisk']:
            conclusiones.append(f"El nivel de riesgo evaluado es {risikoniveau.upper()}, lo que indica la necesidad de atención inmediata.")
        elif risikoniveau == 'moderat':
            conclusiones.append("El nivel de riesgo es MODERADO, indicando algunos indicadores de violencia psicológica.")
        else:
            conclusiones.append("El nivel de riesgo es BAJO, con pocas indicaciones de violencia psicológica.")
        
        if conclusiones:
            for i, conclusion in enumerate(conclusiones, 1):
                lineas.append(f"{i}. {conclusion}\n")
        else:
            lineas.append("No se detectaron indicadores significativos de violencia psicológica en el audio analizado.\n")
        
        lineas.append("\n" + "=" * 80 + "\n")
        lineas.append(f"Fin del informe - Generado el {fecha_analisis}\n")
        lineas.append("=" * 80 + "\n")
        
        return ''.join(lineas)
    
    def guardar_informe(
        self,
        contenido: str,
        nombre_archivo_audio: str,
        carpeta_salida: str
    ) -> str:
        """
        Guarda el informe único en un archivo TXT
        
        Args:
            contenido: Contenido del informe
            nombre_archivo_audio: Nombre del archivo de audio original
            carpeta_salida: Carpeta donde guardar el informe
        
        Returns:
            Ruta del archivo guardado
        """
        # Generar nombre del archivo
        nombre_base = os.path.splitext(nombre_archivo_audio)[0]
        nombre_base = nombre_base.replace(' ', '_').replace('/', '_').replace('\\', '_')
        nombre_archivo = f"{nombre_base}_INFORME_UNICO.txt"
        
        ruta_completa = os.path.join(carpeta_salida, nombre_archivo)
        
        # Asegurar que la carpeta existe
        os.makedirs(carpeta_salida, exist_ok=True)
        
        # Guardar archivo
        with open(ruta_completa, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        self.logger.info(f"Informe único guardado: {ruta_completa}")
        
        return ruta_completa

