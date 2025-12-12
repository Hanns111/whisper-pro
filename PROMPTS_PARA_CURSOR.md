# PROMPTS PARA CURSOR IDE - Análisis de Caso Lars

Este documento contiene prompts optimizados para usar con Cursor IDE en el análisis del caso de Lars Erling Sørensen.

---

## 📋 PROMPT 1: Análisis General del Caso

```
Analiza el caso legal de Lars Erling Sørensen basándote en los siguientes documentos:

CONTEXTO:
- PDFs del proceso legal en: C:\Users\hanns\Downloads\AUDIOS\Procesos Lars (ex esposa)-20251203T004023Z-1-001\Procesos Lars (ex esposa)\
- Transcripciones de audios en: C:\Users\hanns\Proyectos\whisper-pro\transcripciones\

TAREAS:
1. Lee el archivo "informe_patrones_lars.txt" que contiene el análisis consolidado
2. Lee el archivo "patrones_lars.json" con los datos estructurados
3. Identifica los 5 patrones de comportamiento más preocupantes
4. Correlaciona estos patrones con la documentación legal (bitácora de Lars, documentos de Statsforvaltningen)
5. Genera un resumen ejecutivo de máximo 2 páginas

FORMATO DE SALIDA:
- Markdown estructurado
- Usa tablas para datos comparativos
- Incluye referencias a archivos específicos con timestamps cuando sea relevante
```

---

## 📊 PROMPT 2: Análisis Estadístico de Frecuencia

```
Realiza un análisis estadístico detallado de los patrones de comportamiento identificados en el caso Lars.

DATOS A ANALIZAR:
- Archivo JSON: C:\Users\hanns\Proyectos\whisper-pro\patrones_lars.json
- Transcripciones: C:\Users\hanns\Proyectos\whisper-pro\transcripciones\

ANÁLISIS REQUERIDO:
1. Frecuencia de cada categoría de patrón por fecha
2. Identificar escalada temporal (¿aumentan o disminuyen los patrones con el tiempo?)
3. Correlación entre:
   - Amenazas y manipulación financiera
   - Críticas a los hijos y victimización
   - Amenazas de abandono y culpabilización
4. Crear gráficos de:
   - Línea temporal de patrones
   - Distribución por categoría
   - Heatmap de frecuencia por fecha

HERRAMIENTAS:
- Usa Python con pandas, matplotlib, seaborn
- Genera visualizaciones en formato PNG
- Guarda los resultados en: C:\Users\hanns\Proyectos\whisper-pro\analisis_estadistico\
```

---

## ⚖️ PROMPT 3: Correlación con Marco Legal Danés

```
Correlaciona los patrones encontrados con el marco legal danés, específicamente con Straffeloven §243 sobre violencia psicológica.

CONTEXTO LEGAL:
La bitácora de Lars muestra que Rikke (su ex esposa) alega que Lars:
- Manipula a los hijos (Kristian y Frederik)
- Ejerce presión psicológica
- Tiene problemas financieros que afectan a la familia

DATOS ACTUALES:
Tenemos transcripciones de audios de Lars con otra pareja (Claudia) donde se observan patrones similares.

TAREA:
1. Lee los documentos del caso legal (PDFs en danés)
2. Extrae los alegatos específicos de Rikke
3. Compara con los patrones identificados en audios con Claudia
4. Identifica:
   - Patrones que se repiten con ambas parejas
   - Frases o comportamientos idénticos
   - Escalada de comportamientos
5. Evalúa según criterios de Straffeloven §243

FORMATO DE SALIDA:
Tabla comparativa con columnas:
| Alegato de Rikke | Patrón con Claudia | Archivo de evidencia | Severidad (1-5) |
```

---

## 🔍 PROMPT 4: Análisis de Lenguaje y Manipulación

```
Analiza el lenguaje utilizado por Lars en las transcripciones para identificar técnicas de manipulación psicológica.

ARCHIVOS A ANALIZAR:
C:\Users\hanns\Proyectos\whisper-pro\transcripciones\Audios-20251203T004026Z-1-001\

TÉCNICAS A IDENTIFICAR:
1. Gaslighting:
   - "You never learn who I am"
   - "You don't listen to what I say"
   - Negación de realidad

2. DARVO (Deny, Attack, Reverse Victim and Offender):
   - Se presenta como víctima
   - Invierte la responsabilidad
   - Ataca en respuesta a acusaciones

3. Triangulación:
   - Involucra a los hijos en conflictos
   - Compara comportamientos
   - Crea alianzas contra la pareja

4. Control financiero:
   - Referencias constantes a dinero
   - Culpabilización por gastos
   - Menciones de sus pérdidas en trading

ANÁLISIS:
Para cada técnica:
- Extrae 5 ejemplos textuales
- Indica archivo y timestamp
- Explica por qué constituye manipulación
- Clasifica severidad (baja/media/alta)

FORMATO: Informe en Markdown con ejemplos citados
```

