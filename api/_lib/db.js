import pg from 'pg';
import fs from 'fs';
import path from 'path';

const { Pool } = pg;

let pool = null;
let currentDbUrl = null;

function resolveDatabaseUrl() {
  if (process.env.DATABASE_URL) return process.env.DATABASE_URL;
  if (process.env.POSTGRES_URL) return process.env.POSTGRES_URL;

  // Try reading directly from .env.local or src/.env.local if process.env isn't set yet
  const candidates = ['.env.local', 'src/.env.local', '.env'];
  for (const rel of candidates) {
    try {
      const fullPath = path.resolve(process.cwd(), rel);
      if (fs.existsSync(fullPath)) {
        const content = fs.readFileSync(fullPath, 'utf-8');
        for (const line of content.split('\n')) {
          const trimmed = line.trim();
          if (trimmed && !trimmed.startsWith('#') && trimmed.includes('=')) {
            const [k, ...v] = trimmed.split('=');
            const key = k.trim();
            const val = v.join('=').trim().replace(/^["']|["']$/g, '');
            if ((key === 'DATABASE_URL' || key === 'POSTGRES_URL') && val) {
              process.env[key] = val;
              return val;
            }
          }
        }
      }
    } catch (e) {
      // ignore
    }
  }
  return null;
}

export function getPool() {
  const dbUrl = resolveDatabaseUrl();
  
  if (!pool || currentDbUrl !== dbUrl) {
    if (pool) {
      pool.end().catch(() => {});
    }
    if (!dbUrl) {
      console.warn('DATABASE_URL or POSTGRES_URL environment variable is not set.');
    }
    const isLocal = dbUrl && (dbUrl.includes('localhost') || dbUrl.includes('127.0.0.1'));
    pool = new Pool({
      connectionString: dbUrl || undefined,
      ssl: isLocal ? false : { rejectUnauthorized: false },
      connectionTimeoutMillis: 5000,
      idleTimeoutMillis: 30000,
      max: 10
    });
    currentDbUrl = dbUrl;
  }
  return pool;
}

export async function query(text, params) {
  const p = getPool();
  return p.query(text, params);
}

