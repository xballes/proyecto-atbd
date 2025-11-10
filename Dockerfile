# Imagen base con Java 11
FROM eclipse-temurin:11-jdk

# 1. Instalar utilidades básicas
RUN apt-get update && apt-get install -y ssh rsync curl python3 vim && \
    rm -rf /var/lib/apt/lists/*

# 2. Crear usuario hadoop
RUN useradd -m -s /bin/bash hadoop && echo "hadoop:hadoop" | chpasswd

# 3. Copiar script de arranque y darle permisos
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# 4. A partir de aquí usamos el usuario hadoop
USER hadoop
WORKDIR /home/hadoop

# 5. Variables de entorno
ENV HADOOP_VERSION=3.3.1
ENV SPARK_VERSION=3.5.0
ENV HADOOP_HOME=/home/hadoop/hadoop
ENV SPARK_HOME=/home/hadoop/spark
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$SPARK_HOME/bin
ENV HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
ENV YARN_CONF_DIR=$HADOOP_HOME/etc/hadoop
ENV JAVA_HOME=/opt/java/openjdk


# 6. Instalar Hadoop (archivo histórico de Apache)
RUN curl -L https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz \
    -o hadoop.tar.gz && \
    tar -xzf hadoop.tar.gz && mv hadoop-${HADOOP_VERSION} hadoop && rm hadoop.tar.gz

# 7. Instalar Spark (archivo histórico de Apache)
RUN curl -L https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz \
    -o spark.tgz && \
    tar -xzf spark.tgz && mv spark-${SPARK_VERSION}-bin-hadoop3 spark && rm spark.tgz

# 8. Script de arranque
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
