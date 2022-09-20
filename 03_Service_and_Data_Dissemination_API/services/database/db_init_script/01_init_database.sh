#!/bin/bash

# Immediately exits if any error occurs during the script execution. If not set, an error could occur and the script
# would continue its execution.
set -o errexit

# Creating an array that defines the environment variables that must be set. This can be consumed later via arrray
# variable expansion ${REQUIRED_ENV_VARS[@]}.
readonly REQUIRED_ENV_VARS=(
  "DB_DATABASE_NAME"
)

# Checks if all of the required environment variables are set. If one of them isn't, echoes a text explaining which one
# isn't and the name of the ones that need to be
for required_env_var in ${REQUIRED_ENV_VARS[@]}; do
  if [[ -z "${!required_env_var}" ]]; then
    echo "Error:
          Environment variable '$required_env_var' not set.
          Make sure you have the following environment variables set:
          - ${REQUIRED_ENV_VARS[@]}
          Aborting."
    exit 1
  fi
done

# Performs the initialization in the already-started PostgreSQL using the preconfigured POSTGRE_USER user.
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_USER" <<-EOSQL

   CREATE DATABASE $DB_DATABASE_NAME;

EOSQL
