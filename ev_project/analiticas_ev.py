from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, avg, desc, when, max as Fmax, sum as Fsum
)

def main():
    spark = SparkSession.builder.appName("EV_Analytics").getOrCreate()

    # 1. Leer dataset desde HDFS
    df_raw = spark.read.csv(
        "/data/ev/Electric_Vehicle_Population_Data.csv",
        header=True,
        inferSchema=True
    )

    # Renombrar columnas
    df = (
        df_raw
        .withColumnRenamed("Model Year", "model_year")
        .withColumnRenamed("Make", "make")
        .withColumnRenamed("Model", "model")
        .withColumnRenamed("Electric Vehicle Type", "ev_type")
        .withColumnRenamed("Electric Range", "electric_range")
        .withColumnRenamed("Base MSRP", "base_msrp")
        .withColumnRenamed("CAFV Eligibility", "cafv_eligibility")
        .withColumnRenamed("County", "county")
        .withColumnRenamed("City", "city")
        .withColumnRenamed("State", "state")
        .withColumnRenamed("Legislative District", "legislative_district")
        .withColumnRenamed("Electric Utility", "electric_utility")
    ).cache()

    print("Registros totales:", df.count())

    # Carpeta base de resultados en HDFS
    base_out = "/results/ev"
    df.write.mode("overwrite").parquet(f"{base_out}/dataset_limpio")

    # 1) Marcas líderes por estado y año
    q1 = (
        df.groupBy("state", "model_year", "make")
          .agg(count("*").alias("num_vehiculos"))
          .orderBy("state", "model_year", desc("num_vehiculos"))
    )
    q1.show(20, truncate=False)
    q1.write.mode("overwrite").parquet(f"{base_out}/q1_marcas_estado_anio")

    # 2) Evolución anual BEV vs PHEV
    q2 = (
        df.groupBy("model_year", "ev_type")
          .agg(count("*").alias("num_vehiculos"))
          .orderBy("model_year", "ev_type")
    )
    q2.show(20, truncate=False)
    q2.write.mode("overwrite").parquet(f"{base_out}/q2_bev_vs_phev")

    # 3) Correlación autonomía vs año de fabricación (rango medio por año)
    q3 = (
        df.groupBy("model_year")
          .agg(avg("electric_range").alias("autonomia_media"))
          .orderBy("model_year")
    )
    q3.show(20, truncate=False)
    q3.write.mode("overwrite").parquet(f"{base_out}/q3_autonomia_vs_anio")

    # 4) Condados con mayor número de vehículos eléctricos (top 20)
    q4 = (
        df.groupBy("county")
          .agg(count("*").alias("num_vehiculos"))
          .orderBy(desc("num_vehiculos"))
    )
    q4.show(20, truncate=False)
    q4.write.mode("overwrite").parquet(f"{base_out}/q4_condados_top")

    # 5) Precio medio por marca y año
    q5 = (
        df.where(col("base_msrp").isNotNull())
          .groupBy("model_year", "make")
          .agg(avg("base_msrp").alias("precio_medio"))
          .orderBy("model_year", "make")
    )
    q5.show(20, truncate=False)
    q5.write.mode("overwrite").parquet(f"{base_out}/q5_precio_medio_marca_anio")

    # 6) Relación CAFV vs autonomía (autonomía media por elegibilidad)
    q6 = (
        df.where(col("electric_range").isNotNull())
          .groupBy("cafv_eligibility")
          .agg(avg("electric_range").alias("autonomia_media"))
          .orderBy("cafv_eligibility")
    )
    q6.show(20, truncate=False)
    q6.write.mode("overwrite").parquet(f"{base_out}/q6_cafv_vs_autonomia")

    # 7) Modelos por compañía eléctrica
    q7 = (
        df.groupBy("make", "model", "electric_utility")
          .agg(count("*").alias("num_vehiculos"))
          .orderBy(desc("num_vehiculos"))
    )
    q7.show(20, truncate=False)
    q7.write.mode("overwrite").parquet(f"{base_out}/q7_modelos_por_utility")

    # 8) Adopción por distrito legislativo
    q8 = (
        df.groupBy("legislative_district")
          .agg(count("*").alias("num_vehiculos"))
          .orderBy("legislative_district")
    )
    q8.show(20, truncate=False)
    q8.write.mode("overwrite").parquet(f"{base_out}/q8_distrito_legislativo")

    # 9) Marcas con mayor autonomía media en los últimos 5 años
    max_year = df.agg(Fmax("model_year").alias("max_year")).collect()[0]["max_year"]
    last_year = max_year - 5 if max_year else None

    if last_year is not None:
        df_last = df.where(col("model_year") >= last_year)
        q9 = (
            df_last.groupBy("make")
                   .agg(avg("electric_range").alias("autonomia_media"))
                   .orderBy(desc("autonomia_media"))
        )
        q9.show(20, truncate=False)
        q9.write.mode("overwrite").parquet(f"{base_out}/q9_marcas_rango_ult5")
    else:
        print("No se ha podido calcular el año máximo para la pregunta 9.")

    # 10) Proporción de vehículos elegibles CAFV por año
    df_cafv = df.withColumn(
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
    q10.show(20, truncate=False)
    q10.write.mode("overwrite").parquet(f"{base_out}/q10_proporcion_cafv_anio")

    spark.stop()


if __name__ == "__main__":
    main()
