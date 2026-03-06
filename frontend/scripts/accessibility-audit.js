#!/usr/bin/env node

import { execSync } from 'node:child_process'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const projectRoot = path.resolve(__dirname, '..')

function runStep(label, command) {
  console.log(`📋 ${label}...`)
  execSync(command, {
    stdio: 'inherit',
    cwd: projectRoot
  })
  console.log(`✅ ${label} завершен\n`)
}

export function runAccessibilityAudit() {
  console.log('🔍 Starting accessibility smoke audit...\n')

  runStep(
    'Юнит accessibility suite',
    'npx vitest run tests/unit/**/*.accessibility.spec.ts'
  )

  runStep(
    'Playwright gallery smoke audit',
    'npx playwright test tests/e2e/gallery.a11y.spec.ts'
  )

  const reportPath = path.resolve(projectRoot, 'tmp/accessibility-audit-report.json')
  fs.mkdirSync(path.dirname(reportPath), { recursive: true })
  fs.writeFileSync(
    reportPath,
    JSON.stringify(
      {
        timestamp: new Date().toISOString(),
        suites: [
          'tests/unit/**/*.accessibility.spec.ts',
          'tests/e2e/gallery.a11y.spec.ts'
        ],
        status: 'passed'
      },
      null,
      2
    )
  )

  console.log(`📊 Accessibility audit report saved to: ${reportPath}`)
}

runAccessibilityAudit()























