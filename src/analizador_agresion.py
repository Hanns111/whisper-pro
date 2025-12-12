"""
Analizador avanzado de agresión verbal
Detecta insultos, amenazas, descalificaciones, gaslighting, manipulación e invalidación
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging


class AgresionAnalyzer:
    """
    Clase para analizar agresión verbal en transcripciones
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._inicializar_patrones()
    
    def _inicializar_patrones(self):
        """Inicializa todos los patrones de detección"""
        
        # Insultos directos
        self.insultos = [
            r'\b(puta|puto|hijo de puta|hdp|maldito|maldita|imbécil|idiota|estúpido|estúpida|tonto|tonta|tarado|tarada|retrasado|retrasada)\b',
            r'\b(maricón|marica|joto|jota|culero|culera|pendejo|pendeja|mamón|mamona)\b',
            r'\b(chinga|chingado|chingada|verga|pinche|pinchi|joder|jodido|jodida)\b',
            r'\b(cabrón|cabrona|hijueputa|hijueputo|malparido|malparida)\b',
            r'\b(desgraciado|desgraciada|sinvergüenza|sinverguenza|canalla|basura|mierda)\b',
            r'\b(inútil|incompetente|incapaz|inútil|inútil)\b'
        ]
        
        # Amenazas
        self.amenazas = [
            r'\b(te voy a|vas a ver|te haré|te haré pagar|te voy a hacer)\b',
            r'\b(te mato|te mataré|te voy a matar|te mato)\b',
            r'\b(te voy a golpear|te golpeo|te pego|te voy a pegar)\b',
            r'\b(te voy a dejar|te dejo|me voy|te abandono)\b',
            r'\b(vas a arrepentirte|te arrepentirás|lo pagarás|pagarás)\b',
            r'\b(te voy a denunciar|te denuncio|te denunciaré|te voy a reportar)\b',
            r'\b(vas a pagar|pagarás|lo pagarás|te cobraré)\b',
            r'\b(te voy a destruir|te destruiré|te voy a arruinar)\b'
        ]
        
        # Descalificaciones
        self.descalificaciones = [
            r'\b(no sirves|no vales|no eres nada|no eres nadie)\b',
            r'\b(eres un fracaso|eres un desastre|no haces nada bien)\b',
            r'\b(no sabes hacer nada|no sabes nada|no entiendes nada)\b',
            r'\b(eres inútil|no sirves para nada|no vales la pena)\b',
            r'\b(estás loca|estás loco|estás mal de la cabeza)\b',
            r'\b(no tienes cerebro|no piensas|no razonas)\b'
        ]
        
        # Gaslighting
        self.gaslighting = [
            r'\b(eso nunca pasó|no pasó así|te lo estás inventando|eso no es verdad)\b',
            r'\b(estás confundida|estás confundido|no fue así|te equivocas)\b',
            r'\b(lo estás recordando mal|tienes mala memoria|no fue así)\b',
            r'\b(estás loca|estás loco|estás alucinando|te lo inventaste)\b',
            r'\b(eso no es verdad|eso es mentira|mientes|estás mintiendo)\b',
            r'\b(no dije eso|nunca dije eso|te lo inventaste|no fue así)\b',
            r'\b(estás exagerando|siempre exageras|no fue tan grave)\b',
            r'\b(no fue así|no pasó|te lo estás imaginando)\b'
        ]
        
        # Manipulación emocional
        self.manipulacion = [
            r'\b(no me quieres|no me amas|si me quisieras|si me amaras)\b',
            r'\b(eres egoísta|solo piensas en ti|nunca me escuchas)\b',
            r'\b(me haces sentir mal|me haces daño|me lastimas|me duele)\b',
            r'\b(es tu culpa|tú tienes la culpa|por tu culpa|es por ti)\b',
            r'\b(no entiendes|nunca entiendes|no me entiendes)\b',
            r'\b(estás loca|estás loco|estás mal de la cabeza)\b',
            r'\b(exageras|siempre exageras|estás exagerando)\b',
            r'\b(me haces esto|me haces sufrir|me estás matando)\b',
            r'\b(si me quisieras|si me amaras|si me respetaras)\b'
        ]
        
        # Invalidación
        self.invalidacion = [
            r'\b(no es para tanto|no es tan grave|no es nada)\b',
            r'\b(estás exagerando|siempre exageras|no es tan malo)\b',
            r'\b(no tienes razón|estás equivocada|estás equivocado)\b',
            r'\b(tus sentimientos no importan|no es importante|no vale la pena)\b',
            r'\b(no deberías sentirte así|no tienes por qué|no es para llorar)\b',
            r'\b(eso no es nada|no es problema|no es tan grave)\b',
            r'\b(te estás haciendo la víctima|siempre te haces la víctima)\b'
        ]
    
    def _calcular_severidad(self, tipo: str, texto: str) -> str:
        """
        Calcula la severidad de la agresión
        
        Args:
            tipo: Tipo de agresión
            texto: Texto del segmento
            
        Returns:
            'baja', 'media' o 'alta'
        """
        texto_lower = texto.lower()
        
        # Palabras que indican alta severidad
        palabras_alta = ['matar', 'muerte', 'golpear', 'destruir', 'arruinar', 'denunciar']
        palabras_media = ['dejar', 'abandonar', 'culpa', 'egoísta', 'inútil']
        
        # Amenazas y insultos graves son alta severidad
        if tipo in ['amenaza', 'insulto']:
            for palabra in palabras_alta:
                if palabra in texto_lower:
                    return 'alta'
            return 'media'
        
        # Gaslighting y manipulación suelen ser media
        if tipo in ['gaslighting', 'manipulación']:
            if any(palabra in texto_lower for palabra in palabras_media):
                return 'media'
            return 'baja'
        
        # Descalificaciones e invalidación suelen ser media/baja
        if tipo in ['descalificación', 'invalidación']:
            return 'media'
        
        return 'baja'
    
    def _detectar_tipo_agresion(self, texto: str) -> Optional[tuple]:
        """
        Detecta el tipo de agresión en un texto
        
        Args:
            texto: Texto a analizar
            
        Returns:
            Tupla (tipo, patrón_matched) o None
        """
        texto_lower = texto.lower()
        
        # Verificar amenazas primero (más grave)
        for patron in self.amenazas:
            if re.search(patron, texto_lower, re.IGNORECASE):
                return ('amenaza', patron)
        
        # Insultos
        for patron in self.insultos:
            if re.search(patron, texto_lower, re.IGNORECASE):
                return ('insulto', patron)
        
        # Gaslighting
        for patron in self.gaslighting:
            if re.search(patron, texto_lower, re.IGNORECASE):
                return ('gaslighting', patron)
        
        # Manipulación
        for patron in self.manipulacion:
            if re.search(patron, texto_lower, re.IGNORECASE):
                return ('manipulación', patron)
        
        # Descalificaciones
        for patron in self.descalificaciones:
            if re.search(patron, texto_lower, re.IGNORECASE):
                return ('descalificación', patron)
        
        # Invalidación
        for patron in self.invalidacion:
            if re.search(patron, texto_lower, re.IGNORECASE):
                return ('invalidación', patron)
        
        return None
    
    def analizar_segmento(
        self,
        segmento: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Analiza un segmento individual
        
        Args:
            segmento: Segmento de Whisper con 'text', 'start', 'end'
            
        Returns:
            Diccionario con análisis o None si no hay agresión
        """
        texto = segmento.get('text', '').strip()
        inicio = segmento.get('start', 0)
        fin = segmento.get('end', 0)
        
        if not texto:
            return None
        
        # Detectar tipo de agresión
        resultado = self._detectar_tipo_agresion(texto)
        
        if not resultado:
            return None
        
        tipo, _ = resultado
        
        # Calcular severidad
        severidad = self._calcular_severidad(tipo, texto)
        
        return {
            'inicio': inicio,
            'fin': fin,
            'tipo': tipo,
            'frase': texto,
            'severidad': severidad
        }
    
    def analizar_transcripcion(
        self,
        resultado_whisper: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Analiza una transcripción completa
        
        Args:
            resultado_whisper: Resultado completo de Whisper
            
        Returns:
            Lista de detecciones de agresión
        """
        segmentos = resultado_whisper.get('segments', [])
        detecciones = []
        
        for segmento in segmentos:
            analisis = self.analizar_segmento(segmento)
            if analisis:
                detecciones.append(analisis)
        
        self.logger.info(f"Detectadas {len(detecciones)} instancias de agresión verbal")
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
        
        resultado = {
            'fecha_analisis': datetime.now().isoformat(),
            'total_detecciones': len(detecciones),
            'detecciones': detecciones
        }
        
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Análisis exportado a JSON: {ruta_salida}")
    
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
            titulo = "ANÁLISIS DE AGRESIÓN VERBAL\n"
            titulo += "=" * 50 + "\n\n"
            encabezados = ["Inicio", "Fin", "Tipo", "Severidad", "Frase"]
        else:
            titulo = "VERBAL AGGRESSION ANALYSIS\n"
            titulo += "=" * 50 + "\n\n"
            encabezados = ["Start", "End", "Type", "Severity", "Phrase"]
        
        lineas = [titulo]
        lineas.append(f"Total de detecciones: {len(detecciones)}\n\n")
        
        for det in detecciones:
            inicio_str = self._formatear_tiempo(det['inicio'])
            fin_str = self._formatear_tiempo(det['fin'])
            
            linea = f"[{inicio_str} - {fin_str}] {det['tipo'].upper()} ({det['severidad']})\n"
            linea += f"  {det['frase']}\n\n"
            lineas.append(linea)
        
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            f.writelines(lineas)
        
        self.logger.info(f"Análisis exportado a TXT ({idioma}): {ruta_salida}")
    
    def _formatear_tiempo(self, segundos: float) -> str:
        """Formatea tiempo en formato MM:SS"""
        minutos = int(segundos // 60)
        segs = int(segundos % 60)
        return f"{minutos:02d}:{segs:02d}"





