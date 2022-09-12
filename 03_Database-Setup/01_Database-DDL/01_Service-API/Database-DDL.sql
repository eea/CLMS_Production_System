CREATE SCHEMA customer AUTHORIZATION postgres;
CREATE SCHEMA grafana_monitoring AUTHORIZATION postgres;
CREATE SCHEMA indices AUTHORIZATION postgres;
CREATE SCHEMA logging AUTHORIZATION postgres;
CREATE SCHEMA msgeovilleconfig AUTHORIZATION postgres;
CREATE SCHEMA national_products AUTHORIZATION postgres;

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
	company_name varchar(1024) NULL,
	active bool NULL DEFAULT true,
	created_at timestamptz NOT NULL DEFAULT now(),
	deleted_at timestamptz NULL,
	"password" varchar(128) NULL,
	CONSTRAINT customer_pk PRIMARY KEY (customer_id)
);

CREATE TABLE customer.service_statuses (
	id serial4 NOT NULL,
	status_name varchar(32) NOT NULL,
	created_at timestamp(0) NOT NULL DEFAULT now(),
	deleted_at timestamp(0) NULL
);

CREATE TABLE customer.services (
	service_id varchar(64) NOT NULL,
	service_name varchar(500) NULL,
	service_comment varchar(10000) NULL,
	service_validity bool NULL,
	service_owner_geoville varchar(500) NULL,
	created_at timestamptz NOT NULL DEFAULT now(),
	deleted_at timestamptz NULL,
	"external" bool NOT NULL DEFAULT true,
	visible_frontend bool NULL,
	CONSTRAINT services_pk PRIMARY KEY (service_id)
);

CREATE TABLE customer.tasks (
	task_id varchar(64) NOT NULL,
	task_name varchar(500) NOT NULL,
	task_comment varchar(10000) NULL,
	task_validity bool NOT NULL,
	task_owner varchar(500) NOT NULL,
	created_at timestamptz NOT NULL DEFAULT now(),
	deleted_at timestamptz NULL,
	"external" bool NOT NULL DEFAULT true,
	order_id_not_required bool NOT NULL DEFAULT false,
	workflow float4 NULL,
	CONSTRAINT tasks_pk PRIMARY KEY (task_id)
);

