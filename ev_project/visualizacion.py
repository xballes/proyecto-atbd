import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Configuración de estilo
sns.set_theme(style="whitegrid")
plt.rcParams.update({'figure.max_open_warning': 0})

BASE_DIR = "../results/results/ev"
OUTPUT_DIR = "results/plots"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ===========================
# Helpers
# ===========================

def load_parquet(name: str) -> pd.DataFrame | None:
    """Carga un parquet desde BASE_DIR/name."""
    path = os.path.join(BASE_DIR, name)
    if not os.path.exists(path):
        print(f"Advertencia: No se encuentra {path}")
        return None
    return pd.read_parquet(path)


def save_plot(filename: str) -> None:
    """Guarda la figura actual en OUTPUT_DIR/filename."""
    path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(path, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Gráfico guardado: {path}")


# ===========================
# Q1
# ===========================

def plot_q1():
    df = load_parquet("q1_marcas_estado_anio")
    if df is None or df.empty:
        return

    # -----------------------------------------------------------
    # (A) MAPA COROPLÉTICO CON LABEL EN CADA ESTADO
    # -----------------------------------------------------------
    try:
        import plotly.express as px

        # Agrupar vehículos por estado
        df_state = (
            df.groupby("state")["num_vehiculos"]
              .sum()
              .reset_index()
              .rename(columns={"state": "State", "num_vehiculos": "Count"})
        )

        # Mapa base
        fig = px.choropleth(
            df_state,
            locations="State",
            locationmode="USA-states",
            color="Count",
            color_continuous_scale="greens",
            scope="usa",
            title="Distribución de Vehículos Eléctricos por Estado (Q1)",
        )

        # Label con el código del estado encima del mapa
        fig.add_scattergeo(
            locations=df_state["State"],
            locationmode="USA-states",
            text=df_state["State"],  # o df_state["Count"] si quieres el número
            mode="text",
            showlegend=False,
            textfont=dict(size=9, color="black"),
        )

        # Guardar mapa como imagen (si kaleido está instalado)
        img_path = os.path.join(OUTPUT_DIR, "q1_mapa_estados.png")
        html_path = os.path.join(OUTPUT_DIR, "q1_mapa_estados.html")
        try:
            fig.write_image(img_path)
            print(f"Mapa Q1 guardado como {img_path}")
        except Exception as e_img:
            print("No se pudo guardar q1_mapa_estados.png como imagen:", e_img)
            # Fallback: HTML interactivo
            fig.write_html(html_path)
            print(f"Mapa Q1 guardado como {html_path}")

    except Exception as e:
        print("ERROR generando mapa Q1:", e)

    # -----------------------------------------------------------
    # (B) GRÁFICAS DE MARCAS LÍDERES POR ESTADO (EJE Y AUTOESCALADO)
    # -----------------------------------------------------------

    # 1. Filtrar Top 3 estados por volumen total
    top_states = df.groupby("state")["num_vehiculos"].sum().nlargest(3).index
    df_top_states = df[df["state"].isin(top_states)].copy()

    # 2. Ranking Top 5 marcas por estado y año
    df_top_states["rank"] = df_top_states.groupby(
        ["state", "model_year"]
    )["num_vehiculos"].rank("dense", ascending=False)

    df_top = df_top_states[df_top_states["rank"] <= 5]

    # 3. Visualización (un eje Y distinto por estado → autoescala)
    g = sns.relplot(
        data=df_top,
        x="model_year",
        y="num_vehiculos",
        hue="make",
        col="state",
        kind="line",
        col_wrap=1,
        height=5,
        aspect=2.5,
        marker="o",
        palette="tab20",
        facet_kws={"sharey": False},  # eje Y independiente por estado
    )

    g.set_titles("Estado: {col_name}")
    g.set_axis_labels("Año del Modelo", "Nº Vehículos")

    # Mover la leyenda fuera
    sns.move_legend(g, "upper left", bbox_to_anchor=(1, 1))

    g.fig.suptitle("Top 5 Marcas por Año en los Estados con más EV", y=1.02)

    save_plot("q1_marcas_lideres.png")


# ===========================
# Q2
# ===========================

def plot_q2():
    df = load_parquet("q2_bev_vs_phev")
    if df is None or df.empty:
        return

    plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=df,
        x="model_year",
        y="num_vehiculos",
        hue="ev_type",
        marker="o",
    )
    plt.title("Evolución anual BEV vs PHEV")
    plt.ylabel("Nº Vehículos")
    plt.xlabel("Año")
    save_plot("q2_evolucion_bev_phev.png")

# ===========================
# Q3
# ===========================

def plot_q3():
    df = load_parquet("q3_autonomia_vs_anio")
    if df is None or df.empty:
        return
    print(df)
    plt.figure(figsize=(14, 7))

    # Líneas separadas por tipo de vehículo eléctrico
    sns.lineplot(
        data=df,
        x="model_year",
        y="autonomia_media",
        hue="ev_type",
        marker="o",
        linewidth=2.5,
    )

    plt.title("Q3 - Autonomía media por año y tipo de vehículo", fontsize=20)
    plt.xlabel("Año", fontsize=14)
    plt.ylabel("Autonomía media", fontsize=14)
    plt.grid(True, linestyle="--", alpha=0.4)

    plt.legend(
        title="Electric Vehicle Type",
        fontsize=11,
        title_fontsize=12,
        loc="upper left",
        frameon=True,
    )

    save_plot("q3_autonomia_vs_anio.png")

# ===========================
# Q4
# ===========================

