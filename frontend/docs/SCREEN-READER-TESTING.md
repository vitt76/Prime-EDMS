# 🎧 Screen Reader Testing Guide

## Overview

This guide provides instructions for testing the DAM Frontend with screen readers to ensure WCAG 2.1 AA compliance.

## Supported Screen Readers

- **NVDA** (NonVisual Desktop Access) - Windows (Free, Open Source)
- **JAWS** (Job Access With Speech) - Windows (Commercial)
- **VoiceOver** - macOS/iOS (Built-in)
- **TalkBack** - Android (Built-in)

## Prerequisites

### NVDA Setup (Windows)

1. Download NVDA from https://www.nvaccess.org/download/
2. Install NVDA
3. Start NVDA (Ctrl+Alt+N)
4. Configure NVDA:
   - Preferences → Settings → Browse Mode
   - Enable "Use screen layout when possible"
   - Enable "Report formatting"

### JAWS Setup (Windows)

1. Install JAWS (requires license)
2. Start JAWS
3. Configure JAWS:
   - Insert+J → Settings → Web/HTML/PDF
   - Enable "Use virtual cursor"
   - Enable "Announce page structure"

## Testing Checklist

### Navigation Testing

#### Keyboard Navigation
- [ ] Tab through all interactive elements
- [ ] Shift+Tab to navigate backwards
- [ ] Enter/Space to activate buttons
- [ ] Arrow keys to navigate lists/menus
- [ ] Escape to close modals
- [ ] No keyboard traps

#### Screen Reader Navigation
- [ ] H key to navigate headings
- [ ] L key to navigate links
- [ ] B key to navigate buttons
- [ ] F key to navigate form fields
- [ ] R key to navigate regions
- [ ] G key to navigate landmarks

### Page Structure

#### Dashboard Page
- [ ] Main heading announced correctly
- [ ] Stats cards have proper labels
- [ ] Activity feed announced as list
- [ ] Storage metrics progress bar announced
- [ ] Quick actions buttons have labels
- [ ] Recent assets grid announced correctly

#### Settings Page
- [ ] Page title announced
- [ ] Form sections announced
- [ ] Input fields have labels
- [ ] Checkboxes have labels
- [ ] Buttons have descriptive labels
- [ ] Error messages announced

#### Gallery Page
- [ ] Asset cards announced correctly
- [ ] Bulk selection announced
- [ ] Filters panel announced
- [ ] Pagination controls announced
- [ ] Search results announced

### Form Testing

- [ ] All inputs have associated labels
- [ ] Required fields announced
- [ ] Error messages announced
- [ ] Validation messages clear
- [ ] Form submission announced

### Modal Testing

- [ ] Modal opens and focus moves to modal
- [ ] Modal title announced
- [ ] Modal content announced
- [ ] Close button accessible
- [ ] Escape key closes modal
- [ ] Focus returns to trigger after close

### Image Testing

- [ ] All images have alt text
- [ ] Decorative images have empty alt
- [ ] Complex images have descriptions
- [ ] Image links have descriptive text

### Color and Contrast

- [ ] Information not conveyed by color alone
- [ ] Sufficient color contrast (4.5:1 for text)
- [ ] Focus indicators visible
- [ ] Error states clear without color

## Testing Scenarios

### Scenario 1: Navigate to Dashboard

1. Start screen reader
2. Open application
3. Navigate to Dashboard (H key or Tab)
4. Verify:
   - Welcome message announced
   - Stats cards announced with values
   - Activity feed announced as list
   - Storage metrics announced

### Scenario 2: Search for Assets

1. Navigate to Search (H key or Tab)
2. Find search input (F key)
3. Type search query
4. Verify:
   - Search results announced
   - Result count announced
   - Each result has descriptive text
   - Can navigate results with arrow keys

### Scenario 3: Change Settings

1. Navigate to Settings (H key or Tab)
2. Find theme selector (F key)
3. Change theme
4. Verify:
   - Current selection announced
   - Options announced
   - Change confirmed

### Scenario 4: Bulk Operations

1. Navigate to Gallery
2. Select multiple assets (Checkbox navigation)
3. Open bulk actions
4. Verify:
   - Selection count announced
   - Action buttons announced
   - Modal opens with focus
   - Progress announced

## Common Issues to Check

### Missing Labels
- Buttons without text
- Icons without labels
- Links without descriptive text

### Focus Management
- Focus lost after actions
- Focus not moved to modals
- Focus not returned after close

### ARIA Issues
- Missing ARIA labels
- Incorrect ARIA roles
- ARIA attributes not updated

### Announcements
- Dynamic content not announced
- Status changes not announced
- Error messages not announced

## Testing Tools

### Browser Extensions
- **WAVE** (Web Accessibility Evaluation Tool)
- **axe DevTools**
- **Lighthouse** (Accessibility audit)

### Automated Testing
```bash
# Run accessibility tests
pnpm test -- tests/unit/**/*.accessibility.spec.ts

# Run full accessibility audit
pnpm run audit:accessibility
```

## Reporting Issues

When reporting accessibility issues, include:

1. **Screen Reader**: NVDA/JAWS/VoiceOver
2. **Browser**: Chrome/Firefox/Edge
3. **Page/Component**: Dashboard/Settings/etc.
4. **Issue Description**: What was expected vs. what happened
5. **Steps to Reproduce**: Detailed steps
6. **WCAG Criteria**: Which guideline is violated

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [NVDA User Guide](https://www.nvaccess.org/files/nvda/documentation/userGuide.html)
- [JAWS User Guide](https://www.freedomscientific.com/training/jaws/)
- [WebAIM Screen Reader Testing](https://webaim.org/articles/screenreader_testing/)

## Quick Reference

### NVDA Shortcuts
- **Insert+Q**: Exit NVDA
- **Insert+F7**: Elements list
- **Insert+F6**: Object navigation
- **NVDA+Space**: Toggle speech
- **H**: Next heading
- **L**: Next link
- **B**: Next button
- **F**: Next form field

### JAWS Shortcuts
- **Insert+F7**: Elements list
- **Insert+F6**: Virtual PC cursor
- **H**: Next heading
- **L**: Next link
- **B**: Next button
- **F**: Next form field
- **Insert+Escape**: Exit JAWS

---

**Last Updated**: 2025-01-27  
**Version**: 1.0














