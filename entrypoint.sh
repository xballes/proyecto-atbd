#!/bin/bash
set -e

CONF_DIR="$HADOOP_HOME/etc/hadoop"

echo ">>> Generando configuración de Hadoop en $CONF_DIR"

# core-site.xml
cat > "$CONF_DIR/core-site.xml" <<EOF
<configuration>
  <property>
    <name>fs.defaultFS</name>
    <value>hdfs://master:9000</value>
  </property>
</configuration>
EOF

# hdfs-site.xml
mkdir -p /home/hadoop/hdfs/namenode
mkdir -p /home/hadoop/hdfs/datanode

cat > "$CONF_DIR/hdfs-site.xml" <<EOF
<configuration>
  <property>
    <name>dfs.replication</name>
    <value>3</value>
  </property>
  <property>
    <name>dfs.namenode.name.dir</name>
    <value>file:/home/hadoop/hdfs/namenode</value>
  </property>
  <property>
    <name>dfs.datanode.data.dir</name>
    <value>file:/home/hadoop/hdfs/datanode</value>
  </property>
</configuration>
EOF

# yarn-site.xml
cat > "$CONF_DIR/yarn-site.xml" <<EOF
<configuration>
  <property>
    <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
  </property>

  <property>
    <name>yarn.resourcemanager.hostname</name>
    <value>master</value>
  </property>

  <property>
    <name>yarn.resourcemanager.address</name>
    <value>master:8032</value>
  </property>

  <property>
    <name>yarn.resourcemanager.scheduler.address</name>
    <value>master:8030</value>
  </property>

  <property>
    <name>yarn.resourcemanager.resource-tracker.address</name>
    <value>master:8031</value>
  </property>

  <property>
    <name>yarn.resourcemanager.webapp.address</name>
    <value>master:8088</value>
  </property>
</configuration>
EOF

# mapred-site.xml
cat > "$CONF_DIR/mapred-site.xml" <<EOF
<configuration>
  <property>
    <name>mapreduce.framework.name</name>
    <value>yarn</value>
  </property>
</configuration>
EOF

echo ">>> Configuración generada. NODE_ROLE=$NODE_ROLE"

case "$NODE_ROLE" in
  master)
    echo ">>> Arrancando NameNode y ResourceManager en master"

    if [ ! -f "/home/hadoop/hdfs-formatted" ]; then
      $HADOOP_HOME/bin/hdfs namenode -format -force
      touch /home/hadoop/hdfs-formatted
    fi

    $HADOOP_HOME/bin/hdfs --daemon start namenode
    $HADOOP_HOME/bin/yarn --daemon start resourcemanager
    $HADOOP_HOME/bin/mapred --daemon start historyserver || true
    ;;

  worker)
    echo ">>> Arrancando DataNode y NodeManager en worker"
    $HADOOP_HOME/bin/hdfs --daemon start datanode
    $HADOOP_HOME/bin/yarn --daemon start nodemanager
    ;;

  client)
    echo ">>> Nodo client: sin daemons"
    ;;
esac

# Mantener el contenedor vivo
tail -f /dev/null
