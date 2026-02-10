
from fpdf import FPDF
import matplotlib.pyplot as plt
import pandas as pd
import io
import tempfile
import os
import datetime

class ProfessionalPDF(FPDF):
    def header(self):
        # Logo placeholder (if file existed, we'd add it)
        # self.image('logo.png', 10, 8, 33)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, 'Informe de Productividad - Análisis AutoTrac(TM)', 0, 1, 'R')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(54, 124, 57) # Deere Green
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)
        self.set_draw_color(54, 124, 57)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.set_text_color(0)
        self.multi_cell(0, 6, body)
        self.ln()

def create_static_chart(df, title, shift_type):
    """
    Generic function to create matplotlib chart for PDF.
    """
    colors_8h = {"Turno 6-2": "#FFD700", "Turno 2-10": "#228B22", "Turno 10-6": "#808080"}
    colors_12h = {"Turno 6am-6pm": "#f1c40f", "Turno 6pm-6am": "#2c3e50"}
    colors = colors_8h if shift_type == '8h' else colors_12h
    
    # Sort
    df = df.sort_values('maquina')
    
    machines = df['maquina'].unique()
    turnos = [t for t in colors.keys() if t in df['turno'].unique()]
    
    import numpy as np
    x = np.arange(len(machines))
    width = 0.8 / len(turnos) if len(turnos) > 0 else 0.4
    
    # Ajustar tamaño según cantidad de máquinas
    fig_width = min(12, max(8, len(machines) * 0.6))
    fig, ax = plt.subplots(figsize=(fig_width, 5))
    
    for i, turno in enumerate(turnos):
        subset = df[df['turno'] == turno]
        # Align
        subset = subset.set_index('maquina').reindex(machines, fill_value=0).reset_index()
        offset = width * i
        
        # Convertir a porcentaje para visualización
        values_pct = subset['autotrac_activo_pct'] * 100
        
        rects = ax.bar(x + offset, subset['autotrac_activo_pct'], width, label=turno, color=colors.get(turno, 'blue'))
        
        # Etiquetas con formato correcto
        for j, (rect, val) in enumerate(zip(rects, values_pct)):
            height = rect.get_height()
            if height > 0:
                ax.text(rect.get_x() + rect.get_width()/2., height,
                       f'{val:.0f}%',
                       ha='center', va='bottom', fontsize=8, fontweight='bold')
        
    ax.set_ylabel('AutoTrac (% de Uso)', fontsize=11, fontweight='bold')
    ax.set_title(title, pad=20, fontsize=13, fontweight='bold')
    ax.set_xticks(x + width * (len(turnos) - 1) / 2)
    ax.set_xticklabels(machines, rotation=45, ha='right', fontsize=9)
    ax.legend(loc='upper right', framealpha=0.9)
    ax.axhline(y=0.9, color='r', linestyle='--', linewidth=2, label='Meta 90%')
    ax.set_ylim(0, 1.05)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y*100:.0f}%'))
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=200, bbox_inches='tight')
    plt.close(fig)
    return img_buf

