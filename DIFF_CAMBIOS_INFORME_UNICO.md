# 📋 DIFF COMPLETO - Cambio a Informe Único

## Resumen de Cambios

Se modificó completamente el pipeline para generar **UN SOLO archivo TXT** por audio en lugar de múltiples archivos JSON y TXT.

---

## 🆕 ARCHIVO CREADO: `src/generador_informe_unico.py`

**Nuevo módulo** que consolida todos los análisis en un único informe TXT.

### Clase: `GeneradorInformeUnico`

**Métodos principales:**
- `generar_informe()`: Genera el contenido completo del informe
- `guardar_informe()`: Guarda el informe en un archivo TXT
- `_formatear_tiempo()`: Formatea timestamps en formato [MM:SS]
- `_formatear_duracion()`: Formatea duración en formato legible

**Estructura del informe generado:**
1. **A. CABECERA**: Nombre, duración, fecha, identificador único
2. **B. TRANSCRIPCIÓN CON TIMELINE**: Cada línea con formato [MM:SS] texto
3. **C. ANÁLISIS DE AGRESIÓN (ES)**: Insultos, gaslighting, manipulación, amenazas, invalidación, control económico
4. **D. ANÁLISIS DE VOZ / ESTRÉS (ES)**: Picos de volumen, cambios de tono, voz elevada, estrés acústico
5. **E. ANÁLISIS DE VÍCTIMAS (ES)**: Agresión hacia Claudia, Juan Diego, José Carlos
6. **F. ANÁLISIS FORENSE LEGAL DANÉS (§243)**: Clasificación, nivel de riesgo, evidencia textual
7. **G. INFORME UNIFICADO (ES)**: Resumen narrativo, explicación, conclusiones

---

## 🔄 ARCHIVO MODIFICADO: `run_transcription.py`

### Cambio 1: Imports (Líneas 21-26)

**ANTES:**
```python
from src.analizador_agresion import AgresionAnalyzer
from src.detector_voz import VoiceStressDetector
from src.detector_victimas import VictimDetector
from src.analizador_forense_dk import AnalizadorForenseDK
import logging
import json
```

**DESPUÉS:**
```python
from src.analizador_agresion import AgresionAnalyzer
from src.detector_voz import VoiceStressDetector
from src.detector_victimas import VictimDetector
from src.analizador_forense_dk import AnalizadorForenseDK
from src.generador_informe_unico import GeneradorInformeUnico
import logging
```

**Cambios:**
- ✅ Agregado import de `GeneradorInformeUnico`
- ✅ Eliminado import de `json` (ya no se usa)

---

### Cambio 2: Inicialización de Generador (Línea 66)

**ANTES:**
```python
        analizador_agresion = AgresionAnalyzer()
        detector_voz = VoiceStressDetector()
        detector_victimas = VictimDetector()
        analizador_forense_dk = AnalizadorForenseDK()
```

**DESPUÉS:**
```python
        analizador_agresion = AgresionAnalyzer()
        detector_voz = VoiceStressDetector()
        detector_victimas = VictimDetector()
        analizador_forense_dk = AnalizadorForenseDK()
        generador_informe = GeneradorInformeUnico()
```

**Cambios:**
- ✅ Agregada inicialización de `GeneradorInformeUnico`

---

### Cambio 3: Eliminación Completa de Exportaciones Múltiples (Líneas 163-345)