---

## 👨‍👦 PROMPT 5: Análisis de Impacto en los Hijos

```
Analiza las referencias a los hijos (tanto de Lars como de Claudia) en las transcripciones y su posible impacto psicológico.

CONTEXTO:
- Los hijos de Lars con Rikke: Kristian y Frederik (ambos mencionados en documentos legales)
- Los hijos de Claudia: Juan Diego (Juan Di, en espectro autista) y José Carlos

BUSCAR EN TRANSCRIPCIONES:
1. Menciones directas de los hijos
2. Acusaciones contra los hijos
3. Uso de los hijos como:
   - Argumento en discusiones
   - Herramienta de presión ("te quitarán los hijos")
   - Motivo de culpabilización

ANÁLISIS:
1. Crea una tabla de todas las menciones
2. Clasifica por tipo:
   - Positivas
   - Negativas
   - Instrumentalizadoras
   - Amenazantes
3. Identifica patrones repetitivos
4. Evalúa potencial impacto psicológico según literatura especializada

REFERENCIAS:
- Busca similitudes con el caso legal de Rikke
- ¿Lars usa las mismas tácticas con los hijos de Claudia que presuntamente usó con Kristian y Frederik?
```

---

## 📝 PROMPT 6: Generación de Informe Legal

```
Genera un informe forense que pueda ser utilizado como evidencia complementaria en un proceso legal.

ESTRUCTURA DEL INFORME:
1. RESUMEN EJECUTIVO
   - Descripción del caso
   - Metodología de análisis
   - Hallazgos principales

2. METODOLOGÍA
   - Fuentes de datos
   - Herramientas utilizadas
   - Criterios de análisis

3. HALLAZGOS DETALLADOS
   - Por categoría de patrón
   - Con ejemplos textuales y timestamps
   - Frecuencia y progresión temporal

4. ANÁLISIS COMPARATIVO
   - Similitudes con caso legal previo (Rikke)
   - Patrones consistentes entre diferentes parejas
   - Evidencia de comportamiento sistemático

5. EVALUACIÓN SEGÚN STRAFFELOVEN §243
   - Criterios aplicables
   - Nivel de riesgo
   - Elementos que constituyen violencia psicológica

6. CONCLUSIONES
   - Patrones identificados
   - Riesgo evaluado
   - Recomendaciones

7. ANEXOS
   - Lista completa de archivos analizados
   - Tabla de frecuencias
   - Extractos relevantes

FORMATO:
- Documento formal en español
- Lenguaje técnico pero comprensible
- Referencias bibliográficas sobre violencia psicológica
- Guardar como: informe_forense_legal.pdf
```

---

## 🔄 PROMPT 7: Actualización y Re-análisis

```
Actualiza el análisis cuando se agreguen nuevas transcripciones o documentos.

PROCESO:
1. Detecta nuevos archivos en:
   - C:\Users\hanns\Proyectos\whisper-pro\transcripciones\
   - C:\Users\hanns\Downloads\AUDIOS\

2. Ejecuta el script de análisis:
   python analizar_patrones_lars.py

3. Compara resultados con análisis previo:
   - ¿Aparecen nuevos patrones?
   - ¿Se intensifican patrones existentes?
   - ¿Hay evidencia de escalada?

4. Genera informe incremental:
   - Solo con nuevos hallazgos
   - Comparación con tendencia histórica
   - Actualiza estadísticas generales

5. Notifica cambios significativos:
   - Nuevas categorías de riesgo
   - Aumento de frecuencia >20%
   - Patrones críticos emergentes
```

---

## 🎯 PROMPT 8: Búsqueda de Patrones Específicos

```
Busca instancias específicas de comportamiento en las transcripciones.

USAR CUANDO NECESITES BUSCAR:

### Ejemplo 1: Amenazas de reportar a autoridades
"Busca en todas las transcripciones instancias donde Lars mencione:
- 'report you'
- 'police'
- 'take your children'
- 'lose your children'

Para cada instancia encontrada:
1. Muestra el contexto completo (2 minutos antes y después según timestamps)
2. Identifica si hay un detonante (¿qué provocó la amenaza?)
3. Analiza la respuesta de Claudia
4. Clasifica la severidad"

### Ejemplo 2: Referencias a problemas financieros
"Extrae todas las menciones de:
- 'trading'
- 'crypto'
- 'money'
- 'lost money'
- 'pay'

Crea un timeline de problemas financieros y correlaciona con:
- Aumento de tensión en conversaciones
- Culpabilización a Claudia
- Menciones de estrés"

### Ejemplo 3: Victimización
"Busca frases donde Lars se presenta como víctima:
- 'I don't want to live'
- 'I am so stressed'
- 'nightmare for me'
- 'my life was quiet'

Analiza el contexto y determina si es:
- Manipulación emocional
- Expresión genuina de malestar
- Mezcla de ambos"
```

