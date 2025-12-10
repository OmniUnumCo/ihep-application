import { pgTable, text, serial, integer, boolean, timestamp, jsonb, pgEnum } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// Enum for audit event types
export const auditEventTypeEnum = pgEnum('audit_event_type', [
  'PHI_ACCESS',
  'PHI_MODIFICATION',
  'PHI_DELETION',
  'AUTHENTICATION',
  'AUTHORIZATION',
  'SYSTEM_EVENT'
]);

// User model
export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
  email: text("email").notNull().unique(), // Add unique constraint to email
  firstName: text("first_name").notNull(),
  lastName: text("last_name").notNull(),
  role: text("role").notNull().default("patient"),
  profilePicture: text("profile_picture"),
  phone: text("phone"),
  preferredContactMethod: text("preferred_contact_method").default("email"),
  createdAt: timestamp("created_at").defaultNow(),
});

// Resource model
export const resources = pgTable("resources", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  description: text("description").notNull(),
  category: text("category").notNull(),
  contactInfo: text("contact_info").notNull(),
  address: text("address"),
  city: text("city"),
  state: text("state"),
  zipCode: text("zip_code"),
  phone: text("phone"),
  email: text("email"),
  website: text("website"),
  isVirtual: boolean("is_virtual").default(false),
  takingNewPatients: boolean("taking_new_patients").default(true),
  availableToday: boolean("available_today").default(false),
  imageUrl: text("image_url"),
  rating: integer("rating"),
  reviewCount: integer("review_count").default(0),
});

// Event model
export const events = pgTable("events", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  description: text("description").notNull(),
  startTime: timestamp("start_time").notNull(),
  endTime: timestamp("end_time").notNull(),
  location: text("location"),
  isVirtual: boolean("is_virtual").default(false),
  category: text("category"),
  tags: text("tags").array(),
  hostId: integer("host_id").references(() => users.id),
  capacity: integer("capacity"),
  registeredUsers: integer("registered_users").array(),
});

// Community group model
export const communityGroups = pgTable("community_groups", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  description: text("description").notNull(),
  memberCount: integer("member_count").default(0),
  createdAt: timestamp("created_at").defaultNow(),
  lastActive: timestamp("last_active").defaultNow(),
  isPublic: boolean("is_public").default(true),
  groupImage: text("group_image"),
  members: integer("members").array(),
});

// Discussion model
export const discussions = pgTable("discussions", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  content: text("content").notNull(),
  authorId: integer("author_id").references(() => users.id),
  groupId: integer("group_id").references(() => communityGroups.id),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
  replyCount: integer("reply_count").default(0),
  likes: integer("likes").default(0),
});

// Message model
export const messages = pgTable("messages", {
  id: serial("id").primaryKey(),
  senderId: integer("sender_id").references(() => users.id),
  recipientId: integer("recipient_id").references(() => users.id),
  subject: text("subject").notNull(),
  content: text("content").notNull(),
  isRead: boolean("is_read").default(false),
  createdAt: timestamp("created_at").defaultNow(),
});

// Notification model
export const notifications = pgTable("notifications", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").references(() => users.id),
  title: text("title").notNull(),
  message: text("message").notNull(),
  type: text("type").notNull(),
  isRead: boolean("is_read").default(false),
  createdAt: timestamp("created_at").defaultNow(),
  relatedId: integer("related_id"),
  relatedType: text("related_type"),
});

// Educational content model
export const educationalContent = pgTable("educational_content", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  content: text("content").notNull(),
  category: text("category").notNull(),
  tags: text("tags").array(),
  authorId: integer("author_id").references(() => users.id),
  publishedDate: timestamp("published_date").defaultNow(),
  lastUpdated: timestamp("last_updated").defaultNow(),
  mediaUrls: text("media_urls").array(),
  featured: boolean("featured").default(false),
});

