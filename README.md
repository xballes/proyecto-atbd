# Proyecto ATBD – Análisis de Vehículos Eléctricos con Spark y Hadoop (Docker)

## Descripción general

Este proyecto forma parte de la asignatura **Arquitecturas y Tecnologías Big Data (ATBD)** del Máster en Big Data.  
El objetivo es desplegar un **clúster Hadoop + YARN + Spark** sobre Docker y realizar un análisis distribuido del dataset:

> [Electric Vehicle Population Data – Kaggle](https://www.kaggle.com/datasets/adarshsng/electric-vehicle-population-data)

El análisis se centra en la **adopción de vehículos eléctricos (EV)** en EE. UU., estudiando su evolución, marcas líderes y características técnicas.

---

## Estructura del proyecto


---

## ⚙️ Infraestructura desplegada

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

## Puesta en marcha

### Construir y levantar el clúster

```bash
docker compose build
docker compose up -d


