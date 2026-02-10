
import pandas as pd
import numpy as np
import io
import streamlit as st

@st.cache_data
def clean_column_names(df):
    """
    Simulates janitor.clean_names() from R.
    Converts column names to snake_case.
    """
    # Use regex=False for literal replacement of parenthesis
    df.columns = (df.columns.str.lower()
                  .str.replace(' ', '_', regex=False)
                  .str.replace('-', '_', regex=False)
                  .str.replace('.', '_', regex=False)
                  .str.replace('(', '', regex=False)
                  .str.replace(')', '', regex=False))
    return df

@st.cache_data
def process_8h_data(file_6_2, file_2_10, file_10_6, file_alces):
    """
    Processes the 3 files for 8-hour shifts + Alces file.
    """
    
    # Read files
    try:
        df_6_2 = pd.read_excel(file_6_2)
        df_2_10 = pd.read_excel(file_2_10)
        df_10_6 = pd.read_excel(file_10_6)
        df_alces = pd.read_excel(file_alces)
    except Exception as e:
        return None, f"Error reading files: {e}"

    # Clean names
    df_6_2 = clean_column_names(df_6_2)
    df_2_10 = clean_column_names(df_2_10)
    df_10_6 = clean_column_names(df_10_6)
    df_alces = clean_column_names(df_alces)

    def rename_cols(df):
        cols = df.columns
        map_dict = {}
        found_targets = []

        for col in cols:
            # Machine (Más flexible con nombres de columna comunes)
            if any(x in col for x in ['maquina', 'máquina', 'equipo', 'unidad', 'machine']) and 'maquina' not in found_targets:
                 map_dict[col] = 'maquina'
                 found_targets.append('maquina')
                 continue
            
            # AutoTrac H (Buscar específicamente 'h' como unidad, no como parte de palabra)
            if 'autotrac' in col and 'activo' in col and (col.endswith('_h') or '_h_' in col or '(h)' in col) and 'autotrac_activo_h' not in found_targets:
                 map_dict[col] = 'autotrac_activo_h'
                 found_targets.append('autotrac_activo_h')
                 continue

            # Utilizacion Cosecha H (Evitar que el 'h' de 'cosecha' cause falso positivo con %)
            if 'utilizac' in col and 'cosecha' in col and (col.endswith('_h') or '_h_' in col or '(h)' in col) and 'utilizacion_cosecha_h' not in found_targets:
                 map_dict[col] = 'utilizacion_cosecha_h'
                 found_targets.append('utilizacion_cosecha_h')
                 continue

        return df.rename(columns=map_dict)

    df_6_2 = rename_cols(df_6_2)
    df_2_10 = rename_cols(df_2_10)
    df_10_6 = rename_cols(df_10_6)
    
    # Add 'turno' column
    df_6_2['turno'] = "Turno 6-2"
    df_2_10['turno'] = "Turno 2-10"
    df_10_6['turno'] = "Turno 10-6"

    # Combine
    df_completo = pd.concat([df_6_2, df_2_10, df_10_6], ignore_index=True)
    df_completo = df_completo.loc[:, ~df_completo.columns.duplicated()]

    # Ensure numeric types
    df_completo['autotrac_activo_h'] = pd.to_numeric(df_completo['autotrac_activo_h'], errors='coerce').fillna(0)
    df_completo['utilizacion_cosecha_h'] = pd.to_numeric(df_completo['utilizacion_cosecha_h'], errors='coerce').fillna(0)

    # --- AGREGACIÓN ---
    df_completo = df_completo.groupby(['maquina', 'turno']).agg({
        'autotrac_activo_h': 'sum',
        'utilizacion_cosecha_h': 'sum'
    }).reset_index()

    # Calculate percentage over aggregated hours
    df_completo['autotrac_activo_pct'] = df_completo.apply(
        lambda row: row['autotrac_activo_h'] / row['utilizacion_cosecha_h'] if row['utilizacion_cosecha_h'] > 0 else 0, axis=1
    )

    # Replicar lógica de R: si >1 o NA, entonces NA
    df_completo.loc[df_completo['autotrac_activo_pct'] > 1, 'autotrac_activo_pct'] = np.nan

    # Merge with Alces
    cols_alces = df_alces.columns
    alce_map = {}
    for col in cols_alces:
        if any(x in col for x in ['maquina', 'máquina', 'equipo', 'unidad']):
            alce_map[col] = 'maquina'
        if 'alce' in col:
            alce_map[col] = 'alce'
    df_alces = df_alces.rename(columns=alce_map)
    
    df_completo['maquina'] = df_completo['maquina'].astype(str).str.strip()
    df_alces['maquina'] = df_alces['maquina'].astype(str).str.strip()

    df_merged = pd.merge(df_completo, df_alces[['maquina', 'alce']], on='maquina', how='left')
    df_merged['alce'] = pd.to_numeric(df_merged['alce'], errors='coerce')

    return df_merged, None