// Appointment model
export const appointments = pgTable("appointments", {
  id: serial("id").primaryKey(),
  patientId: integer("patient_id").references(() => users.id),
  providerId: integer("provider_id").references(() => users.id),
  startTime: timestamp("start_time").notNull(),
  endTime: timestamp("end_time").notNull(),
  type: text("type").notNull(),
  notes: text("notes"),
  status: text("status").notNull().default("scheduled"),
  location: text("location"),
  isVirtual: boolean("is_virtual").default(false),
  reminderSent: boolean("reminder_sent").default(false),
});

// Forum categories model
export const forumCategories = pgTable("forum_categories", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  description: text("description").notNull(),
  slug: text("slug").notNull().unique(),
  icon: text("icon"),
  color: text("color"),
  postCount: integer("post_count").default(0),
  isActive: boolean("is_active").default(true),
  displayOrder: integer("display_order").default(0),
  createdAt: timestamp("created_at").defaultNow(),
});

// Forum posts model
export const forumPosts = pgTable("forum_posts", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  content: text("content").notNull(),
  authorId: integer("author_id").references(() => users.id),
  categoryId: integer("category_id").references(() => forumCategories.id),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
  commentCount: integer("comment_count").default(0),
  viewCount: integer("view_count").default(0),
  likes: integer("likes").default(0),
  isPinned: boolean("is_pinned").default(false),
  isFeatured: boolean("is_featured").default(false),
  isModerated: boolean("is_moderated").default(false),
  moderationStatus: text("moderation_status").default("pending"),
  moderationNotes: text("moderation_notes"),
  tags: text("tags").array(),
});

// Forum comments model
export const forumComments = pgTable("forum_comments", {
  id: serial("id").primaryKey(),
  content: text("content").notNull(),
  authorId: integer("author_id").references(() => users.id),
  postId: integer("post_id").references(() => forumPosts.id),
  parentCommentId: integer("parent_comment_id"),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
  likes: integer("likes").default(0),
  isModerated: boolean("is_moderated").default(false),
  moderationStatus: text("moderation_status").default("pending"),
  moderationNotes: text("moderation_notes"),
  isArchived: boolean("is_archived").default(false),
  archivedDate: timestamp("archived_date"),
  medicalRelevance: integer("medical_relevance").default(0), // 0-10 scale
  aiModerationNotes: text("ai_moderation_notes"),
});

// Schemas for insertion
export const insertUserSchema = createInsertSchema(users).omit({ id: true, createdAt: true });
export const insertResourceSchema = createInsertSchema(resources).omit({ id: true });
export const insertEventSchema = createInsertSchema(events).omit({ id: true });
export const insertCommunityGroupSchema = createInsertSchema(communityGroups).omit({ id: true, createdAt: true, lastActive: true, memberCount: true });
export const insertDiscussionSchema = createInsertSchema(discussions).omit({ id: true, createdAt: true, updatedAt: true, replyCount: true, likes: true });
export const insertMessageSchema = createInsertSchema(messages).omit({ id: true, createdAt: true, isRead: true });
export const insertNotificationSchema = createInsertSchema(notifications).omit({ id: true, createdAt: true, isRead: true });
export const insertEducationalContentSchema = createInsertSchema(educationalContent).omit({ id: true, publishedDate: true, lastUpdated: true });
export const insertAppointmentSchema = createInsertSchema(appointments).omit({ id: true, reminderSent: true });

// Forum insert schemas
export const insertForumCategorySchema = createInsertSchema(forumCategories).omit({ id: true, createdAt: true, postCount: true });
export const insertForumPostSchema = createInsertSchema(forumPosts).omit({ 
  id: true, 
  createdAt: true, 
  updatedAt: true, 
  commentCount: true, 
  viewCount: true, 
  likes: true, 
  isModerated: true,
  moderationStatus: true,
  moderationNotes: true
});
export const insertForumCommentSchema = createInsertSchema(forumComments).omit({ 
  id: true, 
  createdAt: true, 
  updatedAt: true, 
  likes: true,
  isModerated: true,
  moderationStatus: true,
  moderationNotes: true,
  isArchived: true,
  archivedDate: true,
  medicalRelevance: true,
  aiModerationNotes: true
});

