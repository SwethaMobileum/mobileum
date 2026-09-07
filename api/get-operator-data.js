import { query } from './_lib/db.js';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { country, meta } = req.query;

  try {
    // If no country is requested or meta=true, return country list metadata
    if (!country || meta === 'true') {
      const result = await query(
        `SELECT country_id, country_name, region, gdp_per_capita 
         FROM countries 
         ORDER BY country_name ASC`
      );

      const countriesList = result.rows;
      const regions = [...new Set(countriesList.map(c => c.region).filter(Boolean))];

      return res.status(200).json({
        total_countries: countriesList.length,
        regions,
        countries: countriesList
      });
    }

    // Fetch data for the specified country
    const countryResult = await query(
      `SELECT * FROM countries 
       WHERE LOWER(country_name) = LOWER($1) OR LOWER(country_id) = LOWER($1)`,
      [country]
    );

    if (countryResult.rows.length === 0) {
      return res.status(404).json({ error: `Country '${country}' not found` });
    }

    const countryRow = countryResult.rows[0];

    // Fetch operators for this country
    const operatorsResult = await query(
      `SELECT * FROM operators 
       WHERE LOWER(country_id) = LOWER($1) 
       ORDER BY operator_name ASC`,
      [countryRow.country_id]
    );

    const operators = operatorsResult.rows;
    const operatorIds = operators.map(op => op.operator_id);

    // Fetch financial data for these operators
    let financials = [];
    if (operatorIds.length > 0) {
      const financialsResult = await query(
        `SELECT * FROM operator_financials_5y 
         WHERE operator_id = ANY($1::int[]) 
         ORDER BY year DESC`,
        [operatorIds]
      );
      financials = financialsResult.rows;
    }

    return res.status(200).json({
      country: countryRow,
      operators: operators,
      financials: financials
    });
  } catch (err) {
    console.error('Unexpected error in get-operator-data:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
