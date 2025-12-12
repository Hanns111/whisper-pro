"""
Detector de agresión dirigida a víctimas específicas
Detecta menciones y agresiones dirigidas a Claudia, Juan Diego y José Carlos
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging


class VictimDetector:
    """
    Clase para detectar agresión dirigida a víctimas específicas
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._inicializar_victimas()
        self._inicializar_patrones_agresion()
    
    def _inicializar_victimas(self):
        """Inicializa los nombres de víctimas y sus variantes"""
        self.victimas = {
            'Claudia': {
                'variantes': ['claudia', 'clau', 'claudita'],
                'patron_base': r'\b(claudia|clau|claudita)\b'
            },
            'Juan Diego': {
                'variantes': ['juan diego', 'juan', 'diego', 'juandiego'],
                'patron_base': r'\b(juan\s+diego|juan|diego|juandiego)\b'
            },
            'José Carlos': {
                'variantes': ['josé carlos', 'jose carlos', 'josé', 'jose', 'carlos'],
                'patron_base': r'\b(jos[ée]\s+carlos|jos[ée]|carlos)\b'
            }
        }
    
    def _inicializar_patrones_agresion(self):
        """Inicializa patrones de agresión dirigida"""
        
        # Insulto dirigido
        self.insulto_dirigido = [
            r'\b({victima}).*?(puta|puto|maldita|maldito|estúpida|estúpido|idiota|imbécil|tonta|tonto)\b',
            r'\b(puta|puto|maldita|maldito|estúpida|estúpido|idiota|imbécil|tonta|tonto).*?({victima})\b'
        ]
        
        # Amenaza dirigida
        self.amenaza_dirigida = [
            r'\b({victima}).*?(te voy a|vas a ver|te haré|te mato|te voy a matar|te voy a golpear)\b',
            r'\b(te voy a|vas a ver|te haré|te mato|te voy a matar|te voy a golpear).*?({victima})\b'
        ]
        
        # Invalidación dirigida
        self.invalidacion_dirigida = [
            r'\b({victima}).*?(no tienes razón|estás equivocada|estás equivocado|no es verdad|mientes)\b',
            r'\b(no tienes razón|estás equivocada|estás equivocado|no es verdad|mientes).*?({victima})\b'
        ]
        
        # Manipulación dirigida
        self.manipulacion_dirigida = [
            r'\b({victima}).*?(es tu culpa|por tu culpa|si me quisieras|si me amaras)\b',
            r'\b(es tu culpa|por tu culpa|si me quisieras|si me amaras).*?({victima})\b'
        ]
        
        # Burla dirigida
        self.burla_dirigida = [
            r'\b({victima}).*?(ridícula|ridículo|tonta|tonto|estúpida|estúpido)\b',
            r'\b(ridícula|ridículo|tonta|tonto|estúpida|estúpido).*?({victima})\b'
        ]
        
        # Presión emocional dirigida
        self.presion_emocional_dirigida = [
            r'\b({victima}).*?(me haces sentir mal|me lastimas|me haces daño|me duele)\b',
            r'\b(me haces sentir mal|me lastimas|me haces daño|me duele).*?({victima})\b'
        ]
        
        # Órdenes hostiles
        self.ordenes_hostiles = [
            r'\b({victima}).*?(cállate|cierra la boca|no hables|no digas nada|obedece)\b',
            r'\b(cállate|cierra la boca|no hables|no digas nada|obedece).*?({victima})\b'
        ]
    
    def _detectar_agresion_dirigida(
        self,
        texto: str,
        victima: str,
        patron_victima: str
    ) -> Optional[tuple]:
        """
        Detecta si hay agresión dirigida a una víctima específica
        
        Args:
            texto: Texto a analizar
            victima: Nombre de la víctima
            patron_victima: Patrón regex para la víctima
            
        Returns:
            Tupla (tipo_agresion, severidad) o None
        """
        texto_lower = texto.lower()
        
        # Verificar que se menciona la víctima
        if not re.search(patron_victima, texto_lower, re.IGNORECASE):
            return None
        
        # Reemplazar {victima} en patrones
        patron_victima_clean = patron_victima.replace(r'\b', '').replace('(', '').replace(')', '').replace('|', '|')
        
        # Verificar amenaza dirigida (más grave)
        for patron in self.amenaza_dirigida:
            patron_final = patron.format(victima=patron_victima_clean)
            if re.search(patron_final, texto_lower, re.IGNORECASE):
                return ('amenaza dirigida', 'alta')
        
        # Insulto dirigido
        for patron in self.insulto_dirigido:
            patron_final = patron.format(victima=patron_victima_clean)
            if re.search(patron_final, texto_lower, re.IGNORECASE):
                return ('insulto dirigido', 'alta')
        
        # Órdenes hostiles
        for patron in self.ordenes_hostiles:
            patron_final = patron.format(victima=patron_victima_clean)
            if re.search(patron_final, texto_lower, re.IGNORECASE):
                return ('órdenes hostiles', 'media')
        
        # Presión emocional dirigida
        for patron in self.presion_emocional_dirigida:
            patron_final = patron.format(victima=patron_victima_clean)
            if re.search(patron_final, texto_lower, re.IGNORECASE):
                return ('presión emocional dirigida', 'media')
        
        # Manipulación dirigida
        for patron in self.manipulacion_dirigida:
            patron_final = patron.format(victima=patron_victima_clean)
            if re.search(patron_final, texto_lower, re.IGNORECASE):
                return ('manipulación dirigida', 'media')
        
        # Invalidación dirigida
        for patron in self.invalidacion_dirigida:
            patron_final = patron.format(victima=patron_victima_clean)
            if re.search(patron_final, texto_lower, re.IGNORECASE):
                return ('invalidación dirigida', 'media')
        
        # Burla dirigida
        for patron in self.burla_dirigida:
            patron_final = patron.format(victima=patron_victima_clean)
            if re.search(patron_final, texto_lower, re.IGNORECASE):
                return ('burla dirigida', 'baja')
        
        # Si se menciona pero no hay agresión específica, retornar mención
        return ('mención', 'baja')
    
    def analizar_segmento(
        self,
        segmento: Dict[str, Any],
        analisis_agresion: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Analiza un segmento para detectar agresión dirigida a víctimas
        
        Args:
            segmento: Segmento de Whisper con 'text', 'start', 'end'
            analisis_agresion: Análisis de agresión del AgresionAnalyzer (opcional)
            
        Returns:
            Lista de detecciones de agresión dirigida
        """
        texto = segmento.get('text', '').strip()
        inicio = segmento.get('start', 0)
        fin = segmento.get('end', 0)
        
        if not texto:
            return []
        
        detecciones = []
        
        # Verificar cada víctima
        for nombre_victima, info in self.victimas.items():
            patron_victima = info['patron_base']
            
            # Detectar agresión dirigida
            resultado = self._detectar_agresion_dirigida(texto, nombre_victima, patron_victima)
            
            if resultado:
                tipo, severidad = resultado
                
                # Si hay análisis de agresión previo, combinar información
                if analisis_agresion and analisis_agresion.get('tipo'):
                    # Usar severidad más alta
                    severidad_agresion = analisis_agresion.get('severidad', 'baja')
                    if severidad_agresion == 'alta' or severidad == 'alta':
                        severidad = 'alta'
                    elif severidad_agresion == 'media' or severidad == 'media':
                        severidad = 'media'
                
                detecciones.append({
                    'victima': nombre_victima,
                    'inicio': inicio,
                    'fin': fin,
                    'tipo': tipo,
                    'frase': texto,
                    'severidad': severidad
                })
        
        return detecciones
    
    def analizar_transcripcion(
        self,
        resultado_whisper: Dict[str, Any],
        analisis_agresion: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analiza una transcripción completa para detectar agresión dirigida
        
        Args:
            resultado_whisper: Resultado completo de Whisper
            analisis_agresion: Lista de análisis de agresión del AgresionAnalyzer
            
        Returns:
            Lista de detecciones de agresión dirigida a víctimas
        """
        segmentos = resultado_whisper.get('segments', [])
        detecciones = []
        
        # Crear mapa de análisis de agresión por timestamp
        agresion_por_timestamp = {}
        for ag in analisis_agresion:
            key = (ag['inicio'], ag['fin'])
            agresion_por_timestamp[key] = ag
        
        # Analizar cada segmento
        for segmento in segmentos:
            inicio = segmento.get('start', 0)
            fin = segmento.get('end', 0)
            
            # Buscar análisis de agresión correspondiente
            analisis_correspondiente = None
            for ag in analisis_agresion:
                if abs(ag['inicio'] - inicio) < 1.0:  # Dentro de 1 segundo
                    analisis_correspondiente = ag
                    break
            
            # Analizar segmento
            detecciones_segmento = self.analizar_segmento(segmento, analisis_correspondiente)
            detecciones.extend(detecciones_segmento)
        
        self.logger.info(f"Detectadas {len(detecciones)} instancias de agresión dirigida a víctimas")
        return detecciones
    
    def exportar_json(
        self,
        detecciones: List[Dict[str, Any]],
        ruta_salida: str
    ):
        """
        Exporta análisis a JSON
        
        Args:
            detecciones: Lista de detecciones
            ruta_salida: Ruta del archivo JSON
        """
        import json
        
        # Agrupar por víctima
        por_victima = {}
        for det in detecciones:
            victima = det['victima']
            if victima not in por_victima:
                por_victima[victima] = []
            por_victima[victima].append(det)
        
        resultado = {
            'fecha_analisis': datetime.now().isoformat(),
            'total_detecciones': len(detecciones),
            'por_victima': por_victima,
            'detecciones': detecciones
        }
        
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Análisis de víctimas exportado a JSON: {ruta_salida}")
    
    def exportar_txt(
        self,
        detecciones: List[Dict[str, Any]],
        ruta_salida: str,
        idioma: str = 'es'
    ):
        """
        Exporta análisis a TXT
        
        Args:
            detecciones: Lista de detecciones
            ruta_salida: Ruta del archivo TXT
            idioma: 'es' o 'en'
        """
        if idioma == 'es':
            titulo = "ANÁLISIS DE AGRESIÓN DIRIGIDA A VÍCTIMAS\n"
            titulo += "=" * 50 + "\n\n"
        else:
            titulo = "VICTIM-DIRECTED AGGRESSION ANALYSIS\n"
            titulo += "=" * 50 + "\n\n"
        
        lineas = [titulo]
        lineas.append(f"Total de detecciones: {len(detecciones)}\n\n")
        
        # Agrupar por víctima
        por_victima = {}
        for det in detecciones:
            victima = det['victima']
            if victima not in por_victima:
                por_victima[victima] = []
            por_victima[victima].append(det)
        
        for victima, dets in por_victima.items():
            if idioma == 'es':
                lineas.append(f"VÍCTIMA: {victima} ({len(dets)} detecciones)\n")
                lineas.append("-" * 50 + "\n")
            else:
                lineas.append(f"VICTIM: {victima} ({len(dets)} detections)\n")
                lineas.append("-" * 50 + "\n")
            
            for det in dets:
                inicio_str = self._formatear_tiempo(det['inicio'])
                fin_str = self._formatear_tiempo(det['fin'])
                
                if idioma == 'es':
                    linea = f"[{inicio_str} - {fin_str}] {det['tipo'].upper()} ({det['severidad']})\n"
                else:
                    linea = f"[{inicio_str} - {fin_str}] {det['tipo'].upper()} ({det['severidad']})\n"
                
                linea += f"  {det['frase']}\n\n"
                lineas.append(linea)
            
            lineas.append("\n")
        
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            f.writelines(lineas)
        
        self.logger.info(f"Análisis de víctimas exportado a TXT ({idioma}): {ruta_salida}")
    
    def _formatear_tiempo(self, segundos: float) -> str:
        """Formatea tiempo en formato MM:SS"""
        minutos = int(segundos // 60)
        segs = int(segundos % 60)
        return f"{minutos:02d}:{segs:02d}"