// Types for CRUD operations
export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;

export type InsertResource = z.infer<typeof insertResourceSchema>;
export type Resource = typeof resources.$inferSelect;

export type InsertEvent = z.infer<typeof insertEventSchema>;
export type Event = typeof events.$inferSelect;

export type InsertCommunityGroup = z.infer<typeof insertCommunityGroupSchema>;
export type CommunityGroup = typeof communityGroups.$inferSelect;

export type InsertDiscussion = z.infer<typeof insertDiscussionSchema>;
export type Discussion = typeof discussions.$inferSelect;

export type InsertMessage = z.infer<typeof insertMessageSchema>;
export type Message = typeof messages.$inferSelect;

export type InsertNotification = z.infer<typeof insertNotificationSchema>;
export type Notification = typeof notifications.$inferSelect;

export type InsertEducationalContent = z.infer<typeof insertEducationalContentSchema>;
export type EducationalContent = typeof educationalContent.$inferSelect;

export type InsertAppointment = z.infer<typeof insertAppointmentSchema>;
export type Appointment = typeof appointments.$inferSelect;

// Forum types for CRUD operations
export type InsertForumCategory = z.infer<typeof insertForumCategorySchema>;
export type ForumCategory = typeof forumCategories.$inferSelect;

export type InsertForumPost = z.infer<typeof insertForumPostSchema>;
export type ForumPost = typeof forumPosts.$inferSelect;

export type InsertForumComment = z.infer<typeof insertForumCommentSchema>;
export type ForumComment = typeof forumComments.$inferSelect;

// Gamification system tables

export const healthActivities = pgTable("health_activities", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  description: text("description").notNull(),
  category: text("category").notNull(), // 'physical', 'mental', 'medication', 'appointment', 'education'
  pointsValue: integer("points_value").notNull().default(10),
  frequency: text("frequency").notNull(), // 'daily', 'weekly', 'monthly', 'once'
  isActive: boolean("is_active").notNull().default(true),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const userAchievements = pgTable("user_achievements", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").notNull().references(() => users.id),
  achievementId: integer("achievement_id").notNull().references(() => achievements.id),
  unlockedAt: timestamp("unlocked_at").notNull().defaultNow(),
});

export const achievements = pgTable("achievements", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  description: text("description").notNull(),
  icon: text("icon").notNull().default('award'),
  level: integer("level").notNull().default(1), // 1 = easy, 2 = medium, 3 = hard
  pointsRequired: integer("points_required").notNull(),
  category: text("category").notNull(), // 'physical', 'mental', 'medication', 'appointment', 'education', 'streak'
  createdAt: timestamp("created_at").notNull().defaultNow(),
  isActive: boolean("is_active").notNull().default(true),
});

export const userActivities = pgTable("user_activities", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").notNull().references(() => users.id),
  activityId: integer("activity_id").notNull().references(() => healthActivities.id),
  completedAt: timestamp("completed_at").notNull().defaultNow(),
  pointsEarned: integer("points_earned").notNull(),
  notes: text("notes"),
  proofImageUrl: text("proof_image_url"),
  verificationStatus: text("verification_status").notNull().default('verified'), // 'pending', 'verified', 'rejected'
});

export const userRewards = pgTable("user_rewards", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").notNull().references(() => users.id),
  rewardId: integer("reward_id").notNull().references(() => rewards.id),
  earnedAt: timestamp("earned_at").notNull().defaultNow(),
  redeemedAt: timestamp("redeemed_at"),
  code: text("code"),
  status: text("status").notNull().default('active'), // 'active', 'redeemed', 'expired'
  expiresAt: timestamp("expires_at"),
});

