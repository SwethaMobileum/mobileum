import { supabase } from './_lib/supabase.js';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  if (!supabase) {
    return res.status(500).json({ error: 'Supabase client not initialized' });
  }

  const { countryId, operatorId, section, fieldName, value, updatedBy, baselineValue } = req.body;

  if (!countryId || !section || !fieldName) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  try {
    // 1. Fetch current override to use as old_value
    const { data: existingData, error: fetchError } = await supabase
      .from('country_overrides')
      .select('value')
      .eq('country_id', countryId)
      .eq('operator_id', operatorId || 'Global')
      .eq('section', section)
      .eq('field_name', fieldName)
      .maybeSingle();

    if (fetchError && fetchError.code !== 'PGRST116') {
      console.error('Error fetching existing override:', fetchError);
      return res.status(500).json({ error: 'Database error' });
    }

    const oldValue = existingData ? existingData.value : baselineValue;

    // 2. Upsert into country_overrides
    const { error: upsertError } = await supabase
      .from('country_overrides')
      .upsert({
        country_id: countryId,
        operator_id: operatorId || 'Global',
        section: section,
        field_name: fieldName,
        value: value,
        updated_by: updatedBy || 'Anonymous',
        updated_at: new Date().toISOString()
      }, {
        onConflict: 'country_id, operator_id, section, field_name'
      });

    if (upsertError) {
      console.error('Error upserting override:', upsertError);
      return res.status(500).json({ error: 'Database error' });
    }

    console.log("Attempting to insert into change_history:", {
      country_id: countryId,
      operator_id: operatorId || 'Global',
      section: section,
      field_name: fieldName,
      old_value: oldValue,
      new_value: value
    });

    const { error: historyError } = await supabase
      .from('change_history')
      .insert({
        country_id: countryId,
        operator_id: operatorId || 'Global',
        section: section,
        field_name: fieldName,
        old_value: oldValue,
        new_value: value,
        created_at: new Date().toISOString()
      });

    if (historyError) {
      console.error('Error inserting history:', historyError);
    } else {
      console.log('Successfully inserted into change_history');
    }

    return res.status(200).json({ success: true });
  } catch (err) {
    console.error('Unexpected error in save-override:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
