"""
Analizador forense para grabaciones de audio - Dinamarca
Análisis jurídico y psicológico según Straffeloven §243
Módulo forense objetivo sin diagnósticos ni especulaciones
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging


class AnalizadorForenseDK:
    """
    Clase para análisis forense de transcripciones según legislación danesa
    Enfoque en Straffeloven §243 (violencia psicológica)
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._inicializar_patrones_dk()
    
    def _inicializar_patrones_dk(self):
        """Inicializa patrones de detección según criterios legales daneses"""
        
        # Kontrol (Control)
        self.kontrol = [
            r'\b(du må ikke|du skal ikke|du kan ikke|du får ikke lov|jeg tillader ikke)\b',
            r'\b(jeg bestemmer|jeg bestemmer over|jeg kontrollerer|jeg styrer)\b',
            r'\b(du skal spørge mig|du skal bede om tilladelse|du skal have min tilladelse)\b',
            r'\b(jeg ved bedre|jeg ved hvad der er bedst|du ved ikke hvad du laver)\b',
            r'\b(du kan ikke klare dig uden mig|du er afhængig af mig)\b'
        ]
        
        # Økonomisk pres (Presión económica)
        self.okonomisk_pres = [
            r'\b(du får ingen penge|jeg giver dig ingen penge|du får ikke noget)\b',
            r'\b(jeg betaler ikke|jeg stopper betalingen|du får ikke noget fra mig)\b',
            r'\b(du skylder mig|du er i gæld til mig|du må betale)\b',
            r'\b(jeg tager pengene|jeg stopper overførslen|ingen penge til dig)\b',
            r'\b(du kan ikke få penge|du får ikke adgang til penge)\b'
        ]
        
        # Nedværdigende adfærd (Comportamiento degradante)
        self.nedvaerdigende = [
            r'\b(du er intet værd|du er ingenting|du er ubrugelig|du er værdiløs)\b',
            r'\b(du er dum|du er idiot|du er tåbelig|du er inkompetent)\b',
            r'\b(ingen vil have dig|ingen kan lide dig|du er alene)\b',
            r'\b(du er en fejl|du er en skuffelse|du er en byrde)\b',
            r'\b(du er ikke god nok|du er utilstrækkelig)\b'
        ]
        
        # Trusler (Amenazas)
        self.trusler = [
            r'\b(jeg gør dig noget|jeg skader dig|jeg gør ondt)\b',
            r'\b(jeg tager børnene|du får ikke børnene|jeg tager dem fra dig)\b',
            r'\b(jeg forlader dig|jeg går|jeg smutter|jeg dropper dig)\b',
            r'\b(jeg anmelder dig|jeg melder dig|jeg rapporterer dig)\b',
            r'\b(du kommer til at fortryde|du vil fortryde|du skal betale)\b',
            r'\b(jeg ødelægger dig|jeg ruinerer dig|jeg knuser dig)\b'
        ]
        
        # Gaslighting (Manipulación de la realidad)
        self.gaslighting = [
            r'\b(det skete ikke|det var ikke sådan|det er ikke sandt)\b',
            r'\b(du husker forkert|du tager fejl|du har misforstået)\b',
            r'\b(det var ikke så slemt|du overdriver|du gør det værre)\b',
            r'\b(jeg sagde det ikke|jeg gjorde det ikke|det var ikke mig)\b',
            r'\b(du opfinder ting|du finder på ting|du lyver)\b',
            r'\b(du er forvirret|du er desorienteret|du ved ikke hvad du snakker om)\b'
        ]
        
        # Manipulation (Manipulación)
        self.manipulation = [
            r'\b(hvis du elsker mig|hvis du holder af mig|hvis du respekterer mig)\b',
            r'\b(det er din skyld|du har skylden|det er fordi af dig)\b',
            r'\b(du gør mig ked af det|du sårer mig|du skader mig)\b',
            r'\b(jeg lider på grund af dig|du får mig til at lide)\b',
            r'\b(du er egoistisk|du tænker kun på dig selv)\b',
            r'\b(hvis du ikke|hvis du gør det ikke|hvis du nægter)\b'
        ]
        
        # Isolering (Aislamiento)
        self.isolering = [
            r'\b(du skal ikke se dem|du skal ikke snakke med dem|hold dig væk fra dem)\b',
            r'\b(ingen kan lide dig|de vil ikke have dig|du er ikke velkommen)\b',
            r'\b(du skal være alene|du skal isolere dig|hold dig væk)\b',
            r'\b(jeg er den eneste der kan lide dig|kun jeg forstår dig)\b'
        ]
        
        # Psykisk pres (Presión psicológica)
        self.psykisk_pres = [
            r'\b(du skal|du må|du er nødt til|du er tvunget til)\b',
            r'\b(jeg kræver|jeg forlanger|jeg insisterer på)\b',
            r'\b(du har ikke valg|du har ingen mulighed|du er tvunget)\b',
            r'\b(du må gøre det|du skal gøre det|du er forpligtet)\b'
        ]
    
    def _formatear_tiempo(self, segundos: float) -> str:
        """Formatea tiempo en formato MM:SS"""
        minutos = int(segundos // 60)
        segs = int(segundos % 60)
        return f"{minutos:02d}:{segs:02d}"
    
    def _detectar_patron(self, texto: str, patrones: List[str]) -> Optional[str]:
        """
        Detecta si un texto coincide con algún patrón
        
        Args:
            texto: Texto a analizar
            patrones: Lista de patrones regex
            
        Returns:
            Nombre del patrón detectado o None
        """
        texto_lower = texto.lower()
        
        for patron in patrones:
            if re.search(patron, texto_lower, re.IGNORECASE):
                return patron
        
        return None
    
    def _clasificar_tidsbegivenhed(
        self,
        segmento: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Clasifica un segmento según criterios legales daneses
        
        Args:
            segmento: Segmento de transcripción
            
        Returns:
            Diccionario con clasificación o None
        """
        texto = segmento.get('text', '').strip()
        inicio = segmento.get('start', 0)
        fin = segmento.get('end', 0)
        
        if not texto:
            return None
        
        # Detectar tipo de comportamiento
        tipos_detectados = []
        beskrivelse = []
        
        # Kontrol
        if self._detectar_patron(texto, self.kontrol):
            tipos_detectados.append('Kontrol')
            beskrivelse.append('Kontrolpræget udsagn')
        
        # Økonomisk pres
        if self._detectar_patron(texto, self.okonomisk_pres):
            tipos_detectados.append('Økonomisk pres')
            beskrivelse.append('Mistænkeligt økonomisk pres')
        
        # Nedværdigende
        if self._detectar_patron(texto, self.nedvaerdigende):
            tipos_detectados.append('Nedværdigende')
            beskrivelse.append('Nedværdigende kommentar')
        
        # Trusler
        if self._detectar_patron(texto, self.trusler):
            tipos_detectados.append('Trussel')
            beskrivelse.append('Trussel eller trussel-lignende udsagn')
        
        # Gaslighting
        if self._detectar_patron(texto, self.gaslighting):
            tipos_detectados.append('Gaslighting')
            beskrivelse.append('Gaslighting eller benægtelse af fakta')
        
        # Manipulation
        if self._detectar_patron(texto, self.manipulation):
            tipos_detectados.append('Manipulation')
            beskrivelse.append('Manipulerende udsagn')
        
        # Isolering
        if self._detectar_patron(texto, self.isolering):
            tipos_detectados.append('Isolering')
            beskrivelse.append('Isolerende adfærd')
        
        # Psykisk pres
        if self._detectar_patron(texto, self.psykisk_pres):
            tipos_detectados.append('Psykisk pres')
            beskrivelse.append('Psykisk pres eller tvang')
        
        if not tipos_detectados:
            return None
        
        return {
            'inicio': inicio,
            'fin': fin,
            'tidsstempel': self._formatear_tiempo(inicio),
            'typer': tipos_detectados,
            'beskrivelse': ', '.join(beskrivelse) if beskrivelse else 'Relevant udsagn',
            'tekst': texto
        }
    
    def _vurdere_straffelov_243(
        self,
        tidsbegivenheder: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evalúa si el contenido cumple criterios de Straffeloven §243
        
        Args:
            tidsbegivenheder: Lista de eventos temporales detectados
            
        Returns:
            Diccionario con evaluación legal
        """
        if not tidsbegivenheder:
            return {
                'vurdering': 'Ingen indikation på psykisk vold jf. §243.',
                'indikation': False,
                'begrundelse': 'Ingen relevante mønstre identificeret i optagelsen.'
            }
        
        # Contar tipos de comportamiento
        typer_count = {}
        for event in tidsbegivenheder:
            for typ in event.get('typer', []):
                typer_count[typ] = typer_count.get(typ, 0) + 1
        
        # Criterios para §243
        kriterier_opfyldt = []
        
        if typer_count.get('Kontrol', 0) >= 3:
            kriterier_opfyldt.append('Gentagen kontrol')
        
        if typer_count.get('Nedværdigende', 0) >= 2:
            kriterier_opfyldt.append('Nedværdigende adfærd')
        
        if typer_count.get('Manipulation', 0) >= 3:
            kriterier_opfyldt.append('Gentagen manipulation')
        
        if typer_count.get('Trussel', 0) >= 1:
            kriterier_opfyldt.append('Trusler (direkte eller indirekte)')
        
        if typer_count.get('Gaslighting', 0) >= 2:
            kriterier_opfyldt.append('Gaslighting')
        
        if typer_count.get('Isolering', 0) >= 1:
            kriterier_opfyldt.append('Isolering')
        
        if typer_count.get('Psykisk pres', 0) >= 3:
            kriterier_opfyldt.append('Psykisk pres')
        
        if typer_count.get('Økonomisk pres', 0) >= 2:
            kriterier_opfyldt.append('Økonomisk pres')
        
        if kriterier_opfyldt:
            return {
                'vurdering': 'Det analyserede indhold udviser karakteristika for psykisk vold jf. Straffeloven §243.',
                'indikation': True,
                'kriterier_opfyldt': kriterier_opfyldt,
                'begrundelse': f'Identificeret: {", ".join(kriterier_opfyldt)}.'
            }
        else:
            return {
                'vurdering': 'Begrænsede indikationer, men ikke tilstrækkeligt for §243.',
                'indikation': False,
                'begrundelse': 'Nogle relevante mønstre identificeret, men ikke i tilstrækkelig grad.'
            }
    
    def _vurdere_risikoniveau(
        self,
        tidsbegivenheder: List[Dict[str, Any]],
        juridisk_vurdering: Dict[str, Any]
    ) -> str:
        """
        Evalúa el nivel de riesgo según criterios forenses
        
        Args:
            tidsbegivenheder: Lista de eventos
            juridisk_vurdering: Evaluación legal
            
        Returns:
            Nivel de riesgo: 'Lav risiko', 'Moderat risiko', 'Høj risiko', 'Kritisk risiko'
        """
        if not tidsbegivenheder:
            return 'Lav risiko'
        
        total_events = len(tidsbegivenheder)
        
        # Contar tipos graves
        trusler = sum(1 for e in tidsbegivenheder if 'Trussel' in e.get('typer', []))
        okonomisk = sum(1 for e in tidsbegivenheder if 'Økonomisk pres' in e.get('typer', []))
        isolering = sum(1 for e in tidsbegivenheder if 'Isolering' in e.get('typer', []))
        
        # Criterios para nivel crítico
        if trusler >= 2 or (okonomisk >= 3 and isolering >= 1):
            return 'Kritisk risiko'
        
        # Criterios para alto riesgo
        if juridisk_vurdering.get('indikation', False) and total_events >= 10:
            return 'Høj risiko'
        
        if total_events >= 5 and (trusler >= 1 or okonomisk >= 2):
            return 'Høj risiko'
        
        # Criterios para riesgo moderado
        if total_events >= 3 or juridisk_vurdering.get('indikation', False):
            return 'Moderat risiko'
        
        # Riesgo bajo
        return 'Lav risiko'
    
    def analyser_transkription(
        self,
        resultado_whisper: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analiza una transcripción completa según criterios forenses daneses
        
        Args:
            resultado_whisper: Resultado completo de Whisper
            
        Returns:
            Diccionario con análisis forense completo
        """
        segmentos = resultado_whisper.get('segments', [])
        texto_completo = resultado_whisper.get('text', '')
        idioma = resultado_whisper.get('language', 'desconocido')
        
        # 1. Identificar tidsbegivenheder (eventos temporales)
        tidsbegivenheder = []
        for segmento in segmentos:
            event = self._clasificar_tidsbegivenhed(segmento)
            if event:
                tidsbegivenheder.append(event)
        
        # 2. Juridisk klassifikation
        juridisk_vurdering = self._vurdere_straffelov_243(tidsbegivenheder)
        
        # 3. Risikoniveau
        risikoniveau = self._vurdere_risikoniveau(tidsbegivenheder, juridisk_vurdering)
        
        # 4. Analizar comunicación
        kommunikations_analyse = self._analyser_kommunikation(tidsbegivenheder)
        
        # 5. Evidensoversigt
        evidensoversigt = self._generer_evidensoversigt(tidsbegivenheder)
        
        return {
            'overblik': self._generer_overblik(texto_completo, len(segmentos), len(tidsbegivenheder)),
            'tidsbegivenheder': tidsbegivenheder,
            'juridisk_klassifikation': juridisk_vurdering,
            'kommunikations_analyse': kommunikations_analyse,
            'risikoniveau': risikoniveau,
            'evidensoversigt': evidensoversigt,
            'metadata': {
                'sprog': idioma,
                'antal_segmenter': len(segmentos),
                'antal_relevante_events': len(tidsbegivenheder),
                'analysedato': datetime.now().isoformat()
            }
        }
    
    def _generer_overblik(
        self,
        tekst: str,
        antal_segmenter: int,
        antal_events: int
    ) -> str:
        """Genera resumen técnico neutral"""
        return f"Optagelsen indeholder {antal_segmenter} segmenter med tale. {antal_events} relevante kommunikationsmønstre identificeret til juridisk analyse."
    
    def _analyser_kommunikation(
        self,
        tidsbegivenheder: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analiza patrones de comunicación"""
        typer_count = {}
        for event in tidsbegivenheder:
            for typ in event.get('typer', []):
                typer_count[typ] = typer_count.get(typ, 0) + 1
        
        return {
            'manipulation': typer_count.get('Manipulation', 0),
            'skyldplacering': typer_count.get('Manipulation', 0),  # Incluido en manipulación
            'inkonsekvens': typer_count.get('Gaslighting', 0),
            'emotionelt_pres': typer_count.get('Psykisk pres', 0),
            'kontrol_dominans': typer_count.get('Kontrol', 0),
            'patroniserende_tone': typer_count.get('Nedværdigende', 0),
            'okonomisk_pres': typer_count.get('Økonomisk pres', 0)
        }
    
    def _generer_evidensoversigt(
        self,
        tidsbegivenheder: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Genera resumen de evidencia"""
        pres = []
        manipulation = []
        gaslighting = []
        kontrol = []
        
        for event in tidsbegivenheder:
            tidsstempel = event['tidsstempel']
            tekst = event['tekst']
            
            if 'Psykisk pres' in event.get('typer', []) or 'Økonomisk pres' in event.get('typer', []):
                pres.append(f"[{tidsstempel}] {tekst}")
            
            if 'Manipulation' in event.get('typer', []):
                manipulation.append(f"[{tidsstempel}] {tekst}")
            
            if 'Gaslighting' in event.get('typer', []):
                gaslighting.append(f"[{tidsstempel}] {tekst}")
            
            if 'Kontrol' in event.get('typer', []):
                kontrol.append(f"[{tidsstempel}] {tekst}")
        
        return {
            'pres': pres,
            'manipulation': manipulation,
            'gaslighting': gaslighting,
            'kontrol': kontrol
        }
    
    def generer_forensisk_rapport(
        self,
        analyse: Dict[str, Any],
        filnavn: str
    ) -> str:
        """
        Genera reporte forense completo en danés
        
        Args:
            analyse: Resultado del análisis
            filnavn: Nombre del archivo de audio
            
        Returns:
            Texto del reporte forense
        """
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("FORENSISK ANALYSERAPPORT - LYDOPTAGELSE")
        lines.append("=" * 80)
        lines.append(f"Fil: {filnavn}")
        lines.append(f"Analysedato: {analyse['metadata']['analysedato']}")
        lines.append("")
        
        # 1. OVERBLIK
        lines.append("1. OVERBLIK")
        lines.append("-" * 80)
        lines.append(analyse['overblik'])
        lines.append("")
        
        # 2. TIDSBEGIVENHEDER
        lines.append("2. TIDSBEGIVENHEDER")
        lines.append("-" * 80)
        if analyse['tidsbegivenheder']:
            for event in analyse['tidsbegivenheder']:
                lines.append(f"[{event['tidsstempel']}] {event['beskrivelse']}")
                lines.append(f"   Tekst: {event['tekst']}")
                lines.append("")
        else:
            lines.append("Ingen relevante tidsbegivenheder identificeret.")
            lines.append("")
        
        # 3. JURIDISK KLASSIFIKATION
        lines.append("3. JURIDISK KLASSIFIKATION (Straffeloven §243)")
        lines.append("-" * 80)
        juridisk = analyse['juridisk_klassifikation']
        lines.append(f"Vurdering: {juridisk['vurdering']}")
        if juridisk.get('kriterier_opfyldt'):
            lines.append(f"Kriterier opfyldt: {', '.join(juridisk['kriterier_opfyldt'])}")
        lines.append(f"Begrundelse: {juridisk['begrundelse']}")
        lines.append("")
        
        # 4. ANALYSE AF KOMMUNIKATION
        lines.append("4. ANALYSE AF KOMMUNIKATION")
        lines.append("-" * 80)
        kom = analyse['kommunikations_analyse']
        lines.append(f"Manipulation: {kom['manipulation']} forekomster")
        lines.append(f"Skyldplacering: {kom['skyldplacering']} forekomster")
        lines.append(f"Inkonsekvens i udsagn: {kom['inkonsekvens']} forekomster")
        lines.append(f"Emotionelt pres: {kom['emotionelt_pres']} forekomster")
        lines.append(f"Kontrol eller dominans: {kom['kontrol_dominans']} forekomster")
        lines.append(f"Patroniserende tone: {kom['patroniserende_tone']} forekomster")
        lines.append(f"Økonomisk pres: {kom['okonomisk_pres']} forekomster")
        lines.append("")
        
        # 5. RISIKONIVEAU
        lines.append("5. RISIKONIVEAU (FOR FAMILIERETSHUSET)")
        lines.append("-" * 80)
        lines.append(f"Vurdering: {analyse['risikoniveau']}")
        lines.append("")
        
        # 6. SAMLET EVIDENSOVERSIGT
        lines.append("6. SAMLET EVIDENSOVERSIGT")
        lines.append("-" * 80)
        evidens = analyse['evidensoversigt']
        
        lines.append("Udsagn der kan anses som pres:")
        if evidens['pres']:
            for item in evidens['pres']:
                lines.append(f"  • {item}")
        else:
            lines.append("  Ingen identificeret.")
        lines.append("")
        
        lines.append("Udsagn der kan anses som manipulation:")
        if evidens['manipulation']:
            for item in evidens['manipulation']:
                lines.append(f"  • {item}")
        else:
            lines.append("  Ingen identificeret.")
        lines.append("")
        
        lines.append("Udsagn der kan anses som gaslighting:")
        if evidens['gaslighting']:
            for item in evidens['gaslighting']:
                lines.append(f"  • {item}")
        else:
            lines.append("  Ingen identificeret.")
        lines.append("")
        
        lines.append("Udsagn der kan indikere kontrol:")
        if evidens['kontrol']:
            for item in evidens['kontrol']:
                lines.append(f"  • {item}")
        else:
            lines.append("  Ingen identificeret.")
        lines.append("")
        
        # 7. STRUKTURERET FORENSISK RAPPORT
        lines.append("7. STRUKTURERET FORENSISK RAPPORT")
        lines.append("-" * 80)
        
        lines.append("FAKTA (kun baseret på optagelsen):")
        lines.append(f"  • Antal segmenter: {analyse['metadata']['antal_segmenter']}")
        lines.append(f"  • Antal relevante events: {analyse['metadata']['antal_relevante_events']}")
        lines.append(f"  • Sprog: {analyse['metadata']['sprog']}")
        lines.append("")
        
        lines.append("ANALYSE:")
        lines.append(f"  • Risikoniveau: {analyse['risikoniveau']}")
        lines.append(f"  • Kommunikationsmønstre: {len(analyse['tidsbegivenheder'])} identificeret")
        lines.append("")
        
        lines.append("JURIDISK VURDERING (Straffeloven §243):")
        lines.append(f"  • {juridisk['vurdering']}")
        lines.append("")
        
        lines.append("RISIKOVURDERING:")
        lines.append(f"  • Niveau: {analyse['risikoniveau']}")
        lines.append(f"  • Baseret på: Hyppighed, intensitet, kontrolniveau")
        lines.append("")
        
        lines.append("RELEVANS FOR FAMILIESAGER I DANMARK:")
        lines.append("  • Optagelsen kan være relevant for vurdering af omsorgsforhold")
        lines.append("  • Analyse baseret på objektive kriterier fra Straffeloven §243")
        lines.append("  • Yderligere juridisk vurdering anbefales")
        lines.append("")
        
        lines.append("BILAG: ALLE TIDSSTEMPLEDE HÆNDELSER")
        lines.append("-" * 80)
        for event in analyse['tidsbegivenheder']:
            lines.append(f"[{event['tidsstempel']}] {event['typer']}")
            lines.append(f"  {event['tekst']}")
            lines.append("")
        
        return "\n".join(lines)
    
    def eksporter_rapport(
        self,
        analyse: Dict[str, Any],
        filnavn: str,
        ruta_salida: str
    ):
        """
        Exporta reporte forense a archivo
        
        Args:
            analyse: Resultado del análisis
            filnavn: Nombre del archivo de audio
            ruta_salida: Ruta donde guardar el reporte
        """
        rapport = self.generer_forensisk_rapport(analyse, filnavn)
        
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            f.write(rapport)
        
        self.logger.info(f"Rapport forense eksporteret til: {ruta_salida}")
    
    def eksporter_json(
        self,
        analyse: Dict[str, Any],
        ruta_salida: str
    ):
        """
        Exporta análisis a JSON
        
        Args:
            analyse: Resultado del análisis
            ruta_salida: Ruta donde guardar el JSON
        """
        import json
        
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            json.dump(analyse, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Forensisk analyse eksporteret til JSON: {ruta_salida}")





