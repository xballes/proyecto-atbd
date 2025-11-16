from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count

def main():
    # Crear la sesión de Spark
    spark = (
        SparkSession.builder
        .appName("EV_Test_Script")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    # Ruta del CSV en HDFS 
    input_path = "/data/ev/Electric_Vehicle_Population_Data.csv"

    print("\n======================")
    print("Leyendo CSV desde HDFS:", input_path)
    print("======================\n")

    # Leer el CSV con cabecera e inferencia de tipos
    df_raw = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .csv(input_path)
    )

    print("\n--- Esquema original ---")
    df_raw.printSchema()

    # Seleccionar solo algunas columnas sencillas y renombrarlas
    df = df_raw.select(
        col("Model Year").alias("model_year"),
        col("Make").alias("make"),
        col("State").alias("state")
    )

    print("\n--- Primeras filas del dataframe reducido ---")
    df.show(20, truncate=False)

    # Agrupación de prueba: nº de vehículos por estado y año
    agg = (
        df.groupBy("state", "model_year")
          .agg(count("*").alias("num_vehiculos"))
          .orderBy("state", "model_year")
    )

    print("\n--- Agregación de prueba (state, model_year, num_vehiculos) ---")
    agg.show(50, truncate=False)

    # Escribir resultados en HDFS
    base_out = "/results/ev_test"

    print(f"\n--- Escribiendo resultados en HDFS bajo {base_out} ---")

    df.write.mode("overwrite").parquet(f"{base_out}/sample_df")
    agg.write.mode("overwrite").parquet(f"{base_out}/agg_state_year")

    print("\n*** Script de prueba completado correctamente ***\n")

    spark.stop()


if __name__ == "__main__":
    main()
