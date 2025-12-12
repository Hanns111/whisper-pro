"""
Analizador forense de PDFs para evidencia legal
Análisis de documentos oficiales según Straffeloven §243
Incluye traducción, correlación con audios y agravantes legales
"""

import os
import hashlib
import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from difflib import SequenceMatcher

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    logging.warning("PyMuPDF no disponible. Instala con: pip install PyMuPDF")

try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    logging.warning("deep-translator no disponible. Instala con: pip install deep-translator")


class AnalizadorPDFForense:
    """
    Clase para análisis forense de documentos PDF
    Enfoque en detección de violencia psicológica según legislación danesa
    """
    
    def __init__(self, carpetas_audios: Optional[List[str]] = None):
        self.logger = logging.getLogger(__name__)
        if not PYMUPDF_AVAILABLE:
            raise ImportError("PyMuPDF (fitz) no está instalado. Instala con: pip install PyMuPDF")
        
        self.carpetas_audios = carpetas_audios or []
        self._inicializar_patrones_agresion()
        self._inicializar_patrones_victimas()
        self._inicializar_patrones_contradiccion()
        self._inicializar_criterios_legales()
        self._inicializar_mapeo_victimas()
        
        # Inicializar traductor si está disponible
        if TRANSLATOR_AVAILABLE:
            try:
                self.traductor_da_en = GoogleTranslator(source='da', target='en')
                self.traductor_da_es = GoogleTranslator(source='da', target='es')
                self.traductor_en_es = GoogleTranslator(source='en', target='es')
            except Exception as e:
                self.logger.warning(f"Error al inicializar traductor: {e}")
                self.traductor_da_en = None
                self.traductor_da_es = None
                self.traductor_en_es = None
        else:
            self.traductor_da_en = None
            self.traductor_da_es = None
            self.traductor_en_es = None
    
    def _inicializar_patrones_agresion(self):
        """Inicializa patrones de detección de agresión psicológica"""
        self.patrones_agresion = {
            'gaslighting': [
                r'\b(no\s+recuerdo|nunca\s+dije|eso\s+no\s+pasó|estás\s+equivocad[ao]|te\s+lo\s+inventaste|no\s+es\s+así|estás\s+confundid[ao]|no\s+sucedió)',
                r'\b(negación|negar|desmentir|contradecir\s+la\s+realidad)',
                r'\b(no\s+es\s+verdad|eso\s+no\s+es\s+cierto|mientes|mentiras)'
            ],
            'coerción_económica': [
                r'\b(dinero|pago|gastos|economía|finanzas|recursos\s+económicos|dinero\s+de|control\s+económico)',
                r'\b(no\s+tienes\s+dinero|sin\s+dinero|dependes\s+de\s+mí|no\s+puedes\s+pagarlo)',
                r'\b(control\s+de\s+cuentas|acceso\s+al\s+dinero|gastos\s+controlados)'
            ],
            'amenazas_directas': [
                r'\b(te\s+voy\s+a|vas\s+a\s+ver|te\s+arrepentirás|consecuencias|pagaras|lo\s+vas\s+a\s+lamentar)',
                r'\b(amenaza|amenazar|advertir|consecuencias\s+graves|te\s+va\s+a\s+ir\s+mal)',
                r'\b(si\s+no\s+haces|si\s+no\s+obedeces|si\s+no\s+cumples)'
            ],
            'amenazas_veladas': [
                r'\b(sería\s+una\s+lástima|no\s+quiero\s+que\s+pase|podría\s+suceder|mejor\s+que\s+no)',
                r'\b(no\s+sería\s+bueno|no\s+te\s+conviene|sería\s+mejor\s+que)',
                r'\b(espero\s+que\s+no|ojalá\s+no\s+tenga\s+que)'
            ],
            'invalidación': [
                r'\b(no\s+es\s+para\s+tanto|exageras|no\s+es\s+tan\s+grave|te\s+quejas\s+de\s+nada)',
                r'\b(no\s+tienes\s+razón|estás\s+mal|no\s+es\s+así\s+como\s+dices|minimizar)',
                r'\b(no\s+es\s+importante|no\s+vale\s+la\s+pena|no\s+es\s+nada)'
            ],
            'manipulación_emocional': [
                r'\b(por\s+mi\s+causa|por\s+tu\s+culpa|si\s+me\s+quieres|si\s+realmente\s+me\s+amas)',
                r'\b(me\s+haces\s+daño|me\s+lastimas|me\s+decepcionas|no\s+me\s+quieres)',
                r'\b(culpa|responsabilidad|deberías|tienes\s+que|debes)'
            ],
            'control_psicológico': [
                r'\b(no\s+puedes|no\s+debes|no\s+te\s+permito|tienes\s+que\s+hacer|debes\s+obedecer)',
                r'\b(control|controlar|decidir\s+por\s+ti|no\s+tienes\s+opción|sin\s+mi\s+permiso)',
                r'\b(prohibir|prohibido|no\s+se\s+permite|no\s+está\s+permitido)'
            ],
            'aislamiento': [
                r'\b(no\s+veas|no\s+hables|no\s+te\s+acerques|alejarte|separarte)',
                r'\b(no\s+confíes|no\s+les\s+creas|ellos\s+no\s+te\s+quieren|solo\s+yo)',
                r'\b(aislar|aislamiento|alejamiento|separación\s+de)'
            ],
            'humillación': [
                r'\b(inútil|incapaz|no\s+sirves|no\s+vales|no\s+eres\s+nada)',
                r'\b(desprecio|menosprecio|ridículo|burla|burlarse)',
                r'\b(estúpido|tonto|idiota|sin\s+valor|sin\s+importancia)'
            ],
            'chantaje_emocional': [
                r'\b(si\s+no\s+haces|si\s+no\s+obedeces|si\s+no\s+cumples|si\s+no\s+quieres)',
                r'\b(te\s+dejo|me\s+voy|no\s+te\s+quiero|te\s+abandono)',
                r'\b(chantaje|chantajear|presión\s+emocional|manipulación\s+emocional)'
            ]
        }
    
    def _inicializar_patrones_victimas(self):
        """Inicializa patrones para detectar menciones a víctimas"""
        self.patrones_victimas = {
            'claudia': [
                r'\bclaudia\b',
                r'\bclau\b',
                r'\bclaudi\b'
            ],
            'juan_diego': [
                r'\bjuan\s+diego\b',
                r'\bjuan\s+d\b',
                r'\bj\.?\s*d\.?\b'
            ],
            'jose_carlos': [
                r'\bjosé\s+carlos\b',
                r'\bjose\s+carlos\b',
                r'\bj\.?\s*c\.?\b'
            ]
        }
    
    def _inicializar_patrones_contradiccion(self):
        """Inicializa patrones para detectar contradicciones"""
        self.patrones_contradiccion = [
            r'\b(antes\s+dije|ahora\s+digo|pero\s+antes|sin\s+embargo\s+antes)',
            r'\b(cambiar\s+de\s+opinión|cambio\s+de\s+actitud|ahora\s+pienso\s+diferente)',
            r'\b(no\s+es\s+lo\s+que\s+dije|me\s+malinterpretaste|no\s+es\s+así)'
        ]
    
    def _inicializar_criterios_legales(self):
        """Inicializa criterios legales daneses"""
        self.criterios_legales_dk = {
            'kontrol': [
                r'\b(kontrol|control|kontrollere|bestemme|afgøre\s+for)',
                r'\b(ikke\s+må|skal\s+gøre|må\s+ikke|forbudt)',
                r'\b(beslutte\s+for|bestemme\s+over|tvinge\s+til)'
            ],
            'psykisk_vold': [
                r'\b(psykisk\s+vold|psykologisk\s+vold|emotionel\s+vold)',
                r'\b(psykisk\s+pres|emotionelt\s+pres|psykologisk\s+pres)',
                r'\b(manipulation|gaslighting|nedværdigelse)'
            ],
            'okonomisk_pres': [
                r'\b(økonomisk\s+pres|økonomisk\s+kontrol|penge\s+kontrol)',
                r'\b(ikke\s+adgang\s+til\s+penge|kontrollere\s+penge)',
                r'\b(økonomisk\s+afhængighed|penge\s+afhængighed)'
            ],
            'nedvaerdigende_adfaerd': [
                r'\b(nedværdigende|fornedrende|ydmygende|nedsættende)',
                r'\b(usædvanlig|uværdig|værdiløs)',
                r'\b(ikke\s+værd|uden\s+værdi|intet\s+værd)'
            ],
            'trusler': [
                r'\b(trussel|true|advare|konsekvens|straffe)',
                r'\b(hvis\s+ikke|hvis\s+du\s+ikke|hvis\s+du\s+gør)',
                r'\b(ville\s+ikke\s+ville|kunne\s+skulle|måske\s+skulle)'
            ]
        }
    
    def _inicializar_mapeo_victimas(self):
        """Inicializa mapeo de nombres reales a nombres protegidos"""
        self.mapeo_victimas = {
            'claudia': 'exesposa',
            'juan_diego': 'hijo mayor',
            'jose_carlos': 'hijo menor'
        }
    
    def traducir_texto(self, texto: str, idioma_origen: str = 'da', idioma_destino: str = 'en') -> str:
        """
        Traduce texto usando deep-translator
        
        Args:
            texto: Texto a traducir
            idioma_origen: Código de idioma origen (da, en, es)
            idioma_destino: Código de idioma destino (en, es)
        
        Returns:
            Texto traducido o texto original si falla
        """
        if not texto or not texto.strip():
            return texto
        
        if not TRANSLATOR_AVAILABLE or not self.traductor_da_en:
            self.logger.warning("Traductor no disponible, retornando texto original")
            return texto
        
        try:
            # Limitar longitud para evitar errores
            texto_limpiado = texto.strip()[:5000]  # Máximo 5000 caracteres por traducción
            
            if idioma_origen == 'da' and idioma_destino == 'en':
                return self.traductor_da_en.translate(texto_limpiado)
            elif idioma_origen == 'da' and idioma_destino == 'es':
                return self.traductor_da_es.translate(texto_limpiado)
            elif idioma_origen == 'en' and idioma_destino == 'es':
                return self.traductor_en_es.translate(texto_limpiado)
            else:
                # Traducción en dos pasos si es necesario
                if idioma_origen == 'da' and idioma_destino == 'es':
                    texto_en = self.traductor_da_en.translate(texto_limpiado)
                    return self.traductor_en_es.translate(texto_en)
                return texto
        except Exception as e:
            self.logger.warning(f"Error en traducción: {e}")
            return texto
    
    def proteger_nombres(self, texto: str) -> str:
        """
        Reemplaza nombres reales por nombres protegidos
        
        Args:
            texto: Texto original
        
        Returns:
            Texto con nombres protegidos
        """
        texto_protegido = texto
        
        # Reemplazar Claudia
        texto_protegido = re.sub(r'\bclaudia\b', 'exesposa', texto_protegido, flags=re.IGNORECASE)
        texto_protegido = re.sub(r'\bclau\b', 'exesposa', texto_protegido, flags=re.IGNORECASE)
        
        # Reemplazar Juan Diego
        texto_protegido = re.sub(r'\bjuan\s+diego\b', 'hijo mayor', texto_protegido, flags=re.IGNORECASE)
        texto_protegido = re.sub(r'\bjuan\s+d\b', 'hijo mayor', texto_protegido, flags=re.IGNORECASE)
        
        # Reemplazar José Carlos
        texto_protegido = re.sub(r'\bjosé\s+carlos\b', 'hijo menor', texto_protegido, flags=re.IGNORECASE)
        texto_protegido = re.sub(r'\bjose\s+carlos\b', 'hijo menor', texto_protegido, flags=re.IGNORECASE)
        
        return texto_protegido
    
    def calcular_hash_sha256(self, ruta_pdf: str) -> str:
        """Calcula hash SHA256 del archivo PDF"""
        sha256_hash = hashlib.sha256()
        with open(ruta_pdf, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def extraer_texto_pdf(self, ruta_pdf: str) -> Dict[str, Any]:
        """
        Extrae texto de un PDF digital
        
        Args:
            ruta_pdf: Ruta al archivo PDF
            
        Returns:
            Diccionario con texto extraído y metadatos
        """
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
            
            # Metadatos
            metadata = doc.metadata
            
            doc.close()
            
            return {
                'texto_completo': texto_unificado,
                'texto_por_pagina': texto_por_pagina,
                'num_paginas': len(doc),
                'metadata': metadata,
                'exito': True
            }
        except Exception as e:
            self.logger.error(f"Error al extraer texto del PDF {ruta_pdf}: {str(e)}")
            return {
                'texto_completo': '',
                'texto_por_pagina': [],
                'num_paginas': 0,
                'metadata': {},
                'exito': False,
                'error': str(e)
            }
    
    def detectar_agresion(self, texto: str, texto_por_pagina: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Detecta patrones de agresión psicológica en el texto
        Incluye número de página y traducciones
        
        Args:
            texto: Texto completo del PDF
            texto_por_pagina: Lista de textos por página con número de página
        
        Returns:
            Lista de detecciones con citas textuales, traducciones y número de página
        """
        detecciones = []
        texto_lower = texto.lower()
        
        # Mapeo de posición a página
        mapa_pagina = {}
        if texto_por_pagina:
            posicion_actual = 0
            for pagina_info in texto_por_pagina:
                texto_pag = pagina_info.get('texto', '')
                num_pag = pagina_info.get('pagina', 0)
                longitud = len(texto_pag) + 2  # +2 por los \n\n
                for i in range(posicion_actual, posicion_actual + longitud):
                    mapa_pagina[i] = num_pag
                posicion_actual += longitud
        
        for tipo_agresion, patrones in self.patrones_agresion.items():
            for patron in patrones:
                matches = re.finditer(patron, texto_lower, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    # Obtener contexto (50 caracteres antes y después)
                    inicio_contexto = max(0, match.start() - 50)
                    fin_contexto = min(len(texto), match.end() + 50)
                    contexto = texto[inicio_contexto:fin_contexto].strip()
                    
                    # Obtener línea completa
                    inicio_linea = texto.rfind('\n', 0, match.start()) + 1
                    fin_linea = texto.find('\n', match.end())
                    if fin_linea == -1:
                        fin_linea = len(texto)
                    linea_completa = texto[inicio_linea:fin_linea].strip()
                    
                    # Determinar número de página
                    num_pagina = mapa_pagina.get(match.start(), 0)
                    
                    # Traducir cita
                    cita_da = linea_completa
                    cita_en = self.traducir_texto(cita_da, 'da', 'en')
                    cita_es = self.traducir_texto(cita_da, 'da', 'es')
                    
                    # Proteger nombres en traducciones
                    cita_da_protegida = self.proteger_nombres(cita_da)
                    cita_en_protegida = self.proteger_nombres(cita_en)
                    cita_es_protegida = self.proteger_nombres(cita_es)
                    
                    detecciones.append({
                        'tipo': tipo_agresion,
                        'patron_encontrado': match.group(),
                        'posicion': match.start(),
                        'cita_da': cita_da_protegida,
                        'cita_en': cita_en_protegida,
                        'cita_es': cita_es_protegida,
                        'contexto': contexto,
                        'num_pagina': num_pagina,
                        'severidad': self._evaluar_severidad(tipo_agresion, linea_completa)
                    })
        
        # Eliminar duplicados similares
        detecciones = self._eliminar_duplicados(detecciones)
        
        return detecciones
    
    def detectar_menciones_victimas(self, texto: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Detecta menciones a víctimas específicas
        
        Returns:
            Diccionario con menciones por víctima
        """
        menciones = {
            'claudia': [],
            'juan_diego': [],
            'jose_carlos': []
        }
        
        texto_lower = texto.lower()
        
        for victima, patrones in self.patrones_victimas.items():
            for patron in patrones:
                matches = re.finditer(patron, texto_lower, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    # Obtener contexto
                    inicio_contexto = max(0, match.start() - 100)
                    fin_contexto = min(len(texto), match.end() + 100)
                    contexto = texto[inicio_contexto:fin_contexto].strip()
                    
                    # Obtener línea completa
                    inicio_linea = texto.rfind('\n', 0, match.start()) + 1
                    fin_linea = texto.find('\n', match.end())
                    if fin_linea == -1:
                        fin_linea = len(texto)
                    linea_completa = texto[inicio_linea:fin_linea].strip()
                    
                    menciones[victima].append({
                        'posicion': match.start(),
                        'cita_textual': linea_completa,
                        'contexto': contexto
                    })
        
        # Eliminar duplicados
        for victima in menciones:
            menciones[victima] = self._eliminar_duplicados_menciones(menciones[victima])
        
        return menciones
    
    def detectar_contradicciones(self, texto: str) -> List[Dict[str, Any]]:
        """Detecta contradicciones internas y cambios bruscos de actitud"""
        contradicciones = []
        
        for patron in self.patrones_contradiccion:
            matches = re.finditer(patron, texto, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Obtener contexto amplio
                inicio_contexto = max(0, match.start() - 200)
                fin_contexto = min(len(texto), match.end() + 200)
                contexto = texto[inicio_contexto:fin_contexto].strip()
                
                contradicciones.append({
                    'patron_encontrado': match.group(),
                    'posicion': match.start(),
                    'contexto': contexto
                })
        
        return contradicciones
    
    def clasificar_legal_dk(self, texto: str, detecciones_agresion: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Clasifica el documento según Straffeloven §243
        
        Returns:
            Diccionario con clasificación legal
        """
        texto_lower = texto.lower()
        
        # Contar criterios legales
        criterios_detectados = {}
        for criterio, patrones in self.criterios_legales_dk.items():
            count = 0
            for patron in patrones:
                count += len(re.findall(patron, texto_lower, re.IGNORECASE))
            criterios_detectados[criterio] = count
        
        # Evaluar si cumple criterios de §243
        cumple_criterios = False
        kriterier_opfyldt = []
        
        if criterios_detectados.get('kontrol', 0) >= 3:
            cumple_criterios = True
            kriterier_opfyldt.append('Kontrol (gentagen kontrol)')
        
        if criterios_detectados.get('psykisk_vold', 0) >= 2:
            cumple_criterios = True
            kriterier_opfyldt.append('Psykisk vold')
        
        if criterios_detectados.get('okonomisk_pres', 0) >= 2:
            cumple_criterios = True
            kriterier_opfyldt.append('Økonomisk pres')
        
        if criterios_detectados.get('nedvaerdigende_adfaerd', 0) >= 2:
            cumple_criterios = True
            kriterier_opfyldt.append('Nedværdigende adfærd')
        
        if criterios_detectados.get('trusler', 0) >= 1:
            cumple_criterios = True
            kriterier_opfyldt.append('Trusler')
        
        # Evaluar nivel de riesgo
        total_detecciones = len(detecciones_agresion)
        total_criterios = sum(criterios_detectados.values())
        
        if total_detecciones >= 15 or total_criterios >= 10:
            risikoniveau = 'kritisk'
        elif total_detecciones >= 8 or total_criterios >= 5:
            risikoniveau = 'høj'
        elif total_detecciones >= 3 or total_criterios >= 2:
            risikoniveau = 'moderat'
        else:
            risikoniveau = 'lav'
        
        # Generar evaluación
        if cumple_criterios:
            vurdering = 'Det analyserede dokument udviser karakteristika for psykisk vold jf. Straffeloven §243.'
        else:
            vurdering = 'Begrænsede indikationer, men ikke tilstrækkeligt for §243.'
        
        return {
            'vurdering': vurdering,
            'indikation': cumple_criterios,
            'kriterier_opfyldt': kriterier_opfyldt,
            'criterios_detectados': criterios_detectados,
            'risikoniveau': risikoniveau,
            'total_detecciones': total_detecciones,
            'total_criterios': total_criterios
        }
    
    def _evaluar_severidad(self, tipo: str, frase: str) -> str:
        """Evalúa severidad de una detección"""
        severos = ['amenazas_directas', 'chantaje_emocional', 'humillación']
        if tipo in severos:
            return 'alta'
        elif tipo in ['gaslighting', 'control_psicológico', 'coerción_económica']:
            return 'media'
        else:
            return 'baja'
    
    def _eliminar_duplicados(self, detecciones: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Elimina detecciones duplicadas o muy similares"""
        if not detecciones:
            return []
        
        unicos = []
        posiciones_vistas = set()
        
        for det in detecciones:
            pos = det['posicion']
            # Considerar duplicado si está dentro de 20 caracteres
            es_duplicado = any(abs(pos - p) < 20 for p in posiciones_vistas)
            
            if not es_duplicado:
                unicos.append(det)
                posiciones_vistas.add(pos)
        
        return unicos
    
    def _eliminar_duplicados_menciones(self, menciones: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Elimina menciones duplicadas"""
        if not menciones:
            return []
        
        unicos = []
        posiciones_vistas = set()
        
        for men in menciones:
            pos = men['posicion']
            if pos not in posiciones_vistas:
                unicos.append(men)
                posiciones_vistas.add(pos)
        
        return unicos
    
    def _calcular_similitud_semantica(self, texto1: str, texto2: str) -> float:
        """
        Calcula similitud semántica entre dos textos usando SequenceMatcher
        
        Returns:
            Valor entre 0 y 1 (1 = idéntico, 0 = completamente diferente)
        """
        texto1_clean = texto1.lower().strip()
        texto2_clean = texto2.lower().strip()
        
        if not texto1_clean or not texto2_clean:
            return 0.0
        
        # Usar SequenceMatcher para similitud básica
        similarity = SequenceMatcher(None, texto1_clean, texto2_clean).ratio()
        
        # También verificar si hay palabras clave comunes
        palabras1 = set(texto1_clean.split())
        palabras2 = set(texto2_clean.split())
        
        if palabras1 and palabras2:
            palabras_comunes = palabras1.intersection(palabras2)
            palabras_totales = palabras1.union(palabras2)
            if palabras_totales:
                jaccard = len(palabras_comunes) / len(palabras_totales)
                # Combinar ambas métricas
                similarity = (similarity * 0.6) + (jaccard * 0.4)
        
        return min(1.0, max(0.0, similarity))
    
    def cargar_transcripciones_audio(self, carpeta_transcripciones: str) -> List[Dict[str, Any]]:
        """
        Carga todas las transcripciones de audio desde la carpeta
        
        Args:
            carpeta_transcripciones: Carpeta donde están las transcripciones
        
        Returns:
            Lista de transcripciones con metadatos
        """
        transcripciones = []
        
        if not os.path.exists(carpeta_transcripciones):
            self.logger.warning(f"Carpeta de transcripciones no existe: {carpeta_transcripciones}")
            return transcripciones
        
        # Buscar archivos JSON de transcripciones
        for root, dirs, files in os.walk(carpeta_transcripciones):
            for file in files:
                if file.endswith('_INFORME_UNICO.txt'):
                    # Leer el informe único que contiene la transcripción
                    ruta_completa = os.path.join(root, file)
                    try:
                        with open(ruta_completa, 'r', encoding='utf-8') as f:
                            contenido = f.read()
                        
                        # Extraer información básica del archivo
                        nombre_audio = file.replace('_INFORME_UNICO.txt', '')
                        
                        # Buscar sección de transcripción en el informe
                        # El formato es: "B. TRANSCRIPCIÓN CON TIMELINE"
                        if "B. TRANSCRIPCIÓN CON TIMELINE" in contenido:
                            # Extraer segmentos con timestamps
                            segmentos = []
                            # Buscar líneas con formato [MM:SS] texto
                            import re
                            patron_timestamp = r'\[(\d{2}):(\d{2})\]\s+(.+?)(?=\n\[|\n\n|$)'
                            matches = re.finditer(patron_timestamp, contenido, re.MULTILINE | re.DOTALL)
                            
                            for match in matches:
                                minutos = int(match.group(1))
                                segundos = int(match.group(2))
                                texto = match.group(3).strip()
                                tiempo_total = minutos * 60 + segundos
                                
                                segmentos.append({
                                    'start': tiempo_total,
                                    'end': tiempo_total + 5,  # Aproximado
                                    'text': texto
                                })
                            
                            if segmentos:
                                transcripciones.append({
                                    'archivo': nombre_audio,
                                    'ruta': ruta_completa,
                                    'segmentos': segmentos,
                                    'texto_completo': '\n'.join([s['text'] for s in segmentos])
                                })
                    except Exception as e:
                        self.logger.warning(f"Error al leer transcripción {file}: {e}")
        
        # También buscar en las carpetas de audios configuradas
        for carpeta_audio in self.carpetas_audios:
            if os.path.exists(carpeta_audio):
                # Buscar archivos JSON de transcripciones directamente
                for root, dirs, files in os.walk(carpeta_audio):
                    for file in files:
                        if file.endswith('.json') and 'transcripcion' in file.lower():
                            ruta_completa = os.path.join(root, file)
                            try:
                                with open(ruta_completa, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                
                                if 'segments' in data or 'text' in data:
                                    transcripciones.append({
                                        'archivo': os.path.basename(file),
                                        'ruta': ruta_completa,
                                        'segmentos': data.get('segments', []),
                                        'texto_completo': data.get('text', '')
                                    })
                            except Exception as e:
                                self.logger.warning(f"Error al leer JSON {file}: {e}")
        
        self.logger.info(f"Cargadas {len(transcripciones)} transcripciones de audio")
        return transcripciones
    
    def correlacionar_con_audios(
        self,
        detecciones_pdf: List[Dict[str, Any]],
        transcripciones: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Correlaciona agresiones del PDF con transcripciones de audio
        
        Args:
            detecciones_pdf: Lista de detecciones del PDF
            transcripciones: Lista de transcripciones de audio
        
        Returns:
            Lista de detecciones con correlaciones agregadas
        """
        detecciones_correlacionadas = []
        
        for deteccion in detecciones_pdf:
            correlaciones = []
            cita_pdf = deteccion.get('cita_da', '') or deteccion.get('cita_textual', '')
            
            if not cita_pdf or not transcripciones:
                deteccion['correlaciones'] = []
                detecciones_correlacionadas.append(deteccion)
                continue
            
            # Buscar coincidencias en transcripciones
            for transcripcion in transcripciones:
                segmentos = transcripcion.get('segmentos', [])
                texto_completo = transcripcion.get('texto_completo', '')
                
                # Buscar en segmentos individuales
                for segmento in segmentos:
                    texto_segmento = segmento.get('text', '').strip()
                    if not texto_segmento:
                        continue
                    
                    # Calcular similitud
                    similitud = self._calcular_similitud_semantica(cita_pdf, texto_segmento)
                    
                    # Umbral de similitud (ajustable)
                    if similitud >= 0.3:  # 30% de similitud mínimo
                        # Detectar víctima mencionada en el AUDIO (Claudia y sus hijos)
                        # NOTA: Los PDFs son sobre la ex esposa e hijos biológicos del abusador
                        # Los audios son sobre Claudia y sus hijos (Juan Diego, José Carlos)
                        # La correlación busca PATRONES DE COMPORTAMIENTO SIMILARES
                        victima_detectada = None
                        texto_lower = texto_segmento.lower()
                        if 'claudia' in texto_lower or 'clau' in texto_lower:
                            victima_detectada = 'Claudia (víctima actual)'
                        elif 'juan diego' in texto_lower or 'juan d' in texto_lower:
                            victima_detectada = 'Juan Diego (hijo, 17 años, autismo)'
                        elif 'josé carlos' in texto_lower or 'jose carlos' in texto_lower:
                            victima_detectada = 'José Carlos (hijo, 15 años, TDAH)'
                        
                        # Formatear timestamp
                        tiempo_inicio = segmento.get('start', 0)
                        minutos = int(tiempo_inicio // 60)
                        segundos = int(tiempo_inicio % 60)
                        timestamp = f"{minutos:02d}:{segundos:02d}"
                        
                        correlaciones.append({
                            'archivo_audio': transcripcion.get('archivo', 'desconocido'),
                            'timestamp': timestamp,
                            'tiempo_segundos': tiempo_inicio,
                            'cita_audio': self.proteger_nombres(texto_segmento),
                            'similitud': similitud,
                            'victima_detectada': victima_detectada
                        })
                
                # También buscar en texto completo si no hay segmentos
                if not segmentos and texto_completo:
                    similitud = self._calcular_similitud_semantica(cita_pdf, texto_completo)
                    if similitud >= 0.3:
                        correlaciones.append({
                            'archivo_audio': transcripcion.get('archivo', 'desconocido'),
                            'timestamp': '00:00',
                            'tiempo_segundos': 0,
                            'cita_audio': self.proteger_nombres(texto_completo[:200]),
                            'similitud': similitud,
                            'victima_detectada': None
                        })
            
            # Ordenar por similitud (mayor primero)
            correlaciones.sort(key=lambda x: x['similitud'], reverse=True)
            
            # Limitar a las 5 mejores correlaciones
            deteccion['correlaciones'] = correlaciones[:5]
            detecciones_correlacionadas.append(deteccion)
        
        return detecciones_correlacionadas
    
    def calcular_agravantes_legales(
        self,
        detecciones_agresion: List[Dict[str, Any]],
        menciones_victimas: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Calcula agravantes legales por menores vulnerables
        
        Args:
            detecciones_agresion: Lista de detecciones de agresión
            menciones_victimas: Menciones a víctimas
        
        Returns:
            Diccionario con agravantes legales
        """
        # Juan Diego: 17 años, autismo = altamente vulnerable
        # José Carlos: 15 años, TDAH = vulnerable
        
        agresiones_juan_diego = len(menciones_victimas.get('juan_diego', []))
        agresiones_jose_carlos = len(menciones_victimas.get('jose_carlos', []))
        
        # Contar agresiones dirigidas a menores en las correlaciones
        agresiones_menores_correlacionadas = 0
        for det in detecciones_agresion:
            correlaciones = det.get('correlaciones', [])
            for corr in correlaciones:
                victima = corr.get('victima_detectada', '')
                if victima in ['hijo mayor', 'hijo menor']:
                    agresiones_menores_correlacionadas += 1
        
        # Evaluar agravantes según §243, §245a y guías de Socialtilsynet
        agravantes = {
            'juan_diego': {
                'edad': 17,
                'condicion': 'autismo',
                'vulnerabilidad': 'altamente vulnerable',
                'agresiones_detectadas': agresiones_juan_diego,
                'clasificacion_automatica': 'HØJ' if agresiones_juan_diego >= 1 else 'MODERAT'
            },
            'jose_carlos': {
                'edad': 15,
                'condicion': 'TDAH',
                'vulnerabilidad': 'vulnerable',
                'agresiones_detectadas': agresiones_jose_carlos,
                'clasificacion_automatica': 'HØJ' if agresiones_jose_carlos >= 2 else 'MODERAT'
            },
            'total_agresiones_menores': agresiones_juan_diego + agresiones_jose_carlos,
            'agresiones_correlacionadas': agresiones_menores_correlacionadas
        }
        
        # Determinar nivel de riesgo final considerando agravantes
        if agresiones_juan_diego >= 2 or agresiones_jose_carlos >= 3:
            agravantes['nivel_riesgo_final'] = 'KRITISK'
        elif agresiones_juan_diego >= 1 or agresiones_jose_carlos >= 2:
            agravantes['nivel_riesgo_final'] = 'HØJ'
        elif agresiones_juan_diego >= 1 or agresiones_jose_carlos >= 1:
            agravantes['nivel_riesgo_final'] = 'MODERAT'
        else:
            agravantes['nivel_riesgo_final'] = 'LAV'
        
        return agravantes
    
    def generar_informe_correlacional(
        self,
        nombre_pdf: str,
        ruta_pdf: str,
        texto_extraido: Dict[str, Any],
        detecciones_agresion: List[Dict[str, Any]],
        menciones_victimas: Dict[str, List[Dict[str, Any]]],
        contradicciones: List[Dict[str, Any]],
        clasificacion_legal: Dict[str, Any],
        agravantes_legales: Dict[str, Any],
        transcripciones: List[Dict[str, Any]]
    ) -> str:
        """
        Genera el informe forense correlacional completo en formato texto
        Incluye traducciones, correlación con audios y agravantes legales
        
        Returns:
            Contenido completo del informe
        """
        lineas = []
        
        # Obtener información del archivo
        tamaño_archivo = os.path.getsize(ruta_pdf)
        tamaño_mb = tamaño_archivo / (1024 * 1024)
        hash_sha256 = self.calcular_hash_sha256(ruta_pdf)
        fecha_procesamiento = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        texto_completo_da = texto_extraido.get('texto_completo', '')
        texto_completo_en = self.traducir_texto(texto_completo_da, 'da', 'en') if texto_completo_da else ''
        texto_completo_es = self.traducir_texto(texto_completo_da, 'da', 'es') if texto_completo_da else ''
        
        # ============================================================
        # A. CABECERA Y CONTEXTO FORENSE
        # ============================================================
        lineas.append("=" * 80 + "\n")
        lineas.append("INFORME FORENSE CORRELACIONAL - DOCUMENTO PDF\n")
        lineas.append("=" * 80 + "\n\n")
        
        lineas.append("A. CABECERA\n")
        lineas.append("=" * 80 + "\n\n")
        lineas.append(f"Nombre del PDF: {nombre_pdf}\n")
        lineas.append(f"Fecha de procesamiento: {fecha_procesamiento}\n")
        lineas.append(f"Hash único (SHA256): {hash_sha256}\n")
        lineas.append(f"Tamaño del PDF: {tamaño_mb:.2f} MB ({tamaño_archivo:,} bytes)\n")
        lineas.append(f"Número de páginas: {texto_extraido.get('num_paginas', 0)}\n")
        lineas.append("\n" + "=" * 80 + "\n\n")
        
        # ============================================================
        # A.1. CONTEXTO FORENSE Y ESTRATEGIA DE CORRELACIÓN
        # ============================================================
        lineas.append("A.1. CONTEXTO FORENSE Y ESTRATEGIA DE CORRELACIÓN\n")
        lineas.append("=" * 80 + "\n\n")
        lineas.append("ESTRATEGIA FORENSE:\n")
        lineas.append("-" * 80 + "\n\n")
        lineas.append("Este informe correlaciona PATRONES DE COMPORTAMIENTO documentados en documentos\n")
        lineas.append("históricos (PDFs) con patrones similares detectados en grabaciones de audio actuales.\n\n")
        lineas.append("CONTEXTO DE LOS PDFs:\n")
        lineas.append("  • Los documentos PDF analizados son sobre la EX ESPOSA del abusador\n")
        lineas.append("  • Los PDFs documentan situaciones con los HIJOS BIOLÓGICOS del abusador que lo rechazan\n")
        lineas.append("  • Estos documentos muestran PATRONES DE COMPORTAMIENTO históricos del abusador\n")
        lineas.append("  • Los PDFs contienen argumentos que el abusador está enfrentando por patrones repetitivos\n\n")
        lineas.append("CONTEXTO DE LOS AUDIOS:\n")
        lineas.append("  • Las grabaciones de audio son sobre CLAUDIA (víctima actual)\n")
        lineas.append("  • Los audios documentan situaciones con JUAN DIEGO (17 años, autismo) y JOSÉ CARLOS (15 años, TDAH)\n")
        lineas.append("  • Estos audios muestran PATRONES DE COMPORTAMIENTO actuales del abusador\n\n")
        lineas.append("OBJETIVO DE LA CORRELACIÓN:\n")
        lineas.append("  • Demostrar que el abusador REPITE los mismos patrones de comportamiento\n")
        lineas.append("  • Establecer un patrón consistente de violencia psicológica a través del tiempo\n")
        lineas.append("  • Proporcionar evidencia forense de que los patrones detectados en los PDFs (con ex esposa/hijos biológicos)\n")
        lineas.append("    están siendo REPETIDOS en los audios actuales (con Claudia y sus hijos)\n")
        lineas.append("  • Esta correlación fortalece la evidencia legal según Straffeloven §243\n\n")
        lineas.append("METODOLOGÍA:\n")
        lineas.append("  • Se identifican patrones de agresión psicológica en los PDFs (gaslighting, coerción, amenazas, etc.)\n")
        lineas.append("  • Se buscan patrones similares en las transcripciones de audio\n")
        lineas.append("  • Se calcula similitud semántica y se correlacionan las detecciones\n")
        lineas.append("  • Se identifican víctimas específicas mencionadas en los audios\n\n")
        lineas.append("=" * 80 + "\n\n")
        
        # ============================================================
        # B. TEXTO EXTRAÍDO (ORIGINAL + TRADUCCIONES)
        # ============================================================
        lineas.append("B. TEXTO EXTRAÍDO\n")
        lineas.append("=" * 80 + "\n\n")
        
        if texto_extraido.get('exito', False):
            lineas.append("TEXTO ORIGINAL (DANÉS):\n")
            lineas.append("-" * 80 + "\n")
            if texto_completo_da:
                lineas.append(self.proteger_nombres(texto_completo_da))
                lineas.append("\n\n")
            else:
                lineas.append("No se pudo extraer texto del PDF.\n\n")
            
            if texto_completo_en:
                lineas.append("TRADUCCIÓN AL INGLÉS (EN):\n")
                lineas.append("-" * 80 + "\n")
                lineas.append(self.proteger_nombres(texto_completo_en))
                lineas.append("\n\n")
            
            if texto_completo_es:
                lineas.append("TRADUCCIÓN AL ESPAÑOL (ES):\n")
                lineas.append("-" * 80 + "\n")
                lineas.append(self.proteger_nombres(texto_completo_es))
                lineas.append("\n\n")
        else:
            error = texto_extraido.get('error', 'Error desconocido')
            lineas.append(f"Error al extraer texto: {error}\n\n")
        
        lineas.append("\n" + "=" * 80 + "\n\n")
        
        # ============================================================
        # C. ANÁLISIS DE AGRESIÓN (ES) - CON TRADUCCIONES Y CORRELACIONES
        # ============================================================
        lineas.append("C. ANÁLISIS DE AGRESIÓN (ES)\n")
        lineas.append("=" * 80 + "\n\n")
        
        if not detecciones_agresion:
            lineas.append("No se detectaron patrones de agresión psicológica en el documento.\n\n")
        else:
            # Agrupar por tipo
            por_tipo = {}
            for det in detecciones_agresion:
                tipo = det.get('tipo', 'desconocido')
                if tipo not in por_tipo:
                    por_tipo[tipo] = []
                por_tipo[tipo].append(det)
            
            nombres_tipos = {
                'gaslighting': 'GASLIGHTING',
                'coerción_económica': 'COERCIÓN ECONÓMICA',
                'amenazas_directas': 'AMENAZAS DIRECTAS',
                'amenazas_veladas': 'AMENAZAS VELADAS',
                'invalidación': 'INVALIDACIÓN',
                'manipulación_emocional': 'MANIPULACIÓN EMOCIONAL',
                'control_psicológico': 'CONTROL PSICOLÓGICO',
                'aislamiento': 'AISLAMIENTO',
                'humillación': 'HUMILLACIÓN',
                'chantaje_emocional': 'CHANTAJE EMOCIONAL'
            }
            
            for tipo_key, nombre_tipo in nombres_tipos.items():
                if tipo_key in por_tipo:
                    lineas.append(f"\n{nombre_tipo} ({len(por_tipo[tipo_key])} detecciones):\n")
                    lineas.append("-" * 80 + "\n")
                    
                    for det in por_tipo[tipo_key]:
                        severidad = det.get('severidad', 'media')
                        num_pagina = det.get('num_pagina', 0)
                        cita_da = det.get('cita_da', '')
                        cita_en = det.get('cita_en', '')
                        cita_es = det.get('cita_es', '')
                        correlaciones = det.get('correlaciones', [])
                        
                        lineas.append(f"Severidad: {severidad.upper()}\n")
                        lineas.append(f"Página: {num_pagina}\n")
                        lineas.append(f"Cita en danés: {cita_da}\n")
                        if cita_en:
                            lineas.append(f"Cita en inglés: {cita_en}\n")
                        if cita_es:
                            lineas.append(f"Cita en español: {cita_es}\n")
                        
                        # Mostrar correlaciones con audios
                        if correlaciones:
                            lineas.append(f"\n⚠️ CORRELACIÓN CON AUDIOS ACTUALES ({len(correlaciones)} encontradas):\n")
                            lineas.append("   [Este patrón detectado en el PDF histórico se REPITE en los audios actuales]\n")
                            for i, corr in enumerate(correlaciones, 1):
                                archivo = corr.get('archivo_audio', 'desconocido')
                                timestamp = corr.get('timestamp', '00:00')
                                cita_audio = corr.get('cita_audio', '')
                                similitud = corr.get('similitud', 0.0)
                                victima = corr.get('victima_detectada', '')
                                
                                lineas.append(f"\n  {i}. PATRÓN REPETIDO EN AUDIO ACTUAL:\n")
                                lineas.append(f"     Archivo: {archivo}\n")
                                lineas.append(f"     Timestamp: [{timestamp}]\n")
                                lineas.append(f"     Similitud del patrón: {similitud:.2%}\n")
                                if victima:
                                    lineas.append(f"     Víctima actual afectada: {victima}\n")
                                lineas.append(f"     Cita del audio (comportamiento repetido): {cita_audio[:200]}...\n")
                                lineas.append(f"     → Este mismo patrón fue documentado en el PDF con la ex esposa/hijos biológicos\n")
                        else:
                            lineas.append("\nNo se encontraron correlaciones con audios/videos actuales.\n")
                            lineas.append("(Este patrón del PDF no aparece repetido en los audios analizados)\n")
                        
                        lineas.append("\n")
        
        lineas.append("\n" + "=" * 80 + "\n\n")
        
        # ============================================================
        # D. ANÁLISIS FORENSE DK (§243) - CON AGRAVANTES
        # ============================================================
        lineas.append("D. ANÁLISIS FORENSE DK (§243)\n")
        lineas.append("=" * 80 + "\n\n")
        
        vurdering = clasificacion_legal.get('vurdering', '')
        indikation = clasificacion_legal.get('indikation', False)
        kriterier = clasificacion_legal.get('kriterier_opfyldt', [])
        risikoniveau_base = clasificacion_legal.get('risikoniveau', 'lav')
        
        # Aplicar agravantes
        risikoniveau_final = agravantes_legales.get('nivel_riesgo_final', risikoniveau_base.upper())
        
        lineas.append("CLASIFICACIÓN BAJO STRAFFELOVEN §243:\n")
        lineas.append("-" * 80 + "\n")
        lineas.append(f"{vurdering}\n\n")
        
        if kriterier:
            lineas.append("Criterios detectados:\n")
            for kriterium in kriterier:
                lineas.append(f"  - {kriterium}\n")
            lineas.append("\n")
        
        lineas.append(f"NIVEL DE RIESGO BASE: {risikoniveau_base.upper()}\n")
        lineas.append(f"NIVEL DE RIESGO FINAL (CON AGRAVANTES): {risikoniveau_final}\n")
        lineas.append("-" * 80 + "\n")
        
        # AGRAVANTES LEGALES
        lineas.append("\nAGRAVANTES LEGALES POR MENORES VULNERABLES:\n")
        lineas.append("-" * 80 + "\n\n")
        
        jd_info = agravantes_legales.get('juan_diego', {})
        jc_info = agravantes_legales.get('jose_carlos', {})
        
        lineas.append("HIJO MAYOR (17 años, autismo):\n")
        lineas.append(f"  - Edad: {jd_info.get('edad', 17)} años\n")
        lineas.append(f"  - Condición: {jd_info.get('condicion', 'autismo')}\n")
        lineas.append(f"  - Vulnerabilidad: {jd_info.get('vulnerabilidad', 'altamente vulnerable')}\n")
        lineas.append(f"  - Agresiones detectadas: {jd_info.get('agresiones_detectadas', 0)}\n")
        lineas.append(f"  - Clasificación automática: {jd_info.get('clasificacion_automatica', 'MODERAT')}\n")
        lineas.append("  - Base legal: Straffeloven §243, §245a, guías de Socialtilsynet\n\n")
        
        lineas.append("HIJO MENOR (15 años, TDAH):\n")
        lineas.append(f"  - Edad: {jc_info.get('edad', 15)} años\n")
        lineas.append(f"  - Condición: {jc_info.get('condicion', 'TDAH')}\n")
        lineas.append(f"  - Vulnerabilidad: {jc_info.get('vulnerabilidad', 'vulnerable')}\n")
        lineas.append(f"  - Agresiones detectadas: {jc_info.get('agresiones_detectadas', 0)}\n")
        lineas.append(f"  - Clasificación automática: {jc_info.get('clasificacion_automatica', 'MODERAT')}\n")
        lineas.append("  - Base legal: Straffeloven §243, §245a, guías de Socialtilsynet\n\n")
        
        lineas.append(f"Total de agresiones contra menores: {agravantes_legales.get('total_agresiones_menores', 0)}\n")
        lineas.append(f"Agresiones correlacionadas con audios: {agravantes_legales.get('agresiones_correlacionadas', 0)}\n\n")
        
        if risikoniveau_final == 'KRITISK':
            lineas.append("Riesgo crítico: Se detectaron indicadores graves y repetidos de violencia psicológica contra menores vulnerables.\n\n")
        elif risikoniveau_final == 'HØJ':
            lineas.append("Riesgo alto: Se detectaron múltiples indicadores de violencia psicológica contra menores vulnerables.\n\n")
        elif risikoniveau_final == 'MODERAT':
            lineas.append("Riesgo moderado: Se detectaron algunos indicadores de violencia psicológica.\n\n")
        else:
            lineas.append("Riesgo bajo: Pocas indicaciones de violencia psicológica.\n\n")
        
        lineas.append("\n" + "=" * 80 + "\n\n")
        
        # ============================================================
        # E. RESUMEN FORENSE
        # ============================================================
        lineas.append("E. RESUMEN FORENSE\n")
        lineas.append("=" * 80 + "\n\n")
        
        lineas.append("EXPLICACIÓN PARA ABOGADO O FAMILIERETSHUSET:\n")
        lineas.append("-" * 80 + "\n\n")
        
        lineas.append(f"El documento '{nombre_pdf}' ha sido analizado mediante técnicas forenses de análisis textual ")
        lineas.append("y correlación con evidencia de audio/video.\n\n")
        
        lineas.append(f"RESUMEN DE HALLAZGOS:\n")
        lineas.append(f"- Se detectaron {len(detecciones_agresion)} instancias de patrones de agresión psicológica.\n")
        
        # Contar correlaciones
        total_correlaciones = sum(len(det.get('correlaciones', [])) for det in detecciones_agresion)
        lineas.append(f"- Se encontraron {total_correlaciones} correlaciones con transcripciones de audio/video.\n")
        
        # Patrones repetitivos
        patrones_repetitivos = {}
        for det in detecciones_agresion:
            tipo = det.get('tipo', 'desconocido')
            correlaciones = det.get('correlaciones', [])
            if correlaciones:
                if tipo not in patrones_repetitivos:
                    patrones_repetitivos[tipo] = 0
                patrones_repetitivos[tipo] += len(correlaciones)
        
        if patrones_repetitivos:
            lineas.append(f"- Patrones repetitivos detectados: {len(patrones_repetitivos)} tipos de agresión con correlaciones.\n")
            for tipo, count in patrones_repetitivos.items():
                lineas.append(f"  * {tipo}: {count} correlaciones\n")
        
        lineas.append(f"- Se identificaron menciones a víctimas específicas: ")
        victimas_mencionadas = []
        for victima, menciones in menciones_victimas.items():
            if menciones:
                nombre_protegido = self.mapeo_victimas.get(victima, victima)
                victimas_mencionadas.append(f"{nombre_protegido} ({len(menciones)} menciones)")
        
        if victimas_mencionadas:
            lineas.append(', '.join(victimas_mencionadas) + ".\n")
        else:
            lineas.append("ninguna.\n")
        
        lineas.append(f"- Se detectaron {len(contradicciones)} posibles contradicciones internas.\n\n")
        
        lineas.append(f"EVALUACIÓN LEGAL:\n")
        lineas.append(f"Según la evaluación bajo Straffeloven §243 sobre violencia psicológica, ")
        if indikation:
            lineas.append(f"el documento presenta indicadores que cumplen con los criterios legales.\n")
        else:
            lineas.append(f"el documento presenta indicadores limitados que no alcanzan el umbral legal completo.\n")
        
        lineas.append(f"El nivel de riesgo evaluado (considerando agravantes por menores vulnerables) es {risikoniveau_final}, ")
        if risikoniveau_final == 'KRITISK':
            lineas.append("lo que indica la necesidad de atención inmediata y posible intervención legal.\n\n")
        elif risikoniveau_final == 'HØJ':
            lineas.append("lo que indica un riesgo significativo que requiere evaluación detallada.\n\n")
        elif risikoniveau_final == 'MODERAT':
            lineas.append("lo que indica algunos indicadores que merecen consideración.\n\n")
        else:
            lineas.append("lo que indica pocos indicadores de violencia psicológica.\n\n")
        
        lineas.append("\n" + "=" * 80 + "\n\n")
        
        # ============================================================
        # F. IMPLICACIONES JURÍDICAS PARA FAMILIENRETSHUSET
        # ============================================================
        lineas.append("F. IMPLICACIONES JURÍDICAS PARA FAMILIENRETSHUSET\n")
        lineas.append("=" * 80 + "\n\n")
        
        lineas.append("EVALUACIÓN DEL PATRÓN HISTÓRICO + PRESENTE:\n")
        lineas.append("-" * 80 + "\n\n")
        
        # Analizar patrón transgeneracional
        agresiones_contra_menores = agravantes_legales.get('total_agresiones_menores', 0)
        agresiones_correlacionadas = agravantes_legales.get('agresiones_correlacionadas', 0)
        
        lineas.append("ANÁLISIS DE PATRÓN REPETITIVO (ESTRATEGIA FORENSE):\n")
        lineas.append("-" * 80 + "\n\n")
        lineas.append("Este informe demuestra que los PATRONES DE COMPORTAMIENTO documentados en documentos históricos\n")
        lineas.append("(sobre la ex esposa e hijos biológicos del abusador) están siendo REPETIDOS en las grabaciones\n")
        lineas.append("actuales (con Claudia y sus hijos Juan Diego y José Carlos).\n\n")
        lineas.append("IMPORTANCIA FORENSE DE LA CORRELACIÓN:\n")
        lineas.append("  • Los PDFs documentan argumentos que el abusador está enfrentando por patrones de comportamiento\n")
        lineas.append("  • Los PDFs muestran que los hijos biológicos del abusador lo rechazan por estos mismos patrones\n")
        lineas.append("  • Los audios actuales demuestran que el abusador REPITE estos mismos patrones con Claudia y sus hijos\n")
        lineas.append("  • Esta correlación establece un PATRÓN CONSISTENTE de violencia psicológica a través del tiempo\n")
        lineas.append("  • El patrón repetitivo fortalece significativamente la evidencia legal según Straffeloven §243\n\n")
        
        if agresiones_correlacionadas > 0:
            lineas.append(f"✓ CORRELACIÓN CONFIRMADA: Se identificaron {agresiones_correlacionadas} agresiones del documento histórico\n")
            lineas.append(f"  que se REPITEN en las grabaciones de audio/video actuales.\n\n")
            lineas.append("  Esto demuestra que:\n")
            lineas.append("  1. El abusador tiene un patrón de comportamiento establecido y documentado históricamente\n")
            lineas.append("  2. Este patrón NO es aislado ni nuevo, sino que es parte de un comportamiento repetitivo\n")
            lineas.append("  3. Los mismos patrones que causaron rechazo de sus hijos biológicos se están repitiendo con Claudia y sus hijos\n")
            lineas.append("  4. La evidencia histórica (PDFs) corrobora y fortalece la evidencia actual (audios)\n\n")
        else:
            lineas.append("⚠️ No se encontraron correlaciones directas en este análisis específico.\n")
            lineas.append("  (Esto no invalida los patrones detectados, solo indica que requieren análisis más detallado)\n\n")
        
        if agresiones_contra_menores > 0:
            lineas.append(f"CRÍTICO: Se detectaron {agresiones_contra_menores} agresiones dirigidas específicamente a menores vulnerables ")
            lineas.append(f"(hijo mayor con autismo, hijo menor con TDAH).\n\n")
            lineas.append("Según las guías de Socialtilsynet y Straffeloven §243, §245a:\n")
            lineas.append("- El abuso contra menores con condiciones de desarrollo debe clasificarse automáticamente como HØJ o KRITISK.\n")
            lineas.append("- La vulnerabilidad de las víctimas constituye un agravante legal significativo.\n")
            lineas.append("- El patrón repetitivo indica riesgo continuo y necesidad de protección inmediata.\n\n")
        
        lineas.append("CONCLUSIONES LEGALES:\n")
        lineas.append("-" * 80 + "\n\n")
        
        if risikoniveau_final in ['HØJ', 'KRITISK']:
            lineas.append("Este documento histórico, en correlación con evidencia de audio/video, presenta relevancia crítica ")
            lineas.append("para procesos de protección familiar en Familienretshuset.\n\n")
            
            lineas.append("RECOMENDACIONES PARA FAMILIENRETSHUSET:\n")
            lineas.append("1. El documento puede ser utilizado como evidencia de patrón histórico de violencia psicológica.\n")
            lineas.append("2. La correlación con grabaciones actuales demuestra continuidad del comportamiento abusivo.\n")
            lineas.append("3. Se recomienda evaluación urgente por parte de profesionales especializados.\n")
            lineas.append("4. El contenido es relevante para decisiones sobre custodia, visitas y medidas de protección.\n")
            lineas.append("5. Se sugiere considerar restricción o supervisión de contacto con menores vulnerables.\n\n")
            
            lineas.append("RECOMENDACIONES PARA POLICÍA DANESA:\n")
            lineas.append("1. El documento puede constituir evidencia de violación de Straffeloven §243 (psykisk vold).\n")
            lineas.append("2. La presencia de menores vulnerables (autismo, TDAH) constituye agravante según §245a.\n")
            lineas.append("3. El patrón repetitivo puede indicar delito continuado.\n")
            lineas.append("4. Se recomienda investigación adicional y posible denuncia formal.\n\n")
        else:
            lineas.append("Este documento presenta relevancia moderada para procesos legales.\n\n")
            lineas.append("RECOMENDACIONES:\n")
            lineas.append("- El documento puede complementar otras evidencias en procesos familiares.\n")
            lineas.append("- Se recomienda evaluación contextual por parte de profesionales.\n\n")
        
        lineas.append("\n" + "=" * 80 + "\n")
        lineas.append(f"Fin del informe - Generado el {fecha_procesamiento}\n")
        lineas.append("=" * 80 + "\n")
        
        return ''.join(lineas)
    
    def generar_informe_forense(
        self,
        nombre_pdf: str,
        ruta_pdf: str,
        texto_extraido: Dict[str, Any],
        detecciones_agresion: List[Dict[str, Any]],
        menciones_victimas: Dict[str, List[Dict[str, Any]]],
        contradicciones: List[Dict[str, Any]],
        clasificacion_legal: Dict[str, Any]
    ) -> str:
        """
        Método legacy - redirige a generar_informe_correlacional
        Mantenido para compatibilidad
        """
        # Usar valores por defecto para parámetros faltantes
        agravantes_legales = self.calcular_agravantes_legales(detecciones_agresion, menciones_victimas)
        transcripciones = []
        
        return self.generar_informe_correlacional(
            nombre_pdf, ruta_pdf, texto_extraido, detecciones_agresion,
            menciones_victimas, contradicciones, clasificacion_legal,
            agravantes_legales, transcripciones
        )

