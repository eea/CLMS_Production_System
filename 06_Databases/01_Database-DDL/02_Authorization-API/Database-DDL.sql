CREATE TABLE public."user" (
	id serial4 NOT NULL,
	username varchar(40) NULL,
	"password" varchar(128) NULL,
	CONSTRAINT user_password_key UNIQUE (password),
	CONSTRAINT user_pkey PRIMARY KEY (id),
	CONSTRAINT user_username_key UNIQUE (username)
);

CREATE TABLE public.oauth2_client (
	client_id varchar(48) NULL,
	client_secret varchar(120) NULL,
	client_id_issued_at int4 NOT NULL,
	client_secret_expires_at int4 NOT NULL,
	client_metadata text NULL,
	id serial4 NOT NULL,
	user_id int4 NULL,
	created_at timestamp(0) NOT NULL DEFAULT now(),
	deleted_at timestamp(0) NULL,
	updated_at timestamp(0) NULL,
	CONSTRAINT oauth2_client_pkey PRIMARY KEY (id),
	CONSTRAINT oauth2_client_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id) ON DELETE CASCADE
);
CREATE INDEX ix_oauth2_client_client_id ON public.oauth2_client USING btree (client_id);

CREATE TABLE public.oauth2_token (
	client_id varchar(48) NULL,
	token_type varchar(40) NULL,
	access_token varchar(255) NOT NULL,
	refresh_token varchar(255) NULL,
	"scope" text NULL,
	revoked bool NULL,
	issued_at int4 NOT NULL,
	expires_in int4 NOT NULL,
	id serial4 NOT NULL,
	user_id int4 NULL,
	created_at timestamp NOT NULL DEFAULT now(),
	deleted_at timestamp NULL,
	updated_at timestamp(0) NULL,
	CONSTRAINT oauth2_token_access_token_key UNIQUE (access_token),
	CONSTRAINT oauth2_token_pkey PRIMARY KEY (id),
	CONSTRAINT oauth2_token_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id) ON DELETE CASCADE
);
CREATE INDEX ix_oauth2_token_refresh_token ON public.oauth2_token USING btree (refresh_token);