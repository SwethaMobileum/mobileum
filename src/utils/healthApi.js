export const fetchHealthData = async () => {
    const res = await fetch('/api/customer-health');
    if (!res.ok) throw new Error('Failed to fetch health data');
    return res.json();
};

export const fetchHealthDetail = async (customerName) => {
    const res = await fetch(`/api/customer-health-detail?customer=${encodeURIComponent(customerName)}`);
    if (!res.ok) throw new Error('Failed to fetch health detail');
    return res.json();
};

export const fetchCustomerNames = async (customerName) => {
    const res = await fetch(`/api/customer-names?customer=${encodeURIComponent(customerName)}`);
    if (!res.ok) throw new Error('Failed to fetch customer names');
    return res.json();
};

export const fetchWhiteSpace = async (customerName) => {
    const res = await fetch(`/api/white-space-customer?customer=${encodeURIComponent(customerName)}`);
    if (!res.ok) throw new Error('Failed to fetch white space');
    return res.json();
};

export const fetchAccounts = async () => {
    const res = await fetch('/api/accounts');
    if (!res.ok) throw new Error('Failed to fetch accounts');
    return res.json();
};

export const fetchProductGroups = async () => {
    const res = await fetch('/api/product-groups');
    if (!res.ok) throw new Error('Failed to fetch product groups');
    return res.json();
};

export const fetchKpiDefs = async () => {
    const res = await fetch('/api/kpi-definitions');
    if (!res.ok) throw new Error('Failed to fetch KPI definitions');
    return res.json();
};

export const fetchDataStatus = async () => {
    const res = await fetch('/api/data-status');
    if (!res.ok) throw new Error('Failed to fetch data status');
    return res.json();
};
