// components/digital-twin/TwinDashboard.tsx (continued)
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Research Participation */}
      <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl p-6 border border-purple-200">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="font-semibold text-purple-800 mb-2">🔬 Research Participation</h3>
            <p className="text-purple-700 text-sm mb-4">
              Your digital twin contributes to medical research while maintaining complete privacy.
              Federated learning ensures your data never leaves your device.
            </p>
            <button className="bg-purple-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-purple-700 transition-colors">
              Learn About Research Impact
            </button>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-purple-600">98.7%</div>
            <div className="text-xs text-purple-500">Model Accuracy</div>
          </div>
        </div>
      </div>
    </div>
  );
}
