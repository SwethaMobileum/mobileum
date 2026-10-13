import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'
import { pathToFileURL } from 'url'

// Simulate Vercel /api serverless functions locally
const vercelApiMock = () => {
  return {
    name: 'vercel-api-mock',
    configureServer(server) {
      // Pre-load environment variables at server start
      const initialEnv = loadEnv(server.config.mode || 'development', process.cwd(), '');
      Object.assign(process.env, initialEnv);

      server.middlewares.use(async (req, res, next) => {
        if (req.url.startsWith('/api/')) {
          try {
            const urlPath = req.url.split('?')[0];
            const modulePath = path.resolve('.' + urlPath + '.js');
            
            if (fs.existsSync(modulePath)) {
              const handleRequest = async (bodyData) => {
                if (bodyData) {
                  try { req.body = JSON.parse(bodyData); } catch(e) { req.body = bodyData; }
                }
                
                const query = {};
                if (req.url.includes('?')) {
                  const searchParams = new URLSearchParams(req.url.split('?')[1]);
                  for (const [key, value] of searchParams.entries()) {
                    query[key] = value;
                  }
                }
                req.query = query;

                try {
                  const env = loadEnv(server.config.mode || 'development', process.cwd(), '');
                  Object.assign(process.env, env);

                  const moduleUrl = pathToFileURL(modulePath).href + '?t=' + Date.now();
                  const { default: handler } = await import(moduleUrl);
                  
                  res.status = (code) => { res.statusCode = code; return res; };
                  res.json = (data) => {
                    res.setHeader('Content-Type', 'application/json');
                    res.end(JSON.stringify(data));
                  };
                  
                  await handler(req, res);
                } catch (err) {
                  console.error('API Error:', err);
                  res.statusCode = 500;
                  res.end(JSON.stringify({ error: err.message }));
                }
              };

              if (req.method === 'GET' || req.method === 'HEAD') {
                await handleRequest();
              } else {
                let body = '';
                req.on('data', chunk => { body += chunk.toString(); });
                req.on('end', () => handleRequest(body));
              }
              return;
            }
          } catch(e) {
            console.error('Middleware Error:', e);
          }
        }
        next();
      });
    }
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), vercelApiMock()],
  server: {
    host: true
  }
})
