# Public Frontend DEV Guide

## Overview

Public marketing site runs as a Nuxt 3 SSR app on `http://localhost:3000` and consumes Django public API endpoints under `/api/v4/public/*`.

## Services

- Django backend: `http://localhost:8080`
- Admin SPA (DAM): `http://localhost:5173`
- Public frontend (Nuxt): `http://localhost:3000`

## Run in DEV

```bash
docker-compose up -d
cd public-frontend
npm install
npm run dev
```

## API Endpoints

- `GET /api/v4/public/pages/{slug}/`
- `GET /api/v4/public/posts/`
- `GET /api/v4/public/posts/{slug}/`
- `GET /api/v4/public/plans/`
- `GET /api/v4/public/faq/`
- `POST /api/v4/public/leads/`
- `POST /api/v4/public/auth/register/`
- `POST /api/v4/public/auth/verify-email/`

## Fixtures

Load initial data:

```bash
python manage.py loaddata mayan/apps/marketing_cms/fixtures/initial_data.json
```
