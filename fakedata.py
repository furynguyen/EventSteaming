from time import time
from kafka import KafkaProducer
from faker import Faker
import json, time

faker = Faker()


def get_register():
    return {
        "id": faker.uuid4(),
        "email": faker.email(),
        "event": faker.random_choices(elements=("click", "view", "purchase"), length=1)[0],
        "time": faker.date_time().isoformat(),
        "properties": {
            "address": faker.address(),
            "city": faker.city(),
            "ip": faker.ipv4()
        }
    }


def json_serializer(data):
    return json.dumps(data).encode('utf-8')

def on_send_error(excp):
    print('Having an error', exc_info=excp)

def on_send_success(record_metadata):
    pass
    # print(record_metadata.topic,record_metadata.partition,record_metadata.offset)

producer = KafkaProducer(
    bootstrap_servers = ['localhost:29092'], # server name
    value_serializer = json_serializer # function callable
    )
event_count = 0
start_time = time.time()
while True:
    user = get_register()
    producer.send('event-flink', user).add_callback(on_send_success).add_errback(on_send_error)
    producer.flush()
    
    event_count += 1
    current_time = time.time()
    elapsed_time = current_time - start_time
    
    if elapsed_time >= 1:
        print(f"Events sent per second: {event_count}")
        start_time = current_time
        event_count = 0
