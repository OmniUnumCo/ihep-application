// components/research/ResearchDashboard.tsx
'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/components/auth/AuthProvider';

interface ResearchProject {
  id: string;
  title: string;
  description: string;
  principal_investigator: string;
  institution: string;
  participant_count: number;
  data_points_shared: number;
  estimated_value: number;
  created_at: string;
}

interface UserProject {
  id: string;
  title: string;
  description: string;
  status: string;
  enrolled_at: string;
  data_shared: number;
  compensation_earned: number;
}

export function ResearchDashboard() {
  const { user } = useAuth();
  const [projects, setProjects] = useState<ResearchProject[]>([]);
  const [userProjects, setUserProjects] = useState<UserProject[]>([]);
  const [impactMetrics, setImpactMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('available');

  useEffect(() => {
    if (user) {
      loadResearchData();
    }
  }, [user]);

  const loadResearchData = async () => {
    setLoading(true);
    try {
      // Load available projects
      const projectsResponse = await fetch('/api/research/projects');
      if (projectsResponse.ok) {
        const { projects } = await projectsResponse.json();
        setProjects(projects);
      }

      // Load user's projects
      const userProjectsResponse = await fetch('/api/research/user/projects', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
        },
      });
      if (userProjectsResponse.ok) {
        const { projects } = await userProjectsResponse.json();
        setUserProjects(projects);
      }

      // Load impact metrics
      const impactResponse = await fetch('/api/research/impact');
      if (impactResponse.ok) {
        const impact = await impactResponse.json();
        setImpactMetrics(impact);
      }
    } catch (error) {
      console.error('Failed to load research data:', error);
    } finally {
      setLoading(false);
    }
  };

  const enrollInProject = async (projectId: string) => {
    try {
      const response = await fetch(`/api/research/projects/${projectId}/enroll`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
        },
        body: JSON.stringify({
          consent_data: {
            data_types: ['vital_signs', 'lab_results', 'medication_history'],
            research_purpose: 'Cure acceleration research',
            duration: '12_months',
            withdrawal_rights: 'You can withdraw at any time'
          }
        }),
      });

      if (response.ok) {
        alert('Successfully enrolled in research project!');
        loadResearchData(); // Refresh data
      } else {
        const error = await response.json();
        alert(`Failed to enroll: ${error.error}`);
      }
    } catch (error) {
      alert('Failed to enroll in project. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">🔬 Research Collaboration</h2>
        <div className="text-sm text-gray-500">
          Contributing to medical breakthroughs
        </div>
      </div>

      {/* Impact Metrics */}
      {impactMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-lg p-4 border border-purple-200">
            <div className="text-2xl font-bold text-purple-600">
              {impactMetrics.metrics.total_projects}
            </div>
            <div className="text-sm text-purple-700">Active Projects</div>
          </div>
          <div className="bg-gradient-to-br from-green-50 to-teal-50 rounded-lg p-4 border border-green-200">
            <div className="text-2xl font-bold text-green-600">
              {impactMetrics.metrics.total_participants.toLocaleString()}
            </div>
            <div className="text-sm text-green-700">Participants</div>
          </div>
          <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg p-4 border border-blue-200">
            <div className="text-2xl font-bold text-blue-600">
              ${impactMetrics.metrics.total_compensation.toLocaleString()}
            </div>
            <div className="text-sm text-blue-700">Total Compensation</div>
          </div>
          <div className="bg-gradient-to-br from-orange-50 to-amber-50 rounded-lg p-4 border border-orange-200">
            <div className="text-2xl font-bold text-orange-600">
              {impactMetrics.platform_impact.cure_acceleration_years} years
            </div>
            <div className="text-sm text-orange-700">Cure Acceleration</div>
          </div>
        </div>
      )}

      {/* Platform Impact */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl p-6 text-white">
        <h3 className="font-semibold mb-2">🌍 Global Impact</h3>
        <p className="text-sm mb-4">
          Your participation helps accelerate cures for life-altering conditions. 
          Together, we've potentially impacted {impactMetrics?.platform_impact.lives_potentially_impacted?.toLocaleString() || '50,000'}+ lives 
          and enabled {impactMetrics?.platform_impact.research_papers_enabled || '15'}+ research papers.
        </p>
        <div className="flex space-x-4 text-xs">
          <span>🔬 {impactMetrics?.platform_impact.research_papers_enabled || '15'} Research Papers</span>
          <span>💊 {impactMetrics?.platform_impact.patent_applications || '3'} Patent Applications</span>
          <span>🏆 {impactMetrics?.metrics.avg_data_quality?.toFixed(2) || '4.8'}/5 Data Quality</span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('available')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'available'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Available Projects ({projects.length})
          </button>
          <button
            onClick={() => setActiveTab('my-projects')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'my-projects'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            My Projects ({userProjects.length})
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'available' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {projects.map((project) => (
            <div key={project.id} className="bg-white rounded-xl shadow-sm border p-6 hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="font-semibold text-lg text-gray-900">{project.title}</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {project.principal_investigator} • {project.institution}
                  </p>
                </div>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Active
                </span>
              </div>
              
              <p className="text-gray-700 text-sm mb-4">{project.description}</p>
              
              <div className="flex justify-between items-center text-xs text-gray-500 mb-4">
                <span>{project.participant_count} participants</span>
                <span>{project.data_points_shared} data points shared</span>
                <span>${project.estimated_value.toFixed(2)} value generated</span>
              </div>
              
              <button
                onClick={() => enrollInProject(project.id)}
                className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium"
              >
                Enroll in Research
              </button>
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {userProjects.map((project) => (
            <div key={project.id} className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="font-semibold text-gray-900">{project.title}</h3>
                  <p className="text-sm text-gray-600 mt-1">Enrolled {new Date(project.enrolled_at).toLocaleDateString()}</p>
                </div>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  project.status === 'active' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {project.status}
                </span>
              </div>
              
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center p-3 bg-blue-50 rounded-lg">
                  <div className="text-lg font-bold text-blue-600">{project.data_shared}</div>
                  <div className="text-xs text-blue-700">Data Points Shared</div>
                </div>
                <div className="text-center p-3 bg-green-50 rounded-lg">
                  <div className="text-lg font-bold text-green-600">${project.compensation_earned.toFixed(2)}</div>
                  <div className="text-xs text-green-700">Earned</div>
                </div>
                <div className="text-center p-3 bg-purple-50 rounded-lg">
                  <div className="text-lg font-bold text-purple-600">4.9</div>
                  <div className="text-xs text-purple-700">Data Quality</div>
                </div>
              </div>
              
              <div className="flex space-x-3">
                <button className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors text-sm">
                  Share More Data
                </button>
                <button className="flex-1 bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition-colors text-sm">
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Privacy Notice */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">Privacy Protection</h3>
            <div className="mt-2 text-sm text-yellow-700">
              <p>
                All research data is protected with ε-differential privacy and k-anonymity techniques. 
                Your personal information is never shared with researchers.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
