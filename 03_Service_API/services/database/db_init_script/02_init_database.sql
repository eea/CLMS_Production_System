-- Switch connection to clcplus_backend database
\c clcplus_backend;

------------------------------------------------------------------------------------------------------------------------
-- Creates the PostGIS extension to the public schema
------------------------------------------------------------------------------------------------------------------------
CREATE EXTENSION postgis SCHEMA "public";

------------------------------------------------------------------------------------------------------------------------
-- Creates the necessary schema for the API
------------------------------------------------------------------------------------------------------------------------
CREATE SCHEMA customer AUTHORIZATION postgres;
CREATE SCHEMA msgeovilleconfig AUTHORIZATION postgres;
CREATE SCHEMA logging AUTHORIZATION postgres;

------------------------------------------------------------------------------------------------------------------------
-- Creates the necessary tables for the API
------------------------------------------------------------------------------------------------------------------------
CREATE TABLE customer.customer (
	customer_id varchar(128) NOT NULL,
	title varchar(3) NOT NULL,
	first_name varchar(64) NOT NULL,
	last_name varchar(64) NOT NULL,
	email varchar(128) NOT NULL,
	address varchar(128) NOT NULL,
	city varchar(64) NOT NULL,
	zip_code varchar(16) NOT NULL,
	country varchar(64) NOT NULL,
	nationality varchar(128) NULL,
	phone_number varchar(64) NOT NULL,
	company_name varchar(1000) NULL,
	active bool NULL DEFAULT true,
	created_at timestamptz NOT NULL DEFAULT now(),
	deleted_at timestamptz NULL,
	CONSTRAINT customer_pk PRIMARY KEY (customer_id)
);

------------------------------------------------------------------------------------------------------------------------
-- Creates the necessary tables for the API
------------------------------------------------------------------------------------------------------------------------
CREATE TABLE customer.services (
	service_id varchar(64) NOT NULL,
	service_name varchar(500) NULL,
	service_comment varchar(10000) NULL,
	service_validity bool NULL,
	service_owner_geoville varchar(500) NULL,
	created_at timestamptz NOT NULL DEFAULT now(),
	deleted_at timestamptz NULL,
	external_service bool NOT NULL DEFAULT true,
	CONSTRAINT services_pk PRIMARY KEY (service_id)
);

INSERT INTO customer.services (service_id, service_name, service_comment, service_validity, service_owner_geoville, created_at, external_service) VALUES('5439922d772e8361d5aa6bb40180f7a8150757f39616a0be7ed246749fefde5e', 'logger', 'The internal service that logs', TRUE, 'GeoVille', now(), FALSE);

------------------------------------------------------------------------------------------------------------------------
-- Creates the necessary tables for the API
------------------------------------------------------------------------------------------------------------------------
CREATE TABLE customer.region_of_interests (
	roi_id varchar(64) NOT NULL,
	roi_name varchar(64) NOT NULL,
	description text NULL,
	customer_id varchar(128) NOT NULL,
	geom geometry(MULTIPOLYGON) NULL,
	created_at timestamptz NOT NULL DEFAULT now(),
	deleted_at timestamptz NULL,
	CONSTRAINT region_of_interests_pk PRIMARY KEY (roi_id),
	CONSTRAINT region_of_interests_fk_customer_id FOREIGN KEY (customer_id) REFERENCES customer.customer(customer_id) ON UPDATE CASCADE ON DELETE CASCADE
);

------------------------------------------------------------------------------------------------------------------------
-- Creates the necessary tables for the API
------------------------------------------------------------------------------------------------------------------------
CREATE TABLE customer.roi_service_mapping (
	roi_id varchar(64) NOT NULL,
	service_id varchar(64) NOT NULL,
	created_at timestamptz NOT NULL DEFAULT now(),
	CONSTRAINT roi_service_mapping_pk PRIMARY KEY (roi_id, service_id),
	CONSTRAINT roi_service_mapping_fk_roi_id FOREIGN KEY (roi_id) REFERENCES customer.region_of_interests(roi_id) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT roi_service_mapping_fk_service_id FOREIGN KEY (service_id) REFERENCES customer.services(service_id) ON UPDATE CASCADE ON DELETE CASCADE
);

------------------------------------------------------------------------------------------------------------------------
-- Creates the necessary tables for the API
------------------------------------------------------------------------------------------------------------------------
CREATE TABLE customer.service_customer_mapping (
	customer_id varchar(128) NOT NULL,
	service_id varchar(64) NOT NULL,
	usage_validity bool NULL,
	usage_start timestamp NOT NULL,
	usage_stop timestamp NULL,
	usage_limit numeric(15) NULL,
	usage_interval varchar(64) NULL,
	created_at timestamptz NOT NULL DEFAULT now(),
	CONSTRAINT service_customer_mapping_pk PRIMARY KEY (customer_id, service_id, usage_start),
	CONSTRAINT service_customer_mapping_fk_customer_id FOREIGN KEY (customer_id) REFERENCES customer.customer(customer_id) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT service_customer_mapping_fk_service_id FOREIGN KEY (service_id) REFERENCES customer.services(service_id) ON UPDATE CASCADE ON DELETE CASCADE
);