export const rewards = pgTable("rewards", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  description: text("description").notNull(),
  category: text("category").notNull(), // 'discount', 'gift_card', 'merchandise', 'badge', 'feature_unlock'
  pointsCost: integer("points_cost").notNull(),
  inventory: integer("inventory"),
  isActive: boolean("is_active").notNull().default(true),
  imageUrl: text("image_url"),
  termsAndConditions: text("terms_and_conditions"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const userPoints = pgTable("user_points", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").notNull().references(() => users.id),
  totalPoints: integer("total_points").notNull().default(0),
  availablePoints: integer("available_points").notNull().default(0),
  lifetimePoints: integer("lifetime_points").notNull().default(0),
  lastActivity: timestamp("last_activity").notNull().defaultNow(),
  currentStreak: integer("current_streak").notNull().default(0),
  longestStreak: integer("longest_streak").notNull().default(0),
  lastStreakUpdate: timestamp("last_streak_update").notNull().defaultNow(),
});

export const pointsTransactions = pgTable("points_transactions", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").notNull().references(() => users.id),
  amount: integer("amount").notNull(),
  type: text("type").notNull(), // 'earned', 'spent', 'expired', 'bonus', 'adjustment'
  description: text("description").notNull(),
  sourceId: integer("source_id"), // ID of the activity, reward, etc.
  sourceType: text("source_type"), // 'activity', 'reward', 'achievement', 'admin'
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const insertHealthActivitySchema = createInsertSchema(healthActivities).omit({ 
  id: true, 
  createdAt: true 
});
export const insertAchievementSchema = createInsertSchema(achievements).omit({ 
  id: true, 
  createdAt: true 
});
export const insertUserActivitySchema = createInsertSchema(userActivities).omit({ 
  id: true 
});
export const insertRewardSchema = createInsertSchema(rewards).omit({ 
  id: true, 
  createdAt: true 
});
export const insertUserRewardSchema = createInsertSchema(userRewards).omit({ 
  id: true, 
  earnedAt: true 
});
export const insertUserPointsSchema = createInsertSchema(userPoints).omit({ 
  id: true, 
  lastActivity: true, 
  lastStreakUpdate: true 
});
export const insertPointsTransactionSchema = createInsertSchema(pointsTransactions).omit({ 
  id: true, 
  createdAt: true 
});
export const insertUserAchievementSchema = createInsertSchema(userAchievements).omit({ 
  id: true, 
  unlockedAt: true 
});

export type InsertHealthActivity = z.infer<typeof insertHealthActivitySchema>;
export type HealthActivity = typeof healthActivities.$inferSelect;

export type InsertAchievement = z.infer<typeof insertAchievementSchema>;
export type Achievement = typeof achievements.$inferSelect;

export type InsertUserActivity = z.infer<typeof insertUserActivitySchema>;
export type UserActivity = typeof userActivities.$inferSelect;

export type InsertReward = z.infer<typeof insertRewardSchema>;
export type Reward = typeof rewards.$inferSelect;

export type InsertUserReward = z.infer<typeof insertUserRewardSchema>;
export type UserReward = typeof userRewards.$inferSelect;

export type InsertUserPoints = z.infer<typeof insertUserPointsSchema>;
export type UserPoints = typeof userPoints.$inferSelect;

export type InsertPointsTransaction = z.infer<typeof insertPointsTransactionSchema>;
export type PointsTransaction = typeof pointsTransactions.$inferSelect;

export type InsertUserAchievement = z.infer<typeof insertUserAchievementSchema>;
export type UserAchievement = typeof userAchievements.$inferSelect;

// Audit logs for HIPAA compliance
export const auditLogs = pgTable("audit_logs", {
  id: serial("id").primaryKey(),
  timestamp: timestamp("timestamp").defaultNow().notNull(),
  userId: integer("user_id").references(() => users.id),
  eventType: text("event_type").notNull(),
  resourceType: text("resource_type").notNull(),
  resourceId: text("resource_id"),
  action: text("action").notNull(),
  description: text("description").notNull(),
  ipAddress: text("ip_address").notNull(),
  success: boolean("success").notNull(),
  additionalInfo: jsonb("additional_info")
});

export const insertAuditLogSchema = createInsertSchema(auditLogs).omit({ 
  id: true 
});

export type InsertAuditLog = z.infer<typeof insertAuditLogSchema>;
export type AuditLog = typeof auditLogs.$inferSelect;

// Wellness Tips model for AI-generated personalized content
export const wellnessTips = pgTable("wellness_tips", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").references(() => users.id),
  content: text("content").notNull(),
  category: text("category").notNull(), // 'mental', 'physical', 'nutrition', 'medication', 'general'
  tags: text("tags").array(),
  aiGenerated: boolean("ai_generated").default(true),
  isPersonalized: boolean("is_personalized").default(true),
  associatedDataPoints: jsonb("associated_data_points"), // Health metrics that influenced this tip
  createdAt: timestamp("created_at").defaultNow(),
  expiresAt: timestamp("expires_at"),
  interactionCount: integer("interaction_count").default(0),
  wasHelpful: boolean("was_helpful"),
  savedByUser: boolean("saved_by_user").default(false),
  motivationalQuote: text("motivational_quote"),
  actionSteps: text("action_steps").array(),
});

export const insertWellnessTipSchema = createInsertSchema(wellnessTips).omit({ 
  id: true, 
  createdAt: true,
  interactionCount: true
});

export type InsertWellnessTip = z.infer<typeof insertWellnessTipSchema>;
export type WellnessTip = typeof wellnessTips.$inferSelect;

// Neural Governance Intelligence Features

// AI Governance Configuration
export const aiGovernanceConfig = pgTable("ai_governance_config", {
  id: serial("id").primaryKey(),
  organizationId: text("organization_id").notNull(),
  aiModel: text("ai_model").notNull().default("gpt-4o"),
  maxTokens: integer("max_tokens").default(2000),
  temperature: integer("temperature").default(7), // stored as int (0.7 * 10)
  moderationLevel: text("moderation_level").notNull().default("strict"), // strict, moderate, lenient
  enabledFeatures: text("enabled_features").array().default(['content_moderation', 'risk_assessment', 'compliance_monitoring']),
  complianceFrameworks: text("compliance_frameworks").array().default(['HIPAA', 'GDPR', 'SOX']),
  riskThreshold: integer("risk_threshold").default(75), // 0-100 scale
  auditRetention: integer("audit_retention").default(2555), // days (7 years default)
  emergencyContactEmail: text("emergency_contact_email"),
  isActive: boolean("is_active").default(true),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
});

// AI Risk Assessment
export const aiRiskAssessments = pgTable("ai_risk_assessments", {
  id: serial("id").primaryKey(),
  assessmentType: text("assessment_type").notNull(), // 'content', 'decision', 'data_access', 'automated_action'
  entityId: text("entity_id").notNull(), // ID of the content/action being assessed
  entityType: text("entity_type").notNull(), // 'forum_post', 'message', 'appointment', 'medication_decision'
  riskScore: integer("risk_score").notNull(), // 0-100
  riskCategory: text("risk_category").notNull(), // 'low', 'medium', 'high', 'critical'
  identifiedRisks: text("identified_risks").array(),
  mitigationStrategies: text("mitigation_strategies").array(),
  complianceViolations: text("compliance_violations").array(),
  autoApproved: boolean("auto_approved").default(false),
  requiresHumanReview: boolean("requires_human_review").default(false),
  reviewedBy: integer("reviewed_by").references(() => users.id),
  reviewedAt: timestamp("reviewed_at"),
  reviewNotes: text("review_notes"),
  finalDecision: text("final_decision"), // 'approved', 'rejected', 'requires_modification'
  aiModel: text("ai_model").notNull(),
  confidence: integer("confidence").notNull(), // 0-100
  processingTime: integer("processing_time"), // milliseconds
  createdAt: timestamp("created_at").defaultNow(),
});

// Compliance Monitoring
export const complianceMonitoring = pgTable("compliance_monitoring", {
  id: serial("id").primaryKey(),
  framework: text("framework").notNull(), // 'HIPAA', 'GDPR', 'SOX', 'FDA_21CFR11'
  category: text("category").notNull(), // 'data_access', 'retention', 'breach_notification', 'audit_trail'
  entityType: text("entity_type").notNull(),
  entityId: text("entity_id").notNull(),
  complianceStatus: text("compliance_status").notNull(), // 'compliant', 'violation', 'warning', 'under_review'
  violationType: text("violation_type"), // 'data_breach', 'unauthorized_access', 'retention_violation'
  severity: text("severity").notNull(), // 'low', 'medium', 'high', 'critical'
  description: text("description").notNull(),
  recommendedActions: text("recommended_actions").array(),
  autoRemediated: boolean("auto_remediated").default(false),
  remediationActions: text("remediation_actions").array(),
  assignedTo: integer("assigned_to").references(() => users.id),
  dueDate: timestamp("due_date"),
  resolvedAt: timestamp("resolved_at"),
  resolvedBy: integer("resolved_by").references(() => users.id),
  resolutionNotes: text("resolution_notes"),
  riskLevel: integer("risk_level").notNull(), // 0-100
  businessImpact: text("business_impact"),
  regulatoryReporting: boolean("regulatory_reporting").default(false),
  reportedToRegulator: boolean("reported_to_regulator").default(false),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
});

// AI Decision Logs
export const aiDecisionLogs = pgTable("ai_decision_logs", {
  id: serial("id").primaryKey(),
  decisionType: text("decision_type").notNull(), // 'content_moderation', 'risk_assessment', 'recommendation', 'automation'
  entityType: text("entity_type").notNull(),
  entityId: text("entity_id").notNull(),
  inputData: jsonb("input_data").notNull(),
  outputData: jsonb("output_data").notNull(),
  aiModel: text("ai_model").notNull(),
  modelVersion: text("model_version"),
  confidence: integer("confidence").notNull(),
  processingTime: integer("processing_time").notNull(),
  decision: text("decision").notNull(),
  reasoning: text("reasoning").notNull(),
  alternativeOptions: jsonb("alternative_options"),
  humanOverride: boolean("human_override").default(false),
  overrideReason: text("override_reason"),
  overriddenBy: integer("overridden_by").references(() => users.id),
  overriddenAt: timestamp("overridden_at"),
  biasScore: integer("bias_score"), // 0-100, detected algorithmic bias
  fairnessMetrics: jsonb("fairness_metrics"),
  auditTrail: jsonb("audit_trail"),
  createdAt: timestamp("created_at").defaultNow(),
});

// Regulatory Compliance Templates
export const regulatoryTemplates = pgTable("regulatory_templates", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  framework: text("framework").notNull(), // 'HIPAA', 'GDPR', 'SOX', 'FDA_21CFR11'
  category: text("category").notNull(), // 'breach_notification', 'audit_report', 'risk_assessment'
  templateContent: text("template_content").notNull(),
  requiredFields: text("required_fields").array(),
  automaticGeneration: boolean("automatic_generation").default(false),
  approvalRequired: boolean("approval_required").default(true),
  retentionPeriod: integer("retention_period").notNull(), // days
  version: text("version").notNull().default("1.0"),
  isActive: boolean("is_active").default(true),
  createdBy: integer("created_by").references(() => users.id),
  approvedBy: integer("approved_by").references(() => users.id),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
});

