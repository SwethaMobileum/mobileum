import { supabase } from './_lib/supabase.js';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  if (!supabase) {
    return res.status(500).json({ error: 'Supabase client not initialized' });
  }

  const { countryId, operatorId, section, fieldName, valueToRestore, updatedBy } = req.body;

  if (!countryId || !section || !fieldName || valueToRestore === undefined) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  try {
    // 1. Fetch current override to use as old_value in history
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
      return res.status(500).json({ error: 'Database error fetching current value' });
    }

    const oldValue = existingData ? existingData.value : null;

    console.log("Attempting to restore value for:", { countryId, operatorId, section, fieldName, valueToRestore });

    // 2. Overwrite the country_overrides value with valueToRestore
    const { error: upsertError } = await supabase
      .from('country_overrides')
      .upsert({
        country_id: countryId,
        operator_id: operatorId || 'Global',
        section: section,
        field_name: fieldName,
        value: valueToRestore,
        updated_by: updatedBy || 'Anonymous',
        updated_at: new Date().toISOString()
      }, {
        onConflict: 'country_id, operator_id, section, field_name'
      });

    if (upsertError) {
      console.error('Error upserting restored value:', upsertError);
      return res.status(500).json({ error: 'Database error' });
    }

    console.log("Successfully restored value in country_overrides. Now inserting into change_history.");

    // 3. Insert into change_history indicating a restore
    const { error: historyError } = await supabase
      .from('change_history')
      .insert({
        country_id: countryId,
        operator_id: operatorId || 'Global',
        section: section,
        field_name: fieldName,
        old_value: oldValue, // The value that was replaced
        new_value: valueToRestore, // The value that was restored
        created_at: new Date().toISOString()
      });

    if (historyError) {
      console.error('Error inserting restore history:', historyError);
      // We do not fail the request if just history logging fails, but it's bad.
    } else {
      console.log("Successfully inserted restore event into change_history.");
    }

    return res.status(200).json({ success: true, restoredValue: valueToRestore });
  } catch (err) {
    console.error('Unexpected error in restore-value:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