@st.cache_data
def process_12h_data(file_am, file_pm, file_alces):
    """
    Processes the 2 files for 12-hour shifts.
    """
    try:
        df_am = pd.read_excel(file_am)
        df_pm = pd.read_excel(file_pm)
        df_alces = pd.read_excel(file_alces)
    except Exception as e:
         return None, f"Error reading files: {e}"

    df_am = clean_column_names(df_am)
    df_pm = clean_column_names(df_pm)
    df_alces = clean_column_names(df_alces)

    def rename_cols(df):
        cols = df.columns
        map_dict = {}
        found_targets = []
        
        for col in cols:
            if any(x in col for x in ['maquina', 'máquina', 'equipo', 'unidad', 'machine']) and 'maquina' not in found_targets:
                 map_dict[col] = 'maquina'
                 found_targets.append('maquina')
                 continue
            
            if 'autotrac' in col and 'activo' in col and (col.endswith('_h') or '_h_' in col or '(h)' in col) and 'autotrac_activo_h' not in found_targets:
                 map_dict[col] = 'autotrac_activo_h'
                 found_targets.append('autotrac_activo_h')
                 continue
                 
            if 'utilizac' in col and 'cosecha' in col and (col.endswith('_h') or '_h_' in col or '(h)' in col) and 'utilizacion_cosecha_h' not in found_targets:
                 map_dict[col] = 'utilizacion_cosecha_h'
                 found_targets.append('utilizacion_cosecha_h')
                 continue
                 
        return df.rename(columns=map_dict)

    df_am = rename_cols(df_am)
    df_pm = rename_cols(df_pm)

    df_am['turno'] = "Turno 6am-6pm"
    df_pm['turno'] = "Turno 6pm-6am"

    df_completo = pd.concat([df_am, df_pm], ignore_index=True)
    df_completo = df_completo.loc[:, ~df_completo.columns.duplicated()]

    df_completo['autotrac_activo_h'] = pd.to_numeric(df_completo['autotrac_activo_h'], errors='coerce').fillna(0)
    df_completo['utilizacion_cosecha_h'] = pd.to_numeric(df_completo['utilizacion_cosecha_h'], errors='coerce').fillna(0)

    # AGREGACIÓN
    df_completo = df_completo.groupby(['maquina', 'turno']).agg({
        'autotrac_activo_h': 'sum',
        'utilizacion_cosecha_h': 'sum'
    }).reset_index()

    df_completo['autotrac_activo_pct'] = df_completo.apply(
        lambda row: row['autotrac_activo_h'] / row['utilizacion_cosecha_h'] if row['utilizacion_cosecha_h'] > 0 else 0, axis=1
    )
    
    df_completo.loc[df_completo['autotrac_activo_pct'] > 1, 'autotrac_activo_pct'] = np.nan

    # Alces merge
    cols_alces = df_alces.columns
    alce_map = {}
    for col in cols_alces:
        if any(x in col for x in ['maquina', 'máquina', 'equipo', 'unidad']):
            alce_map[col] = 'maquina'
        if 'alce' in col:
            alce_map[col] = 'alce'
    df_alces = df_alces.rename(columns=alce_map)

    df_completo['maquina'] = df_completo['maquina'].astype(str).str.strip()
    df_alces['maquina'] = df_alces['maquina'].astype(str).str.strip()

    df_merged = pd.merge(df_completo, df_alces[['maquina', 'alce']], on='maquina', how='left')
    df_merged['alce'] = pd.to_numeric(df_merged['alce'], errors='coerce')

    return df_merged, None

def calculate_global_stats(df):
    """
    Calculates global stats per shift.
    """
    global_stats = df.groupby('turno').agg({
        'autotrac_activo_h': 'sum',
        'utilizacion_cosecha_h': 'sum'
    }).reset_index()
    
    global_stats['autotrac_activo_pct'] = global_stats.apply(
        lambda row: row['autotrac_activo_h'] / row['utilizacion_cosecha_h'] if row['utilizacion_cosecha_h'] > 0 else 0,
        axis=1
    )
    global_stats['maquina'] = 'Global'
    global_stats['alce'] = 'Global'
    
    return global_stats
