# DAM Frontend

Modern Digital Asset Management (DAM) system frontend built with Vue 3, TypeScript, and Tailwind CSS.

## 🚀 Tech Stack

- **Framework**: Vue 3 (Composition API)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS with dark mode support
- **State Management**: Pinia with persistence
- **Routing**: Vue Router
- **HTTP Client**: Axios with interceptors
- **Build Tool**: Vite
- **Testing**: Vitest (unit) + Playwright (E2E)
- **Component Docs**: Storybook

## 📋 Prerequisites

- Node.js 18+ 
- npm 9+ (or pnpm 8+)
- Backend API running on `http://localhost:8000`

## 🛠️ Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and configure:
   ```env
   VITE_API_URL=http://localhost:8000/api
   VITE_WS_URL=ws://localhost:8000/ws
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```
   
   App will be available at `http://localhost:5173`

## 📜 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier
- `npm run type-check` - Type check with TypeScript
- `npm run test` - Run unit tests
- `npm run test:ui` - Run tests with UI
- `npm run test:coverage` - Run tests with coverage
- `npm run test:e2e` - Run E2E tests
- `npm run storybook` - Start Storybook
- `npm run build-storybook` - Build Storybook

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable components
│   │   ├── Common/     # Base components (Button, Input, Modal, etc.)
│   │   └── Layout/     # Layout components (Header, Sidebar, etc.)
│   ├── pages/          # Page components
│   ├── stores/         # Pinia stores
│   ├── services/       # API services
│   ├── composables/    # Vue composables
│   ├── utils/          # Utility functions
│   ├── types/          # TypeScript types
│   ├── router/         # Vue Router configuration
│   └── styles/         # Global styles
├── tests/
│   ├── unit/          # Unit tests
│   ├── e2e/           # E2E tests
│   └── setup/         # Test setup files
├── public/            # Static assets
└── .storybook/        # Storybook configuration
```

## 🎨 Design System

The project uses a comprehensive design system with:

- **Colors**: Primary, neutral, semantic (success, warning, error, info)
- **Typography**: System fonts with defined sizes and weights
- **Spacing**: 8px base unit scale
- **Shadows**: Elevation system (xs, sm, md, lg, xl, 2xl)
- **Border Radius**: Consistent radius scale
- **Dark Mode**: Full support with CSS variables

See `tailwind.config.js` and `src/styles/index.css` for details.

## 🧪 Testing

### Unit Tests
```bash
npm run test
```

Tests are located in `tests/unit/` and use Vitest + Vue Test Utils.

**⚠️ Note:** E2E tests are automatically excluded from unit tests. Use `npm run test:e2e` for Playwright tests.

### E2E Tests
```bash
npm run test:e2e
```

E2E tests use Playwright and are located in `tests/e2e/`. They run in real browsers and require the dev server to be running (or will start it automatically).

### Component Documentation
```bash
npm run storybook
```

Storybook provides interactive component documentation at `http://localhost:6006`.

## 🏗️ Building for Production

```bash
npm run build
```

Output will be in `dist/` directory, ready for deployment.

## 🔧 Configuration

### TypeScript
Configuration in `tsconfig.json` with strict mode enabled.

### ESLint
Configuration in `.eslintrc.cjs` with Vue 3 and TypeScript rules.

### Prettier
Configuration in `.prettierrc.json` with Tailwind plugin.

### Vite
Configuration in `vite.config.ts` with:
- Path aliases (`@/` → `src/`)
- Proxy for API requests
- Code splitting
- Source maps

## 📦 Components

### Base Components (Created)

1. **Button** - Primary, secondary, outline, ghost, danger variants
2. **Input** - Text input with label, error, hint support
3. **Modal** - Dialog component with backdrop and animations
4. **Card** - Container component with header/footer slots
5. **Badge** - Status badges with variants

All components:
- Support dark mode
- Are fully typed (TypeScript)
- Have Storybook stories
- Include unit tests
- Follow accessibility best practices

## 🔌 API Integration

API client is configured in `src/services/apiService.ts` with:

- Automatic CSRF token handling
- JWT token management
- Request/response interceptors
- Error handling
- Type-safe responses

## 🚢 CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`) runs:

1. Lint & format check
2. Unit tests with coverage
3. E2E tests
4. Production build

## 📝 Development Guidelines

1. **TypeScript**: Use strict mode, avoid `any`
2. **Components**: Use Composition API with `<script setup>`
3. **Styling**: Use Tailwind utilities, avoid inline styles
4. **State**: Use Pinia stores for global state
5. **Testing**: Write tests for all components and utilities
6. **Documentation**: Add Storybook stories for new components

## 🐛 Troubleshooting

### Port already in use
Change port in `vite.config.ts` or use:
```bash
npm run dev -- --port 3000
```

### API connection issues
Check `.env` file and ensure backend is running on correct port.

### Type errors
Run `npm run type-check` to see detailed TypeScript errors.

## 📚 Resources

- [Vue 3 Documentation](https://vuejs.org/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [Vite Documentation](https://vitejs.dev/)

## 📄 License

Proprietary - Internal use only


