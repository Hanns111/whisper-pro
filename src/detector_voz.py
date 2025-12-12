"""
Detector de estrés vocal y voz elevada
Analiza características acústicas del audio para detectar cambios en volumen y tono
"""

import os
import numpy as np
from typing import List, Dict, Any, Optional
import logging

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logging.warning("librosa no disponible, usando métodos alternativos")


class VoiceStressDetector:
    """
    Clase para detectar estrés vocal y voz elevada en archivos de audio
    """
    
    def __init__(self, umbral_db: float = 10.0, ventana_segundos: float = 2.0):
        """
        Inicializa el detector
        
        Args:
            umbral_db: Umbral de cambio en dB para considerar voz elevada
            ventana_segundos: Tamaño de ventana para análisis en segundos
        """
        self.logger = logging.getLogger(__name__)
        self.umbral_db = umbral_db
        self.ventana_segundos = ventana_segundos
        
        if not LIBROSA_AVAILABLE:
            self.logger.warning("librosa no está instalado. Instala con: pip install librosa")
    
    def _calcular_rms_db(self, audio: np.ndarray, sr: int, inicio: float, fin: float) -> float:
        """
        Calcula el RMS en dB para un segmento
        
        Args:
            audio: Array de audio
            sr: Sample rate
            inicio: Tiempo de inicio en segundos
            fin: Tiempo de fin en segundos
            
        Returns:
            RMS en dB
        """
        inicio_idx = int(inicio * sr)
        fin_idx = int(fin * sr)
        
        if inicio_idx >= len(audio) or fin_idx > len(audio):
            return 0.0
        
        segmento = audio[inicio_idx:fin_idx]
        
        if len(segmento) == 0:
            return 0.0
        
        # Calcular RMS
        rms = np.sqrt(np.mean(segmento**2))
        
        # Convertir a dB (evitar log de 0)
        if rms > 0:
            db = 20 * np.log10(rms + 1e-10)
        else:
            db = -np.inf
        
        return db
    
    def _detectar_picos_bruscos(
        self,
        audio: np.ndarray,
        sr: int,
        segmentos: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detecta picos bruscos de volumen
        
        Args:
            audio: Array de audio
            sr: Sample rate
            segmentos: Segmentos de transcripción con timestamps
            
        Returns:
            Lista de detecciones de picos
        """
        detecciones = []
        
        if len(segmentos) < 2:
            return detecciones
        
        # Calcular niveles de volumen para cada segmento
        niveles = []
        for seg in segmentos:
            inicio = seg.get('start', 0)
            fin = seg.get('end', inicio + 1)
            db = self._calcular_rms_db(audio, sr, inicio, fin)
            niveles.append({
                'inicio': inicio,
                'fin': fin,
                'db': db
            })
        
        # Calcular nivel promedio
        db_promedio = np.mean([n['db'] for n in niveles if n['db'] > -np.inf])
        
        # Detectar segmentos con volumen elevado
        for nivel in niveles:
            if nivel['db'] > -np.inf and nivel['db'] > db_promedio + self.umbral_db:
                detecciones.append({
                    'inicio': nivel['inicio'],
                    'fin': nivel['fin'],
                    'tipo': 'voz elevada',
                    'db_change': nivel['db'] - db_promedio,
                    'db_absoluto': nivel['db']
                })
        
        return detecciones
    
    def analizar_audio(
        self,
        ruta_audio: str,
        segmentos: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analiza el audio para detectar estrés vocal
        
        Args:
            ruta_audio: Ruta al archivo de audio
            segmentos: Segmentos de transcripción con timestamps
            
        Returns:
            Lista de detecciones de estrés vocal
        """
        if not os.path.exists(ruta_audio):
            self.logger.error(f"Archivo de audio no encontrado: {ruta_audio}")
            return []
        
        if not LIBROSA_AVAILABLE:
            self.logger.warning("librosa no disponible, usando análisis simplificado")
            return self._analisis_simplificado(segmentos)
        
        try:
            # Cargar audio
            self.logger.info(f"Analizando audio: {os.path.basename(ruta_audio)}")
            audio, sr = librosa.load(ruta_audio, sr=None, mono=True)
            
            # Detectar picos bruscos
            detecciones = self._detectar_picos_bruscos(audio, sr, segmentos)
            
            self.logger.info(f"Detectados {len(detecciones)} momentos de voz elevada")
            return detecciones
            
        except Exception as e:
            self.logger.error(f"Error al analizar audio: {str(e)}")
            return self._analisis_simplificado(segmentos)
    
    def _analisis_simplificado(
        self,
        segmentos: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Análisis simplificado cuando librosa no está disponible
        Basado en duración y características del texto
        
        Args:
            segmentos: Segmentos de transcripción
            
        Returns:
            Lista vacía o detecciones básicas
        """
        # Sin librosa, no podemos hacer análisis acústico real
        # Retornar lista vacía
        self.logger.warning("Análisis acústico no disponible sin librosa")
        return []
    
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
        from datetime import datetime
        
        resultado = {
            'fecha_analisis': datetime.now().isoformat(),
            'total_detecciones': len(detecciones),
            'umbral_db': self.umbral_db,
            'detecciones': detecciones
        }
        
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Análisis de voz exportado a JSON: {ruta_salida}")
    
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
            titulo = "ANÁLISIS DE ESTRÉS VOCAL\n"
            titulo += "=" * 50 + "\n\n"
        else:
            titulo = "VOCAL STRESS ANALYSIS\n"
            titulo += "=" * 50 + "\n\n"
        
        lineas = [titulo]
        lineas.append(f"Total de detecciones: {len(detecciones)}\n")
        lineas.append(f"Umbral: {self.umbral_db} dB\n\n")
        
        for det in detecciones:
            inicio_str = self._formatear_tiempo(det['inicio'])
            fin_str = self._formatear_tiempo(det['fin'])
            
            if idioma == 'es':
                linea = f"[{inicio_str} - {fin_str}] {det['tipo']}\n"
                linea += f"  Cambio en dB: {det.get('db_change', 0):.2f}\n"
                if 'db_absoluto' in det:
                    linea += f"  dB absoluto: {det['db_absoluto']:.2f}\n"
            else:
                linea = f"[{inicio_str} - {fin_str}] {det['tipo']}\n"
                linea += f"  dB change: {det.get('db_change', 0):.2f}\n"
                if 'db_absoluto' in det:
                    linea += f"  Absolute dB: {det['db_absoluto']:.2f}\n"
            
            linea += "\n"
            lineas.append(linea)
        
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            f.writelines(lineas)
        
        self.logger.info(f"Análisis de voz exportado a TXT ({idioma}): {ruta_salida}")
    
    def _formatear_tiempo(self, segundos: float) -> str:
        """Formatea tiempo en formato MM:SS"""
        minutos = int(segundos // 60)
        segs = int(segundos % 60)
        return f"{minutos:02d}:{segs:02d}"





