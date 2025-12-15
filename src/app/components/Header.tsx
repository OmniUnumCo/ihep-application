"use client";

import { useState } from 'react';
import Image from 'next/image';
import Logo from '@/assets/images/IHEP-Logo.png';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { Menu, User, X, Pill, Activity, Settings, Shield, FileText, Award } from 'lucide-react';
import { NAV_ITEMS, APP_NAME, ADMIN_NAV_ITEMS } from '@/lib/constants';
import SwitchRole from '@/components/ui/switch-role';
import useAuth from '@/hooks/useAuth';

const Header = () => {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();
  const { isAuthenticated, user } = useAuth();

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="container mx-auto px-2 sm:px-4 py-3 sm:py-4 md:py-6 flex justify-between items-center">
        <div className="flex items-center flex-shrink-0">
          <div className="flex items-center">
            <Link href="/">
              <div className="flex items-center">
                <div className="mr-2 sm:mr-3">
                  <Image 
                    src={Logo} 
                    alt="Health Insight Ventures Logo" 
                    className="h-12 sm:h-16 md:h-20 lg:h-24 w-auto max-w-full" 
                    width={300}
                    height={80}
                    priority
                  />
                </div>
                <h1 className="text-lg sm:text-xl md:text-2xl font-montserrat font-bold text-[#114e2b] cursor-pointer sr-only">
                  Health Insight Ventures
                </h1>
              </div>
            </Link>
          </div>
        </div>
        
        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-2 lg:space-x-4 xl:space-x-6 flex-shrink min-w-0">
          {NAV_ITEMS.map((item) => (
            <div key={item.href}>
              <Link href={item.href}>
                <div className={`text-gray-700 hover:text-primary font-medium cursor-pointer text-sm lg:text-base whitespace-nowrap transition-colors duration-200 ${
                  pathname === item.href ? 'text-primary font-semibold' : ''
                }`}>
                  {item.name}
                </div>
              </Link>
            </div>
          ))}
          
          {isAuthenticated ? (
            <div className="flex items-center gap-1 lg:gap-2 xl:gap-3 ml-2 lg:ml-4">
              <span className="text-xs lg:text-sm text-gray-600 mr-1 lg:mr-2 hidden lg:block">
                Welcome, {user?.firstName || user?.username}!
              </span>
              {user?.role === 'admin' && (
                <div className="flex items-center gap-1 lg:gap-2 mr-1 lg:mr-2">
                  <Link href="/admin/audit-logs">
                    <Button variant="ghost" size="sm" className="text-gray-700 hover:text-primary text-xs lg:text-sm p-1 lg:p-2">
                      <Activity size={16} className="mr-0 lg:mr-1" />
                      <span className="hidden xl:inline">Audit Logs</span>
                    </Button>
                  </Link>
                  <Link href="/admin/state-compliance">
                    <Button variant="ghost" size="sm" className="text-gray-700 hover:text-primary text-xs lg:text-sm p-1 lg:p-2">
                      <Shield size={16} className="mr-0 lg:mr-1" />
                      <span className="hidden xl:inline">State Compliance</span>
                    </Button>
                  </Link>
                </div>
              )}
              <Link href="/profile">
                <Button variant="outline" className="flex items-center space-x-1 lg:space-x-2 text-primary border-primary hover:bg-primary hover:text-white text-xs lg:text-sm p-1 lg:p-2">
                  <User size={16} />
                  <span className="hidden lg:inline">My Account</span>
                </Button>
              </Link>
            </div>
          ) : (
            <div className="flex space-x-1 lg:space-x-2">
              <Link href="/login">
                <Button variant="outline" className="text-primary border-primary hover:bg-primary hover:text-white text-xs lg:text-sm p-1 lg:p-2">
                  Log In
                </Button>
              </Link>
              <Link href="/register">
                <Button className="btn-primary text-xs lg:text-sm p-1 lg:p-2">
                  Sign Up
                </Button>
              </Link>
            </div>
          )}
        </nav>
        
        {/* Mobile menu button */}
        <Sheet open={isOpen} onOpenChange={setIsOpen}>
          <SheetTrigger asChild>
            <Button variant="ghost" className="md:hidden p-1 sm:p-2 flex-shrink-0">
              <Menu className="h-5 w-5 sm:h-6 sm:w-6 text-primary" />
            </Button>
          </SheetTrigger>
          <SheetContent side="right" className="w-[80%] sm:w-[350px] bg-white border border-gray-200">
            <div className="flex flex-col h-full">
              <div className="flex justify-between items-center mb-8">
                <h2 className="text-xl font-montserrat font-bold gradient-text">Menu</h2>
                <Button variant="ghost" size="icon" onClick={() => setIsOpen(false)}>
                  <X className="h-5 w-5 text-gray-600" />
                </Button>
              </div>
              <nav className="flex flex-col space-y-3">
                {NAV_ITEMS.map((item) => (
                  <div key={item.href} onClick={() => setIsOpen(false)}>
                    <Link href={item.href}>
                      <div className={`rounded-xl p-4 text-center transition-all duration-200 ${
                        pathname === item.href ? 'gradient-primary text-white' : 'btn-glossy'
                      }`} style={{WebkitTapHighlightColor: 'transparent'}}>
                        <span className={`font-medium text-base ${
                          pathname === item.href ? 'text-white' : 'text-gray-700'
                        }`}>
                          {item.name}
                        </span>
                      </div>
                    </Link>
                  </div>
                ))}
                
                <div className="border-t border-gray-200 pt-6 mt-4">
                  {isAuthenticated ? (
                    <>
                      <div className="space-y-3">
                        <div onClick={() => setIsOpen(false)}>
                          <Link href="/profile">
                            <div className="btn-glossy rounded-xl p-4 flex items-center" style={{WebkitTapHighlightColor: 'transparent'}}>
                              <div className="icon-3d icon-community mr-3">
                                <User size={16} />
                              </div>
                              <span className="font-medium text-gray-700">My Profile</span>
                            </div>
                          </Link>
                        </div>
                        <div onClick={() => setIsOpen(false)}>
                          <Link href="/twilio">
                            <div className="btn-glossy rounded-xl p-4 flex items-center" style={{WebkitTapHighlightColor: 'transparent'}}>
                              <div className="icon-3d mr-3">
                                <Settings size={16} />
                              </div>
                              <span className="font-medium text-gray-700">SMS Settings</span>
                            </div>
                          </Link>
                        </div>
                        <div onClick={() => setIsOpen(false)}>
                          <Link href="/medication-refill">
                            <div className="btn-glossy rounded-xl p-4 flex items-center" style={{WebkitTapHighlightColor: 'transparent'}}>
                              <div className="icon-3d icon-health mr-3">
                                <Pill size={16} />
                              </div>
                              <span className="font-medium text-gray-700">Medication Refill</span>
                            </div>
                          </Link>
                        </div>
                        <div onClick={() => setIsOpen(false)}>
                          <Link href="/risk-assessment">
                            <div className="btn-glossy rounded-xl p-4 flex items-center" style={{WebkitTapHighlightColor: 'transparent'}}>
                              <div className="icon-3d icon-health mr-3">
                                <Activity size={16} />
                              </div>
                              <span className="font-medium text-gray-700">Health Assessment</span>
                            </div>
                          </Link>
                        </div>
                        <div onClick={() => setIsOpen(false)}>
                          <Link href="/rewards">
                            <div className="btn-glossy rounded-xl p-4 flex items-center" style={{WebkitTapHighlightColor: 'transparent'}}>
                              <div className="icon-3d icon-resources mr-3">
                                <Award size={16} />
                              </div>
                              <span className="font-medium text-gray-700">Health Rewards</span>
                            </div>
                          </Link>
                        </div>
                      </div>
                      
                      {/* Admin Navigation Items */}
                      {user?.role === 'admin' && (
                        <div className="border-t border-gray-200 pt-4 mt-4">
                          <h3 className="text-sm text-gray-500 mb-3 font-semibold uppercase tracking-wider">Admin Features</h3>
                          <div className="space-y-3">
                            <div onClick={() => setIsOpen(false)}>
                              <Link href="/admin/audit-logs">
                                <div className="btn-glossy rounded-xl p-4 flex items-center" style={{WebkitTapHighlightColor: 'transparent'}}>
                                  <div className="icon-3d mr-3">
                                    <Activity size={16} />
                                  </div>
                                  <span className="font-medium text-gray-700">Audit Logs</span>
                                </div>
                              </Link>
                            </div>
                            <div onClick={() => setIsOpen(false)}>
                              <Link href="/admin/state-compliance">
                                <div className="btn-glossy rounded-xl p-4 flex items-center" style={{WebkitTapHighlightColor: 'transparent'}}>
                                  <div className="icon-3d mr-3">
                                    <Shield size={16} />
                                  </div>
                                  <span className="font-medium text-gray-700">State Compliance</span>
                                </div>
                              </Link>
                            </div>
                          </div>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="space-y-3">
                      <Link href="/login">
                        <div className="btn-glossy rounded-xl p-4 text-center" onClick={() => setIsOpen(false)} style={{WebkitTapHighlightColor: 'transparent'}}>
                          <span className="font-medium text-gray-700">Log In</span>
                        </div>
                      </Link>
                      <Link href="/register">
                        <div className="gradient-primary rounded-xl p-4 text-center transition-all duration-200" onClick={() => setIsOpen(false)} style={{WebkitTapHighlightColor: 'transparent', cursor: 'pointer', touchAction: 'manipulation'}}>
                          <span className="font-medium text-white">Sign Up</span>
                        </div>
                      </Link>
                    </div>
                  )}
                </div>
              </nav>
            </div>
          </SheetContent>
        </Sheet>
      </div>
      
      {/* Role switcher */}
      {isAuthenticated && <SwitchRole />}
    </header>
  );
};

export default Header;
