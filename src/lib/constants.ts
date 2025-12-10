export const APP_NAME = "Health Insight Ventures";

// Navigation
export const NAV_ITEMS = [
  { name: "Resources", href: "/resources" },
  { name: "Events", href: "/events" },
  { name: "Community", href: "/community" },
  { name: "Forum", href: "/forum" },
  { name: "Education", href: "/education" },
  { name: "Rewards", href: "/rewards" },
  { name: "About Us", href: "/about" },
];

// User roles
export const USER_ROLES = {
  PATIENT: "patient",
  PROVIDER: "provider",
  ADMIN: "admin",
};

// Admin Navigation
export const ADMIN_NAV_ITEMS = [
  { name: "Audit Logs", href: "/admin/audit-logs", icon: "activity" },
  { name: "State Compliance", href: "/admin/state-compliance", icon: "shield" },
  { name: "Reset Demo Data", href: "/admin/reset-data", icon: "refresh" },
];

// Resource categories
export const RESOURCE_CATEGORIES = [
  { id: "medical_providers", name: "Medical Providers" },
  { id: "support_groups", name: "Support Groups" },
  { id: "financial_assistance", name: "Financial Assistance" },
  { id: "housing_resources", name: "Housing Resources" },
  { id: "mental_health", name: "Mental Health" },
];

// Distance options
export const DISTANCE_OPTIONS = [
  { value: "5", label: "Within 5 miles" },
  { value: "10", label: "Within 10 miles" },
  { value: "25", label: "Within 25 miles" },
  { value: "50", label: "Within 50 miles" },
  { value: "any", label: "Any distance" },
];

// Availability options
export const AVAILABILITY_OPTIONS = [
  { id: "available_today", name: "Available Today" },
  { id: "taking_new_patients", name: "Taking New Patients" },
  { id: "virtual_services", name: "Virtual Services" },
];
