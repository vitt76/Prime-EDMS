# MADDAM Public Frontend (Nuxt 3)

SSR Nuxt 3 frontend for the MADDAM public marketing site.

## Features

- Server-Side Rendering (SSR) for SEO optimization
- Internationalization (RU/EN) with URL prefixes
- Dark mode support
- Responsive design with mobile-first approach
- Accessibility (WCAG 2.1 Level AA)
- Performance optimizations (image optimization, caching, lazy loading)
- Google Analytics integration
- Component-based architecture

## Tech Stack

- **Framework**: Nuxt 3
- **UI**: Tailwind CSS, Headless UI
- **Icons**: Heroicons
- **State Management**: Pinia
- **Form Validation**: Zod
- **Testing**: Vitest (unit), Playwright (E2E)
- **Mock Server**: MSW (Mock Service Worker)

## Prerequisites

- Node.js 18+
- npm or yarn
- Django backend running on `http://localhost:8080`

## Installation

1. Install dependencies:

```bash
cd public-frontend
npm install
```

2. Copy environment file:

```bash
cp .env.example .env.development
```

3. Update environment variables in `.env.development` if needed:

```
NUXT_PUBLIC_API_URL=http://localhost:8080
NUXT_PUBLIC_APP_URL=http://localhost:5173
NUXT_PUBLIC_SITE_URL=http://localhost:3000
NUXT_PUBLIC_GA_ID=  # Optional: Google Analytics ID
```

## Development

Start the development server:

```bash
npm run dev
```

The site will be available at `http://localhost:3000`

## Build

Build for production:

```bash
npm run build
```

Preview production build:

```bash
npm run preview
```

## Testing

### Unit Tests

```bash
npm run test
```

### E2E Tests

```bash
npm run test:e2e
```

## Project Structure

```
public-frontend/
├── assets/              # Static assets (CSS, images)
├── components/          # Vue components
│   ├── Blog/           # Blog-related components
│   ├── Common/         # Reusable UI components
│   ├── Forms/          # Form components
│   ├── Sections/       # Page sections
│   └── SEO/            # SEO components
├── composables/         # Vue composables
├── layouts/            # Page layouts
├── locales/            # i18n translations
├── pages/              # File-based routing
├── plugins/            # Nuxt plugins
├── public/             # Static files
├── server/             # Server middleware
├── stores/             # Pinia stores
├── tests/              # Test files
│   ├── e2e/           # Playwright E2E tests
│   ├── integration/   # Integration tests
│   ├── mocks/         # MSW mock handlers
│   └── unit/          # Vitest unit tests
└── types/              # TypeScript types
```

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npm run test` | Run unit tests |
| `npm run test:e2e` | Run E2E tests |
| `npm run lint` | Lint code |
| `npm run format` | Format code with Prettier |

## Configuration

### Nuxt Config

Key configuration in `nuxt.config.ts`:

- **SSR**: Enabled by default
- **i18n**: Russian (default) and English locales
- **Image**: IPX provider with WebP/AVIF support
- **Color Mode**: System preference with light fallback
- **Route Rules**: SWR caching for static pages

### Tailwind Config

Custom theme extensions in `tailwind.config.ts`:

- Extended color palette (primary, neutral, success, error, etc.)
- Custom font families (Inter, Berkeley Mono)
- Animation keyframes
- Dark mode class-based switching

## API Integration

The frontend communicates with the Django backend through proxied API calls:

- `/api/v4/public/pages/:slug/` - Get page content
- `/api/v4/public/posts/` - List blog posts
- `/api/v4/public/plans/` - Get pricing plans
- `/api/v4/public/faq/` - Get FAQ items
- `/api/v4/public/leads/` - Submit contact/lead forms
- `/api/v4/public/register/` - User registration
- `/api/v4/public/verify-email/:token/` - Email verification

## Contributing

1. Follow the existing code style
2. Write tests for new components
3. Update translations for both RU and EN
4. Test on mobile devices
5. Run linter before committing

## License

Proprietary - All rights reserved.
