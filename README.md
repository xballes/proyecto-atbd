# Proyecto ATBD – Análisis de Vehículos Eléctricos con Spark y Hadoop (Docker)

## Descripción general

Este proyecto forma parte de la asignatura **Arquitecturas y Tecnologías Big Data (ATBD)** del Máster en Big Data.  
El objetivo es desplegar un **clúster Hadoop + YARN + Spark** sobre Docker y realizar un análisis distribuido del dataset:

> [Electric Vehicle Population Data – Kaggle](https://www.kaggle.com/datasets/ratikkakkar/electric-vehicle-population-data/code)

El análisis se centra en la **adopción de vehículos eléctricos (EV)** en EE. UU., estudiando su evolución, marcas líderes y características técnicas.

---

## Estructura del proyecto


---

## Infraestructura desplegada

El clúster Docker está compuesto por **5 contenedores**:

| Rol | Hostname | Servicios principales |
|------|-----------|----------------------|
| Master | `master` | NameNode, ResourceManager, HistoryServer |
| Worker 1 | `worker1` | DataNode, NodeManager |
| Worker 2 | `worker2` | DataNode, NodeManager |
| Worker 3 | `worker3` | DataNode, NodeManager |
| Cliente | `client` | Herramientas (`hdfs`, `yarn`, `spark-submit`) |

### Versiones utilizadas

- **Hadoop:** 3.3.1  
- **Spark:** 3.5.0  
- **Java:** Eclipse Temurin 11  
- **Python:** 3.8+  

---

### Puesta en marcha del clúster
Construir y levantar el clúster
```bash
docker compose build
docker compose up -d
```
Carga del dataset en HDFS
1. Copiar el CSV al contenedor client
```bash
docker cp Electric_Vehicle_Population_Data.csv client:/home/hadoop/
```
3. Entrar en el contenedor
```bash
docker exec -it client bash
```
4. Crear directorio en HDFS y subir el fichero
```bash
hdfs dfs -mkdir -p /data/ev
hdfs dfs -put -f Electric_Vehicle_Population_Data.csv /data/ev/
```

### Ejecución del script de analíticas

El script Python se encuentra en:

/home/hadoop/ev_project/analiticas_ev.py

(montado automáticamente por Docker desde ./ev_project).

1. Entrar en el contenedor client
```bash
docker exec -it client bash
```
2. Ejecutar el script con Spark sobre YARN
Ejecución estándar
```bash
cd /home/hadoop/ev_project

spark-submit \
  --master yarn \
  --deploy-mode client \
  analiticas_ev.py
```
Nota: El modo client es el que finaliza correctamente en este entorno Docker debido a límites de memoria de YARN en cluster mode.

## Diferencia entre *client mode* y *cluster mode*

| Modo    | ¿Dónde corre el Driver?                 | ¿Dónde se ven los logs?        | Ventajas                         |
|---------|------------------------------------------|---------------------------------|----------------------------------|
| client  | En el contenedor `client`                | En la consola del usuario       | Ideal para desarrollo y debugging |
| cluster | En un nodo YARN (`worker1/2/3`)          | UI de YARN / `yarn logs`        | Ideal para producción             |

**En este proyecto:**

- **client mode** funciona correctamente.  
- **cluster mode** falla con *Exit code 137* porque el ApplicationMaster (Driver en cluster mode) se queda sin memoria dentro del contenedor YARN.

### Ejecución alternativa en *cluster mode* (memoria ajustada)

Para poder ejecutar el job también en **cluster mode** dentro de este entorno Docker (con recursos limitados), se puede reducir explícitamente la memoria solicitada por el driver y los ejecutores:

```bash
cd /home/hadoop/ev_project

spark-submit \
  --master yarn \
  --deploy-mode cluster \
  --num-executors 1 \
  --executor-cores 1 \
  --executor-memory 512m \
  --driver-memory 512m \
  --conf spark.executor.memoryOverhead=256 \
  analiticas_ev.py
```

### Acceso a los resultados generados

Cada consulta del script se guarda automáticamente en formato Parquet dentro de HDFS, en:

```bash
/results/ev/
```
### Listar los directorios de resultados
```bash
hdfs dfs -ls /results/ev
```

### Ejemplo de salida:
```bash
/results/ev/dataset_limpio
/results/ev/q1_marcas_estado_anio
/results/ev/q2_bev_vs_phev
/results/ev/q3_autonomia_vs_anio
/results/ev/q4_condados_top
...
```

### Ver el contenido de un resultado concreto

```bash
hdfs dfs -ls /results/ev/q1_marcas_estado_anio
```

### Resultados
```bash
--- Q1: Marcas líderes por estado y año ---
+-----+----------+---------+-------------+
|state|model_year|make     |num_vehiculos|
+-----+----------+---------+-------------+
|AK   |2016      |FORD     |1            |
|AL   |2022      |TOYOTA   |1            |
|AR   |2017      |BMW      |1            |
|AR   |2019      |NISSAN   |1            |
|AR   |2020      |TESLA    |1            |
|AR   |2022      |TESLA    |1            |
|AZ   |2013      |NISSAN   |1            |
|AZ   |2015      |TESLA    |1            |
|AZ   |2021      |TESLA    |2            |
|AZ   |2021      |TOYOTA   |1            |
|AZ   |2022      |VOLVO    |1            |
|CA   |2012      |CHEVROLET|1            |
|CA   |2012      |TOYOTA   |1            |
|CA   |2013      |CHEVROLET|1            |
|CA   |2013      |TESLA    |1            |
|CA   |2013      |TOYOTA   |1            |
|CA   |2014      |FORD     |1            |
|CA   |2015      |FORD     |2            |
|CA   |2015      |TOYOTA   |1            |
|CA   |2015      |TESLA    |1            |
+-----+----------+---------+-------------+
only showing top 20 rows


--- Q2: EV por año y tipo (BEV/PHEV) ---
+----------+--------------------------------------+-------------+
|model_year|ev_type                               |num_vehiculos|
+----------+--------------------------------------+-------------+
|1997      |Battery Electric Vehicle (BEV)        |1            |
|1998      |Battery Electric Vehicle (BEV)        |1            |
|1999      |Battery Electric Vehicle (BEV)        |3            |
|2000      |Battery Electric Vehicle (BEV)        |10           |
|2002      |Battery Electric Vehicle (BEV)        |2            |
|2008      |Battery Electric Vehicle (BEV)        |23           |
|2010      |Battery Electric Vehicle (BEV)        |24           |
|2011      |Battery Electric Vehicle (BEV)        |769          |
|2011      |Plug-in Hybrid Electric Vehicle (PHEV)|71           |
|2012      |Battery Electric Vehicle (BEV)        |814          |
|2012      |Plug-in Hybrid Electric Vehicle (PHEV)|891          |
|2013      |Battery Electric Vehicle (BEV)        |3018         |
|2013      |Plug-in Hybrid Electric Vehicle (PHEV)|1673         |
|2014      |Battery Electric Vehicle (BEV)        |1864         |
|2014      |Plug-in Hybrid Electric Vehicle (PHEV)|1821         |
|2015      |Battery Electric Vehicle (BEV)        |3625         |
|2015      |Plug-in Hybrid Electric Vehicle (PHEV)|1315         |
|2016      |Battery Electric Vehicle (BEV)        |3938         |
|2016      |Plug-in Hybrid Electric Vehicle (PHEV)|1797         |
|2017      |Battery Electric Vehicle (BEV)        |4498         |
+----------+--------------------------------------+-------------+
only showing top 20 rows


--- Q3: Autonomía media por año de modelo ---
+----------+------------------+
|model_year|autonomia_media   |
+----------+------------------+
|1997      |39.0              |
|1998      |58.0              |
|1999      |74.0              |
|2000      |58.0              |
|2002      |95.0              |
|2008      |220.0             |
|2010      |245.0             |
|2011      |71.23690476190477 |
|2012      |61.73137829912024 |
|2013      |81.03709230441271 |
|2014      |81.70963364993216 |
|2015      |97.86740890688259 |
|2016      |101.23870967741935|
|2017      |111.56154558074965|
|2018      |155.73445177593712|
|2019      |176.9546074420417 |
|2020      |242.08543214350425|
|2021      |10.452788063602702|
|2022      |3.883867320015077 |
|2023      |0.855779427359491 |
+----------+------------------+


--- Q4: Condados con más EV (top 20) ---
+------------+-------------+
|county      |num_vehiculos|
+------------+-------------+
|King        |59000        |
|Snohomish   |12434        |
|Pierce      |8535         |
|Clark       |6689         |
|Thurston    |4126         |
|Kitsap      |3847         |
|Whatcom     |2840         |
|Spokane     |2792         |
|Benton      |1376         |
|Island      |1307         |
|Skagit      |1258         |
|Clallam     |731          |
|San Juan    |721          |
|Jefferson   |699          |
|Chelan      |654          |
|Yakima      |617          |
|Cowlitz     |569          |
|Mason       |547          |
|Lewis       |431          |
|Grays Harbor|403          |
+------------+-------------+
only showing top 20 rows


--- Q5: Precio medio por marca y año ---
+----------+--------------+------------+
|model_year|make          |precio_medio|
+----------+--------------+------------+
|1997      |CHEVROLET     |0.0         |
|1998      |FORD          |0.0         |
|1999      |FORD          |0.0         |
|2000      |FORD          |0.0         |
|2002      |TOYOTA        |0.0         |
|2008      |TESLA         |98950.0     |
|2010      |TESLA         |110950.0    |
|2011      |AZURE DYNAMICS|0.0         |
|2011      |CHEVROLET     |0.0         |
|2011      |NISSAN        |0.0         |
|2011      |TESLA         |109000.0    |
|2011      |TH!NK         |0.0         |
|2012      |AZURE DYNAMICS|0.0         |
|2012      |CHEVROLET     |0.0         |
|2012      |FISKER        |102000.0    |
|2012      |FORD          |0.0         |
|2012      |MITSUBISHI    |0.0         |
|2012      |NISSAN        |0.0         |
|2012      |TESLA         |59900.0     |
|2012      |TOYOTA        |0.0         |
+----------+--------------+------------+
only showing top 20 rows


--- Q6: Autonomía media por elegibilidad CAFV ---
+------------------------------------------------------------+------------------+
|cafv_eligibility                                            |autonomia_media   |
+------------------------------------------------------------+------------------+
|Clean Alternative Fuel Vehicle Eligible                     |163.79755793925546|
|Eligibility unknown as battery range has not been researched|0.0               |
|Not eligible due to low battery range                       |19.36465885222576 |
+------------------------------------------------------------+------------------+


--- Q7: Modelos por compañía eléctrica ---
+---------+-------+-------------------------------------------------------------------------------+-------------+
|make     |model  |electric_utility                                                               |num_vehiculos|
+---------+-------+-------------------------------------------------------------------------------+-------------+
|TESLA    |MODEL 3|PUGET SOUND ENERGY INC||CITY OF TACOMA - (WA)                                  |9758         |
|TESLA    |MODEL Y|PUGET SOUND ENERGY INC||CITY OF TACOMA - (WA)                                  |7481         |
|TESLA    |MODEL 3|CITY OF SEATTLE - (WA)|CITY OF TACOMA - (WA)                                   |4417         |
|TESLA    |MODEL 3|PUGET SOUND ENERGY INC                                                         |4127         |
|NISSAN   |LEAF   |PUGET SOUND ENERGY INC||CITY OF TACOMA - (WA)                                  |3741         |
|TESLA    |MODEL Y|PUGET SOUND ENERGY INC                                                         |3244         |
|TESLA    |MODEL S|PUGET SOUND ENERGY INC||CITY OF TACOMA - (WA)                                  |3094         |
|TESLA    |MODEL Y|CITY OF SEATTLE - (WA)|CITY OF TACOMA - (WA)                                   |3064         |
|NISSAN   |LEAF   |PUGET SOUND ENERGY INC                                                         |2825         |
|NISSAN   |LEAF   |CITY OF SEATTLE - (WA)|CITY OF TACOMA - (WA)                                   |2817         |
|TESLA    |MODEL X|PUGET SOUND ENERGY INC||CITY OF TACOMA - (WA)                                  |2186         |
|TESLA    |MODEL S|PUGET SOUND ENERGY INC                                                         |1243         |
|CHEVROLET|BOLT EV|PUGET SOUND ENERGY INC                                                         |1189         |
|CHEVROLET|VOLT   |PUGET SOUND ENERGY INC||CITY OF TACOMA - (WA)                                  |1188         |
|TESLA    |MODEL S|CITY OF SEATTLE - (WA)|CITY OF TACOMA - (WA)                                   |1183         |
|CHEVROLET|BOLT EV|PUGET SOUND ENERGY INC||CITY OF TACOMA - (WA)                                  |1179         |
|CHEVROLET|VOLT   |PUGET SOUND ENERGY INC                                                         |1168         |
|TESLA    |MODEL 3|BONNEVILLE POWER ADMINISTRATION||PUD NO 1 OF CLARK COUNTY - (WA)               |1146         |
|CHEVROLET|BOLT EV|CITY OF SEATTLE - (WA)|CITY OF TACOMA - (WA)                                   |1012         |
|TESLA    |MODEL 3|BONNEVILLE POWER ADMINISTRATION||CITY OF TACOMA - (WA)||PENINSULA LIGHT COMPANY|958          |
+---------+-------+-------------------------------------------------------------------------------+-------------+
only showing top 20 rows


--- Q8: EV por distrito legislativo ---
+--------------------+-------------+
|legislative_district|num_vehiculos|
+--------------------+-------------+
|NULL                |286          |
|1                   |4715         |
|2                   |1226         |
|3                   |557          |
|4                   |845          |
|5                   |4694         |
|6                   |1041         |
|7                   |544          |
|8                   |1157         |
|9                   |606          |
|10                  |2061         |
|11                  |2707         |
|12                  |1004         |
|13                  |748          |
|14                  |720          |
|15                  |277          |
|16                  |611          |
|17                  |1907         |
|18                  |3024         |
|19                  |672          |
+--------------------+-------------+
only showing top 20 rows


--- Q9: Marcas con mayor autonomía media (2019-2023) ---
+----------+------------------+
|make      |autonomia_media   |
+----------+------------------+
|JAGUAR    |207.2876712328767 |
|CHEVROLET |137.8237011091652 |
|FIAT      |84.0              |
|NISSAN    |83.25700164744646 |
|TESLA     |82.20366721832558 |
|AUDI      |78.21798520204895 |
|PORSCHE   |73.4290909090909  |
|KIA       |65.8268029528677  |
|SMART     |58.0              |
|HYUNDAI   |48.506144393241165|
|HONDA     |47.023668639053255|
|POLESTAR  |40.92114695340502 |
|LEXUS     |37.0              |
|TOYOTA    |34.487096774193546|
|BMW       |33.794103194103194|
|CHRYSLER  |32.0              |
|VOLKSWAGEN|31.25             |
|MINI      |27.859106529209622|
|LINCOLN   |23.083333333333332|
|JEEP      |22.70746527777778 |
+----------+------------------+
only showing top 20 rows


--- Q10: Proporción de CAFV por año ---
+----------+-----+----------+--------------------+
|model_year|total|total_cafv|proporcion_cafv     |
+----------+-----+----------+--------------------+
|1997      |1    |1         |1.0                 |
|1998      |1    |1         |1.0                 |
|1999      |3    |3         |1.0                 |
|2000      |10   |10        |1.0                 |
|2002      |2    |2         |1.0                 |
|2008      |23   |23        |1.0                 |
|2010      |24   |24        |1.0                 |
|2011      |840  |840       |1.0                 |
|2012      |1705 |1330      |0.7800586510263929  |
|2013      |4691 |3836      |0.8177360903858453  |
|2014      |3685 |2896      |0.7858887381275441  |
|2015      |4940 |4262      |0.862753036437247   |
|2016      |5735 |4330      |0.7550130775937227  |
|2017      |8644 |6348      |0.7343822304488663  |
|2018      |14246|11921     |0.8367962936964762  |
|2019      |10266|8844      |0.8614845119812975  |
|2020      |11038|9784      |0.8863924624026092  |
|2021      |18364|2099      |0.11429971683729034 |
|2022      |26530|2042      |0.07696946852619675 |
|2023      |1886 |43        |0.022799575821845174|
+----------+-----+----------+--------------------+
```
