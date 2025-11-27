#!/bin/sh

export PGPASSWORD="$DJANGO_DB_PASSWORD"
export TEMP_DB="temp_$DJANGO_DB_NAME"

# 1. Create a temporary copy of the database
echo "Creating temporary database $TEMP_DB…"

psql -h "$DJANGO_DB_HOST" -U "$DJANGO_DB_USER" -d postgres -c \
    "CREATE DATABASE $TEMP_DB TEMPLATE $DJANGO_DB_NAME;"

# 2. Generate all UPDATE statements dynamically
UPDATES=$(psql -h "$DJANGO_DB_HOST" -U "$DJANGO_DB_USER" -d "$TEMP_DB" -Atqc "
    SELECT 'UPDATE '
        || quote_ident(n.nspname) || '.' || quote_ident(c.relname)
        || ' SET ' || quote_ident(a.attname)
        || ' = '''';'
    FROM pg_attribute a
    JOIN pg_class c ON c.oid = a.attrelid
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE a.attname = 'email'
      AND a.attnum > 0
      AND NOT a.attisdropped
      AND n.nspname NOT IN ('pg_catalog','information_schema');
")

echo "Hiding email addresses…"
echo "$UPDATES" | psql -h "$DJANGO_DB_HOST" -U "$DJANGO_DB_USER" -d "$TEMP_DB"

# 3. Dump the DB
echo "Creating dump…"
pg_dump -h "$DJANGO_DB_HOST" -U "$DJANGO_DB_USER" -d "$TEMP_DB" | gzip -9 > ./data/nest.sql.gz

# 4. Drop the temporary database
echo "Dropping temporary database $TEMP_DB…"
psql -h "$DJANGO_DB_HOST" -U "$DJANGO_DB_USER" -d postgres -c "DROP DATABASE $TEMP_DB;"

echo "Dump created: data/nest.sql.gz"
