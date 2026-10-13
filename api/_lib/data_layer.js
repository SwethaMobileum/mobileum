import fs from 'fs';
import path from 'path';
import { query } from './db.js';

const getDataSource = () => process.env.DATA_SOURCE || 'json';

const loadJson = (filename) => {
    try {
        const p = path.resolve(process.cwd(), 'data-cache', filename);
        if (fs.existsSync(p)) {
            return JSON.parse(fs.readFileSync(p, 'utf-8'));
        }
    } catch(e) {
        console.error("Error reading JSON", filename, e);
    }
    return [];
};

export const fetchCustomerHealth = async () => {
    if (getDataSource() === 'postgres') {
        const { rows } = await query("SELECT * FROM customer_health");
        return rows;
    }
    return loadJson('customers.json');
};

export const fetchCustomerHealthBU = async (customerName) => {
    if (getDataSource() === 'postgres') {
        const { rows } = await query("SELECT * FROM customer_health_bu WHERE TRIM(LOWER(customer_name)) = TRIM(LOWER($1))", [customerName]);
        return rows;
    }
    const allBus = loadJson('business_units.json');
    return allBus.filter(b => b.customer_name && b.customer_name.toLowerCase().trim() === customerName.toLowerCase().trim());
};

export const fetchCustomerMapping = async (logicalCustomer) => {
    if (getDataSource() === 'postgres') {
        let q = "SELECT * FROM customer_mapping";
        let params = [];
        if (logicalCustomer) {
            q += " WHERE TRIM(LOWER(logical_customer)) = TRIM(LOWER($1))";
            params.push(logicalCustomer);
        }
        const { rows } = await query(q, params);
        return rows;
    }
    const map = loadJson('customer_mapping.json');
    if (logicalCustomer) return map.filter(m => m.logical_customer && m.logical_customer.toLowerCase().trim() === logicalCustomer.toLowerCase().trim());
    return map;
};

export const fetchSkygeni = async () => {
    if (getDataSource() === 'postgres') {
        const { rows } = await query("SELECT * FROM skygeni_product_groups");
        return rows;
    }
    return loadJson('skygeni.json');
};

export const fetchKpiDefs = async () => {
    if (getDataSource() === 'postgres') {
        const { rows } = await query("SELECT * FROM kpi_definitions");
        return rows;
    }
    return loadJson('kpi_definitions.json');
};

export const fetchDataStatus = async () => {
    if (getDataSource() === 'postgres') {
        const { rows } = await query("SELECT * FROM data_status");
        return rows;
    }
    return loadJson('data_status.json');
};
