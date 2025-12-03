# 📊 Audit Guide: Lighthouse & Accessibility

## Overview

This guide explains how to run performance and accessibility audits for the DAM Frontend.

## Prerequisites

### Install Dependencies

```bash
# Install Lighthouse CI (if not already installed)
npm install -g @lhci/cli

# Or use pnpm
pnpm add -D @lhci/cli
```

## Lighthouse Audit

### Quick Start

1. **Start the development server:**
   ```bash
   pnpm dev
   ```

2. **Run Lighthouse audit:**
   ```bash
   pnpm run audit:lighthouse
   ```

### Manual Lighthouse Audit

1. **Open Chrome DevTools** (F12)
2. **Go to Lighthouse tab**
3. **Select categories:**
   - ✅ Performance
   - ✅ Accessibility
   - ✅ Best Practices
   - ✅ SEO
4. **Click "Generate report"**

### Targets

| Metric | Target | Current |
|--------|--------|---------|
| Performance | 90+ | TBD |
| Accessibility | 95+ | TBD |
| Best Practices | 95+ | TBD |
| SEO | 90+ | TBD |

### Performance Metrics

- **First Contentful Paint (FCP)**: < 2.0s
- **Largest Contentful Paint (LCP)**: < 2.5s
- **Total Blocking Time (TBT)**: < 300ms
- **Cumulative Layout Shift (CLS)**: < 0.1
- **Speed Index**: < 3.0s

## Accessibility Audit

### Quick Start

```bash
# Run accessibility unit tests
pnpm run test:accessibility

# Run full accessibility audit
pnpm run audit:accessibility
```

### Using axe-core

The project uses `vitest-axe` for automated accessibility testing:

```typescript
import { axe, toHaveNoViolations } from 'vitest-axe'

expect.extend(toHaveNoViolations)

it('should have no accessibility violations', async () => {
  const { container } = render(MyComponent)
  const results = await axe(container)
  expect(results).toHaveNoViolations()
})
```

### WCAG 2.1 AA Compliance

All components must comply with WCAG 2.1 AA standards:

- ✅ Color contrast: 4.5:1 for text
- ✅ Keyboard navigation: Full support
- ✅ Screen reader: Tested with NVDA/JAWS
- ✅ Focus indicators: Visible
- ✅ ARIA labels: Properly implemented
- ✅ Touch targets: 44px minimum

## Screen Reader Testing

See [SCREEN-READER-TESTING.md](./SCREEN-READER-TESTING.md) for detailed instructions.

### Quick Test Checklist

- [ ] Navigate with Tab key
- [ ] All interactive elements focusable
- [ ] ARIA labels announced correctly
- [ ] Form labels associated
- [ ] Error messages announced
- [ ] Modal focus management works

## Continuous Integration

### GitHub Actions

Add to `.github/workflows/audit.yml`:

```yaml
name: Audit

on: [push, pull_request]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: pnpm install
      - run: pnpm run audit:lighthouse

  accessibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: pnpm install
      - run: pnpm run audit:accessibility
```

## Troubleshooting

### Lighthouse Fails to Start Server

**Issue**: `startServerCommand` fails

**Solution**: 
- Ensure `pnpm dev` works manually
- Check port 5173 is available
- Increase `startServerReadyTimeout` in `lighthouse.config.js`

### Accessibility Tests Fail

**Issue**: Tests report violations

**Solution**:
1. Check violation details in test output
2. Fix issues in components
3. Re-run tests: `pnpm run test:accessibility`

### Screen Reader Not Announcing

**Issue**: Screen reader doesn't announce content

**Solution**:
1. Check ARIA labels are present
2. Verify semantic HTML structure
3. Test with different screen readers
4. Check browser console for errors

## Resources

- [Lighthouse Documentation](https://developers.google.com/web/tools/lighthouse)
- [axe-core Documentation](https://github.com/dequelabs/axe-core)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM Accessibility Checklist](https://webaim.org/standards/wcag/checklist)

---

**Last Updated**: 2025-01-27  
**Version**: 1.0









