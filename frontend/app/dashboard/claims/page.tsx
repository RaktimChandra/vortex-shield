'use client';

import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { 
  FileText, 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertTriangle,
  Filter,
  Download,
  Eye,
  Plus,
  X as CloseIcon
} from 'lucide-react';
import { claimApi } from '@/lib/api';
import { formatCurrency, formatDate } from '@/lib/utils';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

export default function ClaimsPage() {
  const [claims, setClaims] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [selectedClaim, setSelectedClaim] = useState<any>(null);
  const [showReportModal, setShowReportModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    trigger_type: 'weather',
    description: '',
    estimated_loss: '',
    incident_date: new Date().toISOString().split('T')[0],
  });
  const [evidenceImage, setEvidenceImage] = useState<File | null>(null);
  const [imageAnalysis, setImageAnalysis] = useState<any>(null);

  useEffect(() => {
    loadClaims();
  }, []);

  const loadClaims = async () => {
    try {
      setLoading(true);
      const response = await claimApi.getMy();
      setClaims(response.data);
    } catch (error) {
      toast.error('Failed to load claims');
    } finally {
      setLoading(false);
    }
  };

  const handleImageUpload = async (file: File) => {
    setEvidenceImage(file);
    
    // Analyze image with CV API
    const formDataImg = new FormData();
    formDataImg.append('file', file);
    
    try {
      const response = await fetch('http://localhost:8001/ai/analyze-image', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: formDataImg
      });
      const analysis = await response.json();
      setImageAnalysis(analysis);
      
      if (analysis.weather_verified) {
        toast.success('✓ Image verified! Weather conditions detected');
      } else {
        toast.error('⚠ Image authenticity questionable');
      }
    } catch (error) {
      console.error('Image analysis failed:', error);
    }
  };

  const handleSubmitClaim = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      await claimApi.create({
        ...formData,
        estimated_loss: parseFloat(formData.estimated_loss),
      });
      toast.success('Claim submitted successfully! AI is analyzing...');
      setShowReportModal(false);
      setFormData({
        trigger_type: 'weather',
        description: '',
        estimated_loss: '',
        incident_date: new Date().toISOString().split('T')[0],
      });
      setEvidenceImage(null);
      setImageAnalysis(null);
      loadClaims();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to submit claim');
    } finally {
      setSubmitting(false);
    }
  };

  const filteredClaims = claims.filter(claim => {
    if (filter === 'all') return true;
    return claim.status === filter;
  });

  const stats = {
    total: claims.length,
    approved: claims.filter(c => c.status === 'approved').length,
    pending: claims.filter(c => c.status === 'pending').length,
    rejected: claims.filter(c => c.status === 'rejected').length,
    totalPayout: claims
      .filter(c => c.status === 'approved')
      .reduce((sum, c) => sum + (c.approved_amount || 0), 0),
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
        <div className="bg-gradient-to-r from-emerald-500 via-green-500 to-teal-600 rounded-2xl p-8 text-white shadow-2xl">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">📋 Claims Management</h1>
              <p className="text-green-100 text-lg">AI-powered instant claim processing</p>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={() => setShowReportModal(true)}
                className="bg-white/20 backdrop-blur-lg hover:bg-white/30 text-white px-8 py-4 rounded-xl flex items-center space-x-2 font-bold shadow-lg transition-all transform hover:scale-105"
              >
                <Plus className="w-6 h-6" />
                <span className="text-lg">Report Claim</span>
              </button>
              <button className="bg-white/10 backdrop-blur-lg hover:bg-white/20 text-white px-6 py-4 rounded-xl flex items-center space-x-2 transition-all">
                <Download className="w-5 h-5" />
                <span>Export</span>
              </button>
            </div>
          </div>
        </div>

        {/* Stats - Gradient Cards */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
          <div className="bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl p-6 text-white shadow-xl hover:scale-105 transition-transform">
            <div className="text-5xl font-bold mb-2">{stats.total}</div>
            <div className="text-blue-100 font-medium">Total Claims</div>
          </div>
          <div className="bg-gradient-to-br from-green-500 to-emerald-700 rounded-2xl p-6 text-white shadow-xl hover:scale-105 transition-transform">
            <div className="text-5xl font-bold mb-2">{stats.approved}</div>
            <div className="text-green-100 font-medium">Approved</div>
          </div>
          <div className="bg-gradient-to-br from-yellow-500 to-orange-600 rounded-2xl p-6 text-white shadow-xl hover:scale-105 transition-transform">
            <div className="text-5xl font-bold mb-2">{stats.pending}</div>
            <div className="text-yellow-100 font-medium">Pending</div>
          </div>
          <div className="bg-gradient-to-br from-red-500 to-pink-600 rounded-2xl p-6 text-white shadow-xl hover:scale-105 transition-transform">
            <div className="text-5xl font-bold mb-2">{stats.rejected}</div>
            <div className="text-red-100 font-medium">Rejected</div>
          </div>
          <div className="bg-gradient-to-br from-purple-500 to-indigo-700 rounded-2xl p-6 text-white shadow-xl hover:scale-105 transition-transform">
            <div className="text-3xl font-bold mb-2">{formatCurrency(stats.totalPayout)}</div>
            <div className="text-purple-100 font-medium">Total Payout</div>
          </div>
        </div>

        {/* Filters */}
        <Card>
          <div className="flex items-center space-x-2">
            <Filter className="w-5 h-5 text-gray-500" />
            <span className="font-medium text-gray-700">Filter:</span>
            <div className="flex space-x-2">
              {['all', 'approved', 'pending', 'rejected'].map((status) => (
                <button
                  key={status}
                  onClick={() => setFilter(status)}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    filter === status
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </Card>

        {/* Claims List */}
        <div className="space-y-4">
          {filteredClaims.length > 0 ? (
            filteredClaims.map((claim, index) => (
              <motion.div
                key={claim.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <div className="cursor-pointer" onClick={() => setSelectedClaim(claim)}>
                <Card className="hover:shadow-lg transition-shadow">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className={`p-3 rounded-lg ${
                        claim.status === 'approved' ? 'bg-green-100' :
                        claim.status === 'rejected' ? 'bg-red-100' :
                        'bg-yellow-100'
                      }`}>
                        {claim.status === 'approved' ? (
                          <CheckCircle className="w-6 h-6 text-green-600" />
                        ) : claim.status === 'rejected' ? (
                          <XCircle className="w-6 h-6 text-red-600" />
                        ) : (
                          <Clock className="w-6 h-6 text-yellow-600" />
                        )}
                      </div>
                      <div>
                        <div className="flex items-center space-x-2">
                          <h3 className="font-bold text-lg text-gray-900 capitalize">
                            {claim.trigger_type} Disruption
                          </h3>
                          <Badge variant={
                            claim.status === 'approved' ? 'success' :
                            claim.status === 'rejected' ? 'danger' : 'warning'
                          }>
                            {claim.status}
                          </Badge>
                        </div>
                        <div className="text-sm text-gray-600 mt-1">
                          Filed on {formatDate(claim.created_at)}
                        </div>
                        <div className="flex items-center space-x-4 mt-2 text-sm">
                          <span className="text-gray-600">
                            Fraud Score: <span className={`font-medium ${
                              claim.fraud_score < 0.3 ? 'text-green-600' :
                              claim.fraud_score < 0.7 ? 'text-yellow-600' : 'text-red-600'
                            }`}>{(claim.fraud_score * 100).toFixed(0)}%</span>
                          </span>
                          {claim.crowd_validated && (
                            <Badge variant="success" size="sm">
                              Crowd Validated
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-gray-900">
                        {formatCurrency(claim.approved_amount || claim.estimated_loss)}
                      </div>
                      <div className="text-sm text-gray-600 mt-1">
                        Processing: {claim.processing_time_seconds || 0}s
                      </div>
                      <button className="mt-2 flex items-center space-x-1 text-blue-600 hover:text-blue-700">
                        <Eye className="w-4 h-4" />
                        <span className="text-sm">View Details</span>
                      </button>
                    </div>
                  </div>
                </Card>
                </div>
              </motion.div>
            ))
          ) : (
            <Card>
              <div className="text-center py-12">
                <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No claims found</h3>
                <p className="text-gray-600">
                  {filter === 'all' 
                    ? "You haven't filed any claims yet" 
                    : `No ${filter} claims found`}
                </p>
              </div>
            </Card>
          )}
        </div>

        {/* Report Claim Modal */}
        {showReportModal && (
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
            onClick={() => setShowReportModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="bg-white rounded-xl max-w-2xl w-full p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Report a Claim</h2>
                <button 
                  onClick={() => setShowReportModal(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <CloseIcon className="w-6 h-6" />
                </button>
              </div>

              <form onSubmit={handleSubmitClaim} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Disruption Type
                  </label>
                  <select
                    value={formData.trigger_type}
                    onChange={(e) => setFormData({ ...formData, trigger_type: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="weather">Weather Disruption</option>
                    <option value="platform">Platform Outage</option>
                    <option value="accident">Accident</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    rows={4}
                    placeholder="Describe what happened in detail..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Estimated Loss (₹)
                    </label>
                    <input
                      type="number"
                      value={formData.estimated_loss}
                      onChange={(e) => setFormData({ ...formData, estimated_loss: e.target.value })}
                      placeholder="500"
                      min="0"
                      step="0.01"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Incident Date
                    </label>
                    <input
                      type="date"
                      value={formData.incident_date}
                      onChange={(e) => setFormData({ ...formData, incident_date: e.target.value })}
                      max={new Date().toISOString().split('T')[0]}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required
                    />
                  </div>
                </div>

                {/* Evidence Image Upload - Computer Vision */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    📸 Evidence Photo (Optional - AI Analysis)
                  </label>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => e.target.files && handleImageUpload(e.target.files[0])}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                  {imageAnalysis && (
                    <div className={`mt-2 p-3 rounded-lg text-sm ${imageAnalysis.weather_verified ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
                      <p className="font-medium">AI Analysis:</p>
                      <p>Confidence: {(imageAnalysis.confidence * 100).toFixed(0)}%</p>
                      <p>Detected: {imageAnalysis.detected_objects.join(', ')}</p>
                      <p>Authenticity: {(imageAnalysis.authenticity_score * 100).toFixed(0)}%</p>
                    </div>
                  )}
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <AlertTriangle className="w-5 h-5 text-blue-600 mt-0.5" />
                    <div className="text-sm text-blue-800">
                      <p className="font-medium mb-1">AI Fraud Detection Active</p>
                      <p>Your claim will be automatically analyzed for authenticity. Fraudulent claims will be rejected and may affect your trust score.</p>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-3 pt-4">
                  <button
                    type="submit"
                    disabled={submitting}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium disabled:opacity-50 transition-colors"
                  >
                    {submitting ? 'Submitting...' : 'Submit Claim'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowReportModal(false)}
                    className="px-6 py-3 border border-gray-300 rounded-lg font-medium hover:bg-gray-50 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}

        {/* Claim Details Modal */}
        {selectedClaim && (
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedClaim(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Claim Details</h2>
                <button 
                  onClick={() => setSelectedClaim(null)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <XCircle className="w-6 h-6" />
                </button>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-gray-600">Claim ID</div>
                    <div className="font-medium">{selectedClaim.id}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Status</div>
                    <Badge variant={
                      selectedClaim.status === 'approved' ? 'success' :
                      selectedClaim.status === 'rejected' ? 'danger' : 'warning'
                    }>
                      {selectedClaim.status}
                    </Badge>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Trigger Type</div>
                    <div className="font-medium capitalize">{selectedClaim.trigger_type}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Filed Date</div>
                    <div className="font-medium">{formatDate(selectedClaim.created_at)}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Estimated Loss</div>
                    <div className="font-medium">{formatCurrency(selectedClaim.estimated_loss)}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Approved Amount</div>
                    <div className="font-medium">{formatCurrency(selectedClaim.approved_amount)}</div>
                  </div>
                </div>

                {selectedClaim.disruption_data && (
                  <div className="border-t pt-4">
                    <h3 className="font-bold text-gray-900 mb-2">Disruption Data</h3>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      {selectedClaim.disruption_data.rainfall && (
                        <div>
                          <span className="text-gray-600">Rainfall:</span>{' '}
                          <span className="font-medium">{selectedClaim.disruption_data.rainfall} mm</span>
                        </div>
                      )}
                      {selectedClaim.disruption_data.aqi && (
                        <div>
                          <span className="text-gray-600">AQI:</span>{' '}
                          <span className="font-medium">{selectedClaim.disruption_data.aqi}</span>
                        </div>
                      )}
                      {selectedClaim.disruption_data.traffic_congestion && (
                        <div>
                          <span className="text-gray-600">Traffic:</span>{' '}
                          <span className="font-medium">
                            {(selectedClaim.disruption_data.traffic_congestion * 100).toFixed(0)}%
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                <div className="border-t pt-4">
                  <h3 className="font-bold text-gray-900 mb-2">Fraud Analysis</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Fraud Score</span>
                      <span className={`font-medium ${
                        selectedClaim.fraud_score < 0.3 ? 'text-green-600' :
                        selectedClaim.fraud_score < 0.7 ? 'text-yellow-600' : 'text-red-600'
                      }`}>
                        {(selectedClaim.fraud_score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">GPS Fraud Score</span>
                      <span className="font-medium">
                        {(selectedClaim.gps_fraud_score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Crowd Validated</span>
                      <span className="font-medium">
                        {selectedClaim.crowd_validated ? 'Yes' : 'No'}
                      </span>
                    </div>
                  </div>
                </div>

                {selectedClaim.rejection_reason && (
                  <div className="border-t pt-4">
                    <h3 className="font-bold text-gray-900 mb-2">Rejection Reason</h3>
                    <p className="text-gray-700">{selectedClaim.rejection_reason}</p>
                  </div>
                )}
              </div>
            </motion.div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
