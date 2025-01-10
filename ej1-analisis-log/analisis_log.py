# Funciones y código del ejercicio 1 -> análisis logs
from pyspark.sql import functions as F
from datetime import datetime
import locale
from utils.utils import crear_sesion_spark, definir_esquema, verificar_archivo


def cargar_datos_csv(spark, input_file, schema):
    return spark.read.schema(schema).csv(input_file, sep=" ", header=False)


def configurar_locale():
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')


def convertir_fechas(init_datetime, end_datetime, input_format):
    init_dt = datetime.strptime(init_datetime, input_format)
    end_dt = datetime.strptime(end_datetime, input_format)
    return int(init_dt.timestamp() * 1000), int(end_dt.timestamp() * 1000)


def filtrar_datos_por_tiempo(df, init_timestamp, end_timestamp):
    return df.filter(
        (F.col("timestamp") >= init_timestamp) &
        (F.col("timestamp") <= end_timestamp)
    )


def filtrar_por_hostname(df, hostname):
    target_host = hostname.lower()
    return df.filter(
        (F.lower(F.col("hostname_origen")) == target_host) |
        (F.lower(F.col("hostname_destino")) == target_host)
    )


def obtener_hosts_conectados(df, hostname):
    target_host = hostname.lower()
    df_distinct_origin_host = df.filter(
        F.lower(F.col('hostname_origen')) != target_host
    ).select(F.col('hostname_origen').alias('host'))

    df_distinct_destino_host = df.filter(
        F.lower(F.col('hostname_destino')) != target_host
    ).select(F.col('hostname_destino').alias('host'))

    df_result = df_distinct_origin_host.unionByName(
        df_distinct_destino_host).distinct()
    return [row['host'] for row in df_result.toLocalIterator()]


def filtrar_por_hostname(df, hostname):
    target_host = hostname.lower()
    return df.filter(
        (F.lower(F.col("hostname_origen")) == target_host) |
        (F.lower(F.col("hostname_destino")) == target_host)
    )


def obtener_hosts_conectados(df, hostname):
    target_host = hostname.lower()
    df_distinct_origin_host = df.filter(
        F.lower(F.col('hostname_origen')) != target_host
    ).select(F.col('hostname_origen').alias('host'))

    df_distinct_destino_host = df.filter(
        F.lower(F.col('hostname_destino')) != target_host
    ).select(F.col('hostname_destino').alias('host'))

    df_result = df_distinct_origin_host.unionByName(
        df_distinct_destino_host).distinct()
    return [row['host'] for row in df_result.toLocalIterator()]


def analisis_log(input_file, init_datetime, end_datetime, hostname):
    verificar_archivo(input_file)

    spark = crear_sesion_spark("analisisLog", "4g", "4g", "200")
    schema = definir_esquema()
    df_log_csv = cargar_datos_csv(spark, input_file, schema)

    configurar_locale()

    input_format = "%A, %d de %B de %Y %H:%M:%S"
    init_timestamp, end_timestamp = convertir_fechas(
        init_datetime, end_datetime, input_format)

    df_filtered = filtrar_datos_por_tiempo(
        df_log_csv, init_timestamp, end_timestamp)
    df_filtered = filtrar_por_hostname(df_filtered, hostname)

    hosts = obtener_hosts_conectados(df_filtered, hostname)

    spark.stop()

    return hosts