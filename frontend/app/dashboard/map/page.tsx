'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card } from '@/components/ui/Card';
import { MapPin, TrendingUp, AlertTriangle, Users } from 'lucide-react';

const ZoneMap = dynamic(() => import('@/components/maps/ZoneMap').then(mod => mod.ZoneMap), {
  ssr: false,
  loading: () => <div className="flex items-center justify-center h-full"><p className="text-gray-500">Loading map...</p></div>
});

export default function MapPage() {
  const [zoneStats, setZoneStats] = useState<any[]>([]);

  useEffect(() => {
    const loadZoneStats = async () => {
      try {
        const response = await fetch('http://localhost:8001/real-data/zone-stats', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        const data = await response.json();
        setZoneStats(data);
      } catch (error) {
        console.error('Failed to load zone stats:', error);
        // Fallback to empty
        setZoneStats([
          { zone: 'Andheri West', risk: 'low', workers: 0, avgEarnings: 0 },
          { zone: 'Bandra', risk: 'low', workers: 0, avgEarnings: 0 },
          { zone: 'Powai', risk: 'low', workers: 0, avgEarnings: 0 },
          { zone: 'Goregaon', risk: 'low', workers: 0, avgEarnings: 0 },
        ]);
      }
    };
    loadZoneStats();
  }, []);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header with Gradient */}
        <div className="bg-gradient-to-r from-green-500 via-teal-500 to-cyan-600 rounded-2xl p-8 text-white shadow-2xl">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">🗺️ Risk Zone Map</h1>
              <p className="text-green-100 text-lg">Hyperlocal AI-powered risk analysis and worker distribution</p>
            </div>
            <div className="bg-white/20 backdrop-blur-lg rounded-2xl p-4">
              <MapPin className="w-16 h-16" />
            </div>
          </div>
        </div>

        {/* Stats Grid - Gradient Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl p-6 text-white shadow-xl hover:scale-105 transition-transform">
            <div className="text-5xl font-bold mb-2">4</div>
            <div className="text-blue-100 font-medium">Monitored Zones</div>
          </div>
          <div className="bg-gradient-to-br from-red-500 to-pink-600 rounded-2xl p-6 text-white shadow-xl hover:scale-105 transition-transform">
            <div className="text-5xl font-bold mb-2">1</div>
            <div className="text-red-100 font-medium">High Risk</div>
          </div>
          <div className="bg-gradient-to-br from-yellow-500 to-orange-600 rounded-2xl p-6 text-white shadow-xl hover:scale-105 transition-transform">
            <div className="text-5xl font-bold mb-2">2</div>
            <div className="text-yellow-100 font-medium">Medium Risk</div>
          </div>
          <div className="bg-gradient-to-br from-green-500 to-emerald-700 rounded-2xl p-6 text-white shadow-xl hover:scale-105 transition-transform">
            <div className="text-5xl font-bold mb-2">1</div>
            <div className="text-green-100 font-medium">Low Risk</div>
          </div>
        </div>

        {/* Map */}
        <Card>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Interactive Zone Map</h2>
          <div className="h-[500px] rounded-lg overflow-hidden">
            <ZoneMap />
          </div>
        </Card>

        {/* Zone Details */}
        <Card>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Zone Statistics</h2>
          <div className="space-y-3">
            {zoneStats.map((zone) => (
              <div key={zone.zone} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div className="flex items-center space-x-4">
                  <div className={`p-3 rounded-lg ${
                    zone.risk === 'high' ? 'bg-red-100' :
                    zone.risk === 'medium' ? 'bg-yellow-100' :
                    'bg-green-100'
                  }`}>
                    <MapPin className={`w-5 h-5 ${
                      zone.risk === 'high' ? 'text-red-600' :
                      zone.risk === 'medium' ? 'text-yellow-600' :
                      'text-green-600'
                    }`} />
                  </div>
                  <div>
                    <div className="font-bold text-gray-900">{zone.zone}</div>
                    <div className="flex items-center space-x-4 mt-1 text-sm text-gray-600">
                      <span className="flex items-center">
                        <Users className="w-4 h-4 mr-1" />
                        {zone.workers} workers
                      </span>
                      <span className="flex items-center">
                        <TrendingUp className="w-4 h-4 mr-1" />
                        ₹{zone.avgEarnings}/day
                      </span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                    zone.risk === 'high' ? 'bg-red-100 text-red-700' :
                    zone.risk === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-green-100 text-green-700'
                  }`}>
                    {zone.risk.toUpperCase()} RISK
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Legend */}
        <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="w-6 h-6 text-blue-600 mt-1" />
            <div>
              <h3 className="font-bold text-gray-900 mb-2">Risk Calculation</h3>
              <p className="text-sm text-gray-700 mb-2">
                Risk zones are calculated using AI analysis of historical data:
              </p>
              <ul className="text-sm text-gray-700 space-y-1">
                <li>• Weather patterns (rainfall, temperature, air quality)</li>
                <li>• Traffic congestion levels</li>
                <li>• Platform outage frequency</li>
                <li>• Historical claim density</li>
                <li>• Worker earnings fluctuation</li>
              </ul>
            </div>
          </div>
        </Card>
      </div>
    </DashboardLayout>
  );
}