**ANTES (Eliminado completamente):**
```python
                # f) Generar nombre base para archivos
                nombre_base = os.path.splitext(os.path.basename(archivo_audio))[0]
                nombre_base = nombre_base.replace(' ', '_').replace('/', '_').replace('\\', '_')
                timestamp = int(time.time())
                prefijo = f"{nombre_base}_{timestamp}"
                
                # Exportar análisis de agresión
                ruta_agresion_json = os.path.join(CARPETA_TRANSCRIPCIONES, f"{prefijo}_analisis_agresion.json")
                ruta_agresion_es = os.path.join(CARPETA_TRANSCRIPCIONES, f"{prefijo}_analisis_agresion_es.txt")
                analizador_agresion.exportar_json(analisis_agresion, ruta_agresion_json)
                analizador_agresion.exportar_txt(analisis_agresion, ruta_agresion_es, 'es')
                
                # Exportar análisis de voz
                ruta_voz_json = os.path.join(CARPETA_TRANSCRIPCIONES, f"{prefijo}_analisis_voz.json")
                ruta_voz_es = os.path.join(CARPETA_TRANSCRIPCIONES, f"{prefijo}_analisis_voz_es.txt")
                detector_voz.exportar_json(analisis_voz, ruta_voz_json)
                detector_voz.exportar_txt(analisis_voz, ruta_voz_es, 'es')
                
                # Exportar análisis de víctimas
                ruta_victimas_json = os.path.join(CARPETA_TRANSCRIPCIONES, f"{prefijo}_analisis_victimas.json")
                ruta_victimas_es = os.path.join(CARPETA_TRANSCRIPCIONES, f"{prefijo}_analisis_victimas_es.txt")
                detector_victimas.exportar_json(analisis_victimas, ruta_victimas_json)
                detector_victimas.exportar_txt(analisis_victimas, ruta_victimas_es, 'es')
                
                # Exportar análisis forense DK
                ruta_forense_dk = os.path.join(CARPETA_TRANSCRIPCIONES, f"{prefijo}_forensisk_analyse_dk.txt")
                ruta_forense_dk_json = os.path.join(CARPETA_TRANSCRIPCIONES, f"{prefijo}_forensisk_analyse_dk.json")
                analizador_forense_dk.eksporter_rapport(analisis_forense_dk, nombre_base, ruta_forense_dk)
                analizador_forense_dk.eksporter_json(analisis_forense_dk, ruta_forense_dk_json)
                
                # g) Generar informe unificado
                logger.info("Paso 6/6: Generando informe unificado...")
                informe_completo = {
                    'archivo': os.path.basename(archivo_audio),
                    'fecha_analisis': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'transcripcion': {
                        'idioma': idioma_detectado,
                        'duracion_segundos': duracion_audio,
                        'caracteres': len(texto),
                        'texto_completo': texto
                    },
                    'analisis_agresion': {
                        'total': len(analisis_agresion),
                        'detecciones': analisis_agresion
                    },
                    'analisis_voz': {
                        'total': len(analisis_voz),
                        'detecciones': analisis_voz
                    },
                    'analisis_victimas': {
                        'total': len(analisis_victimas),
                        'detecciones': analisis_victimas
                    },
                    'analisis_forense_dk': {
                        'risikoniveau': analisis_forense_dk['risikoniveau'],
                        'juridisk_klassifikation': analisis_forense_dk['juridisk_klassifikation'],
                        'tidsbegivenheder': len(analisis_forense_dk['tidsbegivenheder'])
                    }
                }
                
                # Guardar informe completo JSON
                ruta_informe_json = os.path.join(CARPETA_TRANSCRIPCIONES, f"{prefijo}_informe_completo.json")
                with open(ruta_informe_json, 'w', encoding='utf-8') as f:
                    json.dump(informe_completo, f, ensure_ascii=False, indent=2)
                
                # Generar informe en texto (español) - [~100 líneas eliminadas]
                # Generar informe en inglés - [~50 líneas eliminadas]
                
                logger.info(f"✓ Análisis completo guardado:")
                logger.info(f"  - {os.path.basename(ruta_agresion_json)}")
                # ... [múltiples líneas de logging eliminadas]
```

**DESPUÉS (Nuevo código simplificado):**
```python
                # f) Generar informe único consolidado
                logger.info("Paso 6/6: Generando informe único consolidado...")
                
                # Generar identificador único
                timestamp = int(time.time())
                identificador_unico = f"ID_{timestamp}_{os.path.splitext(os.path.basename(archivo_audio))[0]}"
                fecha_analisis = time.strftime('%Y-%m-%d %H:%M:%S')
                
                # Generar contenido del informe único
                contenido_informe = generador_informe.generar_informe(
                    nombre_archivo=os.path.basename(archivo_audio),
                    duracion_audio=duracion_audio,
                    fecha_analisis=fecha_analisis,
                    identificador_unico=identificador_unico,
                    resultado_whisper=resultado,
                    analisis_agresion=analisis_agresion,
                    analisis_voz=analisis_voz,
                    analisis_victimas=analisis_victimas,
                    analisis_forense_dk=analisis_forense_dk
                )
                
                # Guardar informe único
                ruta_informe_unico = generador_informe.guardar_informe(
                    contenido=contenido_informe,
                    nombre_archivo_audio=os.path.basename(archivo_audio),
                    carpeta_salida=CARPETA_TRANSCRIPCIONES
                )
                
                logger.info(f"✓ Informe único guardado: {os.path.basename(ruta_informe_unico)}")
```

