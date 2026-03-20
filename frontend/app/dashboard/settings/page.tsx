'use client';

import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { useAuthStore } from '@/lib/store';
import { userApi } from '@/lib/api';
import { User, Bell, Lock, Palette, Shield } from 'lucide-react';
import toast from 'react-hot-toast';

export default function SettingsPage() {
  const { user, setUser } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('profile');
  const [theme, setTheme] = useState('light');
  
  const [formData, setFormData] = useState({
    full_name: user?.full_name || '',
    phone: user?.phone || '',
    city: user?.city || '',
    zone: user?.zone || '',
    work_hours_per_day: user?.work_hours_per_day || 8,
    avg_daily_earnings: user?.avg_daily_earnings || 0,
    delivery_platform: user?.delivery_platform || '',
  });

  const handleUpdateProfile = async () => {
    try {
      setLoading(true);
      const response = await userApi.updateMe(formData);
      setUser(response.data);
      toast.success('Profile updated successfully!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Lock },
    { id: 'appearance', label: 'Appearance', icon: Palette },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header with Gradient */}
        <div className="bg-gradient-to-r from-violet-600 via-purple-600 to-fuchsia-600 rounded-2xl p-8 text-white shadow-2xl">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">⚙️ Settings</h1>
              <p className="text-violet-100 text-lg">Manage your account and preferences</p>
            </div>
            <div className="bg-white/20 backdrop-blur-lg rounded-2xl p-4">
              <Shield className="w-16 h-16" />
            </div>
          </div>
        </div>

        <div className="flex gap-6">
          {/* Sidebar - Gradient Tabs */}
          <div className="w-64 bg-white rounded-2xl shadow-xl p-4">
            <nav className="space-y-2">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all transform ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-purple-500 to-pink-600 text-white shadow-lg scale-105'
                      : 'text-gray-700 hover:bg-gray-50 hover:scale-102'
                  }`}
                >
                  <tab.icon className="w-5 h-5" />
                  <span className="font-bold">{tab.label}</span>
                </button>
              ))}
            </nav>
          </div>

          {/* Content */}
          <div className="flex-1 bg-white rounded-2xl shadow-xl p-8">
            {activeTab === 'profile' && (
              <div>
                <h2 className="text-xl font-bold mb-6">Profile Information</h2>
                
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Full Name
                      </label>
                      <input
                        type="text"
                        value={formData.full_name}
                        onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Phone
                      </label>
                      <input
                        type="tel"
                        value={formData.phone}
                        onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        City
                      </label>
                      <input
                        type="text"
                        value={formData.city}
                        onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Zone
                      </label>
                      <input
                        type="text"
                        value={formData.zone}
                        onChange={(e) => setFormData({ ...formData, zone: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Work Hours Per Day
                      </label>
                      <input
                        type="number"
                        value={formData.work_hours_per_day}
                        onChange={(e) => setFormData({ ...formData, work_hours_per_day: parseFloat(e.target.value) })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Average Daily Earnings (₹)
                      </label>
                      <input
                        type="number"
                        value={formData.avg_daily_earnings}
                        onChange={(e) => setFormData({ ...formData, avg_daily_earnings: parseFloat(e.target.value) })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Delivery Platform
                    </label>
                    <select
                      value={formData.delivery_platform}
                      onChange={(e) => setFormData({ ...formData, delivery_platform: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="Swiggy">Swiggy</option>
                      <option value="Zomato">Zomato</option>
                      <option value="Uber Eats">Uber Eats</option>
                      <option value="Dunzo">Dunzo</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>

                  <div className="pt-4">
                    <button
                      onClick={handleUpdateProfile}
                      disabled={loading}
                      className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                    >
                      {loading ? 'Saving...' : 'Save Changes'}
                    </button>
                  </div>
                </div>

                <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-start space-x-3">
                    <Shield className="w-5 h-5 text-blue-600 mt-0.5" />
                    <div>
                      <h3 className="font-medium text-blue-900">Account Information</h3>
                      <p className="text-sm text-blue-700 mt-1">
                        Email: {user?.email}<br />
                        Role: {user?.role}<br />
                        Trust Score: {user?.trust_score?.toFixed(2)}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'notifications' && (
              <div>
                <h2 className="text-xl font-bold mb-6">Notification Preferences</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h3 className="font-medium">Claim Updates</h3>
                      <p className="text-sm text-gray-600">Get notified about claim status changes</p>
                    </div>
                    <input type="checkbox" defaultChecked className="w-5 h-5" />
                  </div>
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h3 className="font-medium">Subscription Reminders</h3>
                      <p className="text-sm text-gray-600">Reminders for subscription renewals</p>
                    </div>
                    <input type="checkbox" defaultChecked className="w-5 h-5" />
                  </div>
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h3 className="font-medium">System Alerts</h3>
                      <p className="text-sm text-gray-600">Important system notifications</p>
                    </div>
                    <input type="checkbox" defaultChecked className="w-5 h-5" />
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div>
                <h2 className="text-xl font-bold mb-6">Security Settings</h2>
                <div className="space-y-6">
                  <div>
                    <h3 className="font-medium mb-3">Change Password</h3>
                    <div className="space-y-3">
                      <input
                        type="password"
                        placeholder="Current Password"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                      />
                      <input
                        type="password"
                        placeholder="New Password"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                      />
                      <input
                        type="password"
                        placeholder="Confirm New Password"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                      />
                      <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                        Update Password
                      </button>
                    </div>
                  </div>

                  <div className="pt-6 border-t">
                    <h3 className="font-medium mb-3">Two-Factor Authentication</h3>
                    <p className="text-sm text-gray-600 mb-3">
                      Add an extra layer of security to your account
                    </p>
                    <button className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                      Enable 2FA
                    </button>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'appearance' && (
              <div>
                <h2 className="text-xl font-bold mb-6">Appearance</h2>
                <div className="space-y-4">
                  <div>
                    <h3 className="font-medium mb-3">Theme</h3>
                    <div className="grid grid-cols-3 gap-4">
                      <div 
                        onClick={() => {
                          setTheme('light');
                          document.documentElement.classList.remove('dark');
                          localStorage.setItem('theme', 'light');
                          toast.success('Light theme activated');
                        }}
                        className={`border-2 ${theme === 'light' ? 'border-blue-600' : 'border-gray-300'} rounded-lg p-4 cursor-pointer hover:border-blue-400 transition-all`}
                      >
                        <div className="w-full h-24 bg-white rounded mb-2 border"></div>
                        <p className="text-center font-medium">Light</p>
                      </div>
                      <div 
                        onClick={() => {
                          setTheme('dark');
                          document.documentElement.classList.add('dark');
                          localStorage.setItem('theme', 'dark');
                          toast.success('Dark theme activated');
                        }}
                        className={`border-2 ${theme === 'dark' ? 'border-blue-600' : 'border-gray-300'} rounded-lg p-4 cursor-pointer hover:border-blue-400 transition-all`}
                      >
                        <div className="w-full h-24 bg-gray-900 rounded mb-2"></div>
                        <p className="text-center">Dark</p>
                      </div>
                      <div 
                        onClick={() => {
                          setTheme('auto');
                          const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                          if (prefersDark) {
                            document.documentElement.classList.add('dark');
                          } else {
                            document.documentElement.classList.remove('dark');
                          }
                          localStorage.setItem('theme', 'auto');
                          toast.success('Auto theme activated');
                        }}
                        className={`border-2 ${theme === 'auto' ? 'border-blue-600' : 'border-gray-300'} rounded-lg p-4 cursor-pointer hover:border-blue-400 transition-all`}
                      >
                        <div className="w-full h-24 bg-gradient-to-br from-white to-gray-900 rounded mb-2"></div>
                        <p className="text-center">Auto</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
