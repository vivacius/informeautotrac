
import plotly.graph_objects as go
import pandas as pd

def get_color_map(shift_type):
    if shift_type == '8h':
        return {
            "Turno 6-2": "#FFD700", # Gold
            "Turno 2-10": "#27ae60", # Green
            "Turno 10-6": "#7f8c8d" # Gray
        }
    else: # 12h
        return {
            "Turno 6am-6pm": "#f1c40f", # Sun Yellow
            "Turno 6pm-6am": "#2c3e50" # Dark Blue
        }

def create_global_chart(df, global_stats, shift_type):
    """
    Creates a Professional Combo Chart: Bars for Machine values, Scatter/Line for Global Average/Target.
    """
    
    # Prepare Data
    cols = ['maquina', 'turno', 'autotrac_activo_pct']
    df_subset = df[cols].copy()
    
    # Sort by Machine Name for consistency
    df_subset = df_subset.sort_values('maquina')
    
    machines = df_subset['maquina'].unique()
    
    fig = go.Figure()

    # Color Map
    colors = get_color_map(shift_type)
    
    # Add Bars for each Turno
    for turno, color in colors.items():
        subset = df_subset[df_subset['turno'] == turno]
        # Reindex to ensure all machines are present in the trace data
        # This prevents misalignment or missing bars in the group
        trace_data = subset.set_index('maquina').reindex(machines).reset_index().fillna(0)
        
        fig.add_trace(go.Bar(
            x=trace_data['maquina'],
            y=trace_data['autotrac_activo_pct'],
            name=turno,
            marker_color=color,
            text=trace_data['autotrac_activo_pct'],
            texttemplate='%{y:.0%}',
            textposition='auto'
        ))

    # Add Target Line (90%)
    fig.add_hline(y=0.9, line_dash="dash", line_color="#e74c3c", annotation_text="Meta 90%", annotation_position="top left")

    # Add Global Average Line
    mean_global = global_stats['autotrac_activo_pct'].mean()
    fig.add_hline(y=mean_global, line_dash="dot", line_color="#2980b9", annotation_text=f"Promedio: {mean_global:.1%}", annotation_position="top right")

    # Layout
    fig.update_layout(
        title="Desempeño Global por Máquina",
        yaxis_title="AutoTrac™ Activo (%)",
        yaxis_tickformat='.0%',
        yaxis_range=[0, 1.1],
        legend_title="Turno",
        barmode='group',
        template="plotly_white",
        hovermode="x unified"
    )

    return fig

def create_alce_chart(df, alce_name, shift_type):
    """
    Creates chart for a specific Alce.
    """
    df_filtered = df[df['alce'] == alce_name].copy()
    
    if df_filtered.empty:
        return None

    df_filtered = df_filtered.sort_values('maquina')

    fig = go.Figure()
    machines = df_filtered['maquina'].unique()
    colors = get_color_map(shift_type)

    for turno, color in colors.items():
        subset = df_filtered[df_filtered['turno'] == turno]
        # Ensure all machines have a slot even if value is 0
        trace_data = subset.set_index('maquina').reindex(machines).reset_index().fillna(0)
        
        fig.add_trace(go.Bar(
            x=trace_data['maquina'],
            y=trace_data['autotrac_activo_pct'],
            name=turno,
            marker_color=color,
            text=trace_data['autotrac_activo_pct'],
            texttemplate='%{y:.0%}',
            textposition='auto'
        ))
            
    fig.add_hline(y=0.9, line_dash="dash", line_color="#e74c3c", annotation_text="Meta", annotation_position="top left")

    fig.update_layout(
        title=f"Desempeño Alce {alce_name}",
        yaxis_title="AutoTrac™ (%)",
        yaxis_tickformat='.0%',
        yaxis_range=[0, 1.1],
        barmode='group',
        template="plotly_white"
    )

    return fig