CREATE TABLE customer.manual_tasks (
	cell_code varchar(128) NOT NULL,
	customer_id varchar(128) NOT NULL,
	service_id varchar(500) NOT NULL,
	task_id varchar(500) NOT NULL,
	task_started timestamptz NULL,
	task_stopped timestamptz NULL,
	status varchar(64) NULL,
	"result" text NULL,
	created_at timestamp NOT NULL DEFAULT now(),
	deleted_at timestamp NULL,
	refers_to_order_id varchar(128) NULL,
	"comment" varchar(500) NULL,
	CONSTRAINT manual_tasks_pk PRIMARY KEY (cell_code, service_id, task_id),
	CONSTRAINT manual_tasks_fk FOREIGN KEY (task_id) REFERENCES customer.tasks(task_id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT manual_tasks_fk_customer FOREIGN KEY (customer_id) REFERENCES customer.customer(customer_id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT manual_tasks_fk_services FOREIGN KEY (service_id) REFERENCES customer.services(service_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE customer.region_of_interests (
	roi_id varchar(64) NOT NULL,
	roi_name varchar(64) NOT NULL,
	description text NULL,
	customer_id varchar(128) NOT NULL,
	geom public.geometry(multipolygon) NULL,
	created_at timestamptz NOT NULL DEFAULT now(),
	deleted_at timestamptz NULL,
	CONSTRAINT region_of_interests_pk PRIMARY KEY (roi_id),
	CONSTRAINT region_of_interests_fk_customer_id FOREIGN KEY (customer_id) REFERENCES customer.customer(customer_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE customer.roi_service_mapping (
	roi_id varchar(64) NOT NULL,
	service_id varchar(64) NOT NULL,
	created_at timestamptz NOT NULL DEFAULT now(),
	deleted_at timestamp NULL,
	CONSTRAINT roi_service_mapping_pk PRIMARY KEY (roi_id, service_id),
	CONSTRAINT roi_service_mapping_fk_roi_id FOREIGN KEY (roi_id) REFERENCES customer.region_of_interests(roi_id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT roi_service_mapping_fk_service_id FOREIGN KEY (service_id) REFERENCES customer.services(service_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE customer.service_customer_mapping (
	customer_id varchar(128) NOT NULL,
	service_id varchar(64) NOT NULL,
	usage_validity bool NULL,
	usage_start timestamp NOT NULL,
	usage_stop timestamp NULL,
	usage_limit numeric(15) NULL,
	usage_interval varchar(64) NULL,
	created_at timestamptz NOT NULL DEFAULT now(),
	deleted_at timestamp NULL,
	CONSTRAINT service_customer_mapping_pk PRIMARY KEY (customer_id, service_id, usage_start),
	CONSTRAINT service_customer_mapping_fk_customer_id FOREIGN KEY (customer_id) REFERENCES customer.customer(customer_id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT service_customer_mapping_fk_service_id FOREIGN KEY (service_id) REFERENCES customer.services(service_id) ON DELETE CASCADE ON UPDATE CASCADE
);

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
	"result" text NULL,
	order_json jsonb NULL,
	created_at timestamp NOT NULL DEFAULT now(),
	deleted_at timestamp NULL,
	CONSTRAINT service_orders_pk PRIMARY KEY (order_id),
	CONSTRAINT service_orders_fk_customer FOREIGN KEY (customer_id) REFERENCES customer.customer(customer_id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT service_orders_fk_services FOREIGN KEY (service_id) REFERENCES customer.services(service_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE grafana_monitoring.all_units (
	cellcode varchar(80) NULL,
	pu_id numeric(9) NULL,
	spu_id text NULL
);

CREATE TABLE grafana_monitoring.all_units_old (
	cellcode varchar(80) NULL,
	pu_id numeric(9) NULL,
	spu_id varchar(50) NULL
);

CREATE TABLE grafana_monitoring.eu_processing_units (
	ogc_fid serial4 NOT NULL,
	cellcode varchar(80) NULL,
	eoforigin numeric(10) NULL,
	noforigin numeric(10) NULL,
	wkb_geometry public.geometry(polygon, 900914) NULL,
	CONSTRAINT eu_processing_units_pkey PRIMARY KEY (ogc_fid)
);
CREATE INDEX eu_processing_units_cellcode_idx ON grafana_monitoring.eu_processing_units USING btree (cellcode);
CREATE INDEX eu_processing_units_wkb_geometry_geom_idx ON grafana_monitoring.eu_processing_units USING gist (wkb_geometry);

CREATE TABLE grafana_monitoring.eu_production_units (
	ogc_fid serial4 NOT NULL,
	partner varchar(50) NULL,
	pu_id numeric(9) NULL,
	spu_id varchar(50) NULL,
	area_km2 numeric(19, 11) NULL,
	sc numeric(4) NULL,
	wkb_geometry public.geometry(multipolygon, 3035) NULL,
	CONSTRAINT eu_production_units_pkey PRIMARY KEY (ogc_fid)
);
CREATE INDEX eu_production_units_spu_id_idx ON grafana_monitoring.eu_production_units USING btree (spu_id);
CREATE INDEX eu_production_units_wkb_geometry_geom_idx ON grafana_monitoring.eu_production_units USING gist (wkb_geometry);

CREATE TABLE grafana_monitoring.europe_10km_eea39_centroids (
	gid serial4 NOT NULL,
	cellcode varchar(80) NULL,
	geom public.geometry(point, 3035) NULL,
	CONSTRAINT europe_10km_eea39_centroids_pkey PRIMARY KEY (gid)
);
CREATE INDEX europe_10km_eea39_centroids_geom_idx ON grafana_monitoring.europe_10km_eea39_centroids USING gist (geom);


CREATE TABLE grafana_monitoring.new_all_units (
	cellcode varchar(80) NULL,
	spu_id text NULL
);

CREATE TABLE grafana_monitoring.tmp_buffer (
	spu_id text NULL,
	wkb_geom public.geometry NULL
);

CREATE TABLE indices.sentinel_bands (
	"name" varchar(50) NOT NULL,
	band varchar(3) NOT NULL,
	resolution int4 NOT NULL,
	description varchar(1000) NULL,
	CONSTRAINT sentinel_bands_pk PRIMARY KEY (name)
);

CREATE TABLE logging.logging (
	id serial4 NOT NULL,
	service_name varchar(50) NULL,
	order_id varchar(64) NULL,
	log_level varchar(15) NOT NULL,
	log_message text NOT NULL,
	"time_stamp" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	deleted_at timestamp NULL,
	CONSTRAINT logger_pkey PRIMARY KEY (id)
);

CREATE TABLE msgeovilleconfig.airflow_config (
	service_name varchar(500) NOT NULL,
	command varchar(1000) NOT NULL,
	description varchar(1000) NULL,
	created_at timestamp NOT NULL DEFAULT now(),
	deleted_at timestamp NULL,
	CONSTRAINT airflow_config_pk PRIMARY KEY (service_name, command)
);

CREATE TABLE msgeovilleconfig.logger_saver_config (
	"key" varchar(50) NOT NULL,
	value varchar(500) NOT NULL,
	CONSTRAINT logger_saver_config_pk PRIMARY KEY (key, value)
);

CREATE TABLE msgeovilleconfig.message_checker (
	"instance" varchar(64) NOT NULL,
	"key" varchar(64) NOT NULL,
	value varchar(500) NOT NULL,
	created_at timestamp NOT NULL DEFAULT now(),
	deleted_at timestamp NULL,
	updated_at varchar(1024) NULL,
	optional bool NOT NULL DEFAULT false,
	CONSTRAINT message_checker_pl PRIMARY KEY (instance, key, value)
);

CREATE TABLE msgeovilleconfig.message_key (
	"name" varchar(500) NOT NULL,
	"key" varchar(50) NOT NULL,
	CONSTRAINT message_key_pk PRIMARY KEY (name, key)
);

CREATE TABLE national_products.national_product_information (
	id int8 NULL,
	ccode text NULL,
	country text NULL,
	dst_wkt text NULL,
	tr_wkt text NULL,
	path_boundary_shp text NULL,
	geometry public.geometry(geometry) NULL
);
CREATE INDEX idx_national_product_information_geometry ON national_products.national_product_information USING gist (geometry);

CREATE TABLE msgeovilleconfig.message_queue_config (
	service_id varchar(64) NOT NULL,
	queue_name varchar(500) NOT NULL,
	host varchar(500) NOT NULL,
	port varchar(50) NOT NULL,
	created_at timestamp NOT NULL DEFAULT now(),
	deleted_at timestamp NULL,
	CONSTRAINT message_queue_config_pk PRIMARY KEY (service_id, queue_name)
);

ALTER TABLE msgeovilleconfig.message_queue_config ADD CONSTRAINT constraint_fk FOREIGN KEY (service_id) REFERENCES customer.services(service_id) ON DELETE CASCADE;