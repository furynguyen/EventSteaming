from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings
from pyflink.datastream.connectors import FlinkKafkaConsumer

env = StreamExecutionEnvironment.get_execution_environment() 
env.add_jars("file:///Users/hoai.nguyen/Documents/LAP/EventStreaming/jars/flink-sql-connector-kafka-3.1.0-1.17.jar")
env.add_jars("file:///Users/hoai.nguyen/Documents/LAP/EventStreaming/jars/flink-connector-kafka-3.1.0-1.18.jar")

# Set up the Table Environment
table_env = StreamTableEnvironment.create(
    env,
    environment_settings=EnvironmentSettings.new_instance().in_streaming_mode().use_blink_planner().build()
)

# Set up Kafka consumer properties
properties = {
    'bootstrap.servers': 'localhost:29092',
    'group.id': 'event-group',
    'auto.offset.reset': 'earliest'
}

# Create a Kafka consumer
consumer = FlinkKafkaConsumer(
    'event-flink',
    SimpleStringSchema(),
    properties=properties
)

# Add the Kafka consumer as a source to the execution environment
ds = env.add_source(consumer)

# Define the schema using the KafkaSchema class
table_env.create_temporary_view(
    'events_table',
    ds,
    KafkaSchema.get_schema()
)

# Perform a query on the Table
table_result = table_env.execute_sql("SELECT * FROM events_table")

# Print the results
with table_result.collect() as results:
    for row in results:
        print(row)


# Execute the job
env.execute("Flink Kafka Application")