------------------------------------------------------------------------------------------------------------------------
-- Creates the necessary tables for the API
------------------------------------------------------------------------------------------------------------------------
CREATE TABLE customer.service_orders (
	customer_id varchar(128) NOT NULL,
	service_id varchar(128) NOT NULL,
	order_id varchar(64) NOT NULL,
	order_received timestamptz NOT NULL,
	order_started timestamptz NULL,
	order_stopped timestamptz NULL,
	cancelled_by_user bool NULL,
	cancelled_by_system bool NULL,
	status varchar(64) NULL,
	success bool NULL,
	"result" varchar(512) NULL,
	order_json jsonb NULL,
	CONSTRAINT service_orders_pk PRIMARY KEY (order_id),
	CONSTRAINT service_orders_fk_customer FOREIGN KEY (customer_id) REFERENCES customer.customer(customer_id) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT service_orders_fk_services FOREIGN KEY (service_id) REFERENCES customer.services(service_id) ON UPDATE CASCADE ON DELETE CASCADE
);

------------------------------------------------------------------------------------------------------------------------
---- Creates
------------------------------------------------------------------------------------------------------------------------
CREATE TABLE msgeovilleconfig.airflow_config (
	service_name varchar(500) NOT NULL,
	command varchar(1000) NOT NULL,
	description varchar(1000) NULL,
	CONSTRAINT airflow_config_pk PRIMARY KEY (service_name, command)
);

------------------------------------------------------------------------------------------------------------------------
---- Creates
------------------------------------------------------------------------------------------------------------------------
CREATE TABLE msgeovilleconfig.logger_saver_config (
	"key" varchar(50) NOT NULL,
	value varchar(500) NOT NULL,
	CONSTRAINT logger_saver_config_pk PRIMARY KEY (key, value)
);

INSERT INTO msgeovilleconfig.logger_saver_config ("key", value) VALUES('duration_in_sec', '60');

------------------------------------------------------------------------------------------------------------------------
---- Creates
------------------------------------------------------------------------------------------------------------------------
CREATE TABLE msgeovilleconfig.message_checker (
	"instance" varchar(64) NOT NULL,
	"key" varchar(64) NOT NULL,
	value varchar(500) NOT NULL,
	CONSTRAINT message_checker_pl PRIMARY KEY (instance, key, value)
);

------------------------------------------------------------------------------------------------------------------------
---- Creates
------------------------------------------------------------------------------------------------------------------------
CREATE TABLE msgeovilleconfig.message_key (
	"name" varchar(500) NOT NULL,
	"key" varchar(50) NOT NULL,
	CONSTRAINT message_key_pk PRIMARY KEY (name, key)
);

INSERT INTO msgeovilleconfig.message_key ("name", "key") VALUES('message_key', 'GqcOMRSp6sOm33fyCsN2KxGh6Z-Vi2oLhYHikJ7UM1I=');

------------------------------------------------------------------------------------------------------------------------
---- Creates
------------------------------------------------------------------------------------------------------------------------
CREATE TABLE msgeovilleconfig.message_queue_config (
	service_id varchar(64) NOT NULL,
	queue_name varchar(500) NOT NULL,
	host varchar(500) NOT NULL,
	port varchar(50) NOT NULL,
	CONSTRAINT message_queue_config_pk PRIMARY KEY (service_id, queue_name)
);

ALTER TABLE msgeovilleconfig.message_queue_config ADD CONSTRAINT constraint_fk FOREIGN KEY (service_id) REFERENCES customer.services(service_id) ON DELETE CASCADE;
INSERT INTO msgeovilleconfig.message_queue_config (service_id, queue_name, host, port) VALUES('5439922d772e8361d5aa6bb40180f7a8150757f39616a0be7ed246749fefde5e', 'tools_logger', 'api.clcplusbackbone.geoville.com', '5672');


------------------------------------------------------------------------------------------------------------------------
---- Creates
------------------------------------------------------------------------------------------------------------------------
CREATE TABLE logging.logging (
	id serial NOT NULL,
	service_name varchar(50) NOT NULL,
	log_level varchar(15) NOT NULL,
	log_message text NOT NULL,
	time_stamp timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT logger_pkey PRIMARY KEY (id)
);
