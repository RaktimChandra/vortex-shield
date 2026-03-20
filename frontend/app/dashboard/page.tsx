'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, StatCard } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { RiskGauge } from '@/components/charts/RiskGauge';
import { TrendChart } from '@/components/charts/TrendChart';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { LiveRiskMonitor } from '@/components/dashboard/LiveRiskMonitor';
import dynamic from 'next/dynamic';

const RLPricingWidget = dynamic(() => import('@/components/pricing/RLPricingWidget').then(mod => mod.RLPricingWidget), {
  ssr: false,
});

import { 
  Shield, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  DollarSign,
  Activity,
  MapPin,
  FileText,
  BarChart3,
  X
} from 'lucide-react';
import { analyticsApi, subscriptionApi, claimApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { formatCurrency, formatDate, getRiskColor } from '@/lib/utils';
import toast from 'react-hot-toast';

export default function Dashboard() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);
  const [subscription, setSubscription] = useState<any>(null);
  const [recentClaims, setRecentClaims] = useState<any[]>([]);
  const [earningsTrendData, setEarningsTrendData] = useState<any[]>([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [statsRes, subsRes, claimsRes] = await Promise.all([
        analyticsApi.getDashboard(),
        subscriptionApi.getActive().catch(() => null),
        claimApi.getMy(),
      ]);

      setStats(statsRes.data);
      setSubscription(subsRes?.data);
      setRecentClaims(claimsRes.data.slice(0, 5));
    } catch (error: any) {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const loadEarningsTrend = async () => {
      try {
        const response = await fetch('http://localhost:8001/real-data/earnings-trend', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        const data = await response.json();
        setEarningsTrendData(data.length > 0 ? data : [
          { month: 'Jan', earnings: 0, protected: 0 },
          { month: 'Feb', earnings: 0, protected: 0 },
          { month: 'Mar', earnings: 0, protected: 0 },
          { month: 'Apr', earnings: 0, protected: 0 },
          { month: 'May', earnings: 0, protected: 0 },
          { month: 'Jun', earnings: 0, protected: 0 },
        ]);
      } catch (error) {
        console.error('Failed to load earnings trend:', error);
      }
    };
    loadEarningsTrend();
  }, []);

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
        <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-2xl p-8 text-white shadow-2xl">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">Welcome back, {user?.full_name}! 👋</h1>
              <p className="text-blue-100 text-lg">Your intelligent income protection dashboard</p>
            </div>
            <div className="bg-white/20 backdrop-blur-lg rounded-2xl p-4">
              <Shield className="w-16 h-16" />
            </div>
          </div>
        </div>

        {/* Stats Grid - Modern Gradient Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl p-6 text-white shadow-xl hover:scale-105 transition-transform">
            <div className="flex items-center justify-between mb-4">
              <FileText className="w-10 h-10 opacity-80" />
              <div className="text-right">
                <p className="text-blue-100 text-sm mb-1">Total Claims</p>
                <p className="text-4xl font-bold">{stats?.total_claims || 0}</p>
              </div>
            </div>
            <div className="flex items-center text-sm">
              <TrendingUp className="w-4 h-4 mr-1" />
              <span className="text-blue-100">+12% from last month</span>
            </div>
          </div>

          <div className="bg-gradient-to-br from-green-500 to-emerald-700 rounded-2xl p-6 text-white shadow-xl hover:scale-105 transition-transform">
            <div className="flex items-center justify-between mb-4">
              <DollarSign className="w-10 h-10 opacity-80" />
              <div className="text-right">
                <p className="text-green-100 text-sm mb-1">Total Payout</p>
                <p className="text-4xl font-bold">{formatCurrency(stats?.total_payout || 0)}</p>
              </div>
            </div>
            <div className="flex items-center text-sm">
              <TrendingUp className="w-4 h-4 mr-1" />
              <span className="text-green-100">+8% this week</span>
            </div>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl p-6 text-white shadow-xl hover:scale-105 transition-transform">
            <div className="flex items-center justify-between mb-4">
              <CheckCircle className="w-10 h-10 opacity-80" />
              <div className="text-right">
                <p className="text-purple-100 text-sm mb-1">Approval Rate</p>
                <p className="text-4xl font-bold">{stats?.approval_rate || 0}%</p>
              </div>
            </div>
            <div className="flex items-center text-sm">
              <span className="text-purple-100">Excellent rating</span>
            </div>
          </div>

          <div className="bg-gradient-to-br from-orange-500 to-red-600 rounded-2xl p-6 text-white shadow-xl hover:scale-105 transition-transform">
            <div className="flex items-center justify-between mb-4">
              <Shield className="w-10 h-10 opacity-80" />
              <div className="text-right">
                <p className="text-orange-100 text-sm mb-1">Trust Score</p>
                <p className="text-4xl font-bold">{(stats?.trust_score || 1.0).toFixed(2)}</p>
              </div>
            </div>
            <div className="flex items-center text-sm">
              <span className="text-orange-100">Maximum trust level</span>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Risk Analysis */}
          <Card className="lg:col-span-2">
            <div className="mb-6">
              <h2 className="text-xl font-bold text-gray-900">Current Risk Analysis</h2>
              <p className="text-sm text-gray-600 mt-1">Real-time assessment of disruption probability</p>
            </div>
            
            {subscription ? (
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <RiskGauge 
                    score={subscription.risk_score || 0.5} 
                    level={subscription.risk_level || 'MEDIUM'}
                  />
                </div>
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-600">Risk Level</span>
                      <Badge variant={
                        subscription.risk_level === 'LOW' ? 'success' : 
                        subscription.risk_level === 'MEDIUM' ? 'warning' : 'danger'
                      }>
                        {subscription.risk_level}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-600">Coverage</span>
                      <span className="text-sm font-bold">{formatCurrency(subscription.coverage_amount)}</span>
                    </div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-600">Weekly Premium</span>
                      <span className="text-sm font-bold">{formatCurrency(subscription.premium_amount)}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-600">Predicted Loss</span>
                      <span className="text-sm font-bold text-red-600">{formatCurrency(subscription.predicted_loss)}</span>
                    </div>
                  </div>
                  
                  <div className="pt-4 border-t">
                    <div className="text-sm font-medium text-gray-700 mb-2">Active Until</div>
                    <div className="text-lg font-bold text-gray-900">{formatDate(subscription.end_date)}</div>
                  </div>

                  <button className="w-full btn-primary">
                    Check Triggers
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <Shield className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Free Protection Enabled</h3>
                <p className="text-gray-600 mb-4">Your income is protected with VORTEX Shield</p>
                <div className="mt-4 p-4 bg-green-50 rounded-lg">
                  <p className="text-sm text-green-800 font-medium">✓ All features unlocked - 100% FREE</p>
                </div>
              </div>
            )}
          </Card>

          {/* Quick Actions - Gradient Buttons */}
          <div className="bg-white rounded-2xl p-6 shadow-xl">
            <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <Activity className="w-6 h-6 mr-2 text-purple-600" />
              Quick Actions
            </h3>
            <div className="space-y-3">
              <button 
                onClick={() => router.push('/dashboard/claims')}
                className="w-full flex items-center justify-between p-4 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-xl transition-all shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                <div className="flex items-center space-x-3">
                  <Activity className="w-6 h-6" />
                  <span className="font-bold text-lg">Check Triggers</span>
                </div>
                <TrendingUp className="w-5 h-5" />
              </button>
              <button 
                onClick={() => router.push('/dashboard/claims')}
                className="w-full flex items-center justify-between p-4 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white rounded-xl transition-all shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                <div className="flex items-center space-x-3">
                  <FileText className="w-6 h-6" />
                  <span className="font-bold text-lg">View Claims</span>
                </div>
                <CheckCircle className="w-5 h-5" />
              </button>
              <button 
                onClick={() => router.push('/dashboard/analytics')}
                className="w-full flex items-center justify-between p-4 bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white rounded-xl transition-all shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                <div className="flex items-center space-x-3">
                  <BarChart3 className="w-6 h-6" />
                  <span className="font-bold text-lg">Analytics</span>
                </div>
                <TrendingUp className="w-5 h-5" />
              </button>
              <button 
                onClick={() => router.push('/dashboard/map')}
                className="w-full flex items-center justify-between p-4 bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 text-white rounded-xl transition-all shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                <div className="flex items-center space-x-3">
                  <MapPin className="w-6 h-6" />
                  <span className="font-bold text-lg">Zone Map</span>
                </div>
                <MapPin className="w-5 h-5" />
              </button>
            </div>

            <div 
              onClick={() => router.push('/dashboard/settings')}
              className="mt-6 p-6 bg-gradient-to-br from-cyan-500 via-blue-600 to-purple-700 rounded-2xl text-white cursor-pointer hover:scale-105 transition-all shadow-xl"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm opacity-90 font-medium">📍 Your Location</span>
                <MapPin className="w-5 h-5" />
              </div>
              <div className="font-bold text-2xl mb-1">{user?.city || 'Mumbai'}</div>
              <div className="text-sm opacity-90">{user?.zone || 'Andheri West'}</div>
              <div className="mt-3 text-xs bg-white/20 backdrop-blur-sm rounded-lg px-3 py-2">
                Click to update location →
              </div>
            </div>
          </div>
        </div>

        {/* Earnings Trend */}
        <Card>
          <div className="mb-6">
            <h2 className="text-xl font-bold text-gray-900">Earnings & Protection Trend</h2>
            <p className="text-sm text-gray-600 mt-1">Monthly earnings and protected amounts</p>
          </div>
          <TrendChart
            data={earningsTrendData}
            dataKey="protected"
            xAxisKey="month"
            color="#8b5cf6"
            height={300}
          />
        </Card>

        {/* Live Risk Monitor */}
        <LiveRiskMonitor />

        {/* RL Dynamic Pricing */}
        <RLPricingWidget />

        {/* Recent Claims */}
        <Card>
          <div className="mb-6">
            <h2 className="text-xl font-bold text-gray-900">Recent Claims</h2>
            <p className="text-sm text-gray-600 mt-1">Your latest claim activities</p>
          </div>
          {recentClaims.length > 0 ? (
            <div className="space-y-3">
              {recentClaims.map((claim) => (
                <div key={claim.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                  <div className="flex items-center space-x-4">
                    <div className={`p-2 rounded-lg ${
                      claim.status === 'approved' ? 'bg-green-100 text-green-600' :
                      claim.status === 'rejected' ? 'bg-red-100 text-red-600' :
                      'bg-yellow-100 text-yellow-600'
                    }`}>
                      {claim.status === 'approved' ? <CheckCircle className="w-5 h-5" /> :
                       claim.status === 'rejected' ? <X className="w-5 h-5" /> :
                       <Clock className="w-5 h-5" />}
                    </div>
                    <div>
                      <div className="font-medium text-gray-900 capitalize">{claim.trigger_type} Disruption</div>
                      <div className="text-sm text-gray-600">{formatDate(claim.created_at)}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-gray-900">{formatCurrency(claim.approved_amount || claim.estimated_loss)}</div>
                    <Badge variant={
                      claim.status === 'approved' ? 'success' : 
                      claim.status === 'rejected' ? 'danger' : 'warning'
                    } size="sm">
                      {claim.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              No claims yet
            </div>
          )}
        </Card>
      </div>
    </DashboardLayout>
  );
}
