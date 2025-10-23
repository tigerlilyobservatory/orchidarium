"""
Provide an InfluxDB Publisher subclass to interact cleanly with the InfluxDB API to publish metrics.
"""


from influxdb_client_3 import InfluxDBClient3


# client = InfluxDBClient3(host="your_influxdb_host",
#                         org="your_org_id",
#                         token="your_api_token",
#                         database="your_database_name")


# class