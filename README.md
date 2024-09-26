# Event Streaming
This is basic demonstrate project to lean how to combine Kafka and Flink. Using Postgresqk as Sink target.

![![high level architecture]](./images/system_design.png)

### Create virtual environment
`python3 -m venv .eventstream`

Active the environment

    source .eventstream/bin/activate

### Build the docker
* Run this command to start kafka and postgresql also flink clusters

    `docker compose up` Note that the first time this runs, it might take a few seconds to build the respective images as the binaries can be a bit big!
    
    Using the postgresql with 2 plugin pg_crone for partition event table

    Using kafdrop as management tool to monitor the kafka lag



## Run the Flink application
### Testing scenario 1:
* Start docker compose: `docker compose up`

* Create a kafka topic with only one partition:
    
    Using kafdrop to create a topic `event_flink`
    
* Run `create_table.sql` to create new event table in Postgresql and its partition.

* Run the data faker `python fakedata.py` to generate fake event data then pulish it to kafka cluster. (This can be run locally or in any testing environment. Be sure to replace the Kafka server with the appropriate one for the environment.)

* Submit the flink job to flink master. 
    `docker exec -it a0baf9f3fd8b6d9724534b03e0600402e3e` replace `a0baf9f3fd8b6d9724534b03e0600402e3e` with id of app container.

    Navigate to `/test/` then run command `/opt/flink/bin/flink run -py app2db.py --jobmanager jobmanager:8081`. 

    ![![high level architecture]](./images/submit_flink_app.png)
    
    `Job has been submitted with JobID 7142af7d752a56cf5427cb4c315c9990` this means the app has been submitted to flink cluster. Check the running job by visiting `http://localhost:8081/`


    ![![high level architecture]](./images/app_running_test_1.png)

    A submitted job has been ran by Flink cluster. We can check Exception, Time line, Checkpoints to monitor the job.

    For it is only run one job therefore the LAG is very high

    ![![high level architecture]](./images/lag_test_1.png)

    To resolve this issue, we move to scenario 2.

### Testing scenerio 2:

In this scenario, we leverage Kafka's parallelism by increasing the number of partitions for the `event-flink` topic from 1 to 4, allowing us to run 4 jobs simultaneously to speed up data processing.

Increasing topic to 4 partions instead of 1

    kafka-topics --alter --bootstrap-server localhost:9092  --topic event-flink  --partitions 4

Checking Kafdrop we will see the topic `event-flink` has 4 partitions.

![![high level architecture]](./images/lag_test_2.png)

The lag is still high, but it's now distributed across 4 partitions. We'll submit new jobs to reduce the lag further.

![![high level architecture]](./images/app_test_2.png)

Two jobs are running, consuming messages from Kafka. Recheck the lag

![![high level architecture]](./images/lag_test_2_2.png)

The lag now is only **448** comapred to **3948** previously.

Select all consumed data

![![high level architecture]](./images/sql_select.png)

it took only 240ms to count 500k rows. which is good enough for testing purposes.