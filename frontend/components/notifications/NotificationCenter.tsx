'use client';

import { useState, useEffect } from 'react';
import { Bell, X, AlertTriangle, CheckCircle, Info, TrendingUp } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useWebSocket } from '@/lib/websocket';
import { useAuthStore } from '@/lib/store';
import toast from 'react-hot-toast';

interface Notification {
  id: string;
  type: 'notification' | 'risk_update' | 'fraud_alert' | 'claim_update' | 'disruption_alert';
  title: string;
  body?: string;
  data: any;
  timestamp: number;
  read: boolean;
}

export function NotificationCenter() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const { user } = useAuthStore();
  const ws = useWebSocket();

  useEffect(() => {
    if (!user) return;

    const token = localStorage.getItem('access_token');
    if (!token) return;

    // Connect WebSocket
    ws.connect(token);

    // Handle different notification types
    ws.on('notification', (data) => {
      addNotification({
        id: `notif-${Date.now()}`,
        type: 'notification',
        title: data.title,
        body: data.body,
        data: data.data,
        timestamp: data.timestamp,
        read: false,
      });
      toast(data.title, { icon: '🔔' });
    });

    ws.on('risk_update', (data) => {
      addNotification({
        id: `risk-${Date.now()}`,
        type: 'risk_update',
        title: `Risk Level: ${data.risk_level}`,
        body: `Your current risk score is ${(data.risk_score * 100).toFixed(0)}%`,
        data: data,
        timestamp: data.timestamp,
        read: false,
      });
      
      if (data.risk_level === 'HIGH') {
        toast.error(`High Risk Alert! Score: ${(data.risk_score * 100).toFixed(0)}%`);
      }
    });

    ws.on('claim_update', (data) => {
      addNotification({
        id: `claim-${Date.now()}`,
        type: 'claim_update',
        title: `Claim ${data.status.toUpperCase()}`,
        body: data.reason,
        data: data,
        timestamp: data.timestamp,
        read: false,
      });
      
      if (data.status === 'approved') {
        toast.success(`Claim approved! ₹${data.approved_amount}`);
      } else {
        toast.error('Claim rejected');
      }
    });

    ws.on('disruption_alert', (data) => {
      addNotification({
        id: `disruption-${Date.now()}`,
        type: 'disruption_alert',
        title: `${data.trigger_type.toUpperCase()} Alert in ${data.zone}`,
        body: `Severity: ${data.severity}`,
        data: data,
        timestamp: data.timestamp,
        read: false,
      });
      toast(`⚠️ Disruption Alert: ${data.trigger_type}`, { icon: '⚠️' });
    });

    // Cleanup
    return () => {
      ws.disconnect();
    };
  }, [user]);

  useEffect(() => {
    const count = notifications.filter(n => !n.read).length;
    setUnreadCount(count);
  }, [notifications]);

  const addNotification = (notification: Notification) => {
    setNotifications(prev => [notification, ...prev].slice(0, 50)); // Keep last 50
  };

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
      case 'risk_update':
        return <TrendingUp className="w-5 h-5 text-orange-500" />;
      case 'claim_update':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'disruption_alert':
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      default:
        return <Info className="w-5 h-5 text-blue-500" />;
    }
  };

  return (
    <>
      {/* Bell Icon */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-lg hover:bg-gray-100 transition-colors"
      >
        <Bell className="w-6 h-6 text-gray-700" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Notification Panel */}
      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black bg-opacity-25 z-40"
              onClick={() => setIsOpen(false)}
            />
            <motion.div
              initial={{ opacity: 0, x: 300 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 300 }}
              className="fixed right-0 top-0 h-full w-96 bg-white shadow-2xl z-50 flex flex-col"
            >
              {/* Header */}
              <div className="p-4 border-b flex items-center justify-between">
                <h2 className="text-lg font-bold">Notifications</h2>
                <div className="flex items-center space-x-2">
                  {unreadCount > 0 && (
                    <button
                      onClick={markAllAsRead}
                      className="text-sm text-blue-600 hover:text-blue-700"
                    >
                      Mark all read
                    </button>
                  )}
                  <button onClick={() => setIsOpen(false)}>
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Notifications List */}
              <div className="flex-1 overflow-y-auto">
                {notifications.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-gray-500">
                    <Bell className="w-12 h-12 mb-2 opacity-50" />
                    <p>No notifications</p>
                  </div>
                ) : (
                  <div className="divide-y">
                    {notifications.map((notification) => (
                      <div
                        key={notification.id}
                        className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
                          !notification.read ? 'bg-blue-50' : ''
                        }`}
                        onClick={() => markAsRead(notification.id)}
                      >
                        <div className="flex items-start space-x-3">
                          <div className="flex-shrink-0 mt-1">
                            {getIcon(notification.type)}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className={`text-sm font-medium ${!notification.read ? 'text-gray-900' : 'text-gray-700'}`}>
                              {notification.title}
                            </p>
                            {notification.body && (
                              <p className="text-sm text-gray-600 mt-1">
                                {notification.body}
                              </p>
                            )}
                            <p className="text-xs text-gray-400 mt-1">
                              {new Date(notification.timestamp * 1000).toLocaleString()}
                            </p>
                          </div>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteNotification(notification.id);
                            }}
                            className="flex-shrink-0 text-gray-400 hover:text-gray-600"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
