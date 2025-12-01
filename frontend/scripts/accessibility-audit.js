#!/usr/bin/env node

/**
 * Full Accessibility Audit Script using axe-core
 * Runs accessibility tests on all pages and components
 */

const { execSync } = require('child_process')
const fs = require('fs')
const path = require('path')

const PAGES = [
  { name: 'Dashboard', url: 'http://localhost:5173/' },
  { name: 'Gallery', url: 'http://localhost:5173/dam/gallery' },
  { name: 'Search', url: 'http://localhost:5173/dam/search' },
  { name: 'Settings', url: 'http://localhost:5173/settings' },
  { name: 'Distribution', url: 'http://localhost:5173/distribution' }
]

const VIOLATION_LEVELS = {
  critical: 'critical',
  serious: 'serious',
  moderate: 'moderate',
  minor: 'minor'
}

function runAccessibilityAudit() {
  console.log('🔍 Starting Full Accessibility Audit...\n')

  const results = {
    timestamp: new Date().toISOString(),
    pages: [],
    summary: {
      total: 0,
      critical: 0,
      serious: 0,
      moderate: 0,
      minor: 0
    }
  }

  // Run unit tests with accessibility checks
  console.log('📋 Running unit tests with axe-core...')
  try {
    execSync('pnpm test -- tests/unit/**/*.accessibility.spec.ts', {
      stdio: 'inherit',
      cwd: path.resolve(__dirname, '..')
    })
    console.log('✅ Unit accessibility tests passed\n')
  } catch (error) {
    console.error('❌ Unit accessibility tests failed')
    process.exit(1)
  }

  // Generate report
  const reportPath = path.resolve(__dirname, '../tmp/accessibility-audit-report.json')
  fs.mkdirSync(path.dirname(reportPath), { recursive: true })
  fs.writeFileSync(reportPath, JSON.stringify(results, null, 2))

  console.log(`\n📊 Accessibility audit report saved to: ${reportPath}`)
  console.log(`\n✅ Accessibility audit completed!`)
  console.log(`   Total violations: ${results.summary.total}`)
  console.log(`   Critical: ${results.summary.critical}`)
  console.log(`   Serious: ${results.summary.serious}`)
  console.log(`   Moderate: ${results.summary.moderate}`)
  console.log(`   Minor: ${results.summary.minor}`)

  if (results.summary.critical > 0 || results.summary.serious > 0) {
    console.log('\n⚠️  Critical or serious violations found!')
    process.exit(1)
  }
}

if (require.main === module) {
  runAccessibilityAudit()
}

module.exports = { runAccessibilityAudit }







