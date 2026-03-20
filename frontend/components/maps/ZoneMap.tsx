'use client';

import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

interface ZoneMapProps {
  center?: [number, number];
  zoom?: number;
  zones?: Array<{
    name: string;
    coordinates: [number, number];
    riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
    activeUsers: number;
  }>;
}

export function ZoneMap({ 
  center = [28.6139, 77.2090], // Delhi coordinates
  zoom = 11,
  zones = []
}: ZoneMapProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);

  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return;

    // Initialize map
    const map = L.map(mapRef.current).setView(center, zoom);

    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 18,
    }).addTo(map);

    mapInstanceRef.current = map;

    // Add zone markers
    zones.forEach((zone) => {
      const color = 
        zone.riskLevel === 'LOW' ? '#10b981' :
        zone.riskLevel === 'MEDIUM' ? '#f59e0b' : '#ef4444';

      const marker = L.circleMarker(zone.coordinates, {
        radius: 12,
        fillColor: color,
        color: '#fff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.7,
      }).addTo(map);

      marker.bindPopup(`
        <div style="padding: 8px;">
          <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px;">${zone.name}</div>
          <div style="font-size: 12px; color: #666;">
            Risk Level: <span style="color: ${color}; font-weight: 600;">${zone.riskLevel}</span>
          </div>
          <div style="font-size: 12px; color: #666;">
            Active Users: ${zone.activeUsers}
          </div>
        </div>
      `);
    });

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [center, zoom, zones]);

  return (
    <div className="relative w-full h-full rounded-lg overflow-hidden border border-gray-200">
      <div ref={mapRef} className="w-full h-full min-h-[400px]" />
      
      {/* Legend */}
      <div className="absolute bottom-4 right-4 bg-white p-3 rounded-lg shadow-lg z-[1000]">
        <div className="text-xs font-bold text-gray-700 mb-2">Risk Levels</div>
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span className="text-xs text-gray-600">Low Risk</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500" />
            <span className="text-xs text-gray-600">Medium Risk</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <span className="text-xs text-gray-600">High Risk</span>
          </div>
        </div>
      </div>
    </div>
  );
}
