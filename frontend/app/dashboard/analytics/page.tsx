'use client';

import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card } from '@/components/ui/Card';
import { TrendChart } from '@/components/charts/TrendChart';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { 
  PieChart, 
  Pie, 
  Cell, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  ResponsiveContainer 
} from 'recharts';
import { 
  TrendingUp, 
  DollarSign, 
  Shield, 
  AlertTriangle,
  Download 
} from 'lucide-react';
import { analyticsApi } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';
import toast from 'react-hot-toast';

export default function AnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState<any>(null);
  const [lstmPredictions, setLstmPredictions] = useState<any>(null);
  const [riskDistribution, setRiskDistribution] = useState<any[]>([]);
  const [claimsByMonth, setClaimsByMonth] = useState<any[]>([]);
  const [payoutTrend, setPayoutTrend] = useState<any[]>([]);

  useEffect(() => {
    loadAnalytics();
    loadLSTMPredictions();
    loadRealCharts();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const response = await analyticsApi.getDashboard();
      setAnalytics(response.data);
    } catch (error) {
      toast.error('Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  const loadRealCharts = async () => {
    try {
      const response = await fetch('http://localhost:8001/real-data/analytics-charts?demo=true', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      const data = await response.json();
      setRiskDistribution(data.risk_distribution);
      setClaimsByMonth(data.claims_by_month);
      setPayoutTrend(data.payout_trend);
    } catch (error) {
      console.error('Failed to load real analytics:', error);
    }
  };

  const loadLSTMPredictions = async () => {
    try {
      // Use historical risk data (mock for now, can be from database)
      const historicalData = [0.3, 0.35, 0.4, 0.38, 0.42, 0.45, 0.5];
      
      const response = await fetch('http://localhost:8001/ai/predict-disruptions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          historical_data: historicalData,
          predict_steps: 7
        })
      });
      
      const data = await response.json();
      setLstmPredictions(data);
    } catch (error) {
      console.error('Failed to load LSTM predictions:', error);
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

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header with Gradient */}
        <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-2xl p-8 text-white shadow-2xl">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">📊 Analytics Dashboard</h1>
              <p className="text-indigo-100 text-lg">AI-powered insights and performance metrics</p>
            </div>
            <button className="bg-white/20 backdrop-blur-lg hover:bg-white/30 text-white px-8 py-4 rounded-xl flex items-center space-x-2 font-bold shadow-lg transition-all transform hover:scale-105">
              <Download className="w-5 h-5" />
              <span>Export Report</span>
            </button>
          </div>
        </div>

        {/* Key Metrics - Gradient Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl p-6 text-white shadow-xl hover:scale-105 transition-transform">
            <div className="flex items-center justify-between mb-4">
              <DollarSign className="w-10 h-10 opacity-80" />
              <div className="text-right">
                <p className="text-blue-100 text-sm mb-1">Total Revenue</p>
                <p className="text-4xl font-bold">
                  {formatCurrency(analytics?.total_payout || 0)}
                </p>
              </div>
            </div>
            <div className="flex items-center text-sm">
              <TrendingUp className="w-4 h-4 mr-1" />
              <span className="text-blue-100">+15% this month</span>
            </div>
          </div>

          <Card gradient hover>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-600">Claims Filed</div>
                <div className="text-2xl font-bold text-gray-900 mt-1">
                  {analytics?.total_claims || 0}
                </div>
                <div className="text-xs text-green-600 mt-1 flex items-center">
                  <TrendingUp className="w-3 h-3 mr-1" />
                  +8% from last month
                </div>
              </div>
              <div className="p-3 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg">
                <Shield className="w-6 h-6 text-white" />
              </div>
            </div>
          </Card>

          <Card gradient hover>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-600">Approval Rate</div>
                <div className="text-2xl font-bold text-gray-900 mt-1">
                  {analytics?.approval_rate || 0}%
                </div>
                <div className="text-xs text-green-600 mt-1 flex items-center">
                  <TrendingUp className="w-3 h-3 mr-1" />
                  +3% from last month
                </div>
              </div>
              <div className="p-3 bg-gradient-to-br from-green-500 to-green-600 rounded-lg">
                <Shield className="w-6 h-6 text-white" />
              </div>
            </div>
          </Card>

          <Card gradient hover>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-600">Avg Processing</div>
                <div className="text-2xl font-bold text-gray-900 mt-1">
                  4.2s
                </div>
                <div className="text-xs text-green-600 mt-1 flex items-center">
                  <TrendingUp className="w-3 h-3 mr-1" />
                  -0.5s from last month
                </div>
              </div>
              <div className="p-3 bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg">
                <AlertTriangle className="w-6 h-6 text-white" />
              </div>
            </div>
          </Card>
        </div>

        {/* LSTM Disruption Predictions */}
        {lstmPredictions && (
          <Card>
            <h2 className="text-xl font-bold text-gray-900 mb-4">🤖 AI Disruption Predictions (LSTM)</h2>
            <p className="text-sm text-gray-600 mb-4">7-day forecast using machine learning</p>
            <div className="space-y-3">
              {lstmPredictions.predictions.map((pred: number, idx: number) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="font-medium">Day {idx + 1}</span>
                  <div className="flex items-center space-x-3">
                    <div className="w-48 bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${pred > 0.7 ? 'bg-red-500' : pred > 0.4 ? 'bg-yellow-500' : 'bg-green-500'}`}
                        style={{ width: `${pred * 100}%` }}
                      ></div>
                    </div>
                    <span className="font-bold text-sm w-12">{(pred * 100).toFixed(0)}%</span>
                  </div>
                </div>
              ))}
              <div className="mt-4 p-3 bg-blue-50 rounded-lg text-sm">
                <p className="font-medium text-blue-900">Trend: {lstmPredictions.trend}</p>
                <p className="text-blue-700 mt-1">Using real-time LSTM neural network predictions</p>
              </div>
            </div>
          </Card>
        )}

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Risk Distribution */}
          <Card>
            <h2 className="text-xl font-bold text-gray-900 mb-4">Risk Distribution</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={riskDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {riskDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>

          {/* Claims by Month */}
          <Card>
            <h2 className="text-xl font-bold text-gray-900 mb-4">Claims by Month</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={claimsByMonth}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="approved" fill="#10b981" name="Approved" />
                <Bar dataKey="rejected" fill="#ef4444" name="Rejected" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </div>

        {/* Payout Trend */}
        <Card>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Payout Trend</h2>
          <TrendChart
            data={payoutTrend}
            dataKey="amount"
            xAxisKey="month"
            color="#8b5cf6"
            height={350}
          />
        </Card>

        {/* Fraud Analysis */}
        <Card>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Fraud Detection Stats</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-6 bg-red-50 rounded-lg">
              <div className="text-4xl font-bold text-red-600">2</div>
              <div className="text-sm text-gray-600 mt-2">Fraud Detected</div>
              <div className="text-xs text-gray-500 mt-1">Last 30 days</div>
            </div>
            <div className="text-center p-6 bg-green-50 rounded-lg">
              <div className="text-4xl font-bold text-green-600">98%</div>
              <div className="text-sm text-gray-600 mt-2">Detection Accuracy</div>
              <div className="text-xs text-gray-500 mt-1">AI Model Performance</div>
            </div>
            <div className="text-center p-6 bg-blue-50 rounded-lg">
              <div className="text-4xl font-bold text-blue-600">₹12,400</div>
              <div className="text-sm text-gray-600 mt-2">Fraud Prevented</div>
              <div className="text-xs text-gray-500 mt-1">Total savings</div>
            </div>
          </div>
        </Card>

        {/* Insights */}
        <Card>
          <h2 className="text-xl font-bold text-gray-900 mb-4">AI Insights & Recommendations</h2>
          <div className="space-y-4">
            <div className="flex items-start space-x-3 p-4 bg-blue-50 rounded-lg">
              <Shield className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <div className="font-medium text-blue-900">Risk Level Stable</div>
                <div className="text-sm text-blue-700 mt-1">
                  Your current zone shows stable risk patterns. No immediate disruptions expected.
                </div>
              </div>
            </div>
            <div className="flex items-start space-x-3 p-4 bg-green-50 rounded-lg">
              <TrendingUp className="w-5 h-5 text-green-600 mt-0.5" />
              <div>
                <div className="font-medium text-green-900">High Claim Success Rate</div>
                <div className="text-sm text-green-700 mt-1">
                  Your claims have a 92% approval rate, indicating accurate filing practices.
                </div>
              </div>
            </div>
            <div className="flex items-start space-x-3 p-4 bg-purple-50 rounded-lg">
              <DollarSign className="w-5 h-5 text-purple-600 mt-0.5" />
              <div>
                <div className="font-medium text-purple-900">Cost Optimization</div>
                <div className="text-sm text-purple-700 mt-1">
                  Based on your risk profile, you could save ₹200/month by adjusting coverage.
                </div>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </DashboardLayout>
  );
}
