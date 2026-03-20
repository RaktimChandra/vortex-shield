'use client';

import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { 
  Cloud, 
  AlertTriangle, 
  Activity,
  CheckCircle,
  XCircle,
  Clock,
  MapPin,
  Zap
} from 'lucide-react';
import { claimApi } from '@/lib/api';
import toast from 'react-hot-toast';
import { formatDate } from '@/lib/utils';

export default function TriggersPage() {
  const [triggers, setTriggers] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [checking, setChecking] = useState(false);

  useEffect(() => {
    loadTriggers();
  }, []);

  const loadTriggers = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8001/triggers/check?demo=true', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      const data = await response.json();
      
      // Convert backend format to frontend format
      const triggersData = data.triggers_data.map((t: any, idx: number) => ({
        id: idx + 1,
        type: t.type,
        status: t.status,
        location: t.location,
        conditions: t.conditions,
        triggered: t.triggered,
        severity: t.severity,
        timestamp: new Date().toISOString(),
      }));
      
      setTriggers(triggersData);
      
      if (data.triggered) {
        toast.success(`${data.triggers_activated.length} trigger(s) activated!`);
      }
    } catch (error) {
      toast.error('Failed to load triggers');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckTriggers = async () => {
    try {
      setChecking(true);
      await fetch('http://localhost:8001/triggers/check', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      toast.success('Trigger check initiated! Monitoring for disruptions...');
      loadTriggers();
    } catch (error) {
      toast.error('Failed to check triggers');
    } finally {
      setChecking(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-96">
          <LoadingSpinner size="lg" />
        </div>
      </DashboardLayout>
    );
  }

  const stats = {
    active: triggers.filter(t => t.status === 'active').length,
    triggered: triggers.filter(t => t.triggered).length,
    monitoring: triggers.filter(t => t.status === 'monitoring').length,
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header with Gradient */}
        <div className="bg-gradient-to-r from-orange-500 via-red-500 to-pink-600 rounded-2xl p-8 text-white shadow-2xl">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">⚡ Parametric Triggers</h1>
              <p className="text-orange-100 text-lg">Real-time monitoring of disruption conditions</p>
            </div>
            <div className="bg-white/20 backdrop-blur-lg rounded-2xl p-4">
              <Zap className="w-16 h-16" />
            </div>
          </div>
        </div>
        <button 
          onClick={handleCheckTriggers}
          disabled={checking}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg flex items-center space-x-2 font-medium shadow-lg transition-all disabled:opacity-50"
        >
          <Zap className="w-5 h-5" />
          <span>{checking ? 'Checking...' : 'Check Now'}</span>
        </button>

        {/* Stats - Gradient Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl p-6 text-white shadow-xl hover:scale-105 transition-transform">
            <div className="text-5xl font-bold mb-2">{stats.active}</div>
            <div className="text-blue-100 font-medium">Active Monitors</div>
          </div>
          <div className="bg-gradient-to-br from-red-500 to-pink-600 rounded-2xl p-6 text-white shadow-xl hover:scale-105 transition-transform">
            <div className="text-5xl font-bold mb-2">{stats.triggered}</div>
            <div className="text-red-100 font-medium">Triggered</div>
          </div>
          <div className="bg-gradient-to-br from-yellow-500 to-orange-600 rounded-2xl p-6 text-white shadow-xl hover:scale-105 transition-transform">
            <div className="text-5xl font-bold mb-2">{stats.monitoring}</div>
            <div className="text-yellow-100 font-medium">Monitoring</div>
          </div>
          <div className="bg-gradient-to-br from-green-500 to-emerald-700 rounded-2xl p-6 text-white shadow-xl hover:scale-105 transition-transform">
            <div className="text-5xl font-bold mb-2">{stats.active}</div>
            <div className="text-green-100 font-medium">Active</div>
          </div>
        </div>

        {/* Info Card - Enhanced */}
        <div className="bg-gradient-to-r from-blue-500 via-purple-600 to-pink-500 rounded-2xl p-8 text-white shadow-2xl">
          <div className="flex items-start space-x-4">
            <div className="p-4 bg-white/20 backdrop-blur-lg rounded-2xl">
              <AlertTriangle className="w-8 h-8" />
            </div>
            <div>
              <h3 className="text-2xl font-bold mb-3">🤖 How AI-Powered Parametric Triggers Work</h3>
              <p className="text-blue-100 text-base leading-relaxed">
                Our AI monitors real-time data from weather APIs, traffic systems, and platform status. 
                When conditions meet predefined thresholds (e.g., rainfall ≥ 40mm, traffic congestion ≥ 70%), 
                triggers automatically activate and claims are processed instantly without manual intervention.
              </p>
              <div className="mt-4 flex items-center space-x-2 text-sm bg-white/10 backdrop-blur-sm rounded-lg px-4 py-2 w-fit">
                <CheckCircle className="w-4 h-4" />
                <span>100% Automated • Zero Documentation • Instant Payout</span>
              </div>
            </div>
          </div>
        </div>

        {/* Triggers List */}
        <div className="space-y-4">
          {triggers.map((trigger) => (
            <Card key={trigger.id} className="hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className={`p-3 rounded-lg ${
                    trigger.type === 'weather' ? 'bg-blue-100' :
                    trigger.type === 'platform' ? 'bg-purple-100' :
                    'bg-orange-100'
                  }`}>
                    {trigger.type === 'weather' ? (
                      <Cloud className="w-6 h-6 text-blue-600" />
                    ) : trigger.type === 'platform' ? (
                      <Activity className="w-6 h-6 text-purple-600" />
                    ) : (
                      <AlertTriangle className="w-6 h-6 text-orange-600" />
                    )}
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <h3 className="font-bold text-lg text-gray-900 capitalize">
                        {trigger.type} Trigger
                      </h3>
                      <Badge variant={trigger.triggered ? 'success' : 'default'}>
                        {trigger.status}
                      </Badge>
                      {trigger.triggered && (
                        <Badge variant="danger">
                          <Zap className="w-3 h-3 mr-1" />
                          TRIGGERED
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-gray-600 mt-1">
                      <MapPin className="w-4 h-4" />
                      <span>{trigger.location}</span>
                    </div>
                    <div className="mt-2 text-sm">
                      {trigger.type === 'weather' && (
                        <div className="flex space-x-4">
                          <span className="text-gray-600">
                            Rainfall: <span className="font-medium text-blue-600">{trigger.conditions.rainfall}mm</span>
                          </span>
                          <span className="text-gray-600">
                            Temp: <span className="font-medium">{trigger.conditions.temperature}°C</span>
                          </span>
                        </div>
                      )}
                      {trigger.type === 'platform' && (
                        <span className="text-gray-600">
                          Uptime: <span className="font-medium text-green-600">{trigger.conditions.uptime}%</span>
                        </span>
                      )}
                      {trigger.type === 'traffic' && (
                        <span className="text-gray-600">
                          Congestion: <span className="font-medium text-orange-600">{trigger.conditions.congestion}%</span>
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-600">Last checked</div>
                  <div className="font-medium">{formatDate(trigger.timestamp)}</div>
                  {trigger.triggered ? (
                    <div className="mt-2">
                      <Badge variant="success" size="sm">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Auto-claim eligible
                      </Badge>
                    </div>
                  ) : (
                    <div className="mt-2">
                      <Badge variant="default" size="sm">
                        <Clock className="w-3 h-3 mr-1" />
                        Monitoring
                      </Badge>
                    </div>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>

        {triggers.length === 0 && (
          <Card>
            <div className="text-center py-12">
              <Zap className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Active Triggers</h3>
              <p className="text-gray-600">Click "Check Now" to scan for disruptions in your area</p>
            </div>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
