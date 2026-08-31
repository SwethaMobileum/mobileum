import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const CLUSTER_COLORS = {
  'Frontier': '#E74C3C',
  'Emerging': '#F39C12',
  'Growth': '#1ABC9C',
  'Mature': '#4A90D9',
  'Advanced': '#9B59B6',
  'Mature & Saturated': '#9B59B6',
  'High Growth Exposed': '#F39C12',
  'Roaming Hub': '#1ABC9C',
  'Emerging Opportunity': '#2ECC71',
  'Regulatory Transition': '#7F8C8D',
  'Unknown': '#7F8C8D'
};

export default function MapComponent({
  countries,
  currentLens,
  activeRegion,
  onSelectCountry,
  theme
}) {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const geojsonLayerRef = useRef(null);
  const tileLayerRef = useRef(null);
  const labelsLayerRef = useRef(null);

  // Helper colors
  const scoreToColor = (score, palette) => {
    if (score === null || score === undefined) return '#1e3054';
    const s = Math.max(0, Math.min(100, score));
    if (palette === 'fraud') {
      if (s < 20) return '#1ABC9C';
      if (s < 40) return '#F39C12';
      if (s < 60) return '#E67E22';
      if (s < 80) return '#E74C3C';
      return '#C0392B';
    }
    if (palette === 'heat') {
      if (s < 20) return '#1e3054';
      if (s < 40) return '#1A5276';
      if (s < 60) return '#2471A3';
      if (s < 80) return '#2980B9';
      return '#1ABC9C';
    }
    if (palette === 'arpu') {
      if (s < 25) return '#27AE60';
      if (s < 50) return '#F39C12';
      if (s < 75) return '#E67E22';
      return '#E74C3C';
    }
    return '#4A90D9';
  };

  const getCountryColor = (countryName, lens) => {
    const v = countries[countryName];
    if (!v) return theme === 'light' ? '#cbd5e1' : '#1e2d4a';
    switch (lens) {
      case 'cluster':
        return CLUSTER_COLORS[v.cluster_name] || '#4A90D9';
      case 'fraud': {
        const s = v.stats?.fraud_score || 3;
        const pct = ((s - 1) / 4) * 100;
        return scoreToColor(pct, 'fraud');
      }
      case 'fiveG': {
        const f = v.stats?.avg_5g || 0;
        return scoreToColor(f, 'heat');
      }
      case 'roaming': {
        const r = (((v.stats?.roaming_intensity || 3) - 1) / 4) * 100;
        return scoreToColor(r, 'heat');
      }
      case 'arpu': {
        const ap = v.radar?.arpu_pressure || 3;
        const pct = ((5 - ap) / 4) * 100;
        return scoreToColor(pct, 'arpu');
      }
      default:
        return CLUSTER_COLORS[v.cluster_name] || '#4A90D9';
    }
  };

  // Geojson NAME (often abbreviated) -> the key actually used in our data.
  const NAME_ALIASES = {
    'dem. rep. congo': 'DR Congo', 'democratic republic of the congo': 'DR Congo',
    'congo': 'Congo (Brazzaville)', 'republic of the congo': 'Congo (Brazzaville)',
    "côte d'ivoire": "Cote d'Ivoire", 'ivory coast': "Cote d'Ivoire",
    'central african rep.': 'Central African Republic',
    's. sudan': 'South Sudan', 'eq. guinea': 'Equatorial Guinea',
    'eswatini': 'Eswatini', 'swaziland': 'Eswatini',
    'são tomé and principe': 'Sao Tome and Principe', 'são tomé and príncipe': 'Sao Tome and Principe',
    'russia': 'Russia', 'russian federation': 'Russia',
    'united states of america': 'United States', 'united states': 'United States',
    'czechia': 'Czech Republic', 'czech rep.': 'Czech Republic',
    'bosnia and herz.': 'Bosnia and Herzegovina', 'dominican rep.': 'Dominican Republic',
    'south korea': 'South Korea', 'republic of korea': 'South Korea',
    'north korea': 'North Korea', 'dem. rep. korea': 'North Korea',
    'macedonia': 'North Macedonia', 'lao pdr': 'Laos', 'burma': 'Myanmar',
    'viet nam': 'Vietnam', 'united republic of tanzania': 'Tanzania',
    'w. sahara': 'Western Sahara', 'solomon is.': 'Solomon Islands',
  };

  const resolveKey = (raw) => {
    if (!raw) return null;
    if (countries[raw]) return raw;
    const up = raw.toUpperCase();
    if (countries[up]) return up;
    for (const key of Object.keys(countries)) {
      if (key.toUpperCase() === up) return key;
    }
    const alias = NAME_ALIASES[raw.toLowerCase().trim()];
    if (alias) {
      if (countries[alias]) return alias;
      for (const key of Object.keys(countries)) {
        if (key.toUpperCase() === alias.toUpperCase()) return key;
      }
    }
    return null;
  };

  const findCountryName = (props) => {
    const candidates = [props.NAME, props.ADMIN, props.NAME_LONG, props.SOVEREIGNT, props.NAME_EN, props.BRK_NAME];
    for (const c of candidates) {
      const k = resolveKey(c);
      if (k) return k;
    }
    return null;
  };

  const styleFeature = (feature) => {
    const name = findCountryName(feature.properties);
    const color = name ? getCountryColor(name, currentLens) : (theme === 'light' ? '#cbd5e1' : '#1e2d4a');
    const hasData = !!name && !!countries[name];

    // Determine region dimming
    let opacity = hasData ? 0.75 : 0.15;
    if (hasData && activeRegion !== 'all') {
      const v = countries[name];
      if (v.region !== activeRegion && !v.region.startsWith(activeRegion)) {
        opacity = 0.1;
      } else {
        opacity = 0.85;
      }
    }

    return {
      fillColor: color,
      fillOpacity: opacity,
      color: hasData ? (theme === 'light' ? '#64748b88' : '#ffffff22') : (theme === 'light' ? '#e2e8f0' : '#1e3054'),
      weight: 0.5,
      opacity: 1
    };
  };

  // 1. Initialize Map
  useEffect(() => {
    if (!mapRef.current) return;
    let isMounted = true;

    const map = L.map(mapRef.current, {
      center: [20, 10],
      zoom: 2.5,
      zoomControl: true,
      attributionControl: false,
      minZoom: 1.5,
      maxZoom: 8,
      preferCanvas: true
    });

    mapInstanceRef.current = map;

    // Load initial tile layer based on current theme
    const tileUrl = theme === 'light'
      ? 'https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png'
      : 'https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png';

    const tileLayer = L.tileLayer(tileUrl, {
      subdomains: 'abcd',
      maxZoom: 19
    }).addTo(map);

    tileLayerRef.current = tileLayer;

    map.createPane('labels');
    map.getPane('labels').style.zIndex = 450;
    map.getPane('labels').style.pointerEvents = 'none';

    // Add labels layer
    const labelsUrl = theme === 'light'
      ? 'https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png'
      : 'https://{s}.basemaps.cartocdn.com/dark_only_labels/{z}/{x}/{y}{r}.png';

    const labelsLayer = L.tileLayer(labelsUrl, {
      subdomains: 'abcd',
      maxZoom: 19,
      pane: 'labels'
    }).addTo(map);

    labelsLayerRef.current = labelsLayer;

    // Load GeoJSON world
    fetch('https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson')
      .then(r => r.json())
      .then(geo => {
        if (!isMounted) return;
        const layer = L.geoJSON(geo, {
          style: styleFeature,
          onEachFeature: (feature, layer) => {
            const name = findCountryName(feature.properties);
            const v = name ? countries[name] : null;

            layer.on({
              mouseover: (e) => {
                const l = e.target;
                const label = name || feature.properties.NAME || '?';
                let tip = `<strong>${label}</strong>`;
                if (v) {
                  const opNames = v.operators ? v.operators.map(o => o.operator).join(', ') : '';
                  tip += `<br><span style="color:var(--text-muted)">${v.region}</span>`;
                  tip += `<br>Operators (${v.num_operators}): <strong>${opNames}</strong>`;
                  tip += `<br>Cluster: ${v.cluster_name}`;
                  if (v.stats?.avg_5g) tip += `<br>5G: ${v.stats.avg_5g?.toFixed(0)}%`;
                }

                l.bindTooltip(tip, {
                  className: 'custom-tooltip',
                  sticky: true
                }).openTooltip();
              },
              mouseout: () => { },
              click: () => {
                if (v) onSelectCountry(name);
              }
            });
          }
        }).addTo(map);

        geojsonLayerRef.current = layer;

        // Add static continent labels
        const continents = [
          { name: 'Europe', coords: [50.0, 15.0] },
          { name: 'Asia', coords: [45.0, 80.0] },
          { name: 'Africa', coords: [10.0, 20.0] },
          { name: 'North America', coords: [45.0, -100.0] },
          { name: 'South America', coords: [-15.0, -60.0] },
          { name: 'Oceania', coords: [-25.0, 135.0] }
        ];

        continents.forEach(c => {
          const icon = L.divIcon({
            className: 'continent-label',
            html: `<span style="font-weight: 800; font-size: 13px; color: #ffffff; text-shadow: 0px 1px 3px rgba(0,0,0,0.95), 0px 0px 6px rgba(0,0,0,0.8); letter-spacing: 0.5px; text-transform: uppercase;">${c.name}</span>`,
            iconSize: [120, 24],
            iconAnchor: [60, 12]
          });
          L.marker(c.coords, {
            icon,
            interactive: false,
            pane: 'labels'
          }).addTo(map);
        });
      })
      .catch((err) => {
        if (!isMounted) return;
        console.error('GeoJSON load failed, falling back to circle markers', err);
        // Fallback: circle markers
        Object.entries(countries).forEach(([name, v]) => {
          if (!v.lat || !v.lng) return;
          const color = getCountryColor(name, currentLens);
          const radius = Math.max(4, Math.min(12, (v.num_operators || 1) * 2));
          const marker = L.circleMarker([v.lat, v.lng], {
            radius,
            fillColor: color,
            fillOpacity: 0.8,
            color: theme === 'light' ? '#64748b44' : '#ffffff22',
            weight: 0.5
          }).addTo(map);

          marker.on('click', () => onSelectCountry(name));
          const opNames = v.operators ? v.operators.map(o => o.operator).join(', ') : '';
          marker.bindTooltip(`<strong>${name}</strong><br>${v.region} · ${v.num_operators} operators (${opNames})`, {
            className: 'custom-tooltip'
          });
        });
      });

    return () => {
      isMounted = false;
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // 2. React to Theme Swapping
  useEffect(() => {
    if (!mapInstanceRef.current || !tileLayerRef.current) return;

    // Remove old base layer
    mapInstanceRef.current.removeLayer(tileLayerRef.current);
    // Remove old labels layer if present
    if (labelsLayerRef.current) {
      mapInstanceRef.current.removeLayer(labelsLayerRef.current);
    }

    const tileUrl = theme === 'light'
      ? 'https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png'
      : 'https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png';

    const tileLayer = L.tileLayer(tileUrl, {
      subdomains: 'abcd',
      maxZoom: 19
    }).addTo(mapInstanceRef.current);

    tileLayerRef.current = tileLayer;

    // Add updated labels layer
    const labelsUrl = theme === 'light'
      ? 'https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png'
      : 'https://{s}.basemaps.cartocdn.com/dark_only_labels/{z}/{x}/{y}{r}.png';

    const labelsLayer = L.tileLayer(labelsUrl, {
      subdomains: 'abcd',
      maxZoom: 19,
      pane: 'labels'
    }).addTo(mapInstanceRef.current);

    labelsLayerRef.current = labelsLayer;

    // Refresh geojson styles
    if (geojsonLayerRef.current) {
      geojsonLayerRef.current.setStyle(styleFeature);
    }
  }, [theme]);

  // 3. React to Lens & Region Filter Changes
  useEffect(() => {
    if (geojsonLayerRef.current) {
      geojsonLayerRef.current.setStyle(styleFeature);
    }

    if (mapInstanceRef.current && activeRegion !== 'all') {
      const regionBounds = {
        'MENA': [[10, -10], [50, 80]],
        'Europe': [[35, -10], [72, 40]],
        'APAC': [[-45, 60], [55, 180]],
        'LATAM': [[-60, -145], [75, -30]],
        'Africa': [[-35, -20], [38, 52]]
      };
      if (regionBounds[activeRegion]) {
        mapInstanceRef.current.fitBounds(regionBounds[activeRegion]);
      }
    } else if (mapInstanceRef.current && activeRegion === 'all') {
      mapInstanceRef.current.setView([20, 10], 2.5);
    }

    if (mapInstanceRef.current) {
      setTimeout(() => {
        if (mapInstanceRef.current) {
          mapInstanceRef.current.invalidateSize();
        }
      }, 250);
    }
  }, [currentLens, activeRegion]);

  return <div id="map" ref={mapRef} style={{ height: '100%', width: '100%' }}></div>;
}
