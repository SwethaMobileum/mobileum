import { supabase } from './_lib/supabase.js';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  if (!supabase) {
    return res.status(500).json({ error: 'Supabase client not initialized' });
  }

  const { countryId, operatorId } = req.query;

  if (!countryId) {
    return res.status(400).json({ error: 'Missing countryId' });
  }

  try {
    console.log("Fetching history for:", { countryId, operatorId });
    
    const { data, error } = await supabase
      .from('change_history')
      .select('*')
      .eq('country_id', countryId)
      .eq('operator_id', operatorId || 'Global')
      .order('created_at', { ascending: false });

    console.log("Supabase history fetch result:", { dataLength: data ? data.length : 0, error });

    if (error) {
      console.error('Error fetching history:', error);
      return res.status(500).json({ error: 'Database error' });
    }

    return res.status(200).json(data || []);
  } catch (err) {
    console.error('Unexpected error in get-history:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
