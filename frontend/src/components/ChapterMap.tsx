import React from 'react';
import L from 'leaflet';
import { useEffect, useMemo, useRef, useCallback } from 'react';
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
  geoLocData: { _geoloc?: { lat: number; lng: number }; geoLocation?: { lat: number; lng: number }; key: string; name: string }[];
  showLocal: boolean;
  style?: React.CSSProperties;
  isDarkMode: boolean;
}

const ChapterMap: React.FC<ChapterMapProps> = ({ geoLocData, showLocal, style, isDarkMode }) => {
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
        worldCopyJump: false,
        maxBounds: [[-90, -180], [90, 180]],
        maxBoundsViscosity: 1.0,
        preferCanvas: true,
        attributionControl: false,
      }).setView([20, 0], 2);
    }
  }, []);

  useEffect(() => {
    if (!mapRef.current) return;
    mapRef.current.eachLayer((layer) => {
      if (layer instanceof L.TileLayer) {
        mapRef.current?.removeLayer(layer);
      }
    });

    const tileLayerUrl = isDarkMode
      ? 'https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_nolabels/{z}/{x}/{y}.png'
      : 'https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_nolabels/{z}/{x}/{y}.png';

    L.tileLayer(tileLayerUrl, {
      attribution: '',
    }).addTo(mapRef.current);
  }, [isDarkMode]);

  const updateMarkers = useCallback(() => {
    if (!mapRef.current) return;
    const map = mapRef.current;

    if (!markerClusterRef.current) {
      markerClusterRef.current = L.markerClusterGroup({
        clusterPane: 'markers',
        iconCreateFunction: (cluster) => {
          const childCount = cluster.getChildCount();
          const markerSize = childCount < 10 ? 'small' : childCount < 100 ? 'medium' : 'large';

          return L.divIcon({
            html: `<div><span>${childCount}</span></div>`,
            className: `marker-cluster marker-cluster-${markerSize}`,
            iconSize: L.point(40, 40)
          });
        }
      });
    } else {
      markerClusterRef.current.clearLayers();
    }

    const markerClusterGroup = markerClusterRef.current;
    const bounds: L.LatLngExpression[] = [];

    chapters.forEach((chapter) => {
      const markerIcon = L.divIcon({
        className: 'custom-marker',
        html: `<div class="marker-pin ${isDarkMode ? 'dark-mode' : 'light-mode'}"></div>`,
        iconSize: [30, 42],
        popupAnchor: [0, -20]
      });

      const marker = L.marker([chapter.lat, chapter.lng], { icon: markerIcon });

      // Create a label div that precisely matches the images
      const labelDiv = L.divIcon({
        className: `chapter-label ${isDarkMode ? 'dark-mode' : 'light-mode'}`,
        html: `<div style="
          position: absolute;
          white-space: nowrap;
          background-color: ${isDarkMode ? 'rgba(44, 44, 44, 0.8)' : 'rgba(255, 255, 255, 0.8)'};
          color: ${isDarkMode ? 'white' : 'black'};
          font-size: 12px;
          line-height: 16px;
          padding: 2px 4px;
          border-radius: 2px;
          transform: translate(-50%, -120%);
          pointer-events: none;
          box-shadow: none;
          border: none;
          font-family: Arial, sans-serif;
          text-align: center;
        ">${chapter.name}</div>`,
        iconSize: [0, 0],
        iconAnchor: [0, 0]
      });

      // Create a label marker that will always be visible
      const labelMarker = L.marker([chapter.lat, chapter.lng], {
        icon: labelDiv,
        interactive: false,
        zIndexOffset: 1000
      });

      markerClusterGroup.addLayer(marker);
      markerClusterGroup.addLayer(labelMarker);
      bounds.push([chapter.lat, chapter.lng]);
    });

    map.addLayer(markerClusterGroup);

    if (showLocal && chapters.length > 0) {
      const maxNearestChapters = 5;
      const localChapters = chapters.slice(0, maxNearestChapters);
      const localBounds = L.latLngBounds(localChapters.map((ch) => [ch.lat, ch.lng]));
      const nearestChapter = chapters[0];

      map.setView([nearestChapter.lat, nearestChapter.lng], 7);
      map.fitBounds(localBounds, { maxZoom: 7 });
    }
  }, [chapters, showLocal, isDarkMode]);

  useEffect(() => {
    updateMarkers();
  }, [updateMarkers]);

  return (
    <div>
      <style>{`
        .marker-pin {
          width: 20px;
          height: 20px;
          border-radius: 50% 50% 50% 0;
          background: #48c774; /* Changed to green */
          position: absolute;
          transform: rotate(-45deg);
          left: 50%;
          top: 50%;
          margin: -10px 0 0 -10px;
        }
        .marker-pin.dark-mode {
          background: #3ca753; /* Darker green for dark mode */
        }
        .chapter-label div {
          transition: none !important;
          outline: none !important;
        }
        .chapter-label.dark-mode div {
          background-color: rgba(44, 44, 44, 0.8) !important;
          color: white !important;
        }
        .chapter-label.light-mode div {
          background-color: rgba(255, 255, 255, 0.8) !important;
          color: black !important;
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
