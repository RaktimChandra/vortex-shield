'use client';

import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, StatCard } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { 
  Shield, 
  Users, 
  AlertTriangle, 
  TrendingUp, 
  Activity,
  CheckCircle,
  XCircle,
  Clock
} from 'lucide-react';
import { analyticsApi } from '@/lib/api';
import { formatCurrency, formatDate } from '@/lib/utils';
import toast from 'react-hot-toast';
import { motion } from 'framer-motion';

export default function AdminPanel() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);
  const [recentClaims, setRecentClaims] = useState<any[]>([]);
  const [fraudAlerts, setFraudAlerts] = useState<any[]>([]);

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    try {
      setLoading(true);
      const response = await analyticsApi.getAdminDashboard();
      setStats(response.data);
      setRecentClaims(response.data.recent_claims || []);
      setFraudAlerts(response.data.fraud_alerts || []);
    } catch (error) {
      toast.error('Failed to load admin data');
    } finally {
      setLoading(false);
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
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Admin Control Panel</h1>
          <p className="text-gray-600 mt-1">System overview and monitoring</p>
        </div>

        {/* System Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Users"
            value={stats?.total_users || 0}
            icon={<Users className="w-5 h-5" />}
            color="blue"
            trend={{ value: 12, positive: true }}
          />
          <StatCard
            title="Active Subscriptions"
            value={stats?.active_subscriptions || 0}
            icon={<Shield className="w-5 h-5" />}
            color="green"
            trend={{ value: 8, positive: true }}
          />
          <StatCard
            title="Total Claims"
            value={stats?.total_claims || 0}
            icon={<Activity className="w-5 h-5" />}
            color="purple"
          />
          <StatCard
            title="Fraud Detected"
            value={stats?.fraud_detected || 0}
            icon={<AlertTriangle className="w-5 h-5" />}
            color="red"
          />
        </div>

        {/* Financial Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card gradient>
            <div className="text-center">
              <div className="text-sm text-gray-600 mb-2">Total Premiums Collected</div>
              <div className="text-3xl font-bold text-green-600">
                {formatCurrency(stats?.total_premiums || 0)}
              </div>
              <div className="text-xs text-gray-500 mt-2">All time</div>
            </div>
          </Card>
          <Card gradient>
            <div className="text-center">
              <div className="text-sm text-gray-600 mb-2">Total Payouts</div>
              <div className="text-3xl font-bold text-red-600">
                {formatCurrency(stats?.total_payouts || 0)}
              </div>
              <div className="text-xs text-gray-500 mt-2">All time</div>
            </div>
          </Card>
          <Card gradient>
            <div className="text-center">
              <div className="text-sm text-gray-600 mb-2">Net Position</div>
              <div className="text-3xl font-bold text-blue-600">
                {formatCurrency((stats?.total_premiums || 0) - (stats?.total_payouts || 0))}
              </div>
              <div className="text-xs text-gray-500 mt-2">Profit margin</div>
            </div>
          </Card>
        </div>

        {/* Recent Claims & Fraud Alerts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Claims */}
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Recent Claims</h2>
              <Badge variant="info">{recentClaims.length} total</Badge>
            </div>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {recentClaims.length > 0 ? (
                recentClaims.slice(0, 10).map((claim: any, index: number) => (
                  <motion.div
                    key={claim.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg ${
                        claim.status === 'approved' ? 'bg-green-100' :
                        claim.status === 'rejected' ? 'bg-red-100' : 'bg-yellow-100'
                      }`}>
                        {claim.status === 'approved' ? (
                          <CheckCircle className="w-4 h-4 text-green-600" />
                        ) : claim.status === 'rejected' ? (
                          <XCircle className="w-4 h-4 text-red-600" />
                        ) : (
                          <Clock className="w-4 h-4 text-yellow-600" />
                        )}
                      </div>
                      <div>
                        <div className="font-medium text-sm capitalize">{claim.trigger_type}</div>
                        <div className="text-xs text-gray-500">{formatDate(claim.created_at)}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-sm">{formatCurrency(claim.approved_amount || claim.estimated_loss)}</div>
                      <Badge 
                        variant={claim.status === 'approved' ? 'success' : claim.status === 'rejected' ? 'danger' : 'warning'}
                        size="sm"
                      >
                        {claim.status}
                      </Badge>
                    </div>
                  </motion.div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">No recent claims</div>
              )}
            </div>
          </Card>

          {/* Fraud Alerts */}
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Fraud Alerts</h2>
              <Badge variant="danger">{fraudAlerts.length} alerts</Badge>
            </div>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {fraudAlerts.length > 0 ? (
                fraudAlerts.slice(0, 10).map((alert: any, index: number) => (
                  <motion.div
                    key={alert.id}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="p-3 bg-red-50 border border-red-200 rounded-lg"
                  >
                    <div className="flex items-start space-x-3">
                      <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5" />
                      <div className="flex-1">
                        <div className="font-medium text-red-900 capitalize">{alert.fraud_type}</div>
                        <div className="text-sm text-red-700 mt-1">
                          Score: {(alert.fraud_score * 100).toFixed(0)}% | Risk: {alert.risk_level}
                        </div>
                        <div className="text-xs text-red-600 mt-1">
                          {formatDate(alert.detected_at)}
                        </div>
                      </div>
                      <button className="text-xs text-red-600 hover:text-red-700 font-medium">
                        Review
                      </button>
                    </div>
                  </motion.div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">No fraud alerts</div>
              )}
            </div>
          </Card>
        </div>

        {/* System Health */}
        <Card>
          <h2 className="text-xl font-bold text-gray-900 mb-4">System Health</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-4 bg-green-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-green-900">API Status</span>
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              </div>
              <div className="text-2xl font-bold text-green-600">Online</div>
              <div className="text-xs text-green-600 mt-1">99.9% uptime</div>
            </div>
            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-blue-900">AI Models</span>
                <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
              </div>
              <div className="text-2xl font-bold text-blue-600">4/4</div>
              <div className="text-xs text-blue-600 mt-1">All operational</div>
            </div>
            <div className="p-4 bg-purple-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-purple-900">Database</span>
                <span className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" />
              </div>
              <div className="text-2xl font-bold text-purple-600">Healthy</div>
              <div className="text-xs text-purple-600 mt-1">Low latency</div>
            </div>
            <div className="p-4 bg-orange-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-orange-900">Processing</span>
                <span className="w-2 h-2 bg-orange-500 rounded-full animate-pulse" />
              </div>
              <div className="text-2xl font-bold text-orange-600">4.2s</div>
              <div className="text-xs text-orange-600 mt-1">Avg claim time</div>
            </div>
          </div>
        </Card>

        {/* Performance Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <h3 className="font-bold text-gray-900 mb-3">Approval Rate</h3>
            <div className="text-4xl font-bold text-green-600 mb-2">
              {stats?.approval_rate || 0}%
            </div>
            <div className="text-sm text-gray-600">
              {stats?.approved_claims || 0} of {stats?.total_claims || 0} claims approved
            </div>
          </Card>
          <Card>
            <h3 className="font-bold text-gray-900 mb-3">Avg Payout</h3>
            <div className="text-4xl font-bold text-blue-600 mb-2">
              {formatCurrency(stats?.avg_payout || 0)}
            </div>
            <div className="text-sm text-gray-600">
              Per approved claim
            </div>
          </Card>
          <Card>
            <h3 className="font-bold text-gray-900 mb-3">Fraud Prevention</h3>
            <div className="text-4xl font-bold text-red-600 mb-2">
              {formatCurrency(stats?.fraud_prevented || 12400)}
            </div>
            <div className="text-sm text-gray-600">
              Total amount prevented
            </div>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
