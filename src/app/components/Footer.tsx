import Link from 'next/link';
import { Facebook, Twitter, Instagram, MapPin, Phone, Mail } from 'lucide-react';
import { APP_NAME } from '@/lib/constants';

const Footer = () => {
  return (
    <footer className="bg-primary text-white py-8">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="font-montserrat font-bold text-lg mb-4">{APP_NAME}</h3>
            <p className="text-sm text-gray-300">
              Empowering patients with resources, support, and community connections since 2020.
            </p>
            <div className="flex mt-4 space-x-4">
              <a href="#" className="text-white hover:text-accent">
                <Facebook size={20} />
              </a>
              <a href="#" className="text-white hover:text-accent">
                <Twitter size={20} />
              </a>
              <a href="#" className="text-white hover:text-accent">
                <Instagram size={20} />
              </a>
            </div>
          </div>
          
          <div>
            <h3 className="font-montserrat font-bold text-md mb-4">Quick Links</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <div>
                  <Link href="/">
                    <div className="text-gray-300 hover:text-white cursor-pointer">Home</div>
                  </Link>
                </div>
              </li>
              <li>
                <div>
                  <Link href="/resources">
                    <div className="text-gray-300 hover:text-white cursor-pointer">Resources</div>
                  </Link>
                </div>
              </li>
              <li>
                <div>
                  <Link href="/events">
                    <div className="text-gray-300 hover:text-white cursor-pointer">Events</div>
                  </Link>
                </div>
              </li>
              <li>
                <div>
                  <Link href="/community">
                    <div className="text-gray-300 hover:text-white cursor-pointer">Community</div>
                  </Link>
                </div>
              </li>
              <li>
                <div>
                  <Link href="/education">
                    <div className="text-gray-300 hover:text-white cursor-pointer">Education</div>
                  </Link>
                </div>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-montserrat font-bold text-md mb-4">Support</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <div>
                  <Link href="/help">
                    <div className="text-gray-300 hover:text-white cursor-pointer">Help Center</div>
                  </Link>
                </div>
              </li>
              <li>
                <div>
                  <Link href="/contact">
                    <div className="text-gray-300 hover:text-white cursor-pointer">Contact Us</div>
                  </Link>
                </div>
              </li>
              <li>
                <div>
                  <Link href="/privacy">
                    <div className="text-gray-300 hover:text-white cursor-pointer">Privacy Policy</div>
                  </Link>
                </div>
              </li>
              <li>
                <div>
                  <Link href="/terms">
                    <div className="text-gray-300 hover:text-white cursor-pointer">Terms of Service</div>
                  </Link>
                </div>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-montserrat font-bold text-md mb-4">Contact</h3>
            <ul className="space-y-2 text-sm">
              <li className="flex items-start">
                <Phone className="text-accent mr-2 h-4 w-4 mt-0.5" />
                <span className="text-gray-300">(917) 566-8112</span>
              </li>
              <li className="flex items-start">
                <Mail className="text-accent mr-2 h-4 w-4 mt-0.5" />
                <span className="text-gray-300">support@healthinsightventures.com</span>
              </li>
              <li className="flex items-start mt-2">
                <MapPin className="text-accent mr-2 h-4 w-4 mt-0.5" />
                <span className="text-gray-300">12 W 129th St, 1E, New York, NY 10027</span>
              </li>
              <li className="flex items-start mt-2">
                <Phone className="text-accent mr-2 h-4 w-4 mt-0.5" />
                <span className="text-gray-300">24/7 Support Available</span>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-700 mt-8 pt-6 text-center text-sm text-gray-400">
          <p>© {new Date().getFullYear()} {APP_NAME}. All rights reserved. This website is HIPAA compliant and uses secure encryption.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
