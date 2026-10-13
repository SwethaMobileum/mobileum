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
    const { data, error } = await supabase
      .from('country_overrides')
      .select('section, field_name, value')
      .eq('country_id', countryId)
      .eq('operator_id', operatorId || 'Global');

    if (error) {
      console.error('Error fetching overrides:', error);
      return res.status(500).json({ error: 'Database error' });
    }

    // Transform into a nested object: { [section]: { [fieldName]: value } }
    const overrides = {};
    for (const row of (data || [])) {
      if (!overrides[row.section]) {
        overrides[row.section] = {};
      }
      overrides[row.section][row.field_name] = row.value;
    }

    return res.status(200).json(overrides);
  } catch (err) {
    console.error('Unexpected error in get-overrides:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
