-- BigQuery schema for Health Insight Ventures platform

-- Create dataset
CREATE SCHEMA IF NOT EXISTS `health_insight_platform`
OPTIONS(
  description="Health Insight Ventures platform data",
  location="US"
);

-- Users table
CREATE OR REPLACE TABLE `health_insight_platform.users` (
  id STRING NOT NULL,
  first_name STRING,
  last_name STRING,
  email STRING NOT NULL,
  password_hash STRING,
  phone STRING,
  date_of_birth DATE,
  gender STRING,
  role STRING DEFAULT 'patient',
  profile_picture STRING,
  emergency_contact_name STRING,
  emergency_contact_phone STRING,
  preferred_language STRING DEFAULT 'en',
  timezone STRING DEFAULT 'America/New_York',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
CLUSTER BY role, email;

-- Resources table
CREATE OR REPLACE TABLE `health_insight_platform.resources` (
  id STRING NOT NULL,
  title STRING NOT NULL,
  description STRING,
  category STRING,
  website STRING,
  phone STRING,
  email STRING,
  address STRING,
  city STRING,
  state STRING,
  zip_code STRING,
  latitude FLOAT64,
  longitude FLOAT64,
  hours_of_operation JSON,
  services_offered ARRAY<STRING>,
  languages_supported ARRAY<STRING>,
  insurance_accepted ARRAY<STRING>,
  accessibility_features ARRAY<STRING>,
  rating FLOAT64,
  review_count INT64,
  verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
CLUSTER BY category, state;

-- Appointments table
CREATE OR REPLACE TABLE `health_insight_platform.appointments` (
  id STRING NOT NULL,
  patient_id STRING NOT NULL,
  provider_id STRING,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP NOT NULL,
  type STRING,
  status STRING DEFAULT 'pending',
  notes STRING,
  location STRING,
  is_virtual BOOLEAN DEFAULT FALSE,
  reminder_sent BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(start_time)
CLUSTER BY patient_id, status;

-- Medications table
CREATE OR REPLACE TABLE `health_insight_platform.medications` (
  id STRING NOT NULL,
  user_id STRING NOT NULL,
  name STRING NOT NULL,
  dosage STRING,
  frequency STRING,
  time_of_day ARRAY<STRING>,
  instructions STRING,
  prescribing_doctor STRING,
  pharmacy STRING,
  refill_date DATE,
  refills_remaining INT64,
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
CLUSTER BY user_id, active;

-- Medication logs table
CREATE OR REPLACE TABLE `health_insight_platform.medication_logs` (
  id STRING NOT NULL,
  user_id STRING NOT NULL,
  medication_id STRING NOT NULL,
  taken_at TIMESTAMP NOT NULL,
  status STRING NOT NULL,
  notes STRING,
  points_earned INT64,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(taken_at)
CLUSTER BY user_id, medication_id;

-- User points table
CREATE OR REPLACE TABLE `health_insight_platform.user_points` (
  id STRING NOT NULL,
  user_id STRING NOT NULL,
  total_points INT64 DEFAULT 0,
  level INT64 DEFAULT 1,
  current_streak INT64 DEFAULT 0,
  longest_streak INT64 DEFAULT 0,
  last_activity_date DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY user_id;

-- Points transactions table
CREATE OR REPLACE TABLE `health_insight_platform.points_transactions` (
  id STRING NOT NULL,
  user_id STRING NOT NULL,
  points INT64 NOT NULL,
  transaction_type STRING NOT NULL,
  source_type STRING NOT NULL,
  source_id STRING,
  description STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
CLUSTER BY user_id, transaction_type;

-- Events table
CREATE OR REPLACE TABLE `health_insight_platform.events` (
  id STRING NOT NULL,
  title STRING NOT NULL,
  description STRING,
  organizer_id STRING NOT NULL,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP NOT NULL,
  location STRING,
  category STRING,
  max_participants INT64,
  is_virtual BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(start_time)
CLUSTER BY category, organizer_id;

-- Forum posts table
CREATE OR REPLACE TABLE `health_insight_platform.forum_posts` (
  id STRING NOT NULL,
  title STRING NOT NULL,
  content STRING NOT NULL,
  author_id STRING NOT NULL,
  category STRING,
  tags ARRAY<STRING>,
  upvotes INT64 DEFAULT 0,
  downvotes INT64 DEFAULT 0,
  view_count INT64 DEFAULT 0,
  is_pinned BOOLEAN DEFAULT FALSE,
  is_locked BOOLEAN DEFAULT FALSE,
  moderation_status STRING DEFAULT 'approved',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
CLUSTER BY category, author_id;

-- Forum comments table
CREATE OR REPLACE TABLE `health_insight_platform.forum_comments` (
  id STRING NOT NULL,
  post_id STRING NOT NULL,
  author_id STRING NOT NULL,
  content STRING NOT NULL,
  parent_comment_id STRING,
  upvotes INT64 DEFAULT 0,
  downvotes INT64 DEFAULT 0,
  moderation_status STRING DEFAULT 'approved',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
CLUSTER BY post_id, author_id;

-- Audit logs table for HIPAA compliance
CREATE OR REPLACE TABLE `health_insight_platform.audit_logs` (
  id STRING NOT NULL,
  user_id INT64,
  event_type STRING NOT NULL,
  resource_type STRING,
  resource_id STRING,
  action STRING NOT NULL,
  description STRING,
  ip_address STRING,
  user_agent STRING,
  success BOOLEAN NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  additional_info JSON
)
PARTITION BY DATE(timestamp)
CLUSTER BY event_type, user_id;

-- Wellness tips table
CREATE OR REPLACE TABLE `health_insight_platform.wellness_tips` (
  id STRING NOT NULL,
  user_id STRING NOT NULL,
  category STRING NOT NULL,
  tip_content STRING NOT NULL,
  motivational_quote STRING,
  actionable_steps ARRAY<STRING>,
  ai_generated BOOLEAN DEFAULT TRUE,
  user_feedback STRING,
  is_saved BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
CLUSTER BY user_id, category;