from time import time
from kafka import KafkaProducer
from faker import Faker
import json, time

faker = Faker()


def get_register():
    return {
        "id": faker.random_int(),
        "organization_name": faker.name(),
        "organization_id": faker.random_int(),
        "time": faker.date_time().isoformat(),
        "test_case_id": faker.random_int(),
        "adjust": faker.random_digit(),
        "info": {
            "address": faker.address(),
            "city": faker.city(),
            "state": faker.state(),
            "zipcode": faker.zipcode()
        },
        "contact": {"name": faker.name(), "email": faker.email()},
    }


def json_serializer(data):
    return json.dumps(data).encode('utf-8')

def on_send_error(excp):
    print('Having an error', exc_info=excp)

def on_send_success(record_metadata):
    print(record_metadata.topic,record_metadata.partition,record_metadata.offset)

producer = KafkaProducer(
    bootstrap_servers = ['localhost:29092'], # server name
    value_serializer = json_serializer # function callable
    )

while True:
    user = get_register()
    print(user)
    # send data to  event-flink kafka topic
    producer.send('event-flink', user).add_callback(on_send_success).add_errback(on_send_error)
    producer.flush()
    # wait 3 seconds
    time.sleep(3)
