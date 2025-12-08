# Environment Variables

This document describes all environment variables used by the frontend application.

## Required Variables

### `VITE_API_URL`
- **Description**: Base URL for the Django REST API
- **Default**: `http://localhost:8000/api`
- **Example**: `https://api.example.com/api`
- **Usage**: Used by `apiService` to make HTTP requests to the backend

### `VITE_WS_URL`
- **Description**: WebSocket URL for real-time updates
- **Default**: `ws://localhost:8000/ws`
- **Example**: `wss://api.example.com/ws`
- **Usage**: Used for WebSocket connections (notifications, real-time updates)

## Optional Variables

### `VITE_APP_ENV`
- **Description**: Application environment (development, staging, production)
- **Default**: `development`
- **Example**: `production`
- **Usage**: Used to enable/disable features based on environment

### `VITE_ENABLE_ANALYTICS`
- **Description**: Enable analytics tracking
- **Default**: `false`
- **Example**: `true`
- **Usage**: Controls whether analytics are enabled

### `VITE_ENABLE_ERROR_TRACKING`
- **Description**: Enable error tracking (e.g., Sentry)
- **Default**: `false`
- **Example**: `true`
- **Usage**: Controls whether error tracking is enabled

### `VITE_BFF_ENABLED`
- **Description**: Включает использование headless/BFF endpoint’ов (`/api/v4/headless/*`)
- **Default**: `false`
- **Example**: `true`
- **Usage**: При `true` фронтенд вызывает headless пароли/конфиг типов/лента активности

### `VITE_SENTRY_DSN`
- **Description**: Sentry DSN for error tracking
- **Default**: (empty)
- **Example**: `https://xxx@xxx.ingest.sentry.io/xxx`
- **Usage**: Sentry DSN for error reporting (only used if `VITE_ENABLE_ERROR_TRACKING` is true)

### `VITE_PUBLIC_URL`
- **Description**: Public URL of the application (for production)
- **Default**: (empty)
- **Example**: `https://dam.example.com`
- **Usage**: Used for generating absolute URLs (e.g., in emails, sharing)

## Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update the values in `.env` according to your environment.

3. Restart the development server if it's running:
   ```bash
   npm run dev
   ```

## Notes

- All environment variables must be prefixed with `VITE_` to be accessible in the frontend code.
- Environment variables are embedded at build time, not runtime.
- Never commit `.env` files to version control (they are already in `.gitignore`).
- For production builds, set environment variables in your CI/CD pipeline or hosting platform.

