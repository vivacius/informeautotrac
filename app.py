import os
import sys
import streamlit as st
import pandas as pd

# Asegurar que el directorio raíz esté en el PATH para importaciones en Streamlit Cloud
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.processing import process_8h_data, process_12h_data, calculate_global_stats
from modules.visualization import create_global_chart, create_alce_chart

# Configuración de Página Ultra Pro
st.set_page_config(
    page_title="IPSA Analytics Pro | Precision Ag",
    page_icon="logo_ipsa.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Premium y Animaciones ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background-color: #f8fafc;
    }

    /* Tarjetas de Métricas Premium */
    .metric-container {
        display: flex;
        justify-content: space-between;
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.05);
        border: 1px solid rgba(0,0,0,0.03);
        flex: 1;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    .card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 45px rgba(0,0,0,0.1);
    }
    
    .card-label {
        color: #94a3b8;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 0.75rem;
    }
    
    .card-value {
        color: #1e293b;
        font-size: 2.75rem;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 0.5rem;
    }

    .card-subtext {
        font-size: 0.875rem;
        color: #64748b;
    }

    .chart-container {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.03);
        margin-bottom: 2rem;
        border: 1px solid #f1f5f9;
    }

    .deere-green { color: #367c39; }

    /* Estilo del Sidebar - ALTO CONTRASTE MEJORADO */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }
    
    /* Todos los textos del sidebar en blanco */
    [data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }
    
    /* Títulos específicos */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* Labels de inputs */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown p {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
    }
    
    /* File uploader */
    [data-testid="stSidebar"] .stFileUploader label {
        color: #ffffff !important;
        font-size: 0.95rem !important;
    }
    
    [data-testid="stSidebar"] .stFileUploader section {
        background-color: #1e293b !important;
        border: 2px dashed #475569 !important;
        border-radius: 12px !important;
    }
    
    [data-testid="stSidebar"] .stFileUploader div[data-testid="stMarkdownContainer"] p {
        color: #cbd5e1 !important;
    }

    /* Radio buttons */
    [data-testid="stSidebar"] .stRadio label {
        color: #f1f5f9 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
        padding: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        background-color: #cbd5e1;
        border-radius: 12px;
        padding: 8px 24px;
        color: #334155;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #367c39;
        color: white;
    }
    
    /* Animaciones */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.8;
        }
    }
    
    .chart-container {
        animation: fadeInUp 0.6s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# --- Gestión de Estado (Session State) ---
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'global_stats' not in st.session_state:
    st.session_state.global_stats = None

# --- Sidebar ---
with st.sidebar:
    logo_path = os.path.join(os.path.dirname(__file__), "logo_ipsa.jpg")
    if os.path.exists(logo_path):
        st.image(logo_path, width=200)
    
    st.title("IPSA Analytics Pro")
    st.markdown("Analizador Diario de Uso de Autotrac")
    st.divider()
    
    shift_type = st.radio("Configuración de Turno", ["8 Horas", "12 Horas"], index=0)
    
    st.subheader("📁 Carga de Archivos")
    
    with st.expander("Subir Reportes", expanded=True):
        if shift_type == "8 Horas":
            f1 = st.file_uploader("Turno 6-2", type=["xlsx"])
            f2 = st.file_uploader("Turno 2-10", type=["xlsx"])
            f3 = st.file_uploader("Turno 10-6", type=["xlsx"])
            fa = st.file_uploader("Maestro Alces", type=["xlsx"])
            
            if st.button("🚀 PROCESAR ANALÍTICA", type="primary", use_container_width=True):
                if f1 and f2 and f3 and fa:
                    with st.spinner("Compilando datos..."):
                        data, err = process_8h_data(f1, f2, f3, fa)
                        if data is not None:
                            st.session_state.processed_data = data
                            st.session_state.global_stats = calculate_global_stats(data)
                        else:
                            st.error(err)
                else:
                    st.warning("⚠️ Faltan archivos por cargar.")

        else: # 12 Horas
            fam = st.file_uploader("Turno AM", type=["xlsx"])
            fpm = st.file_uploader("Turno PM", type=["xlsx"])
            fa = st.file_uploader("Maestro Alces", type=["xlsx"])
            
            if st.button("🚀 PROCESAR ANALÍTICA", type="primary", use_container_width=True):
                if fam and fpm and fa:
                    with st.spinner("Compilando datos..."):
                        data, err = process_12h_data(fam, fpm, fa)
                        if data is not None:
                            st.session_state.processed_data = data
                            st.session_state.global_stats = calculate_global_stats(data)
                        else:
                            st.error(err)
                else:
                    st.warning("⚠️ Faltan archivos por cargar.")

    if st.session_state.processed_data is not None:
        if st.sidebar.button("🗑️ Limpiar Datos"):
            st.session_state.processed_data = None
            st.session_state.global_stats = None
            st.rerun()

# --- Main Dashboard ---
if st.session_state.processed_data is not None:
    data = st.session_state.processed_data
    stats = st.session_state.global_stats
    
    st.markdown('<h1 style="font-size: 3.5rem; margin-bottom: 0px;">🚀 Dashboard de Desempeño</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 1.2rem; color: #64748b; margin-top: 0px; margin-bottom: 2rem;">Análisis de Productividad Operacional y Eficiencia AutoTrac</p>', unsafe_allow_html=True)
    
    # KPIs Row (Custom HTML Cards)
    total_machines = data['maquina'].nunique()
    avg_autotrac = stats['autotrac_activo_pct'].mean()
    total_h = stats['utilizacion_cosecha_h'].sum()
    
    st.markdown(f"""
    <div class="metric-container">
        <div class="card">
            <div class="card-label">Flota Activa</div>
            <div class="card-value deere-green">{total_machines}</div>
            <div class="card-subtext">Unidades Operativas</div>
        </div>
        <div class="card">
            <div class="card-label">AutoTrac™ Global</div>
            <div class="card-value" style="color: {'#27ae60' if avg_autotrac >= 0.9 else '#e74c3c'}">{avg_autotrac:.1%}</div>
            <div class="card-subtext">Meta de Desempeño: 90%</div>
        </div>
        <div class="card">
            <div class="card-label">Horas Totales</div>
            <div class="card-value">{total_h:,.0f}</div>
            <div class="card-subtext">Horas de Cosecha Acumuladas</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📊 Análisis Completo", "📄 Reporte Ejecutivo"])
    
    st_shift = '8h' if shift_type == "8 Horas" else '12h'
    
    with tab1:
        # Gráfico Global con Insights
        st.markdown("""
        <div style="background: white; padding: 2.5rem; border-radius: 20px; 
                    box-shadow: 0 10px 40px rgba(0,0,0,0.08); margin-bottom: 2rem;
                    border: 2px solid #e2e8f0;">
        """, unsafe_allow_html=True)
        
        st.markdown('<h2 style="color: #1e293b; margin-bottom: 1.5rem;">🌎 Rendimiento Global de la Flota</h2>', unsafe_allow_html=True)
        
        # Insight automático
        machines_above_target = (data.groupby('maquina')['autotrac_activo_pct'].mean() >= 0.9).sum()
        total_machines_unique = data['maquina'].nunique()
        machines_zero = (data.groupby('maquina')['autotrac_activo_pct'].mean() == 0).sum()
        
        col_insight1, col_insight2, col_insight3 = st.columns([2, 1, 1])
        with col_insight1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 1.2rem; border-radius: 12px; color: white; margin-bottom: 1rem;
                        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);">
                <strong style="font-size: 1.1rem;">💡 Insight:</strong><br>
                <span style="font-size: 1.3rem; font-weight: 700;">{machines_above_target}</span> de {total_machines_unique} máquinas 
                ({machines_above_target/total_machines_unique*100:.0f}%) superan la meta del 90%
            </div>
            """, unsafe_allow_html=True)
        with col_insight2:
            performance_emoji = "🎯" if avg_autotrac >= 0.9 else "⚠️"
            st.markdown(f"""
            <div style="background: {'#27ae60' if avg_autotrac >= 0.9 else '#e74c3c'}; 
                        padding: 1.2rem; border-radius: 12px; color: white; text-align: center;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{performance_emoji}</div>
                <div style="font-size: 0.85rem; font-weight: 600;">ESTADO GLOBAL</div>
            </div>
            """, unsafe_allow_html=True)
        with col_insight3:
            if machines_zero > 0:
                st.markdown(f"""
                <div style="background: #ff6b6b; 
                            padding: 1.2rem; border-radius: 12px; color: white; text-align: center;
                            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🚫</div>
                    <div style="font-size: 0.85rem; font-weight: 600;">{machines_zero} SIN USO</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: #4ecdc4; 
                            padding: 1.2rem; border-radius: 12px; color: white; text-align: center;
                            box-shadow: 0 4px 15px rgba(78, 205, 196, 0.4);">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">✅</div>
                    <div style="font-size: 0.85rem; font-weight: 600;">100% ACTIVAS</div>
                </div>
                """, unsafe_allow_html=True)
        
        fig_global = create_global_chart(data, stats, st_shift)
        st.plotly_chart(fig_global, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Separador elegante
        st.markdown("""
        <div style="height: 3px; background: linear-gradient(90deg, transparent, #367c39, transparent); 
                    margin: 3rem 0; border-radius: 2px;"></div>
        """, unsafe_allow_html=True)
        
        # Análisis por Zonas (Alces)
        st.markdown('<h2 style="color: #367c39; margin-bottom: 2rem; text-align: center;">📍 Análisis Detallado por Zona</h2>', unsafe_allow_html=True)
        
        # Filtrar y ordenar alces
        valid_alces = data['alce'].dropna().unique()
        alces = sorted([int(a) for a in valid_alces])
        
        # Grid de 2 columnas con insights por alce
        cols = st.columns(2)
        for i, alce in enumerate(alces):
            with cols[i % 2]:
                # Calcular métricas del alce
                df_alce = data[data['alce'] == alce]
                avg_alce = df_alce['autotrac_activo_pct'].mean()
                machines_in_alce = df_alce['maquina'].nunique()
                machines_zero_alce = (df_alce.groupby('maquina')['autotrac_activo_pct'].mean() == 0).sum()
                
                # Contenedor con borde prominente
                border_color = '#27ae60' if avg_alce >= 0.9 else '#e74c3c'
                st.markdown(f"""
                <div style="background: white; 
                            padding: 1.5rem; 
                            border-radius: 16px; 
                            margin-bottom: 2rem;
                            border: 3px solid {border_color};
                            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                            animation: fadeInUp 0.6s ease-out {i*0.1}s both;">
                    <div style="display: flex; justify-content: space-between; align-items: center; 
                                margin-bottom: 1rem; padding-bottom: 1rem; 
                                border-bottom: 2px solid #f1f5f9;">
                        <h3 style="margin: 0; color: #1e293b; font-size: 1.4rem;">
                            🏭 Alce {alce}
                        </h3>
                        <div style="background: {'#d4edda' if avg_alce >= 0.9 else '#f8d7da'}; 
                                    color: {'#155724' if avg_alce >= 0.9 else '#721c24'}; 
                                    padding: 0.6rem 1.2rem; border-radius: 25px; 
                                    font-weight: 700; font-size: 1rem;
                                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                            {avg_alce:.1%}
                        </div>
                    </div>
                    <div style="display: flex; gap: 1rem; margin-bottom: 1.5rem;">
                        <div style="background: #f8fafc; padding: 0.75rem; border-radius: 8px; flex: 1;
                                    border-left: 3px solid #3b82f6;">
                            <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 0.25rem;">MÁQUINAS</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #1e293b;">{machines_in_alce}</div>
                        </div>
                        <div style="background: #f8fafc; padding: 0.75rem; border-radius: 8px; flex: 1;
                                    border-left: 3px solid {'#ef4444' if machines_zero_alce > 0 else '#10b981'};">
                            <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 0.25rem;">SIN USO</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: {'#ef4444' if machines_zero_alce > 0 else '#10b981'};">{machines_zero_alce}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Gráfico dentro del contenedor
                fig_alce = create_alce_chart(data, alce, st_shift)
                st.plotly_chart(fig_alce, use_container_width=True)
                
                # Mini insight dentro del contenedor
                best_machine = df_alce.loc[df_alce['autotrac_activo_pct'].idxmax(), 'maquina'] if not df_alce.empty else 'N/A'
                best_value = df_alce['autotrac_activo_pct'].max() if not df_alce.empty else 0
                
                # Detectar si no se usó la tecnología
                if machines_zero_alce == machines_in_alce:
                    st.markdown(f"""
                    <div style="background: #fff3cd; padding: 1rem; border-radius: 8px; 
                                border-left: 4px solid #ffc107; margin-top: 0.5rem;">
                        <strong>⚠️ Alerta:</strong> La tecnología AutoTrac no fue utilizada en ninguna máquina de esta zona
                    </div>
                    """, unsafe_allow_html=True)
                elif machines_zero_alce > 0:
                    st.markdown(f"""
                    <div style="background: #fff3cd; padding: 1rem; border-radius: 8px; 
                                border-left: 4px solid #ffc107; margin-top: 0.5rem;">
                        <strong>⚠️ Atención:</strong> {machines_zero_alce} máquina(s) no utilizaron AutoTrac
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: #d1ecf1; padding: 1rem; border-radius: 8px; 
                                border-left: 4px solid #0c5460; margin-top: 0.5rem;">
                        <strong>⭐ Mejor desempeño:</strong> {best_machine} con {best_value:.1%}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Cerrar el contenedor
                st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("Generador de Reporte Institucional")
        st.info("Este módulo genera un informe profesional en formato PDF con todos los gráficos y métricas consolidadas.")
        
        from modules.reporting import generate_pdf
        
        if st.button("📑 GENERAR Y DESCARGAR PDF"):
            try:
                with st.spinner("Construyendo documento..."):
                    pdf_bytes = generate_pdf(data, stats, st_shift)
                    st.download_button(
                        label="📥 Click aquí para guardar PDF",
                        data=pdf_bytes,
                        file_name=f"Reporte_Productividad_{shift_type.replace(' ', '')}.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"Error al generar PDF: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("📊 Tabla de Datos Procesados"):
        st.dataframe(data, use_container_width=True)

else:
    # Pantalla de Bienvenida - Presentación
    st.markdown("""
    <div style="text-align: center; margin-top: 100px;">
        <h1 style="font-size: 3rem;">Bienvenido a Analizador Diario de Uso de Autotrac</h1>
        <p style="font-size: 1.25rem; color: #666;"> ¡Hola Nilson! Por favor cargue los archivos en la barra lateral para generar su análisis de uso de autotrac.</p>
        <img src="https://tecnicana.org/wp-content/uploads/2025/09/image-8.png" style="border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-top: 2rem; width: 60%;">
    </div>
    """, unsafe_allow_html=True)
