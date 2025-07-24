-- AutoServe Database Initialization Script
-- This script sets up the initial database schema and seed data

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS autoserve;
USE autoserve;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Services table for tracking microservices
CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    version VARCHAR(20) NOT NULL,
    status ENUM('running', 'stopped', 'error', 'scaling') DEFAULT 'stopped',
    replicas INT DEFAULT 1,
    cpu_request VARCHAR(20) DEFAULT '100m',
    memory_request VARCHAR(20) DEFAULT '128Mi',
    cpu_limit VARCHAR(20) DEFAULT '500m',
    memory_limit VARCHAR(20) DEFAULT '512Mi',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Metrics table for storing historical metrics
CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,4) NOT NULL,
    labels JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_service_metric (service_name, metric_name),
    INDEX idx_timestamp (timestamp)
);

-- Scaling events table
CREATE TABLE IF NOT EXISTS scaling_events (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    action ENUM('scale_up', 'scale_down', 'no_action') NOT NULL,
    from_replicas INT NOT NULL,
    to_replicas INT NOT NULL,
    reason VARCHAR(255),
    triggered_by ENUM('hpa', 'ml_controller', 'manual') NOT NULL,
    prediction_score DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks table for Celery task tracking
CREATE TABLE IF NOT EXISTS tasks (
    id VARCHAR(36) PRIMARY KEY,
    task_name VARCHAR(255) NOT NULL,
    status ENUM('PENDING', 'STARTED', 'SUCCESS', 'FAILURE', 'RETRY', 'REVOKED') DEFAULT 'PENDING',
    result JSON,
    error_message TEXT,
    worker_name VARCHAR(100),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ML models table
CREATE TABLE IF NOT EXISTS ml_models (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    version VARCHAR(20) NOT NULL,
    model_type ENUM('logistic_regression', 'decision_tree', 'random_forest', 'lstm') NOT NULL,
    accuracy DECIMAL(5,4),
    precision_score DECIMAL(5,4),
    recall_score DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    feature_importance JSON,
    model_path VARCHAR(255),
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_active_model (name, is_active, model_type)
);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    alert_name VARCHAR(100) NOT NULL,
    severity ENUM('info', 'warning', 'critical') NOT NULL,
    service_name VARCHAR(100),
    message TEXT NOT NULL,
    labels JSON,
    status ENUM('firing', 'resolved') DEFAULT 'firing',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    INDEX idx_status (status),
    INDEX idx_severity (severity)
);

-- Insert initial seed data
INSERT INTO users (username, email, password_hash, is_admin) VALUES
('admin', 'admin@autoserve.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8LJqV8J0N2', TRUE),
('demo', 'demo@autoserve.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8LJqV8J0N2', FALSE);

INSERT INTO services (name, version, status, replicas) VALUES
('frontend', 'v1.0.0', 'running', 2),
('backend', 'v1.0.0', 'running', 2),
('worker', 'v1.0.0', 'running', 1),
('ml-controller', 'v1.0.0', 'running', 1);

INSERT INTO ml_models (name, version, model_type, accuracy, is_active) VALUES
('default_scaler', 'v1.0.0', 'random_forest', 0.8500, TRUE),
('backup_scaler', 'v1.0.0', 'logistic_regression', 0.7800, FALSE);

-- Create indexes for better performance
CREATE INDEX idx_metrics_service_time ON metrics(service_name, timestamp);
CREATE INDEX idx_scaling_events_service ON scaling_events(service_name);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_users_email ON users(email);

-- Create views for common queries
CREATE OR REPLACE VIEW service_health AS
SELECT 
    s.name,
    s.status,
    s.replicas,
    COUNT(DISTINCT se.id) as scaling_events_today,
    AVG(CASE WHEN m.metric_name = 'cpu_usage' THEN m.metric_value END) as avg_cpu,
    AVG(CASE WHEN m.metric_name = 'memory_usage' THEN m.metric_value END) as avg_memory
FROM services s
LEFT JOIN scaling_events se ON s.name = se.service_name AND se.created_at >= CURDATE()
LEFT JOIN metrics m ON s.name = m.service_name AND m.timestamp >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
GROUP BY s.id, s.name, s.status, s.replicas;

CREATE OR REPLACE VIEW recent_alerts AS
SELECT 
    alert_name,
    severity,
    service_name,
    message,
    status,
    started_at,
    TIMESTAMPDIFF(MINUTE, started_at, COALESCE(resolved_at, NOW())) as duration_minutes
FROM alerts 
WHERE started_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY started_at DESC;

-- Grant permissions
GRANT ALL PRIVILEGES ON autoserve.* TO 'autoserve_user'@'%';
FLUSH PRIVILEGES;

-- Insert sample metrics data
INSERT INTO metrics (service_name, metric_name, metric_value, timestamp) VALUES
('backend', 'cpu_usage', 45.5, NOW() - INTERVAL 5 MINUTE),
('backend', 'memory_usage', 67.8, NOW() - INTERVAL 5 MINUTE),
('frontend', 'cpu_usage', 23.2, NOW() - INTERVAL 5 MINUTE),
('frontend', 'memory_usage', 34.5, NOW() - INTERVAL 5 MINUTE),
('worker', 'cpu_usage', 12.1, NOW() - INTERVAL 5 MINUTE),
('worker', 'memory_usage', 89.3, NOW() - INTERVAL 5 MINUTE);

COMMIT;