---

## 💡 PROMPT 9: Análisis Predictivo

```
Basándote en los patrones identificados, genera un análisis predictivo del riesgo de escalada.

MODELO DE ANÁLISIS:
1. Crea una línea de tiempo de severidad:
   - Marca cada incidente con nivel de severidad (1-10)
   - Identifica tendencia (¿aumenta, disminuye, estable?)

2. Factores de riesgo:
   - Frecuencia aumentada de amenazas
   - Introducción de nuevas tácticas
   - Aislamiento social de la víctima
   - Control financiero creciente
   - Menciones de desesperación

3. Indicadores de escalada:
   - Amenazas más explícitas
   - Involucramiento de autoridades
   - Referencias a violencia
   - Ultimátums

4. Evaluación de riesgo:
   - Bajo (patrones estables, baja frecuencia)
   - Medio (incremento gradual, múltiples categorías)
   - Alto (escalada rápida, amenazas explícitas)
   - Crítico (riesgo inmediato)

SALIDA:
- Informe de evaluación de riesgo
- Gráficos de tendencia
- Recomendaciones de seguridad
- Señales de alerta temprana
```

---

## 🔧 PROMPT 10: Mejora del Script de Análisis

```
Mejora el script "analizar_patrones_lars.py" con las siguientes funcionalidades:

MEJORAS A IMPLEMENTAR:
1. Análisis de sentimiento:
   - Usa NLTK o TextBlob
   - Clasifica tono (agresivo, neutro, víctima)
   - Genera gráfico de sentimiento por archivo

2. Detección de named entities:
   - Identifica automáticamente nombres mencionados
   - Crea grafo de relaciones
   - Visualiza con NetworkX

3. Análisis de progresión temporal mejorado:
   - Convierte fechas a datetime
   - Calcula intervalos entre incidentes
   - Identifica patrones semanales/mensuales

4. Export adicionales:
   - Excel con múltiples hojas
   - HTML interactivo con gráficos
   - PDF del informe con formateo profesional

5. Dashboard interactivo:
   - Usa Streamlit o Dash
   - Visualizaciones dinámicas
   - Filtros por fecha/categoría/severidad

6. Sistema de alertas:
   - Notifica cuando se detecten patrones críticos
   - Email automático con resumen
   - Logs detallados

PRIORIDAD: Implementar en orden de arriba a abajo
```

---

## 📚 RECURSOS ADICIONALES

### Archivos Clave del Proyecto:
```
C:\Users\hanns\Proyectos\whisper-pro\
├── analizar_patrones_lars.py          (Script principal de análisis)
├── informe_patrones_lars.txt          (Informe consolidado texto)
├── patrones_lars.json                 (Datos estructurados)
└── transcripciones\
    ├── Audios de Lars -20251203T004029Z-1-001\  (Transcripciones carpeta 1)
    └── Audios-20251203T004026Z-1-001\            (Transcripciones carpeta 2)

C:\Users\hanns\Downloads\AUDIOS\
└── Procesos Lars (ex esposa)-20251203T004023Z-1-001\
    └── Procesos Lars (ex esposa)\  (PDFs del caso legal)
```

### Comandos Útiles:
```bash
# Ejecutar análisis completo
cd C:\Users\hanns\Proyectos\whisper-pro
python analizar_patrones_lars.py

# Leer informe generado
type informe_patrones_lars.txt

# Ver datos JSON
type patrones_lars.json | python -m json.tool
```

---

## 🎓 TIPS PARA USAR CON CURSOR

1. **Contexto Automático**: Cursor puede leer automáticamente los archivos del proyecto. Simplemente menciona "lee el archivo X" y lo hará.

2. **Multi-archivo**: Puedes pedirle que compare múltiples archivos: "Compara los patrones en archivo A vs archivo B"

3. **Generación de Código**: Si necesitas nuevas funciones en el script, Cursor puede generarlas directamente.

4. **Debugging**: Si hay errores, pega el error completo y Cursor te ayudará a solucionarlo.

5. **Iteración**: Puedes pedir mejoras incrementales: "Ahora agrega también análisis de X"

---

## ⚠️ CONSIDERACIONES ÉTICAS Y LEGALES

**IMPORTANTE**: Este análisis tiene fines legales y de documentación. Asegúrate de:

1. Mantener la confidencialidad de los datos
2. Usar los hallazgos solo con asesoría legal adecuada
3. No compartir información personal o sensible
4. Respetar las leyes de protección de datos de Dinamarca
5. Consultar con un abogado especializado en derecho de familia danés

---

## 📞 SOPORTE

Si necesitas ayuda adicional con cualquiera de estos prompts, puedes:
1. Modificarlos según tus necesidades específicas
2. Combinar múltiples prompts
3. Crear variaciones personalizadas

**Última actualización**: Diciembre 2025
