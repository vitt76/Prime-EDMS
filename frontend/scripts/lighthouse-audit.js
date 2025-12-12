#!/usr/bin/env node

/**
 * Lighthouse Audit Script
 * Runs Lighthouse CI on all pages and generates reports
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

function runLighthouseAudit() {
  console.log('🚀 Starting Lighthouse Audit...\n')
  console.log('Targets:')
  console.log('  - Performance: 90+')
  console.log('  - Accessibility: 95+')
  console.log('  - Best Practices: 95+')
  console.log('  - SEO: 90+\n')

  const resultsDir = path.resolve(__dirname, '../tmp/lighthouse-reports')
  fs.mkdirSync(resultsDir, { recursive: true })

  try {
    // Run Lighthouse CI
    console.log('📊 Running Lighthouse CI...')
    execSync('lhci autorun', {
      stdio: 'inherit',
      cwd: path.resolve(__dirname, '..'),
      env: {
        ...process.env,
        LHCI_GITHUB_APP_TOKEN: process.env.LHCI_GITHUB_APP_TOKEN || ''
      }
    })

    console.log('\n✅ Lighthouse audit completed!')
    console.log(`📁 Reports saved to: ${resultsDir}`)
  } catch (error) {
    console.error('\n❌ Lighthouse audit failed!')
    console.error('Make sure the dev server is running: pnpm dev')
    process.exit(1)
  }
}

if (require.main === module) {
  runLighthouseAudit()
}

module.exports = { runLighthouseAudit }




















