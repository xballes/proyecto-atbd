from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, avg, desc, when, max as Fmax, sum as Fsum
)


def main():
    spark = (
        SparkSession.builder
        .appName("EV_Analytics_2")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    input_path = "/data/ev/Electric_Vehicle_Population_Data.csv"

    print("\n======================", flush=True)
    print("Leyendo CSV desde HDFS:", input_path, flush=True)
    print("======================\n", flush=True)

    try:
        df_raw = (
            spark.read
            .option("header", "true")
            .option("inferSchema", "true")
            .csv(input_path)
        )

        print("\n--- Esquema original ---", flush=True)
        df_raw.printSchema()

        # Seleccionamos SOLO las columnas que necesitamos y les damos alias
        df = df_raw.select(
            col("Model Year").alias("model_year"),
            col("Make").alias("make"),
            col("Model").alias("model"),
            col("Electric Vehicle Type").alias("ev_type"),
            col("Clean Alternative Fuel Vehicle (CAFV) Eligibility").alias("cafv_eligibility"),
            col("Electric Range").alias("electric_range"),
            col("Base MSRP").alias("base_msrp"),
            col("County").alias("county"),
            col("City").alias("city"),
            col("State").alias("state"),
            col("Legislative District").alias("legislative_district"),
            col("Electric Utility").alias("electric_utility"),
        )

        print("\n--- Esquema reducido/renombrado ---", flush=True)
        df.printSchema()

        print("\nCalculando número total de registros...", flush=True)
        total = df.count()
        print("Registros totales:", total, flush=True)

        # ============================================================
        # filtrar años con pocos registros
        # ============================================================
        MIN_REG_POR_ANIO = 500

        registros_por_anio = (
            df.groupBy("model_year")
              .agg(count("*").alias("n_registros"))
              .orderBy("model_year")
        )

        print("\n--- Registros por año ---", flush=True)
        registros_por_anio.show(100, truncate=False)

        anios_validos = (
            registros_por_anio
            .where(col("n_registros") >= MIN_REG_POR_ANIO)
            .select("model_year")
        )

        print(f"\nAños válidos (>= {MIN_REG_POR_ANIO} registros):", flush=True)
        anios_validos.show(100, truncate=False)

        # df_filtrado SOLO contiene años con suficientes datos
        df_filtrado = df.join(anios_validos, on="model_year", how="inner").cache()
        print("\nRegistros tras filtrar años con pocos datos:", df_filtrado.count(), flush=True)
        # ============================================================

    except Exception as e:
        print("\n*** ERROR leyendo o preparando el DataFrame ***", flush=True)
        print(repr(e), flush=True)
        spark.stop()
        return

    base_out = "/results/ev"

    try:
        print(f"\nGuardando dataset limpio en {base_out}/dataset_limpio ...", flush=True)
        df.write.mode("overwrite").parquet(f"{base_out}/dataset_limpio")
    except Exception as e:
        print("\n*** ERROR guardando dataset_limpio ***", flush=True)
        print(repr(e), flush=True)

    # A partir de aquí:
    # - consultas que NO van por año usan df
    # - consultas por año usan df_filtrado

    # ============================================================
    # 1) Marcas líderes por estado y año  (usa df_filtrado)
    # ============================================================
    try:
        q1 = (
            df_filtrado.groupBy("state", "model_year", "make")
              .agg(count("*").alias("num_vehiculos"))
              .orderBy("state", "model_year", desc("num_vehiculos"))
        )
        print("\n--- Q1: Marcas líderes por estado y año ---", flush=True)
        q1.show(20, truncate=False)
        q1.write.mode("overwrite").parquet(f"{base_out}/q1_marcas_estado_anio")
    except Exception as e:
        print("\n*** ERROR en Q1 ***", flush=True)
        print(repr(e), flush=True)

    # ============================================================
    # 2) Evolución anual BEV vs PHEV  (usa df_filtrado)
    # ============================================================
    try:
        q2 = (
            df_filtrado.groupBy("model_year", "ev_type")
              .agg(count("*").alias("num_vehiculos"))
              .orderBy("model_year", "ev_type")
        )
        print("\n--- Q2: EV por año y tipo (BEV/PHEV) ---", flush=True)
        q2.show(20, truncate=False)
        q2.write.mode("overwrite").parquet(f"{base_out}/q2_bev_vs_phev")
    except Exception as e:
        print("\n*** ERROR en Q2 ***", flush=True)
        print(repr(e), flush=True)

    # ============================================================
    # 3) Autonomía media por año  (usa df_filtrado)
    # ============================================================
    try:
        q3 = (
            df_filtrado.groupBy("model_year")
              .agg(avg("electric_range").alias("autonomia_media"))
              .orderBy("model_year")
        )
        print("\n--- Q3: Autonomía media por año de modelo ---", flush=True)
        q3.show(20, truncate=False)
        q3.write.mode("overwrite").parquet(f"{base_out}/q3_autonomia_vs_anio")
    except Exception as e:
        print("\n*** ERROR en Q3 ***", flush=True)
        print(repr(e), flush=True)

    # ============================================================
    # 4) Condados con más EV  (no depende de año -> df)
    # ============================================================
    try:
        q4 = (
            df.groupBy("county")
              .agg(count("*").alias("num_vehiculos"))
              .orderBy(desc("num_vehiculos"))
        )
        print("\n--- Q4: Condados con más EV (top 20) ---", flush=True)
        q4.show(20, truncate=False)
        q4.write.mode("overwrite").parquet(f"{base_out}/q4_condados_top")
    except Exception as e:
        print("\n*** ERROR en Q4 ***", flush=True)
        print(repr(e), flush=True)

    # ============================================================
    # 5) Precio medio por marca y año  (usa df_filtrado)
    # ============================================================
    try:
        q5 = (
            df_filtrado.where(col("base_msrp").isNotNull())
              .groupBy("model_year", "make")
              .agg(avg("base_msrp").alias("precio_medio"))
              .orderBy("model_year", "make")
        )
        print("\n--- Q5: Precio medio por marca y año ---", flush=True)
        q5.show(20, truncate=False)
        q5.write.mode("overwrite").parquet(f"{base_out}/q5_precio_medio_marca_anio")
    except Exception as e:
        print("\n*** ERROR en Q5 ***", flush=True)
        print(repr(e), flush=True)

    # ============================================================
    # 6) Autonomía media por elegibilidad CAFV  (no por año -> df)
    # ============================================================
    try:
        q6 = (
            df.where(col("electric_range").isNotNull())
              .groupBy("cafv_eligibility")
              .agg(avg("electric_range").alias("autonomia_media"))
              .orderBy("cafv_eligibility")
        )
        print("\n--- Q6: Autonomía media por elegibilidad CAFV ---", flush=True)
        q6.show(20, truncate=False)
        q6.write.mode("overwrite").parquet(f"{base_out}/q6_cafv_vs_autonomia")
    except Exception as e:
        print("\n*** ERROR en Q6 ***", flush=True)
        print(repr(e), flush=True)

    # ============================================================
    # 7) Modelos por compañía eléctrica  (no por año -> df)
    # ============================================================
    try:
        q7 = (
            df.groupBy("make", "model", "electric_utility")
              .agg(count("*").alias("num_vehiculos"))
              .orderBy(desc("num_vehiculos"))
        )
        print("\n--- Q7: Modelos por compañía eléctrica ---", flush=True)
        q7.show(20, truncate=False)
        q7.write.mode("overwrite").parquet(f"{base_out}/q7_modelos_por_utility")
    except Exception as e:
        print("\n*** ERROR en Q7 ***", flush=True)
        print(repr(e), flush=True)

    # ============================================================
    # 8) EV por distrito legislativo  (no por año -> df)
    # ============================================================
    try:
        q8 = (
            df.groupBy("legislative_district")
              .agg(count("*").alias("num_vehiculos"))
              .orderBy("legislative_district")
        )
        print("\n--- Q8: EV por distrito legislativo ---", flush=True)
        q8.show(20, truncate=False)
        q8.write.mode("overwrite").parquet(f"{base_out}/q8_distrito_legislativo")
    except Exception as e:
        print("\n*** ERROR en Q8 ***", flush=True)
        print(repr(e), flush=True)

    # ============================================================
    # 9) Marcas con mayor autonomía media en los últimos 5 años
    #    (usa df_filtrado para evitar años raros)
    # ============================================================
    try:
        max_year = df_filtrado.agg(Fmax("model_year").alias("max_year")).collect()[0]["max_year"]
        if max_year is not None:
            last_year = max_year - 4  # últimos 5 años
            df_last = df_filtrado.where(col("model_year") >= last_year)
            q9 = (
                df_last.groupBy("make")
                       .agg(avg("electric_range").alias("autonomia_media"))
                       .orderBy(desc("autonomia_media"))
            )
            print(f"\n--- Q9: Marcas con mayor autonomía media ({last_year}-{max_year}) ---", flush=True)
            q9.show(20, truncate=False)
            q9.write.mode("overwrite").parquet(f"{base_out}/q9_marcas_rango_ult5")
        else:
            print("No se ha podido calcular el año máximo para la pregunta 9.", flush=True)
    except Exception as e:
        print("\n*** ERROR en Q9 ***", flush=True)
        print(repr(e), flush=True)

    # ============================================================
    # 10) Proporción de CAFV por año  (usa df_filtrado)
    # ============================================================
    try:
        df_cafv = df_filtrado.withColumn(
            "es_cafv",
            when(col("cafv_eligibility").contains("Eligible"), 1).otherwise(0)
        )

        q10 = (
            df_cafv.groupBy("model_year")
                   .agg(
                       count("*").alias("total"),
                       Fsum("es_cafv").alias("total_cafv")
                   )
                   .withColumn("proporcion_cafv", col("total_cafv") / col("total"))
                   .orderBy("model_year")
        )
        print("\n--- Q10: Proporción de CAFV por año (años filtrados) ---", flush=True)
        q10.show(20, truncate=False)
        q10.write.mode("overwrite").parquet(f"{base_out}/q10_proporcion_cafv_anio")
    except Exception as e:
        print("\n*** ERROR en Q10 ***", flush=True)
        print(repr(e), flush=True)

    print("\n*** Script EV_Analytics completado (o con errores detallados arriba) ***\n", flush=True)
    spark.stop()


if __name__ == "__main__":
    main()
