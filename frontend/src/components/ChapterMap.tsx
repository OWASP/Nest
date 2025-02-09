import L from 'leaflet';
import { useEffect, useRef, useState } from 'react';
import 'leaflet/dist/leaflet.css';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
import 'leaflet.markercluster';

interface GeoLocData {
  _geoloc: {
    lat: number;
    lng: number;
  };
  name: string;
  key: string;
}
interface ChapterMapProps {
  geoLocData?: GeoLocData[];
  style?: React.CSSProperties;
}

const ChapterMap: React.FC<ChapterMapProps> = ({ geoLocData = [], style }) => {
  const mapRef = useRef<L.Map | null>(null);
  const tileLayerRef = useRef<L.TileLayer | null>(null);
  const markerClusterGroupRef = useRef<L.MarkerClusterGroup | null>(null);
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const [isDarkMode, setIsDarkMode] = useState<boolean>(
    localStorage.getItem('theme') === 'dark'
  );

  useEffect(() => {
    const handleThemeChange = () => {
      setIsDarkMode(localStorage.getItem('theme') === 'dark');
    };
    window.addEventListener('storage', handleThemeChange);
    return () => {
      window.removeEventListener('storage', handleThemeChange);
    };
  }, []);

  useEffect(() => {
    if (!mapContainerRef.current) return;
    if (!mapRef.current) {
      mapRef.current = L.map(mapContainerRef.current).setView([20, 0], 2);
    }
    const map = mapRef.current;

    // Update Tile Layer when theme changes
    const tileLayerUrl = isDarkMode
      ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
      : 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';

    if (tileLayerRef.current) {
      map.removeLayer(tileLayerRef.current); // Remove old tile layer
    }
    tileLayerRef.current = L.tileLayer(tileLayerUrl, { attribution: '© OpenStreetMap' });
    tileLayerRef.current.addTo(map);

    // Update Markers
    if (markerClusterGroupRef.current) {
      map.removeLayer(markerClusterGroupRef.current);
    }
    const markerClusterGroup = L.markerClusterGroup();
    markerClusterGroupRef.current = markerClusterGroup;

    let bounds: L.LatLngBounds | null = null;
    geoLocData.forEach((chapter) => {
      const { lat, lng } = chapter._geoloc;
      const marker = L.marker([lat, lng]);
      marker.bindPopup(`<div>${chapter.name}</div>`);
      markerClusterGroup.addLayer(marker);

      bounds = bounds ? bounds.extend([lat, lng]) : L.latLngBounds([lat, lng]);
    });
    map.addLayer(markerClusterGroup);
    if (bounds) {
      map.fitBounds(bounds, { maxZoom: 10 });
    }
    return () => {
      if (tileLayerRef.current) {
        map.removeLayer(tileLayerRef.current);
      }
      if (markerClusterGroupRef.current) {
        map.removeLayer(markerClusterGroupRef.current);
      }
    };
  }, [geoLocData, isDarkMode]);
  return <div ref={mapContainerRef} id="chapter-map" className="rounded-2xl" style={style}></div>;
};
export default ChapterMap;
