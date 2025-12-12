"""
Módulo para detectar violencia verbal en transcripciones
Detecta insultos, manipulación, gaslighting, amenazas y denigración
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging


class ViolenceDetector:
    """
    Clase para detectar diferentes tipos de violencia verbal en transcripciones
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._inicializar_patrones()
    
    def _inicializar_patrones(self):
        """Inicializa los patrones de detección"""
        
        # Insultos comunes (español)
        self.insultos = [
            r'\b(puta|puto|hijo de puta|hdp|maldito|maldita|imbécil|idiota|estúpido|estúpida|tonto|tonta|tarado|tarada|retrasado|retrasada)\b',
            r'\b(maricón|marica|joto|jota|culero|culera|pendejo|pendeja|mamón|mamona)\b',
            r'\b(chinga|chingado|chingada|verga|pinche|pinchi|joder|jodido|jodida)\b',
            r'\b(cabrón|cabrona|hijueputa|hijueputo|malparido|malparida)\b',
            r'\b(desgraciado|desgraciada|sinvergüenza|sinverguenza|canalla|basura)\b'
        ]
        
        # Patrones de manipulación emocional
        self.manipulacion = [
            r'\b(no me quieres|no me amas|si me quisieras|si me amaras)\b',
            r'\b(eres egoísta|solo piensas en ti|nunca me escuchas)\b',
            r'\b(me haces sentir mal|me haces daño|me lastimas)\b',
            r'\b(es tu culpa|tú tienes la culpa|por tu culpa)\b',
            r'\b(no entiendes|nunca entiendes|no me entiendes)\b',
            r'\b(estás loca|estás loco|estás mal de la cabeza)\b',
            r'\b(exageras|siempre exageras|estás exagerando)\b'
        ]
        
        # Patrones de gaslighting
        self.gaslighting = [
            r'\b(eso nunca pasó|no pasó así|te lo estás inventando)\b',
            r'\b(estás confundida|estás confundido|no fue así)\b',
            r'\b(lo estás recordando mal|tienes mala memoria)\b',
            r'\b(estás loca|estás loco|estás alucinando)\b',
            r'\b(eso no es verdad|eso es mentira|mientes)\b',
            r'\b(no dije eso|nunca dije eso|te lo inventaste)\b'
        ]
        
        # Patrones de amenazas
        self.amenazas = [
            r'\b(te voy a|vas a ver|te haré|te haré pagar)\b',
            r'\b(te mato|te mataré|te voy a matar)\b',
            r'\b(te voy a golpear|te golpeo|te pego)\b',
            r'\b(te voy a dejar|te dejo|me voy)\b',
            r'\b(vas a arrepentirte|te arrepentirás)\b',
            r'\b(te voy a denunciar|te denuncio|te denunciaré)\b',
            r'\b(vas a pagar|pagarás|lo pagarás)\b'
        ]
        
        # Nombres de víctimas
        self.victimas = {
            'claudia': ['claudia', 'clau'],
            'juan_diego': ['juan diego', 'juan', 'diego'],
            'jose_carlos': ['josé carlos', 'jose carlos', 'josé', 'jose', 'carlos']
        }
        
        # Patrones de denigración hacia Claudia
        self.denigracion_claudia = [
            r'\b(claudia.*puta|claudia.*maldita|claudia.*desgraciada)\b',
            r'\b(claudia.*estúpida|claudia.*idiota|claudia.*tonta)\b',
            r'\b(clau.*puta|clau.*maldita)\b'
        ]
    
    def detectar_violencia(
        self,
        texto: str,
        timestamp: Optional[float] = None,
        minuto_segundo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Detecta violencia verbal en un texto
        
        Args:
            texto: Texto a analizar
            timestamp: Timestamp en segundos
            minuto_segundo: Timestamp formateado como "MM:SS"
            
        Returns:
            Diccionario con información de violencia detectada
        """
        texto_lower = texto.lower()
        resultado = {
            'violencia': False,
            'tipo': None,
            'minuto_segundo': minuto_segundo or self._formatear_tiempo(timestamp) if timestamp else '',
            'texto': texto.strip()
        }
        
        # Detectar insultos
        for patron in self.insultos:
            if re.search(patron, texto_lower, re.IGNORECASE):
                resultado['violencia'] = True
                resultado['tipo'] = 'insulto'
                return resultado
        
        # Detectar amenazas
        for patron in self.amenazas:
            if re.search(patron, texto_lower, re.IGNORECASE):
                resultado['violencia'] = True
                resultado['tipo'] = 'amenaza'
                return resultado
        
        # Detectar gaslighting
        for patron in self.gaslighting:
            if re.search(patron, texto_lower, re.IGNORECASE):
                resultado['violencia'] = True
                resultado['tipo'] = 'gaslighting'
                return resultado
        
        # Detectar manipulación
        for patron in self.manipulacion:
            if re.search(patron, texto_lower, re.IGNORECASE):
                resultado['violencia'] = True
                resultado['tipo'] = 'manipulación'
                return resultado
        
        return resultado
    
    def detectar_victimas_mencionadas(self, texto: str) -> List[str]:
        """
        Detecta si se mencionan víctimas en el texto
        
        Args:
            texto: Texto a analizar
            
        Returns:
            Lista de víctimas mencionadas
        """
        texto_lower = texto.lower()
        victimas_encontradas = []
        
        for victima_key, variantes in self.victimas.items():
            for variante in variantes:
                if variante in texto_lower:
                    # Convertir clave a nombre legible
                    nombre_legible = victima_key.replace('_', ' ').title()
                    if nombre_legible not in victimas_encontradas:
                        victimas_encontradas.append(nombre_legible)
        
        return victimas_encontradas
    
    def detectar_denigracion_claudia(self, texto: str) -> bool:
        """
        Detecta denigración específica hacia Claudia
        
        Args:
            texto: Texto a analizar
            
        Returns:
            True si se detecta denigración hacia Claudia
        """
        texto_lower = texto.lower()
        
        for patron in self.denigracion_claudia:
            if re.search(patron, texto_lower, re.IGNORECASE):
                return True
        
        return False
    
    def analizar_segmento(
        self,
        segmento: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analiza un segmento completo de transcripción
        
        Args:
            segmento: Segmento de transcripción con 'text' y 'start'
            
        Returns:
            Diccionario con análisis completo
        """
        texto = segmento.get('text', '')
        start = segmento.get('start', 0)
        minuto_segundo = self._formatear_tiempo(start)
        
        # Detectar violencia
        violencia = self.detectar_violencia(texto, timestamp=start, minuto_segundo=minuto_segundo)
        
        # Detectar víctimas mencionadas
        victimas = self.detectar_victimas_mencionadas(texto)
        
        # Detectar denigración hacia Claudia
        denigracion_claudia = self.detectar_denigracion_claudia(texto)
        
        return {
            'violencia': violencia['violencia'],
            'tipo_violencia': violencia['tipo'],
            'victimas_mencionadas': victimas,
            'denigracion_claudia': denigracion_claudia,
            'minuto_segundo': minuto_segundo,
            'texto': texto.strip()
        }
    
    def analizar_transcripcion_completa(
        self,
        resultado_whisper: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analiza una transcripción completa y genera reporte
        
        Args:
            resultado_whisper: Resultado completo de Whisper
            
        Returns:
            Diccionario con análisis completo
        """
        segmentos = resultado_whisper.get('segments', [])
        momentos_agresion = []
        victimas_totales = set()
        contiene_insultos = False
        
        for segmento in segmentos:
            analisis = self.analizar_segmento(segmento)
            
            if analisis['violencia']:
                momentos_agresion.append({
                    'texto': analisis['texto'],
                    'minuto_segundo': analisis['minuto_segundo'],
                    'tipo': analisis['tipo_violencia']
                })
                
                if analisis['tipo_violencia'] == 'insulto':
                    contiene_insultos = True
            
            # Agregar víctimas mencionadas
            for victima in analisis['victimas_mencionadas']:
                victimas_totales.add(victima)
        
        return {
            'contiene_insultos': contiene_insultos,
            'victima_mencionada': list(victimas_totales),
            'momentos_agresion': momentos_agresion,
            'total_momentos_agresion': len(momentos_agresion)
        }
    
    def _formatear_tiempo(self, segundos: float) -> str:
        """
        Formatea tiempo en formato MM:SS
        
        Args:
            segundos: Tiempo en segundos
            
        Returns:
            Tiempo formateado como "MM:SS"
        """
        minutos = int(segundos // 60)
        segs = int(segundos % 60)
        return f"{minutos:02d}:{segs:02d}"