def generate_pdf(processed_data, global_stats, shift_type):
    pdf = ProfessionalPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- Cover Page ---
    pdf.add_page()
    pdf.ln(60)
    pdf.set_font('Arial', 'B', 24)
    pdf.set_text_color(54, 124, 57)
    pdf.cell(0, 20, 'Informe de Productividad', 0, 1, 'C')
    
    pdf.set_font('Arial', '', 14)
    pdf.set_text_color(80)
    pdf.cell(0, 10, 'Análisis de Uso de AutoTrac(TM)', 0, 1, 'C')
    
    pdf.ln(20)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Fecha: {datetime.date.today()}', 0, 1, 'C')
    pdf.ln(50)
    
    # --- Executive Summary ---
    pdf.add_page()
    pdf.chapter_title('Resumen Ejecutivo')
    
    avg_autotrac = global_stats['autotrac_activo_pct'].mean()
    total_machines = processed_data['maquina'].nunique()
    total_hours = global_stats['utilizacion_cosecha_h'].sum()
    
    # Calcular máquinas sin uso
    machines_zero = (processed_data.groupby('maquina')['autotrac_activo_pct'].mean() == 0).sum()
    machines_above_target = (processed_data.groupby('maquina')['autotrac_activo_pct'].mean() >= 0.9).sum()
    
    summary_text = (
        f"Este informe presenta un analisis detallado del uso de la tecnologia AutoTrac(TM) en la flota de maquinaria. "
        f"Se han monitoreado un total de {total_machines} maquinas, acumulando {total_hours:,.1f} horas de operacion.\n\n"
        f"El promedio global de uso de AutoTrac(TM) es del {avg_autotrac:.1%}. "
        f"La meta establecida es del 90%.\n\n"
        f"HALLAZGOS CLAVE:\n"
        f"- {machines_above_target} maquinas ({machines_above_target/total_machines*100:.0f}%) superan la meta del 90%\n"
    )
    
    if machines_zero > 0:
        summary_text += f"- ALERTA: {machines_zero} maquinas ({machines_zero/total_machines*100:.0f}%) NO utilizaron la tecnologia AutoTrac(TM)\n"
    else:
        summary_text += f"- Excelente: El 100% de las maquinas utilizaron la tecnologia AutoTrac(TM)\n"
    
    pdf.chapter_body(summary_text)
    
    # Global Chart
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Visión Global de la Flota', 0, 1)
    
    # Prepare global data for plotting - EXCLUDE 'Global' from machines
    cols = ['maquina', 'turno', 'autotrac_activo_pct']
    df_for_chart = processed_data[processed_data['maquina'] != 'Global'][cols].copy()
    
    img_global = create_static_chart(df_for_chart, 'Desempeño Global por Máquina', shift_type)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        tmp.write(img_global.getvalue())
        tmp_path = tmp.name
    pdf.image(tmp_path, x=10, w=190)
    os.unlink(tmp_path)
    
    # --- Detail Pages ---
    # Filtrar nulos y ordenar numéricamente
    valid_alces = processed_data['alce'].dropna().unique()
    unique_alces = sorted([int(a) for a in valid_alces])
    
    for i, alce in enumerate(unique_alces):
        pdf.add_page()
        pdf.chapter_title(f'Alce: {alce}')
        
        # Filtrar datos del alce
        df_alce = processed_data[processed_data['alce'] == alce]
        
        # Calcular métricas para insights
        avg_alce = df_alce['autotrac_activo_pct'].mean()
        max_machine = df_alce.loc[df_alce['autotrac_activo_pct'].idxmax(), 'maquina'] if not df_alce.empty else 'N/A'
        max_value = df_alce['autotrac_activo_pct'].max() if not df_alce.empty else 0
        min_machine = df_alce.loc[df_alce['autotrac_activo_pct'].idxmin(), 'maquina'] if not df_alce.empty else 'N/A'
        min_value = df_alce['autotrac_activo_pct'].min() if not df_alce.empty else 0
        machines_count = df_alce['maquina'].nunique()
        above_target = (df_alce['autotrac_activo_pct'] >= 0.9).sum()
        machines_zero_alce = (df_alce.groupby('maquina')['autotrac_activo_pct'].mean() == 0).sum()
        
        # Texto de análisis
        pdf.set_font('Arial', '', 11)
        
        if machines_zero_alce == machines_count:
            analysis_text = (
                f"ALERTA CRITICA: El alce {alce} cuenta con {machines_count} maquinas, "
                f"pero NINGUNA utilizo la tecnologia AutoTrac(TM) durante el periodo analizado. "
                f"Se requiere investigacion inmediata sobre las causas de esta situacion."
            )
        elif machines_zero_alce > 0:
            analysis_text = (
                f"El alce {alce} cuenta con {machines_count} maquinas en operacion. "
                f"El promedio de uso de AutoTrac es del {avg_alce:.1%}. "
                f"{above_target} maquinas superan la meta del 90%. "
                f"ATENCION: {machines_zero_alce} maquina(s) NO utilizaron AutoTrac(TM). "
                f"La maquina con mejor desempeno es {max_machine} ({max_value:.1%})."
            )
        else:
            analysis_text = (
                f"El alce {alce} cuenta con {machines_count} maquinas en operacion. "
                f"El promedio de uso de AutoTrac es del {avg_alce:.1%}. "
                f"{above_target} maquinas superan la meta del 90%. "
                f"La maquina con mejor desempeno es {max_machine} ({max_value:.1%}), "
                f"mientras que {min_machine} presenta el menor uso ({min_value:.1%})."
            )
        
        pdf.multi_cell(0, 6, analysis_text)
        pdf.ln(5)
        
        # Gráfico
        img_alce = create_static_chart(df_alce, f'Rendimiento Detallado - Alce {alce}', shift_type)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            tmp.write(img_alce.getvalue())
            tmp_path = tmp.name
        
        pdf.image(tmp_path, x=10, w=190)
        os.unlink(tmp_path)
        
        # Recomendaciones
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 11)
        pdf.set_text_color(54, 124, 57)
        pdf.cell(0, 8, 'Recomendaciones:', 0, 1)
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(0)
        
        if avg_alce < 0.9:
            recommendation = f"- Reforzar capacitacion en el uso de AutoTrac para operadores del alce {alce}.\n- Revisar configuracion de equipos con bajo rendimiento."
        else:
            recommendation = f"- Mantener las practicas actuales que han resultado en un excelente desempeno.\n- Compartir mejores practicas con otros alces."
        
        pdf.multi_cell(0, 5, recommendation)
        
        # Espacio para notas
        pdf.ln(5)
        pdf.set_draw_color(200)
        pdf.set_fill_color(250, 250, 250)
        pdf.rect(10, pdf.get_y(), 190, 25, 'F')
        pdf.set_xy(15, pdf.get_y() + 3)
        pdf.set_font('Arial', 'I', 9)
        pdf.set_text_color(120)
        pdf.multi_cell(180, 4, "Notas adicionales:\n_____________________________________________________________________________\n_____________________________________________________________________________")

    # Return as bytes
    output = pdf.output(dest='S')
    if isinstance(output, str):
        return output.encode('latin-1')
    return output
