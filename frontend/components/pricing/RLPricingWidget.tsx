'use client';

import { useState } from 'react';
import { DollarSign, TrendingUp, Zap } from 'lucide-react';
import toast from 'react-hot-toast';

export function RLPricingWidget() {
  const [loading, setLoading] = useState(false);
  const [pricingResult, setPricingResult] = useState<any>(null);

  const calculateOptimalPricing = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8001/ai/rl-pricing', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          user_risk_score: 0.3,
          market_demand: 0.7,
          claims_history: 2,
          work_hours: 8
        })
      });
      
      const data = await response.json();
      setPricingResult(data);
      toast.success('Optimal pricing calculated!');
    } catch (error) {
      toast.error('Failed to calculate pricing');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl p-6 shadow-xl border border-gray-200">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-gray-900 flex items-center">
            <Zap className="w-6 h-6 mr-2 text-purple-600" />
            AI Dynamic Pricing (RL)
          </h3>
          <p className="text-sm text-gray-600 mt-1">Reinforcement learning optimization</p>
        </div>
        <button
          onClick={calculateOptimalPricing}
          disabled={loading}
          className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-xl font-bold hover:from-purple-700 hover:to-pink-700 transition-all disabled:opacity-50 shadow-lg"
        >
          {loading ? 'Calculating...' : 'Calculate'}
        </button>
      </div>

      {pricingResult ? (
        <div className="space-y-4">
          {/* Optimal Premium */}
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-4 border border-green-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-green-700 font-medium">Optimal Weekly Premium</p>
                <p className="text-3xl font-bold text-green-900 mt-1">
                  ₹{pricingResult.optimal_premium.toFixed(2)}
                </p>
              </div>
              <DollarSign className="w-12 h-12 text-green-600 opacity-50" />
            </div>
          </div>

          {/* Expected Profit */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-blue-700 font-medium">Expected Profit</p>
                <p className="text-2xl font-bold text-blue-900 mt-1">
                  ₹{pricingResult.expected_profit.toFixed(2)}
                </p>
              </div>
              <TrendingUp className="w-10 h-10 text-blue-600 opacity-50" />
            </div>
          </div>

          {/* Q-Values */}
          <div className="bg-gray-50 rounded-xl p-4">
            <p className="text-sm font-medium text-gray-700 mb-3">RL Q-Values (Action Values):</p>
            <div className="space-y-2">
              {Object.entries(pricingResult.q_values).map(([action, value]: [string, any]) => (
                <div key={action} className="flex items-center justify-between">
                  <span className="text-sm capitalize text-gray-600">{action.replace('_', ' ')}</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${action === pricingResult.action_taken ? 'bg-purple-600' : 'bg-gray-400'}`}
                        style={{ width: `${(value / Math.max(...Object.values(pricingResult.q_values))) * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium w-12">₹{value}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Action Taken */}
          <div className="bg-purple-50 rounded-xl p-4 border border-purple-200">
            <p className="text-sm text-purple-700 font-medium">Best Action Selected:</p>
            <p className="text-lg font-bold text-purple-900 capitalize mt-1">
              {pricingResult.action_taken.replace('_', ' ')}
            </p>
          </div>

          <div className="text-xs text-gray-500 text-center mt-4">
            Using Q-learning reinforcement learning algorithm
          </div>
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          <p>Click "Calculate" to get AI-optimized pricing</p>
          <p className="text-xs mt-2">Based on your risk profile and market demand</p>
        </div>
      )}
    </div>
  );
}