// Neural Network Performance Metrics
export const neuralMetrics = pgTable("neural_metrics", {
  id: serial("id").primaryKey(),
  modelName: text("model_name").notNull(),
  metricType: text("metric_type").notNull(), // 'accuracy', 'precision', 'recall', 'f1_score', 'bias_detection'
  value: integer("value").notNull(), // stored as percentage * 100
  threshold: integer("threshold").notNull(),
  status: text("status").notNull(), // 'passing', 'failing', 'warning'
  testDataset: text("test_dataset"),
  evaluationDate: timestamp("evaluation_date").defaultNow(),
  performanceTrend: text("performance_trend"), // 'improving', 'declining', 'stable'
  alertGenerated: boolean("alert_generated").default(false),
  notes: text("notes"),
  createdAt: timestamp("created_at").defaultNow(),
});

// Intelligent Automation Rules
export const automationRules = pgTable("automation_rules", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  description: text("description").notNull(),
  triggerType: text("trigger_type").notNull(), // 'content_posted', 'user_action', 'time_based', 'risk_threshold'
  triggerConditions: jsonb("trigger_conditions").notNull(),
  actionType: text("action_type").notNull(), // 'moderate_content', 'send_notification', 'create_report', 'escalate'
  actionParameters: jsonb("action_parameters").notNull(),
  isActive: boolean("is_active").default(true),
  priority: integer("priority").default(50), // 0-100
  successRate: integer("success_rate").default(0), // percentage
  executionCount: integer("execution_count").default(0),
  lastExecuted: timestamp("last_executed"),
  createdBy: integer("created_by").references(() => users.id),
  approvedBy: integer("approved_by").references(() => users.id),
  requiresApproval: boolean("requires_approval").default(true),
  riskLevel: text("risk_level").default("medium"), // low, medium, high
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
});

