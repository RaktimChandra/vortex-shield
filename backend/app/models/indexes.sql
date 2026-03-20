-- Database Indexes for Performance Optimization
-- VORTEX Shield 2.0

-- Users Table Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_city_zone ON users(city, zone);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_trust_score ON users(trust_score);

-- Subscriptions Table Indexes
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_end_date ON subscriptions(end_date);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_status ON subscriptions(user_id, status);

-- Claims Table Indexes
CREATE INDEX IF NOT EXISTS idx_claims_user_id ON claims(user_id);
CREATE INDEX IF NOT EXISTS idx_claims_status ON claims(status);
CREATE INDEX IF NOT EXISTS idx_claims_trigger_type ON claims(trigger_type);
CREATE INDEX IF NOT EXISTS idx_claims_created_at ON claims(created_at);
CREATE INDEX IF NOT EXISTS idx_claims_fraud_score ON claims(fraud_score);
CREATE INDEX IF NOT EXISTS idx_claims_auto_approved ON claims(auto_approved);
CREATE INDEX IF NOT EXISTS idx_claims_user_status ON claims(user_id, status);
CREATE INDEX IF NOT EXISTS idx_claims_payout_status ON claims(payout_status);

-- Activity Logs Table Indexes
CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_timestamp ON activity_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_activity_logs_user_timestamp ON activity_logs(user_id, timestamp);

-- Disruption Events Table Indexes
CREATE INDEX IF NOT EXISTS idx_disruption_events_city_zone ON disruption_events(city, zone);
CREATE INDEX IF NOT EXISTS idx_disruption_events_trigger_type ON disruption_events(trigger_type);
CREATE INDEX IF NOT EXISTS idx_disruption_events_detected_at ON disruption_events(detected_at);
CREATE INDEX IF NOT EXISTS idx_disruption_events_severity ON disruption_events(severity);

-- Fraud Logs Table Indexes
CREATE INDEX IF NOT EXISTS idx_fraud_logs_user_id ON fraud_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_fraud_logs_claim_id ON fraud_logs(claim_id);
CREATE INDEX IF NOT EXISTS idx_fraud_logs_flagged ON fraud_logs(flagged);
CREATE INDEX IF NOT EXISTS idx_fraud_logs_risk_level ON fraud_logs(risk_level);
CREATE INDEX IF NOT EXISTS idx_fraud_logs_detected_at ON fraud_logs(detected_at);

-- Composite Indexes for Common Queries
CREATE INDEX IF NOT EXISTS idx_claims_composite ON claims(user_id, status, created_at);
CREATE INDEX IF NOT EXISTS idx_users_location ON users(city, zone, is_active);
CREATE INDEX IF NOT EXISTS idx_subscriptions_active ON subscriptions(user_id, status, end_date);