def plot_q4():
    df = load_parquet("q4_condados_top")
    if df is None or df.empty:
        return

    df_top = df.sort_values("num_vehiculos", ascending=False).head(20)

    plt.figure(figsize=(12, 8))
    sns.barplot(data=df_top, x="num_vehiculos", y="county", palette="viridis")
    plt.title("Top 20 Condados con mayor densidad de EV")
    plt.xlabel("Nº Vehículos")
    plt.ylabel("Condado")
    save_plot("q4_condados_top.png")


# ===========================
# Q5
# ===========================

def plot_q5():
    df = load_parquet("q5_precio_medio_marca_anio")
    if df is None or df.empty:
        return

    plt.figure(figsize=(14, 8))

    # Eliminar outlier concreto (FISKER 2012) si distorsiona
    df = df[~((df["make"] == "FISKER") & (df["model_year"] == 2012))]

    top_makes = (
        df.groupby("make")["precio_medio"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .index
    )
    df_top = df[df["make"].isin(top_makes)]

    sns.lineplot(
        data=df_top,
        x="model_year",
        y="precio_medio",
        hue="make",
        marker="o",
    )
    plt.title("Precio medio por marca y año (Top 10 marcas más caras)")
    plt.ylabel("Precio Medio ($)")
    plt.xlabel("Año")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    save_plot("q5_precio_medio.png")


# ===========================
# Q6
# ===========================

def plot_q6():
    df = load_parquet("q6_cafv_vs_autonomia")
    if df is None or df.empty:
        return

    # Solo tenemos la media (autonomia_media), no los datos crudos.
    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=df,
        x="autonomia_media",
        y="cafv_eligibility",
        palette="coolwarm",
    )
    plt.title("Autonomía Media por Elegibilidad CAFV")
    plt.xlabel("Autonomía Media (millas)")
    plt.ylabel("Elegibilidad")
    save_plot("q6_cafv_autonomia_avg.png")


# ===========================
# Q7
# ===========================

def plot_q7():
    df = load_parquet("q7_modelos_por_utility")
    if df is None or df.empty:
        return

    # Mostramos las top 5 utilities y dentro de cada una, sus 5 modelos con más vehículos
    top_utilities = (
        df.groupby("electric_utility")["num_vehiculos"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .index
    )
    df_filtered = df[df["electric_utility"].isin(top_utilities)]

    df_final = (
        df_filtered.groupby("electric_utility")
        .apply(lambda x: x.nlargest(5, "num_vehiculos"))
        .reset_index(drop=True)
    )

    plt.figure(figsize=(14, 8))

    # Acortamos nombres largos de utility para la leyenda
    df_final["utility_short"] = df_final["electric_utility"].apply(
        lambda x: x[:50] + "..." if len(x) > 50 else x
    )

    sns.barplot(
        data=df_final,
        x="num_vehiculos",
        y="model",
        hue="utility_short",
        dodge=False,
    )
    plt.title("Modelos destacados por Compañía Eléctrica (Top 5 Utilities)")
    plt.xlabel("Nº Vehículos")
    plt.ylabel("Modelo")
    plt.legend(title="Utility", bbox_to_anchor=(1.05, 1), loc="upper left")
    save_plot("q7_modelos_utility.png")


# ===========================
# Q8
# ===========================

def plot_q8():
    df = load_parquet("q8_distrito_legislativo")
    if df is None or df.empty:
        return

    df["legislative_district"] = df["legislative_district"].fillna("Not Washington").astype(str)

    # Intentamos ordenar numéricamente si es posible
    try:
        df["sort_val"] = pd.to_numeric(df["legislative_district"], errors="coerce")
        df = df.sort_values("sort_val")

        def format_district(x):
            try:
                return str(int(float(x)))
            except Exception:
                return str(x)

        df["legislative_district"] = df["legislative_district"].apply(format_district)
    except Exception:
        df = df.sort_values("legislative_district")

    plt.figure(figsize=(10, 12))
    sns.barplot(
        data=df,
        x="num_vehiculos",
        y="legislative_district",
        color="skyblue",
    )
    plt.title("Adopción de EV por Distrito Legislativo de Washington (WA)")
    plt.xlabel("Nº Vehículos")
    plt.ylabel("Distrito")
    save_plot("q8_distrito_legislativo.png")


# ===========================
# Q9
# ===========================

def plot_q9():
    df = load_parquet("q9_marcas_rango_ult5")
    if df is None or df.empty:
        return

    df_top = df.sort_values("autonomia_media", ascending=False).head(10)

    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=df_top,
        x="autonomia_media",
        y="make",
        palette="magma",
    )
    plt.title("Marcas con mayor autonomía media (Últimos 5 años)")
    plt.xlabel("Autonomía Media (millas)")
    plt.ylabel("Marca")
    save_plot("q9_top_autonomia.png")


# ===========================
# Q10
# ===========================

def plot_q10():
    df = load_parquet("q10_proporcion_cafv_anio")
    if df is None or df.empty:
        return

    # Filtramos años con suficientes registros
    df = df[df["total"] >= 500]

    # Limitamos a un rango razonable
    df = df[(df["model_year"] >= 2011) & (df["model_year"] <= 2023)]

    plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=df,
        x="model_year",
        y="proporcion_cafv",
        marker="o",
        color="green",
    )
    plt.title("Evolución de la proporción de vehículos elegibles CAFV")
    plt.ylabel("Proporción (0-1)")
    plt.xlabel("Año")
    plt.ylim(0, 1.1)
    save_plot("q10_proporcion_cafv.png")


# ===========================
# Main
# ===========================

def main():
    print("Iniciando generación de gráficos...")
    plot_q1()
    plot_q2()
    plot_q3()
    plot_q4()
    plot_q5()
    plot_q6()
    plot_q7()
    plot_q8()
    plot_q9()
    plot_q10()
    print(f"Generación completada. Gráficos en {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
