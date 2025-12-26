'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Eye, EyeOff, Mail, Lock, User, Phone, ArrowRight, AlertCircle, CheckCircle } from 'lucide-react';

interface FormData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  password: string;
  confirmPassword: string;
  acceptTerms: boolean;
  acceptHipaa: boolean;
}

const initialFormData: FormData = {
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: '',
  acceptTerms: false,
  acceptHipaa: false,
};

const passwordRequirements = [
  { label: 'At least 8 characters', test: (p: string) => p.length >= 8 },
  { label: 'One uppercase letter', test: (p: string) => /[A-Z]/.test(p) },
  { label: 'One lowercase letter', test: (p: string) => /[a-z]/.test(p) },
  { label: 'One number', test: (p: string) => /\d/.test(p) },
  { label: 'One special character', test: (p: string) => /[!@#$%^&*]/.test(p) },
];

export default function SignupPage() {
  const router = useRouter();
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState(1);

  const updateFormData = (field: keyof FormData, value: string | boolean) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const validateStep1 = () => {
    if (!formData.firstName || !formData.lastName) {
      setError('Please enter your full name.');
      return false;
    }
    if (!formData.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      setError('Please enter a valid email address.');
      return false;
    }
    setError('');
    return true;
  };

  const validateStep2 = () => {
    const failedRequirements = passwordRequirements.filter((req) => !req.test(formData.password));
    if (failedRequirements.length > 0) {
      setError('Please meet all password requirements.');
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match.');
      return false;
    }
    if (!formData.acceptTerms || !formData.acceptHipaa) {
      setError('Please accept all required agreements.');
      return false;
    }
    setError('');
    return true;
  };

  const handleNext = () => {
    if (step === 1 && validateStep1()) {
      setStep(2);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateStep2()) return;

    setIsLoading(true);
    setError('');

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 2000));
      router.push('/dashboard');
    } catch {
      setError('An error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-block">
            <h1 className="text-3xl font-bold text-white">
              <span className="text-purple-400">IHEP</span> Health
            </h1>
          </Link>
          <p className="text-purple-300 mt-2">Integrated Health Empowerment Program</p>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center gap-4 mb-8">
          <div className={`flex items-center gap-2 ${step >= 1 ? 'text-purple-400' : 'text-purple-600'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 1 ? 'bg-purple-600' : 'bg-purple-900'}`}>
              1
            </div>
            <span className="text-sm hidden sm:inline">Account</span>
          </div>
          <div className={`w-8 h-px ${step >= 2 ? 'bg-purple-400' : 'bg-purple-700'}`} />
          <div className={`flex items-center gap-2 ${step >= 2 ? 'text-purple-400' : 'text-purple-600'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 2 ? 'bg-purple-600' : 'bg-purple-900'}`}>
              2
            </div>
            <span className="text-sm hidden sm:inline">Security</span>
          </div>
        </div>

        {/* Signup Card */}
        <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-8">
          <h2 className="text-2xl font-bold text-white mb-2">
            {step === 1 ? 'Create your account' : 'Set up security'}
          </h2>
          <p className="text-purple-300 mb-6">
            {step === 1
              ? 'Start your health empowerment journey'
              : 'Protect your health information'}
          </p>

          {error && (
            <div className="mb-6 p-4 bg-red-500/20 border border-red-500/30 rounded-lg flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
              <p className="text-red-300 text-sm">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            {step === 1 && (
              <>
                {/* Name Fields */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="firstName" className="block text-sm font-medium text-purple-300 mb-2">
                      First Name
                    </label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-purple-400" />
                      <input
                        id="firstName"
                        type="text"
                        value={formData.firstName}
                        onChange={(e) => updateFormData('firstName', e.target.value)}
                        className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-purple-400 focus:outline-none focus:border-purple-500 transition-colors"
                        placeholder="John"
                        required
                      />
                    </div>
                  </div>
                  <div>
                    <label htmlFor="lastName" className="block text-sm font-medium text-purple-300 mb-2">
                      Last Name
                    </label>
                    <input
                      id="lastName"
                      type="text"
                      value={formData.lastName}
                      onChange={(e) => updateFormData('lastName', e.target.value)}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-purple-400 focus:outline-none focus:border-purple-500 transition-colors"
                      placeholder="Doe"
                      required
                    />
                  </div>
                </div>

                {/* Email */}
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-purple-300 mb-2">
                    Email Address
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-purple-400" />
                    <input
                      id="email"
                      type="email"
                      value={formData.email}
                      onChange={(e) => updateFormData('email', e.target.value)}
                      className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-purple-400 focus:outline-none focus:border-purple-500 transition-colors"
                      placeholder="you@example.com"
                      required
                    />
                  </div>
                </div>

                {/* Phone */}
                <div>
                  <label htmlFor="phone" className="block text-sm font-medium text-purple-300 mb-2">
                    Phone Number <span className="text-purple-500">(optional)</span>
                  </label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-purple-400" />
                    <input
                      id="phone"
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => updateFormData('phone', e.target.value)}
                      className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-purple-400 focus:outline-none focus:border-purple-500 transition-colors"
                      placeholder="(555) 123-4567"
                    />
                  </div>
                </div>

                <button
                  type="button"
                  onClick={handleNext}
                  className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-medium rounded-lg transition-all flex items-center justify-center gap-2"
                >
                  Continue
                  <ArrowRight className="w-5 h-5" />
                </button>
              </>
            )}

            {step === 2 && (
              <>
                {/* Password */}
                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-purple-300 mb-2">
                    Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-purple-400" />
                    <input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      value={formData.password}
                      onChange={(e) => updateFormData('password', e.target.value)}
                      className="w-full pl-10 pr-12 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-purple-400 focus:outline-none focus:border-purple-500 transition-colors"
                      placeholder="Create a strong password"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-purple-400 hover:text-purple-300"
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>

                  {/* Password Requirements */}
                  <div className="mt-3 space-y-1">
                    {passwordRequirements.map((req, index) => {
                      const passed = req.test(formData.password);
                      return (
                        <div key={index} className="flex items-center gap-2">
                          <CheckCircle
                            className={`w-4 h-4 ${passed ? 'text-green-400' : 'text-purple-600'}`}
                          />
                          <span
                            className={`text-xs ${passed ? 'text-green-400' : 'text-purple-400'}`}
                          >
                            {req.label}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Confirm Password */}
                <div>
                  <label htmlFor="confirmPassword" className="block text-sm font-medium text-purple-300 mb-2">
                    Confirm Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-purple-400" />
                    <input
                      id="confirmPassword"
                      type={showConfirmPassword ? 'text' : 'password'}
                      value={formData.confirmPassword}
                      onChange={(e) => updateFormData('confirmPassword', e.target.value)}
                      className="w-full pl-10 pr-12 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-purple-400 focus:outline-none focus:border-purple-500 transition-colors"
                      placeholder="Confirm your password"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-purple-400 hover:text-purple-300"
                    >
                      {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                {/* Agreements */}
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <input
                      id="acceptTerms"
                      type="checkbox"
                      checked={formData.acceptTerms}
                      onChange={(e) => updateFormData('acceptTerms', e.target.checked)}
                      className="mt-1 w-4 h-4 rounded border-white/20 bg-white/5 text-purple-600 focus:ring-purple-500"
                    />
                    <label htmlFor="acceptTerms" className="text-sm text-purple-300">
                      I agree to the{' '}
                      <Link href="/terms" className="text-purple-400 hover:underline">
                        Terms of Service
                      </Link>{' '}
                      and{' '}
                      <Link href="/privacy" className="text-purple-400 hover:underline">
                        Privacy Policy
                      </Link>
                    </label>
                  </div>
                  <div className="flex items-start gap-3">
                    <input
                      id="acceptHipaa"
                      type="checkbox"
                      checked={formData.acceptHipaa}
                      onChange={(e) => updateFormData('acceptHipaa', e.target.checked)}
                      className="mt-1 w-4 h-4 rounded border-white/20 bg-white/5 text-purple-600 focus:ring-purple-500"
                    />
                    <label htmlFor="acceptHipaa" className="text-sm text-purple-300">
                      I understand and consent to the{' '}
                      <Link href="/hipaa" className="text-purple-400 hover:underline">
                        HIPAA Authorization
                      </Link>{' '}
                      for handling my health information
                    </label>
                  </div>
                </div>

                <div className="flex gap-4">
                  <button
                    type="button"
                    onClick={() => setStep(1)}
                    className="flex-1 py-3 bg-white/10 hover:bg-white/20 text-white font-medium rounded-lg transition-colors"
                  >
                    Back
                  </button>
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="flex-1 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-medium rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        Creating...
                      </>
                    ) : (
                      <>
                        Create Account
                        <ArrowRight className="w-5 h-5" />
                      </>
                    )}
                  </button>
                </div>
              </>
            )}
          </form>
        </div>

        {/* Login Link */}
        <p className="text-center text-purple-300 mt-6">
          Already have an account?{' '}
          <Link href="/auth/login" className="text-purple-400 hover:text-purple-300 font-medium">
            Sign in
          </Link>
        </p>

        {/* Security Notice */}
        <p className="text-center text-purple-400/60 text-xs mt-4">
          Your health data is protected with enterprise-grade encryption.
          <br />
          HIPAA compliant and secure.
        </p>
      </div>
    </div>
  );
}
