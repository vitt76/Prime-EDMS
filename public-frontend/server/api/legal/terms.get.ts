import { readFileSync } from 'fs'
import { dirname, join } from 'path'
import { fileURLToPath } from 'url'
import MarkdownIt from 'markdown-it'

const __dirname = dirname(fileURLToPath(import.meta.url))

function readMarkdown(filename: string): string {
  const candidates = [
    join(__dirname, '..', '..', '..', 'public', 'legal', filename),
    join(process.cwd(), 'public', 'legal', filename)
  ]
  for (const pathToMd of candidates) {
    try {
      return readFileSync(pathToMd, 'utf-8')
    } catch {
      continue
    }
  }
  throw new Error(`Legal file not found: ${filename} (tried ${candidates.join(', ')})`)
}

export default defineEventHandler(() => {
  const raw = readMarkdown('user-agreement-ru.md')
  const md = new MarkdownIt()
  const html = md.render(raw)
  const titleMatch = raw.match(/^#\s+(.+)$/m)
  const title = titleMatch ? titleMatch[1].trim() : 'Пользовательское соглашение'
  return { html, title }
})
