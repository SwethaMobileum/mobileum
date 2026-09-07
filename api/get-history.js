import { query } from './_lib/db.js';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { countryId, operatorId } = req.query;

  if (!countryId) {
    return res.status(400).json({ error: 'Missing countryId' });
  }

  try {
    console.log("Fetching history for:", { countryId, operatorId });
    
    const result = await query(
      `SELECT * FROM change_history 
       WHERE country_id = $1 AND operator_id = $2 
       ORDER BY created_at DESC`,
      [countryId, operatorId || 'Global']
    );

    console.log("PostgreSQL history fetch result length:", result.rows.length);

    return res.status(200).json(result.rows || []);
  } catch (err) {
    console.error('Unexpected error in get-history:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
