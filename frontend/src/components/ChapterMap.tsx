import L from 'leaflet';
import React, { useEffect, useMemo, useRef, useCallback } from 'react';
import 'leaflet/dist/leaflet.css';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
import 'leaflet.markercluster';
import { GeoLocDataAlgolia, GeoLocDataGraphQL } from 'types/chapter';

const ChapterMap = ({ geoLocData, showLocal, style, isDarkMode }) => {
  const mapRef = useRef(null);
  const markerClusterRef = useRef(null);

  const chapters = useMemo(
    () =>
      geoLocData.map((chapter) => ({
        lat: '_geoloc' in chapter ? chapter._geoloc.lat : chapter.geoLocation.lat,
        lng: '_geoloc' in chapter ? chapter._geoloc.lng : chapter.geoLocation.lng,
        key: chapter.key,
        name: chapter.name,
      })),
    [geoLocData]
  );

  useEffect(() => {
    if (!mapRef.current) {
      const map = L.map('chapter-map', {
        worldCopyJump: false,
        maxBounds: [
          [-90, -180],
          [90, 180],
        ],
        maxBoundsViscosity: 1.0,
        preferCanvas: true,
      }).setView([20, 0], 2);

      mapRef.current = map;
    }
  }, []);

  useEffect(() => {
    if (!mapRef.current) return;

    mapRef.current.eachLayer(layer => {
      if (layer instanceof L.TileLayer) {
        mapRef.current.removeLayer(layer);
      }
    });

    const tileLayerUrl = isDarkMode
      ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
      : 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';

    L.tileLayer(tileLayerUrl, {
      attribution: '&copy; OpenStreetMap contributors &copy; CartoDB',
    }).addTo(mapRef.current);
  }, [isDarkMode]);

  const updateMarkers = useCallback(() => {
    if (!mapRef.current) return;
    const map = mapRef.current;

    if (!markerClusterRef.current) {
      markerClusterRef.current = L.markerClusterGroup();
    } else {
      markerClusterRef.current.clearLayers();
    }

    const markerClusterGroup = markerClusterRef.current;
    const bounds = [];

    chapters.forEach((chapter) => {
      const markerIcon = new L.Icon({
        iconAnchor: [12, 41],
        iconRetinaUrl: '/img/marker-icon-2x.png',
        iconSize: [25, 41],
        iconUrl: '/img/marker-icon.png',
        popupAnchor: [1, -34],
        shadowSize: [41, 41],
        shadowUrl: '/img/marker-shadow.png',
      });

      const marker = L.marker([chapter.lat, chapter.lng], { icon: markerIcon });

      const popupContent = document.createElement('div');
      popupContent.className = 'leaflet-popup-content-wrapper';
      popupContent.style.backgroundColor = isDarkMode ? '#2b2b2b' : '#ffffff';
      popupContent.style.color = isDarkMode ? '#ffffff' : '#000000';
      popupContent.style.border = 'none';
      popupContent.style.padding = '10px 15px';
      popupContent.style.borderRadius = '8px';
      popupContent.style.boxShadow = '0 2px 6px rgba(0,0,0,0.3)';
      popupContent.style.textAlign = 'center';
      popupContent.style.fontSize = '14px';
      popupContent.style.fontWeight = 'bold';

      const chapterTitle = document.createElement('span');
      chapterTitle.textContent = chapter.name;
      popupContent.appendChild(chapterTitle);

      marker.bindPopup(popupContent, { closeButton: false });

      markerClusterGroup.addLayer(marker);
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
    <div
      id="chapter-map"
      style={{
        ...style,
        backgroundColor: isDarkMode ? '#1e1e1e' : '#ffffff',
        padding: '10px',
        borderRadius: '8px',
        border: isDarkMode ? '1px solid #444' : '1px solid #ddd',
      }}
    />
  );
};

export default ChapterMap;
