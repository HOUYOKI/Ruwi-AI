#!/bin/sh
set -eu
rm -f backend/ruwi.db backend/test_ruwi.db
cd backend
alembic upgrade head
python -m app.seed
