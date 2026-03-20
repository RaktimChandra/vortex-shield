'use client';

import { useState, useEffect } from 'react';
import { TrendingUp, RefreshCw, AlertTriangle } from 'lucide-react';
import { useWebSocket } from '@/lib/websocket';
import { RiskGauge } from '../charts/RiskGauge';
import { motion } from 'framer-motion';

interface RiskData {
  risk_level: string;
  risk_score: number;
  risk_factors: any;
  recommendations: string[];
}

export function LiveRiskMonitor() {
  const [riskData, setRiskData] = useState<RiskData | null>(null);
  const [isLive, setIsLive] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const ws = useWebSocket();

  useEffect(() => {
    // Fetch REAL risk data from triggers API
    const fetchRealRiskData = async () => {
      try {
        const response = await fetch('http://localhost:8001/triggers/check?demo=true', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        const data = await response.json();
        
        // Convert trigger data to risk data
        const weatherTrigger = data.triggers_data.find((t: any) => t.type === 'weather');
        const trafficTrigger = data.triggers_data.find((t: any) => t.type === 'traffic');
        
        const riskLevel = data.triggered ? 'HIGH' : weatherTrigger?.severity === 'medium' ? 'MEDIUM' : 'LOW';
        const riskScore = data.triggered ? 0.8 : weatherTrigger?.severity === 'medium' ? 0.5 : 0.2;
        
        const newRiskData: RiskData = {
          risk_level: riskLevel,
          risk_score: riskScore,
          risk_factors: {
            weather: { 
              impact: `${weatherTrigger?.conditions.rainfall_mm}mm rainfall, ${weatherTrigger?.conditions.temperature}°C`, 
              severity: weatherTrigger?.severity || 'low' 
            },
            traffic: { 
              impact: `${trafficTrigger?.conditions.congestion}% congestion`, 
              severity: trafficTrigger?.severity || 'low' 
            },
          },
          recommendations: riskLevel === 'HIGH' 
            ? ['Avoid deliveries - heavy rain detected', 'High risk zone', 'Wait for conditions to improve']
            : riskLevel === 'MEDIUM'
            ? ['Monitor weather closely', 'Moderate risk', 'Proceed with caution']
            : ['Optimal conditions for deliveries', 'Low risk', 'Normal operations'],
        };
        
        setRiskData(newRiskData);
        setLastUpdate(new Date());
        setIsLive(true);
      } catch (error) {
        console.error('Failed to fetch real risk data:', error);
      }
    };

    // Fetch immediately
    fetchRealRiskData();

    // Listen for risk updates from WebSocket
    const handleRiskUpdate = (data: any) => {
      setRiskData({
        risk_level: data.risk_level,
        risk_score: data.risk_score,
        risk_factors: data.factors || {},
        recommendations: data.recommendations || [],
      });
      setLastUpdate(new Date());
      setIsLive(true);
    };

    ws.on('risk_update', handleRiskUpdate);

    // Fetch real data every 60 seconds
    const interval = setInterval(fetchRealRiskData, 60000);

    return () => {
      ws.off('risk_update', handleRiskUpdate);
      clearInterval(interval);
    };
  }, []);

  const requestUpdate = () => {
    ws.requestRiskUpdate();
    setIsLive(false);
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'HIGH':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'MEDIUM':
        return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'LOW':
        return 'text-green-600 bg-green-50 border-green-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <TrendingUp className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold">Live Risk Monitor</h3>
          {isLive && (
            <span className="flex items-center space-x-1 text-xs text-green-600">
              <span className="w-2 h-2 bg-green-600 rounded-full animate-pulse"></span>
              <span>LIVE</span>
            </span>
          )}
        </div>
        <button
          onClick={requestUpdate}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          title="Refresh risk data"
        >
          <RefreshCw className={`w-4 h-4 ${isLive ? '' : 'animate-spin'}`} />
        </button>
      </div>

      {riskData ? (
        <div className="space-y-4">
          {/* Risk Gauge */}
          <div className="flex justify-center">
            <RiskGauge
              score={riskData.risk_score}
              level={riskData.risk_level}
              size={200}
            />
          </div>

          {/* Risk Level Badge */}
          <div className="text-center">
            <span
              className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium border ${getRiskColor(
                riskData.risk_level
              )}`}
            >
              {riskData.risk_level} RISK
            </span>
          </div>

          {/* Risk Factors */}
          {Object.keys(riskData.risk_factors).length > 0 && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="text-sm font-semibold mb-2 flex items-center">
                <AlertTriangle className="w-4 h-4 mr-2 text-orange-500" />
                Active Risk Factors
              </h4>
              <div className="space-y-2">
                {Object.entries(riskData.risk_factors).map(([key, factor]: [string, any]) => (
                  <motion.div
                    key={key}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="flex items-center justify-between text-sm"
                  >
                    <span className="text-gray-700">{factor.impact}</span>
                    <span
                      className={`px-2 py-1 rounded text-xs ${
                        factor.severity === 'high'
                          ? 'bg-red-100 text-red-700'
                          : 'bg-orange-100 text-orange-700'
                      }`}
                    >
                      {factor.severity}
                    </span>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {riskData.recommendations.length > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="text-sm font-semibold mb-2 text-blue-900">Recommendations</h4>
              <ul className="space-y-1 text-sm text-blue-800">
                {riskData.recommendations.map((rec, idx) => (
                  <li key={idx} className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Last Update */}
          {lastUpdate && (
            <p className="text-xs text-gray-500 text-center">
              Last updated: {lastUpdate.toLocaleTimeString()}
            </p>
          )}
        </div>
      ) : (
        <div className="text-center py-8">
          <button
            onClick={requestUpdate}
            className="btn-primary inline-flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Get Risk Assessment</span>
          </button>
          <p className="text-sm text-gray-500 mt-2">
            Click to fetch real-time risk data
          </p>
        </div>
      )}
    </div>
  );
}
