import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/components/auth/AuthProvider';
import { Toaster } from '@/components/ui/toaster';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'IHEP - Integrated Health Empowerment Program',
  description: 'Comprehensive healthcare platform for life-altering conditions',
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'https://ihep-platform.org'),
  keywords: ['healthcare', 'digital twin', 'patient care', 'health management'],
  authors: [{ name: 'IHEP Foundation' }],
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: '/',
    title: 'IHEP Platform',
    description: 'Empowering patients with life-altering conditions',
    siteName: 'IHEP',
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <AuthProvider>
          {children}
          <Toaster />
        </AuthProvider>
      </body>
    </html>
  );
}
