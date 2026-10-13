# Deployment Notes - Mobileum Global Telecom Intelligence Platform

**Target Environment:** VM at IP `10.10.51.71`
**Database Environment:** PostgreSQL (`10.10.51.71:5432/portal`)
**Application Stack:** React + Vite, Node.js Serverless Functions

## Prerequisites
1. Ensure Node.js (v18+) is installed on the VM.
2. Ensure Python 3.10+ is installed (for the data loading scripts).
3. Ensure PostgreSQL is actively running on `10.10.51.71` on port `5432` with a database named `portal`.

## 1. Code Transfer
Clone or copy the updated codebase to the VM.

## 2. Environment Configuration
Ensure the `.env` file on the VM matches the following configuration for PostgreSQL:
```
VITE_API_URL=/api
DB_HOST=10.10.51.71
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=<your_db_password>
DB_NAME=portal
DATA_SOURCE=postgres
```
*Note: Since the local `.env` currently has `DATA_SOURCE=json`, you **must** update this to `postgres` on the VM so the serverless API hits the real database.*

## 3. Package Installation
Run the following from the project root:
```bash
npm install
```

## 4. Database Seeding
If the PostgreSQL database is empty or needs to be refreshed from the latest Excel files, run:
```bash
npm run load:data
```
Verify the integrity of the data with:
```bash
npm run check:data
```
*Wait for output confirming that 258 SkyGeni accounts and all 37 health customers are mapped successfully.*

## 5. Build and Deploy
Build the production-ready assets:
```bash
npm run build
```
This generates the optimized bundle in the `dist/` directory.

### To run via Node/Express (Recommended for simple VM deployment):
If you have a simple express wrapper, you can run it. Alternatively, use a static file server:
```bash
npm install -g serve
serve -s dist -p 80
```

### Serverless API Route Deployment (Vercel / Next / Express proxy):
If you are deploying the `/api/*` endpoints to a Node server instead of Vercel, ensure you run the proxy server that directs `/api` calls to the `api/` directory functions.

## 6. Verification
1. Access `http://10.10.51.71` from your browser.
2. Ensure the Global Map loads and countries are color-coded correctly.
3. Toggle the **"Health Score"** Map Lens and verify it accurately colors the regions.
4. Select **STC** or **Vodafone UK**, and verify that the Account Profile and Support & AMC tabs contain the green **"SOURCED DATA"** badges indicating that the database connection is live and serving the mapped data.
5. Generate an Export PPT and verify that the exact AMC Support Contract values are exported correctly.