**Cambios:**
- ✅ Eliminadas ~180 líneas de código de exportación múltiple
- ✅ Reemplazadas por ~20 líneas de código simplificado
- ✅ Un solo archivo generado: `{nombre_audio}_INFORME_UNICO.txt`
- ✅ Código más limpio y mantenible

---

## 📊 Comparación: Antes vs. Después

### ANTES (Múltiples archivos):
Por cada audio se generaban **11 archivos**:
1. `{nombre}_{timestamp}_analisis_agresion.json`
2. `{nombre}_{timestamp}_analisis_agresion_es.txt`
3. `{nombre}_{timestamp}_analisis_voz.json`
4. `{nombre}_{timestamp}_analisis_voz_es.txt`
5. `{nombre}_{timestamp}_analisis_victimas.json`
6. `{nombre}_{timestamp}_analisis_victimas_es.txt`
7. `{nombre}_{timestamp}_forensisk_analyse_dk.json`
8. `{nombre}_{timestamp}_forensisk_analyse_dk.txt`
9. `{nombre}_{timestamp}_informe_completo.json`
10. `{nombre}_{timestamp}_informe_es.txt`
11. `{nombre}_{timestamp}_informe_en.txt`

### DESPUÉS (Un solo archivo):
Por cada audio se genera **1 archivo**:
1. `{nombre_audio}_INFORME_UNICO.txt`

---

## ✅ Verificaciones

- ✅ No se copian ni mueven archivos de audio originales
- ✅ Solo se genera un archivo TXT por audio
- ✅ El informe incluye todas las secciones requeridas
- ✅ Formato de timestamps: [MM:SS]
- ✅ Todas las detecciones están incluidas
- ✅ Análisis forense danés completo
- ✅ Código simplificado y mantenible

---

## 📝 Formato del Archivo Generado

El archivo `{nombre_audio}_INFORME_UNICO.txt` contiene:

```
================================================================================
INFORME ÚNICO DE ANÁLISIS FORENSE
================================================================================

INFORMACIÓN DEL ARCHIVO
--------------------------------------------------------------------------------
Nombre del archivo: [nombre]
Duración: [Xh Xm Xs] ([X.XX] segundos)
Fecha del análisis: [YYYY-MM-DD HH:MM:SS]
Identificador único: [ID_...]
Idioma detectado: [idioma]

================================================================================

B. TRANSCRIPCIÓN CON TIMELINE
================================================================================

[00:00] Texto del primer segmento
[00:15] Texto del segundo segmento
...

================================================================================

C. ANÁLISIS DE AGRESIÓN (ES)
================================================================================

INSULTOS (X detecciones):
--------------------------------------------------------------------------------
[MM:SS - MM:SS] Severidad: ALTA
  [frase detectada]

...

================================================================================

D. ANÁLISIS DE VOZ / ESTRÉS (ES)
================================================================================

DETECCIÓN DE PICOS DE VOLUMEN:
--------------------------------------------------------------------------------
[MM:SS - MM:SS] Aumento de volumen: X.XX dB

...

================================================================================

E. ANÁLISIS DE VÍCTIMAS (ES)
================================================================================

AGRESIÓN HACIA CLAUDIA (X detecciones):
--------------------------------------------------------------------------------

  Tipo: AMENAZA DIRIGIDA (X instancias)
    [MM:SS - MM:SS] Severidad: ALTA
      [frase]

...

================================================================================

F. ANÁLISIS FORENSE LEGAL DANÉS (§243)
================================================================================

CLASIFICACIÓN BAJO STRAFFELOVEN §243:
--------------------------------------------------------------------------------
[Evaluación legal]

NIVEL DE RIESGO: [LAV/MODERAT/HØJ/KRITISK]
--------------------------------------------------------------------------------
[Descripción del nivel]

EVIDENCIA TEXTUAL CON TIMESTAMPS:
--------------------------------------------------------------------------------
[MM:SS] [Tipo]: [Texto]

...

================================================================================

G. INFORME UNIFICADO (ES)
================================================================================

RESUMEN NARRATIVO COMPLETO:
--------------------------------------------------------------------------------

[Resumen completo del análisis]

EXPLICACIÓN CLARA Y ENTENDIBLE:
--------------------------------------------------------------------------------

[Explicación detallada]

CONCLUSIONES:
--------------------------------------------------------------------------------

1. [Conclusión 1]
2. [Conclusión 2]
...

================================================================================
Fin del informe - Generado el [fecha]
================================================================================
```

---

**Fecha de cambios**: Diciembre 2025
**Estado**: ✅ Implementación completa





