# Module 1 Homework: Docker & SQL — Answers

## Setup

The data is loaded into Postgres with [`ingest_data.py`](ingest_data.py), which reads both Parquet and CSV files in chunks. Everything runs with Docker Compose:

```bash
docker compose up -d --build
docker compose exec pgdatabase psql -U root -d ny_taxi
```

This creates two tables:

| Table              | Source                           |
|--------------------|----------------------------------|
| `green_taxi_trips` | `green_tripdata_2025-11.parquet` |
| `zones`            | `taxi_zone_lookup.csv`           |


## Question 1. Understanding Docker images

Run docker with the `python:3.13` image. Use an entrypoint `bash` to interact with the container.

What's the version of `pip` in the image?

```bash
docker container run -it python:3.13 /bin/bash
pip --version
```

**Answer:** `pip 26.2.1`


## Question 2. Understanding Docker networking and docker-compose

Given the following `docker-compose.yaml`, what is the `hostname` and `port` that pgadmin should use to connect to the postgres database?

**Answer:** `db:5432`


## Question 3. Counting short trips

For the trips in November 2025 (lpep_pickup_datetime between '2025-11-01' and '2025-12-01', exclusive of the upper bound), how many trips had a `trip_distance` of less than or equal to 1 mile?

```sql
SELECT 
    count(*)
FROM green_taxi_trips
WHERE lpep_pickup_datetime >= '2025-11-01'
AND lpep_pickup_datetime < '2025-12-01'
AND trip_distance <= 1
```

**Answer:** 8,007


## Question 4. Longest trip for each day

Which was the pick up day with the longest trip distance? Only consider trips with `trip_distance` less than 100 miles (to exclude data errors).

```sql
SELECT
    lpep_pickup_datetime
FROM green_taxi_trips
WHERE trip_distance = (
    SELECT 
        max(trip_distance) 
    FROM green_taxi_trips 
    WHERE trip_distance < 100
)
```

**Answer:** 2025-11-14


## Question 5. Biggest pickup zone

Which was the pickup zone with the largest `total_amount` (sum of all trips) on November 18th, 2025?

```sql
SELECT
    "Zone"
FROM
(
    SELECT
        "PULocationID",
        sum(total_amount) AS total_am
    FROM green_taxi_trips
    WHERE lpep_pickup_datetime >= '2025-11-18' AND lpep_pickup_datetime < '2025-11-19'
    GROUP BY "PULocationID"
    ORDER BY total_am DESC
    LIMIT 1
)
INNER JOIN
(
    SELECT
        "LocationID" AS "PULocationID",
        "Zone"
    FROM zones
) USING ("PULocationID")
```

**Answer:** East Harlem North


## Question 6. Largest tip

For the passengers picked up in the zone named "East Harlem North" in November 2025, which was the drop off zone that had the largest tip?

```sql
SELECT
    "Zone"
FROM
(
    SELECT
        "DOLocationID"
    FROM green_taxi_trips
    WHERE lpep_pickup_datetime >= '2025-11-01' AND lpep_pickup_datetime < '2025-12-01'
    AND "PULocationID" = (
        SELECT
            "LocationID"
        FROM zones
        WHERE "Zone" = 'East Harlem North'
    )
    ORDER BY tip_amount DESC
    LIMIT 1
)
INNER JOIN
(
    SELECT
        "LocationID" AS "DOLocationID",
        "Zone"
    FROM zones
) USING ("DOLocationID")
```

**Answer:** Yorkville West


## Question 7. Terraform Workflow

Which of the following sequences, respectively, describes the workflow for:
1. Downloading the provider plugins and setting up backend,
2. Generating proposed changes and auto-executing the plan
3. Remove all resources managed by terraform`

**Answer:** terraform init, terraform apply -auto-approve, terraform destroy
