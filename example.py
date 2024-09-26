import json
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common import WatermarkStrategy, Row
from pyflink.datastream.connectors.kafka import KafkaOffsetsInitializer, KafkaSource, KafkaOffsetResetStrategy
from pyflink.datastream.functions import MapFunction
from pyflink.common.typeinfo import Types, RowTypeInfo
from pyflink.datastream.connectors.jdbc import JdbcConnectionOptions, JdbcExecutionOptions, JdbcSink
from pyflink.datastream import ExternalizedCheckpointCleanup
import pandas as pd

env = StreamExecutionEnvironment.get_execution_environment() 

env.add_jars("file:///test/jars/flink-sql-connector-kafka-3.1.0-1.17.jar")
env.add_jars("file:///test/jars/flink-connector-kafka-3.2.0-1.19.jar")
env.add_jars("file:///test/jars/flink-connector-jdbc_2.11-1.14.6.jar")
env.add_jars("file:///test/jars/postgresql-42.7.3.jar")

env.enable_checkpointing(3000)  # Enable checkpointing every 1 seconds
env.get_checkpoint_config().set_checkpoint_timeout(16000)  # 16 seconds
env.get_checkpoint_config().set_max_concurrent_checkpoints(1)
env.get_checkpoint_config().set_externalized_checkpoint_cleanup(ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION)


class JsonToDict(MapFunction):
    def map(self, value):
        record = json.loads(value)
        # Flatten the nested JSON
        flattened_record = pd.json_normalize(record)
        # Convert the flattened record back to a dictionary
        flattened_dict = flattened_record.to_dict(orient='records')[0]
        print(flattened_record)
        return Row(*flattened_dict.values())

def read_event_from_kafka():
    kafka_source = (
            KafkaSource.builder()
            .set_bootstrap_servers("kafka:9092")
            .set_topics("event-flink")
            .set_group_id("flink_group")
            .set_starting_offsets(KafkaOffsetsInitializer.committed_offsets(offset_reset_strategy=KafkaOffsetResetStrategy.EARLIEST))
            .set_value_only_deserializer(SimpleStringSchema())
            .set_property("enable.auto.commit","True")
            .build()
        )
    # Add the Kafka consumer as a source to the execution environment
    ds = env.from_source(kafka_source,  WatermarkStrategy.no_watermarks(), "Kafka Source")

    output_type = RowTypeInfo(
        [Types.STRING(), Types.STRING(), Types.STRING(), Types.STRING(), Types.STRING(), Types.STRING(), Types.STRING()],
        ["id", "email", "event", "time", "properties.address", "properties.city", "properties.ip"]
    )

    cleaned_stream = ds.map(JsonToDict(), output_type=output_type)
    # Define the JDBC Sink
    jdbc_sink = JdbcSink.sink(
        "INSERT INTO events (id, email, event, time, address, city, ip) VALUES (?::uuid, ?, ?, ?::timestamp, ?, ?, ?)",
        # Provide the query parameters mapping from the tuple
        output_type,
        JdbcConnectionOptions.JdbcConnectionOptionsBuilder()
            .with_url("jdbc:postgresql://pg:5432/postgres") # Replace with your database URL
            .with_driver_name("org.postgresql.Driver")
            .with_user_name("postgres")
            .with_password("123")
            .build(),
        JdbcExecutionOptions.builder()
            .with_batch_size(1)  # Adjust batch size as needed. I used 1 for testing
            .with_max_retries(2) # Adjust max retries as needed
            .with_batch_interval_ms(200)
            .build(),
    )

    cleaned_stream.add_sink(jdbc_sink).name("Postgresql Sink")

    # Execute the job
    env.execute("Streaming Events to DB: Group 0")

if __name__ == '__main__':
    print("Starting Flink job")
    read_event_from_kafka()


