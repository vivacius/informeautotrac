# Productivity App - John Deere Telemetría

Este es un dashboard interactivo desarrollado en **Streamlit** para analizar el desempeño de la tecnología **AutoTrac™** en cosechadoras de caña de azúcar (John Deere CH570).

## 🚀 Características

- **Análisis de Flota**: Visualización global del desempeño por máquina y turno.
- **Visión por Alce**: Análisis detallado por zona de operación (Alce), con identificación de mejores desempeños y alertas de falta de uso tecnológico.
- **Reporte Ejecutivo**: Generación de informes en formato PDF con insights automáticos y recomendaciones.
- **Procesamiento Robusto**: Agregación automática por horas para asegurar precisión en los porcentajes de uso.

## 🛠️ Tecnologías Utilizadas

- **Python**: Lógica central del negocio.
- **Streamlit**: Framework para la interfaz web.
- **Pandas/NumPy**: Procesamiento y análisis de datos.
- **Plotly**: Gráficos interactivos dinámicos.
- **FPDF/Matplotlib**: Generación del reporte PDF.

## 📦 Instalación y Uso

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/productivity-app.git
   cd productivity-app
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Ejecutar la aplicación:
   ```bash
   streamlit run app.py
   ```

## 📄 Notas

- El archivo `run_app.bat` es para uso local en Windows y puede requerir ajustes en las rutas de Python.
- Los datos de entrada deben seguir el formato de exportación de la plataforma de telemetría de John Deere (8h o 12h).