// Insert schemas for neural governance features
export const insertAiGovernanceConfigSchema = createInsertSchema(aiGovernanceConfig).omit({ 
  id: true, 
  createdAt: true, 
  updatedAt: true 
});

export const insertAiRiskAssessmentSchema = createInsertSchema(aiRiskAssessments).omit({ 
  id: true, 
  createdAt: true 
});

export const insertComplianceMonitoringSchema = createInsertSchema(complianceMonitoring).omit({ 
  id: true, 
  createdAt: true, 
  updatedAt: true 
});

export const insertAiDecisionLogSchema = createInsertSchema(aiDecisionLogs).omit({ 
  id: true, 
  createdAt: true 
});

export const insertRegulatoryTemplateSchema = createInsertSchema(regulatoryTemplates).omit({ 
  id: true, 
  createdAt: true, 
  updatedAt: true 
});

export const insertNeuralMetricSchema = createInsertSchema(neuralMetrics).omit({ 
  id: true, 
  createdAt: true 
});

export const insertAutomationRuleSchema = createInsertSchema(automationRules).omit({ 
  id: true, 
  createdAt: true, 
  updatedAt: true 
});

// Types for neural governance features
export type InsertAiGovernanceConfig = z.infer<typeof insertAiGovernanceConfigSchema>;
export type AiGovernanceConfig = typeof aiGovernanceConfig.$inferSelect;

export type InsertAiRiskAssessment = z.infer<typeof insertAiRiskAssessmentSchema>;
export type AiRiskAssessment = typeof aiRiskAssessments.$inferSelect;

export type InsertComplianceMonitoring = z.infer<typeof insertComplianceMonitoringSchema>;
export type ComplianceMonitoring = typeof complianceMonitoring.$inferSelect;

export type InsertAiDecisionLog = z.infer<typeof insertAiDecisionLogSchema>;
export type AiDecisionLog = typeof aiDecisionLogs.$inferSelect;

export type InsertRegulatoryTemplate = z.infer<typeof insertRegulatoryTemplateSchema>;
export type RegulatoryTemplate = typeof regulatoryTemplates.$inferSelect;

export type InsertNeuralMetric = z.infer<typeof insertNeuralMetricSchema>;
export type NeuralMetric = typeof neuralMetrics.$inferSelect;

export type InsertAutomationRule = z.infer<typeof insertAutomationRuleSchema>;
export type AutomationRule = typeof automationRules.$inferSelect;
