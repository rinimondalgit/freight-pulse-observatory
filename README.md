Problem statement :
In many logistics environments, shipment data exists across multiple systems without a unified analytics layer. This lack of centralized visibility makes it difficult to monitor on-time delivery performance, evaluate carrier reliability, and identify high-risk routes. As a result, decision-making becomes reactive rather than data-driven, leading to operational inefficiencies and SLA breaches.

# Freight Pulse Observatory

> A cloud-native batch data pipeline analyzing freight ecosystem health by correlating shipment delay trends with carrier profile data across routes, modes, and geographies.

## Live Dashboard

[View Dashboard on Looker Studio](https://datastudio.google.com/s/mAllXuyFkR8)

The dashboard has this page:

* Shipment Trends: Monthly shipment trend, top delayed carriers, geo map, scorecards

&#x20;Ecosystem Health: Delay rate by carrier, scorecards

## Dashboard Preview

![Dashboard](images/dashboard.png)

\---

## Architecture

&#x20;   Shipments CSV + Carrier Reference JSON
│
▼
Kestra (batch orchestration — weekly Monday 6AM UTC)
│
▼
Google Cloud Storage (raw CSV / JSON data lake)
│
▼
BigQuery (partitioned + clustered tables)
│
▼
dbt Cloud (staging views → mart tables)
│
▼
Looker Studio (dashboard)



The following diagram illustrates the end-to-end data pipeline:



!\[Architecture Diagram](images/architecture\_diagram.png.png)



### Kestra Orchestration DAG

The pipeline runs as a 4-task sequential DAG inside Kestra:

&#x20;   weekly\_schedule → ingest\_shipments → ingest\_carriers → verify\_bigquery → log\_success



* `weekly\\\_schedule` — cron trigger every Monday 6AM UTC
* `ingest\\\_shipments` — reads CSV from local source, uploads to GCS, loads to BigQuery
* `ingest\\\_carriers` — uploads carrier reference JSON and loads to BigQuery
* `verify\\\_bigquery` — confirms both tables have expected row counts
* `log\\\_success` — logs pipeline completion timestamp

\---

## Problem Description

Freight operations leaders need visibility into shipment performance, carrier reliability, and route-level delays. This project builds an end-to-end data pipeline to answer:

* Which carriers have the highest shipment delay rates?
* Which origin-destination lanes show the worst transit performance?
* How do monthly shipment volumes change across geographies?
* Which shipment modes are most cost-efficient?
* Is there a relationship between carrier fleet size and throughput?
* Which carriers show the most ecosystem stress (high delay rate relative to operational scale)?

\---

## Tech Stack

|Layer|Tool|Purpose|
|-|-|-|
|Infrastructure|Terraform|Provision GCS bucket and BigQuery datasets|
|Containerization|Docker|Package ingestion scripts into a portable image|
|Orchestration|Kestra v1.1.1|Schedule and run the batch pipeline weekly|
|Data Lake|Google Cloud Storage|Store raw CSV and JSON files|
|Data Warehouse|BigQuery|Partitioned and clustered analytical tables|
|Transformations|dbt Cloud|Staging views and mart tables|
|Visualization|Looker Studio|Two-page interactive dashboard|
|Version Control|GitHub|Source code and pipeline definitions|

\---

## Data Sources

|Source|Description|Rows|Format|
|-|-|-:|-|
|`ingestion/shipments.csv`|Synthetic freight shipments covering carriers, routes, modes, and SLAs|2,500|CSV|
|`ingestion/carrier\\\_reference\\\_sample.json`|Carrier profile reference data for enrichment|6|JSON|

### Sample Carrier Reference Response

```json
{
  "carrier": "FedEx Freight",
  "carrier\\\_type": "National",
  "fleet\\\_size": 38000,
  "service\\\_regions": "US, Canada",
  "digital\\\_maturity": "High",
  "status": "Active"
}
```

### Shipments CSV Columns

|Column|Type|Description|
|-|-|-|
|shipment\_id|STRING|Unique shipment identifier|
|ship\_date|DATE|Shipment creation date|
|delivery\_date|DATE|Final delivery date|
|carrier|STRING|Carrier or logistics partner|
|mode|STRING|Shipment mode|
|origin\_city|STRING|Origin city|
|origin\_state|STRING|Origin state|
|destination\_city|STRING|Destination city|
|destination\_state|STRING|Destination state|
|distance\_miles|INTEGER|Approximate shipment distance|
|promised\_days|INTEGER|SLA target transit days|
|actual\_days|INTEGER|Actual transit days|
|delayed\_flag|INTEGER|1 if actual > promised|
|shipping\_cost|FLOAT|Shipment cost in USD|
|customer\_segment|STRING|Business segment|

\---

## Data Warehouse Design

### Tables

|Table|Layer|Type|Rows|
|-|-|-|-:|
|`raw.raw\\\_shipments\\\_partitioned`|Raw|Partitioned + Clustered|2,500|
|`raw.raw\\\_carriers\\\_partitioned`|Raw|Partitioned + Clustered|6|
|`freight\\\_staging.stg\\\_shipments`|Staging|View|—|
|`freight\\\_staging.stg\\\_carriers`|Staging|View|—|
|`freight\\\_mart.mart\\\_monthly\\\_shipments`|Mart|Table|—|
|`freight\\\_mart.mart\\\_freight\\\_ecosystem`|Mart|Table|—|

### Partitioning and Clustering

`raw\\\_shipments\\\_partitioned`

* Partitioned by: `DATE\\\_TRUNC(ship\\\_date, MONTH)`
* Clustered by: `carrier`, `origin\\\_state`

`raw\\\_carriers\\\_partitioned`

* Small enrichment table retained in raw; can remain unpartitioned or be ingestion-time partitioned.
* Clustered by: `carrier\\\_type`, `status`

\---

## dbt Transformations

&#x20;   raw layer (BigQuery)
└── staging (dbt views)
├── stg\_shipments           — standardizes shipment columns and casts types
└── stg\_carriers            — standardizes carrier reference attributes
└── marts (dbt tables)
├── mart\_monthly\_shipments  — monthly aggregation by carrier and lane
└── mart\_freight\_ecosystem  — carrier-level join of shipment metrics + carrier profile



`stg\\\_shipments` — filters invalid dates, standardizes column names, casts numeric fields, and derives `ship\\\_month`.

`stg\\\_carriers` — standardizes carrier profile attributes and casts fleet size.

`mart\\\_monthly\\\_shipments` — aggregates by month, carrier, origin\_state, and destination\_state.

`mart\\\_freight\\\_ecosystem` — joins carrier shipment performance to carrier profile data. Produces `delay\\\_rate\\\_pct`, `avg\\\_transit\\\_days`, `avg\\\_shipping\\\_cost`, `fleet\\\_size`, and `shipments\\\_per\\\_1000\\\_fleet`.

\---

## Dashboard

[Live Dashboard](https://lookerstudio.google.com/)

### Shipment Trends (source: `mart\\\_monthly\\\_shipments`)

|#|Chart Type|X-axis|Y-axis|Title|
|-|-|-|-|-|
|1|Time series|`ship\\\_month`|`total\\\_shipments`|Monthly freight shipment trend|
|2|Horizontal bar|`delayed\\\_shipments`|`carrier`|Top delayed carriers|
|3|Geo map|`origin\\\_state`|`total\\\_shipments`|Shipment distribution by origin state|
|4|Scorecard|—|`total\\\_shipments` (SUM)|Total shipments|
|5|Scorecard|—|`delayed\\\_shipments` (SUM)|Total delayed shipments|

### Ecosystem Health (source: `mart\\\_freight\\\_ecosystem`)

|#|Chart Type|X-axis|Y-axis|Title|
|-|-|-|-|-|
|6|Horizontal bar|`delay\\\_rate\\\_pct`|`carrier`|Carrier delay rate|
|7|Horizontal bar|`shipments\\\_per\\\_1000\\\_fleet`|`carrier`|Fleet-normalized throughput|
|8|Scorecard|—|`carrier` (COUNT DISTINCT)|Total carriers analyzed|
|9|Scorecard|—|`avg\\\_transit\\\_days` (AVG)|Average transit days|

\---

## Reproducing the Project

### Prerequisites

* GCP account with billing enabled
* [Docker](https://docs.docker.com/) and Docker Compose installed
* [Terraform](https://developer.hashicorp.com/terraform) installed
* [dbt Cloud](https://cloud.getdbt.com/) account (free Developer tier)

### Step 1 — Clone the repo

```bash
git clone https://github.com/rinimondalgit/freight-pulse-observatory
cd freight-pulse-observatory
```

### Step 2 — Set up GCP

1. Create a new GCP project and note the Project ID.
2. Enable BigQuery API and Cloud Storage API.
3. Create a service account named `freight-obs-sa`.
4. Grant roles: `BigQuery Admin`, `Storage Admin`.
5. Download the JSON key.

```bash
mkdir -p \\\~/.gcp
mv \\\~/Downloads/your-key.json \\\~/.gcp/freight-obs-sa.json
```

### Step 3 — Provision infrastructure with Terraform

```bash
cd terraform

cat > terraform.tfvars << EOF
project\\\_id  = "

"
region      = "us-central1"
credentials = "\\\~/.gcp/freight-obs-sa.json"
EOF

terraform init
terraform apply
```

This provisions:

* GCS bucket: `freight-pulse-observatory-data-lake`
* BigQuery datasets: `raw`, `freight\\\_staging`, `freight\\\_mart`

### Step 4 — Upload the shipments CSV to GCS

```bash
gsutil cp ingestion/shipments.csv gs://freight-pulse-observatory-data-lake/raw/shipments/shipments.csv
```

### Step 5 — Build the Docker image

```bash
cd docker
cp \\\~/.gcp/freight-obs-sa.json credentials.json
docker build -t tech-obs-ingestion:v1 .
```

### Step 6 — Start Kestra

```bash
cd kestra
docker compose up -d
```

Open `http://localhost:8080` and complete the account setup wizard.

### Step 7 — Register the Kestra flow

In the Kestra UI:

1. Go to Flows → New Flow
2. Paste the contents of `kestra/freight\\\_observatory\\\_flow.yml`
3. Save

### Step 8 — Trigger the pipeline

In the Kestra UI:

1. Go to `freight\\\_observatory\\\_pipeline`
2. Click Execute
3. Confirm:

   * `ingest\\\_shipments` loads `raw.raw\\\_shipments`
   * `ingest\\\_carriers` loads `raw.raw\\\_carriers`
   * `verify\\\_bigquery` confirms data
   * `log\\\_success` records the run

### Step 9 — Create partitioned and clustered tables

```sql
CREATE OR REPLACE TABLE `freight-pulse-observatory.raw.raw\\\_shipments\\\_partitioned`
PARTITION BY DATE\\\_TRUNC(ship\\\_date, MONTH)
CLUSTER BY carrier, origin\\\_state
AS SELECT \\\* FROM `freight-pulse-observatory.raw.raw\\\_shipments`;

CREATE OR REPLACE TABLE `freight-pulse-observatory.raw.raw\\\_carriers\\\_partitioned`
AS SELECT \\\* FROM `freight-pulse-observatory.raw.raw\\\_carriers`;
```

### Step 10 — Run dbt transformations

Create a dbt Cloud project, connect it to BigQuery and your GitHub repo, then run:

```bash
dbt run
```

### Step 11 — Build the dashboard

Create a Looker Studio report using:

* `freight\\\_mart.mart\\\_monthly\\\_shipments`
* `freight\\\_mart.mart\\\_freight\\\_ecosystem`

Recreate the charts documented above.

\---

## Project Structure

```text
freight-pulse-observatory/
├── docker/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── ingest\\\_shipments.py
│   ├── ingest\\\_carriers.py
│   └── verify.py
├── images/
│   └── architecture.png
├── ingestion/
│   ├── shipments.csv
│   ├── carrier\\\_reference\\\_sample.json
│   ├── ingest\\\_shipments.py
│   └── ingest\\\_carriers.py
├── kestra/
│   ├── docker-compose.yml
│   └── freight\\\_observatory\\\_flow.yml
├── models/
│   ├── staging/
│   │   ├── stg\\\_shipments.sql
│   │   └── stg\\\_carriers.sql
│   └── marts/
│       ├── mart\\\_monthly\\\_shipments.sql
│       └── mart\\\_freight\\\_ecosystem.sql
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── .gitignore
├── dbt\\\_project.yml
└── README.md
```

\# Freight Pulse Analytics 📦🚚



\## Overview

Freight Pulse Analytics is an end-to-end cloud-based data engineering and analytics solution designed to provide real-time visibility into shipment performance, carrier reliability, and SLA adherence across logistics operations.



The platform simulates enterprise-grade freight analytics by integrating data ingestion, cloud storage, data warehousing, and business intelligence into a unified pipeline.



\---



\## Business Problem

Logistics organizations often lack centralized visibility into:



\- Shipment performance trends

\- Carrier reliability and delays

\- SLA adherence across routes

\- Operational bottlenecks



This project addresses these challenges by delivering actionable insights through a scalable analytics pipeline.



\---

&#x20;   +----------------------+

&#x20;   |   Python Generator   |

&#x20;   | (Synthetic Data)     |

&#x20;   +----------+-----------+

&#x20;              |

&#x20;              v

&#x20;   +----------------------+

&#x20;   |  Google Cloud Storage|

&#x20;   |  (Raw Data Layer)    |

&#x20;   +----------+-----------+

&#x20;              |

&#x20;              v

&#x20;   +----------------------+

&#x20;   |     BigQuery         |

&#x20;   | (Data Warehouse)     |

&#x20;   +----------+-----------+

&#x20;              |

&#x20;              v

&#x20;   +----------------------+

&#x20;   |   SQL Transformations|

&#x20;   | (Analytics Layer)    |

&#x20;   +----------+-----------+

&#x20;              |

&#x20;              v

&#x20;   +----------------------+

&#x20;   |  Looker Studio       |

&#x20;   | (Dashboard \& BI)     |

&#x20;   +----------------------+



\---



\## Tech Stack



| Layer | Technology |

|------|-----------|

| Data Generation | Python, Pandas |

| Storage | Google Cloud Storage (GCS) |

| Data Warehouse | BigQuery |

| Transformation | SQL (dbt-ready) |

| Visualization | Looker Studio |

| Cloud Platform | Google Cloud Platform (GCP) |



\---



\## Data Pipeline



1\. Synthetic shipment data generated using Python

2\. Data uploaded to GCS (raw layer)

3\. Data ingested into BigQuery

4\. Transformation applied to create analytics-ready tables

5\. Dashboard built for business insights



\---



\## Data Model



\### Raw Table

`raw\\\_shipments`

\- Direct ingestion from source CSV



\### Fact Table

`fct\\\_shipments`

\- Cleaned and transformed dataset

\- Includes derived fields:

&#x20; - `delay\\\_days`

&#x20; - `on\\\_time\\\_flag`



\---



\## Key Metrics



\- Total Shipments

\- On-Time Delivery %

\- Average Transit Time

\- Delay Rate %

\- Shipping Cost Trends



\---



\## Dashboard Features



\- 📊 KPI scorecards for quick insights

\- 📈 Shipment volume trends over time

\- 🚚 Carrier performance analysis

\- 🌍 Geographic shipment distribution

\- 🔍 Interactive filters (Carrier, Mode, State)

\- ⚠️ Identification of high-delay routes



\---



\## Dashboard Preview



!\[Dashboard Overview](images/dashboard\_overview.png)



\---



\## Sample Insights



\- Certain carriers show consistently higher delay percentages

\- Specific origin-destination routes experience SLA breaches

\- Shipment volume trends highlight seasonal fluctuations

\- Mode-based cost differences impact operational efficiency



\---



\## How to Run the Project



\### 1. Generate Data

```bash

python scripts/generate\\\_data.py



Upload to GCS

python scripts/load\\\_to\\\_gcs.py



Load into BigQuery



Use GCP UI or scripts to load CSV into dataset:freight\\\_pulse.raw\\\_shipments



Run Transformations



Execute SQL to create:freight\\\_pulse.fct\\\_shipments



Build Dashboard



Connect Looker Studio to BigQuery table:fct\\\_shipments



Cloud Configuration

Project ID: freight-pulse-observatory

Dataset: freight\\\_pulse

Storage Bucket: freight-pulse-bucket-koushik



Key Learnings

Designing scalable data pipelines on GCP

Transforming raw data into business-ready insights

Building interactive dashboards for decision-making

Applying data modeling for analytics use cases





Future Enhancements

dbt integration for modular transformations

Orchestration using Kestra / Airflow

Real-time streaming pipeline

Advanced predictive analytics (delay forecasting)

## 


