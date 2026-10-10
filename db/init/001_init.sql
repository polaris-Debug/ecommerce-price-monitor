CREATE DATABASE IF NOT EXISTS price_monitor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE price_monitor;

CREATE USER IF NOT EXISTS 'price_etl'@'%' IDENTIFIED BY 'change_me';
GRANT ALL PRIVILEGES ON price_monitor.* TO 'price_etl'@'%';
CREATE USER IF NOT EXISTS 'metabase'@'%' IDENTIFIED BY 'change_me_metabase';
GRANT SELECT ON price_monitor.* TO 'metabase'@'%';
FLUSH PRIVILEGES;

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS ods;
CREATE SCHEMA IF NOT EXISTS dim;
CREATE SCHEMA IF NOT EXISTS dwd;
CREATE SCHEMA IF NOT EXISTS dws;
CREATE SCHEMA IF NOT EXISTS ads;
CREATE SCHEMA IF NOT EXISTS etl;

CREATE TABLE raw.raw_product_item (
  raw_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  source VARCHAR(128) NOT NULL,
  external_id VARCHAR(128) NOT NULL,
  url VARCHAR(1024) NOT NULL,
  name VARCHAR(512) NOT NULL,
  category_name VARCHAR(256) NULL,
  price DECIMAL(12,4) NULL,
  currency CHAR(3) NULL,
  availability VARCHAR(32) NULL,
  rating TINYINT NULL,
  raw_payload JSON NOT NULL,
  crawl_fingerprint CHAR(32) NOT NULL,
  batch_id VARCHAR(64) NOT NULL,
  captured_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_raw_fingerprint (source, external_id, crawl_fingerprint),
  KEY idx_raw_batch (batch_id),
  KEY idx_raw_source_external (source, external_id, captured_at)
) ENGINE=InnoDB;

CREATE TABLE ods.ods_product_snapshot (
  ods_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  raw_id BIGINT NOT NULL UNIQUE,
  source VARCHAR(128) NOT NULL,
  external_id VARCHAR(128) NOT NULL,
  url VARCHAR(1024) NOT NULL,
  product_name VARCHAR(512) NOT NULL,
  category_name VARCHAR(256) NULL,
  price DECIMAL(12,4) NULL,
  currency CHAR(3) NULL,
  availability VARCHAR(32) NULL,
  rating TINYINT NULL,
  raw_payload JSON NOT NULL,
  captured_at TIMESTAMP NOT NULL,
  batch_id VARCHAR(64) NOT NULL,
  etl_created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_ods_source_external (source, external_id)
) ENGINE=InnoDB;

CREATE TABLE dim.dim_category (
  category_key INT AUTO_INCREMENT PRIMARY KEY,
  category_name VARCHAR(256) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE dim.dim_product (
  product_key BIGINT AUTO_INCREMENT PRIMARY KEY,
  source VARCHAR(128) NOT NULL,
  external_id VARCHAR(128) NOT NULL,
  product_name VARCHAR(512) NOT NULL,
  product_url VARCHAR(1024) NOT NULL,
  first_seen_at TIMESTAMP NOT NULL,
  last_seen_at TIMESTAMP NOT NULL,
  UNIQUE KEY uq_product_identity (source, external_id)
) ENGINE=InnoDB;

CREATE TABLE dim.dim_date (
  date_key INT PRIMARY KEY,
  calendar_date DATE NOT NULL UNIQUE,
  year SMALLINT NOT NULL,
  month TINYINT NOT NULL,
  day TINYINT NOT NULL,
  week_of_year TINYINT NOT NULL,
  weekday TINYINT NOT NULL
) ENGINE=InnoDB;

CREATE TABLE dwd.fact_price_snapshot (
  fact_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  snapshot_date_key INT NOT NULL,
  product_key BIGINT NOT NULL,
  category_key INT NULL,
  source VARCHAR(128) NOT NULL,
  price DECIMAL(12,4) NULL,
  availability VARCHAR(32) NULL,
  rating TINYINT NULL,
  ods_raw_id BIGINT NOT NULL UNIQUE,
  KEY idx_fact_date_product (snapshot_date_key, product_key),
  CONSTRAINT fk_fact_date FOREIGN KEY (snapshot_date_key) REFERENCES dim.dim_date(date_key),
  CONSTRAINT fk_fact_product FOREIGN KEY (product_key) REFERENCES dim.dim_product(product_key),
  CONSTRAINT fk_fact_category FOREIGN KEY (category_key) REFERENCES dim.dim_category(category_key)
) ENGINE=InnoDB;

CREATE TABLE dws.product_daily_price (
  date_key INT NOT NULL,
  product_key BIGINT NOT NULL,
  source VARCHAR(128) NOT NULL,
  min_price DECIMAL(12,4) NOT NULL,
  max_price DECIMAL(12,4) NOT NULL,
  avg_price DECIMAL(12,4) NOT NULL,
  last_price DECIMAL(12,4) NOT NULL,
  snapshot_count INT NOT NULL,
  PRIMARY KEY (date_key, product_key, source),
  CONSTRAINT fk_dws_date FOREIGN KEY (date_key) REFERENCES dim.dim_date(date_key)
) ENGINE=InnoDB;

CREATE TABLE ads.price_anomaly (
  anomaly_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  date_key INT NOT NULL,
  product_key BIGINT NOT NULL,
  source VARCHAR(128) NOT NULL,
  current_price DECIMAL(12,4) NOT NULL,
  previous_price DECIMAL(12,4) NOT NULL,
  change_rate DECIMAL(10,4) NOT NULL,
  anomaly_type VARCHAR(32) NOT NULL,
  UNIQUE KEY uq_anomaly (date_key, product_key, source),
  CONSTRAINT fk_ads_date FOREIGN KEY (date_key) REFERENCES dim.dim_date(date_key),
  CONSTRAINT fk_ads_product FOREIGN KEY (product_key) REFERENCES dim.dim_product(product_key)
) ENGINE=InnoDB;

CREATE TABLE etl.job_run (
  run_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  job_name VARCHAR(128) NOT NULL,
  status VARCHAR(32) NOT NULL,
  started_at TIMESTAMP NOT NULL,
  finished_at TIMESTAMP NULL,
  KEY idx_job_status (job_name, status, started_at)
) ENGINE=InnoDB;
