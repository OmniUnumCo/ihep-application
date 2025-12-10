#!/usr/bin/env node
import fs from 'fs'
import path from 'path'

const root = process.cwd()
const targets = [
  'client',
  'backup_debug',
  'gcp/functions',
  'src/server/routes',
  'src/server/services',
  'src/server/vite.ts',
  'src/server/index.ts',
  'src/server/routes.ts',
  'server.js',
]

function rm(target) {
  const p = path.join(root, target)
  if (!fs.existsSync(p)) return
  const stat = fs.statSync(p)
  if (stat.isDirectory()) {
    fs.rmSync(p, { recursive: true, force: true })
    console.log(`Removed directory: ${target}`)
  } else {
    fs.rmSync(p, { force: true })
    console.log(`Removed file: ${target}`)
  }
}

for (const t of targets) {
  try { rm(t) } catch (e) { console.warn(`Skip ${t}:`, e?.message) }
}

console.log('Purge complete.')

