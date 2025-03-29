import L from 'leaflet';
import React, { useEffect, useMemo, useRef, useCallback } from 'react';
import 'leaflet/dist/leaflet.css';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
import 'leaflet.markercluster';

interface Chapter {
  lat: number;
  lng: number;
  key: string;
  name: string;
}

interface ChapterMapProps {
  geoLocData: {
    _geoloc?: { lat: number; lng: number };
    geoLocation?: { lat: number; lng: number };
    key: string;
    name: string
  }[];
  showLocal?: boolean;
  style?: React.CSSProperties;
  isDarkMode: boolean;
}

const ChapterMap: React.FC<ChapterMapProps> = ({
  geoLocData,
  showLocal = false,
  style,
  isDarkMode
}) => {
  const mapRef = useRef<L.Map | null>(null);
  const markerClusterRef = useRef<L.MarkerClusterGroup | null>(null);

  const chapters: Chapter[] = useMemo(
    () =>
      geoLocData.map((chapter) => ({
        lat: chapter._geoloc ? chapter._geoloc.lat : chapter.geoLocation?.lat || 0,
        lng: chapter._geoloc ? chapter._geoloc.lng : chapter.geoLocation?.lng || 0,
        key: chapter.key,
        name: chapter.name,
      })),
    [geoLocData]
  );

  useEffect(() => {
    if (!mapRef.current) {
      mapRef.current = L.map('chapter-map', {
        center: [20.5937, 78.9629],
        zoom: 4,
        minZoom: 3,
        maxZoom: 18,
        worldCopyJump: false,
        attributionControl: false,
      });
    }
  }, []);

  useEffect(() => {
    if (!mapRef.current) return;

    // Remove existing tile layers
    mapRef.current.eachLayer((layer) => {
      if (layer instanceof L.TileLayer) {
        mapRef.current?.removeLayer(layer);
      }
    });

    // Select tile layer based on mode with fallback
    const tileLayerUrl = isDarkMode
      ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
      : 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';

    L.tileLayer(tileLayerUrl, {
      attribution: '© OpenStreetMap contributors, © CARTO',
      maxZoom: 19,
      subdomains: 'abcd'
    }).addTo(mapRef.current);
  }, [isDarkMode]);

  const updateMarkers = useCallback(() => {
    if (!mapRef.current) return;
    const map = mapRef.current;

    // Clear existing marker cluster
    if (markerClusterRef.current) {
      map.removeLayer(markerClusterRef.current);
    }

    // Create new marker cluster group
    markerClusterRef.current = L.markerClusterGroup({
      iconCreateFunction: (cluster) => {
        const childCount = cluster.getChildCount();
        return L.divIcon({
          html: `<div class="custom-cluster-icon ${isDarkMode ? 'dark-mode' : 'light-mode'}">
                   <span>${childCount}</span>
                 </div>`,
          className: 'custom-cluster-marker',
          iconSize: L.point(40, 40)
        });
      }
    });

    chapters.forEach((chapter) => {
      // Create custom marker
      const markerIcon = L.divIcon({
        className: `custom-marker ${isDarkMode ? 'dark-mode' : 'light-mode'}`,
        html: `<div class="marker-pin"></div>`,
        iconSize: [30, 42],
        popupAnchor: [0, -20]
      });

      const marker = L.marker([chapter.lat, chapter.lng], {
        icon: markerIcon
      });

      // Add popup
      marker.bindPopup(`
        <div class="owasp-popup ${isDarkMode ? 'dark-mode' : 'light-mode'}">
          <div class="owasp-popup-content">
            <span class="owasp-chapter-name">${chapter.name}</span>
            <span class="owasp-chapter-tag">OWASP Chapter</span>
          </div>
        </div>
      `, {
        className: 'custom-popup-container',
        minWidth: 200,
        maxWidth: 300,
        closeButton: false
      });

      // Add to cluster group
      markerClusterRef.current.addLayer(marker);
    });

    // Add cluster group to map
    map.addLayer(markerClusterRef.current);

    // Optional: fit bounds if showLocal is true
    if (showLocal && chapters.length > 0) {
      const bounds = L.latLngBounds(chapters.map(ch => [ch.lat, ch.lng]));
      map.fitBounds(bounds, {
        padding: [50, 50],
        maxZoom: 7
      });
    }
  }, [chapters, showLocal, isDarkMode]);

  useEffect(() => {
    updateMarkers();
  }, [updateMarkers]);

  return (
    <div>
      <style>{`
        .custom-popup-container .leaflet-popup-content-wrapper {
          background: transparent !important;
          box-shadow: none !important;
          padding: 0 !important;
        }
        .custom-popup-container .leaflet-popup-content {
          margin: 0 !important;
          padding: 0 !important;
        }
        .owasp-popup {
          display: flex;
          align-items: center;
          padding: 10px;
          border-radius: 6px;
        }
        .owasp-popup.dark-mode {
          background-color: rgba(44, 44, 44, 0.9);
          color: white;
        }
        .owasp-popup.light-mode {
          background-color: rgba(255, 255, 255, 0.9);
          color: black;
        }
        .owasp-popup-content {
          display: flex;
          flex-direction: column;
        }
        .owasp-chapter-name {
          font-size: 16px;
          font-weight: 500;
        }
        .owasp-chapter-tag {
          font-size: 12px;
          opacity: 0.7;
        }

        .custom-marker .marker-pin {
          width: 20px;
          height: 20px;
          border-radius: 50% 50% 50% 0;
          background: #48c774;
          position: absolute;
          transform: rotate(-45deg);
          left: 50%;
          top: 50%;
          margin: -10px 0 0 -10px;
          box-shadow: 0 0 5px rgba(0,0,0,0.5);
        }
        .custom-marker.dark-mode .marker-pin {
          background: #3ca753;
        }
      `}</style>
      <div
        id="chapter-map"
        style={{
          ...style,
          height: '500px',
          width: '100%',
          backgroundColor: isDarkMode ? '#1e1e1e' : '#ffffff',
          border: isDarkMode ? '1px solid #444' : '1px solid #ddd',
          borderRadius: '8px',
        }}
      />
    </div>
  );
};

export default ChapterMap;
