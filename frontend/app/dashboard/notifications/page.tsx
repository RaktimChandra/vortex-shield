'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Bell, CheckCircle, AlertTriangle, TrendingUp, X, Clock } from 'lucide-react';

interface Notification {
  id: string;
  type: 'claim_update' | 'risk_alert' | 'trigger_alert' | 'system';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  priority: 'high' | 'medium' | 'low';
}

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([
    {
      id: '1',
      type: 'claim_update',
      title: 'Claim Approved',
      message: 'Your weather disruption claim of ₹500 has been approved and will be processed within 24 hours.',
      timestamp: '2 hours ago',
      read: false,
      priority: 'high'
    },
    {
      id: '2',
      type: 'trigger_alert',
      title: 'Heavy Rainfall Alert',
      message: 'Heavy rainfall detected in Andheri West. Auto-claim eligible if disruptions occur.',
      timestamp: '5 hours ago',
      read: false,
      priority: 'high'
    },
    {
      id: '3',
      type: 'risk_alert',
      title: 'High Risk Zone Detected',
      message: 'Your current zone (Andheri West) has elevated risk levels. Consider postponing deliveries.',
      timestamp: '1 day ago',
      read: true,
      priority: 'medium'
    },
    {
      id: '4',
      type: 'system',
      title: 'Trust Score Increased',
      message: 'Your trust score has improved to 1.00 after recent approved claims.',
      timestamp: '2 days ago',
      read: true,
      priority: 'low'
    },
    {
      id: '5',
      type: 'trigger_alert',
      title: 'Platform Outage Detected',
      message: 'Swiggy platform experiencing downtime. Claims for this period are auto-eligible.',
      timestamp: '3 days ago',
      read: true,
      priority: 'high'
    }
  ]);

  const [filter, setFilter] = useState<'all' | 'unread'>('all');

  const markAsRead = (id: string) => {
    setNotifications(prev =>
      prev.map(n => (n.id === id ? { ...n, read: true } : n))
    );
  };

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  };

  const deleteNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const getIcon = (type: string) => {
    switch (type) {
      case 'claim_update':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'trigger_alert':
        return <AlertTriangle className="w-6 h-6 text-orange-500" />;
      case 'risk_alert':
        return <TrendingUp className="w-6 h-6 text-red-500" />;
      default:
        return <Bell className="w-6 h-6 text-blue-500" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'border-l-red-500 bg-red-50';
      case 'medium':
        return 'border-l-orange-500 bg-orange-50';
      default:
        return 'border-l-blue-500 bg-blue-50';
    }
  };

  const filteredNotifications = filter === 'unread'
    ? notifications.filter(n => !n.read)
    : notifications;

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header with Gradient */}
        <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-2xl p-8 text-white shadow-xl">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">Notifications</h1>
              <p className="text-blue-100">Stay updated with real-time alerts and updates</p>
            </div>
            <div className="bg-white/20 backdrop-blur-lg rounded-2xl p-4">
              <Bell className="w-12 h-12" />
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm">Total Notifications</p>
                <p className="text-3xl font-bold mt-1">{notifications.length}</p>
              </div>
              <Bell className="w-10 h-10 opacity-50" />
            </div>
          </div>

          <div className="bg-gradient-to-br from-orange-500 to-red-500 rounded-xl p-6 text-white shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-100 text-sm">Unread</p>
                <p className="text-3xl font-bold mt-1">{unreadCount}</p>
              </div>
              <AlertTriangle className="w-10 h-10 opacity-50" />
            </div>
          </div>

          <div className="bg-gradient-to-br from-green-500 to-teal-500 rounded-xl p-6 text-white shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100 text-sm">High Priority</p>
                <p className="text-3xl font-bold mt-1">
                  {notifications.filter(n => n.priority === 'high').length}
                </p>
              </div>
              <TrendingUp className="w-10 h-10 opacity-50" />
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl p-4 shadow-sm flex items-center justify-between">
          <div className="flex space-x-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                filter === 'all'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              All ({notifications.length})
            </button>
            <button
              onClick={() => setFilter('unread')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                filter === 'unread'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Unread ({unreadCount})
            </button>
          </div>

          {unreadCount > 0 && (
            <button
              onClick={markAllAsRead}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-all font-medium shadow-md"
            >
              Mark All as Read
            </button>
          )}
        </div>

        {/* Notifications List */}
        <div className="space-y-3">
          {filteredNotifications.length === 0 ? (
            <div className="bg-white rounded-xl p-12 text-center shadow-sm">
              <Bell className="w-16 h-16 mx-auto text-gray-300 mb-4" />
              <p className="text-gray-500 text-lg">No notifications to display</p>
            </div>
          ) : (
            filteredNotifications.map((notification) => (
              <div
                key={notification.id}
                className={`bg-white rounded-xl shadow-sm hover:shadow-lg transition-all border-l-4 ${getPriorityColor(
                  notification.priority
                )} ${!notification.read ? 'ring-2 ring-blue-200' : ''}`}
              >
                <div className="p-6">
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0 mt-1">
                      {getIcon(notification.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className={`text-lg font-bold ${!notification.read ? 'text-gray-900' : 'text-gray-700'}`}>
                            {notification.title}
                          </h3>
                          <p className="text-gray-600 mt-1">{notification.message}</p>
                          <div className="flex items-center space-x-4 mt-3">
                            <div className="flex items-center text-sm text-gray-500">
                              <Clock className="w-4 h-4 mr-1" />
                              {notification.timestamp}
                            </div>
                            <span className={`text-xs px-3 py-1 rounded-full font-medium ${
                              notification.priority === 'high'
                                ? 'bg-red-100 text-red-700'
                                : notification.priority === 'medium'
                                ? 'bg-orange-100 text-orange-700'
                                : 'bg-blue-100 text-blue-700'
                            }`}>
                              {notification.priority.toUpperCase()}
                            </span>
                            {!notification.read && (
                              <span className="text-xs px-3 py-1 bg-blue-100 text-blue-700 rounded-full font-medium">
                                NEW
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center space-x-2 ml-4">
                          {!notification.read && (
                            <button
                              onClick={() => markAsRead(notification.id)}
                              className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-all"
                              title="Mark as read"
                            >
                              <CheckCircle className="w-5 h-5" />
                            </button>
                          )}
                          <button
                            onClick={() => deleteNotification(notification.id)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-all"
                            title="Delete"
                          >
                            <X className="w-5 h-5" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
