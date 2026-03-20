'use client';

import Link from 'next/link';
import { Shield, Zap, Brain, Lock, TrendingUp, Users } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <nav className="glass-effect border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <Shield className="w-8 h-8 text-blue-600" />
              <span className="text-2xl font-bold gradient-text">VORTEX Shield 2.0</span>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/login" className="text-gray-700 hover:text-blue-600 transition-colors">
                Login
              </Link>
              <Link href="/register" className="btn-primary">
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main>
        <section className="py-20 px-4">
          <div className="max-w-7xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <h1 className="text-6xl font-bold mb-6">
                Intelligent Income Protection
                <br />
                <span className="gradient-text">Powered by AI</span>
              </h1>
              <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
                Revolutionary parametric insurance for gig workers. Automatic claims, AI-powered risk prediction, 
                and fraud-resistant protection that pays you in minutes, not weeks.
              </p>
              <div className="flex justify-center space-x-4">
                <Link href="/register" className="btn-primary text-lg px-8 py-4">
                  Start Protection Now
                </Link>
                <button className="btn-secondary text-lg px-8 py-4">
                  Watch Demo
                </button>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="mt-16 relative"
            >
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 shadow-2xl">
                <div className="grid grid-cols-3 gap-8 text-white">
                  <div>
                    <div className="text-4xl font-bold">95%</div>
                    <div className="text-blue-100">Fraud Detection Rate</div>
                  </div>
                  <div>
                    <div className="text-4xl font-bold">&lt; 5 min</div>
                    <div className="text-blue-100">Claim Processing</div>
                  </div>
                  <div>
                    <div className="text-4xl font-bold">₹39</div>
                    <div className="text-blue-100">Starting Weekly</div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        <section className="py-20 bg-white">
          <div className="max-w-7xl mx-auto px-4">
            <h2 className="text-4xl font-bold text-center mb-12">World-Class Features</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              <FeatureCard
                icon={<Brain className="w-12 h-12 text-blue-600" />}
                title="AI Risk Prediction"
                description="LSTM models predict disruptions before they happen. Get proactive protection, not reactive insurance."
              />
              <FeatureCard
                icon={<Zap className="w-12 h-12 text-purple-600" />}
                title="Zero-Touch Claims"
                description="Automatic detection and approval. No forms, no waiting. Money in your account instantly."
              />
              <FeatureCard
                icon={<Lock className="w-12 h-12 text-green-600" />}
                title="Fraud Detection AI"
                description="Multi-layer security detects GPS spoofing, fraud rings, and coordinated attacks with 95% accuracy."
              />
              <FeatureCard
                icon={<TrendingUp className="w-12 h-12 text-orange-600" />}
                title="Dynamic Pricing"
                description="Weekly premiums based on your actual risk. Pay less when conditions are safe."
              />
              <FeatureCard
                icon={<Users className="w-12 h-12 text-red-600" />}
                title="Crowd Validation"
                description="Community-verified events ensure real disruptions get paid, fake claims get blocked."
              />
              <FeatureCard
                icon={<Shield className="w-12 h-12 text-indigo-600" />}
                title="Digital Twin Simulation"
                description="City-wide disruption modeling predicts impact on your income before it happens."
              />
            </div>
          </div>
        </section>

        <section className="py-20 bg-gradient-to-br from-blue-600 to-purple-600">
          <div className="max-w-7xl mx-auto px-4 text-center text-white">
            <h2 className="text-4xl font-bold mb-6">How It Works</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mt-12">
              <StepCard number="1" title="Subscribe" description="Choose your weekly plan based on AI risk analysis" />
              <StepCard number="2" title="Monitor" description="Real-time tracking of weather, traffic, and air quality" />
              <StepCard number="3" title="Auto-Trigger" description="System detects disruptions automatically" />
              <StepCard number="4" title="Get Paid" description="Instant approval and payout in under 5 minutes" />
            </div>
          </div>
        </section>

        <section className="py-20 bg-white">
          <div className="max-w-4xl mx-auto px-4 text-center">
            <h2 className="text-4xl font-bold mb-6">Ready to Protect Your Income?</h2>
            <p className="text-xl text-gray-600 mb-8">
              Join thousands of gig workers who trust VORTEX Shield for intelligent income protection.
            </p>
            <Link href="/register" className="btn-primary text-lg px-12 py-4 inline-block">
              Get Started for ₹39/week
            </Link>
          </div>
        </section>
      </main>

      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Shield className="w-6 h-6" />
                <span className="text-xl font-bold">VORTEX Shield</span>
              </div>
              <p className="text-gray-400">AI-powered parametric insurance for the gig economy.</p>
            </div>
            <div>
              <h3 className="font-bold mb-4">Product</h3>
              <ul className="space-y-2 text-gray-400">
                <li>Features</li>
                <li>Pricing</li>
                <li>How It Works</li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold mb-4">Company</h3>
              <ul className="space-y-2 text-gray-400">
                <li>About</li>
                <li>Contact</li>
                <li>Careers</li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold mb-4">Legal</h3>
              <ul className="space-y-2 text-gray-400">
                <li>Privacy</li>
                <li>Terms</li>
                <li>Security</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>© 2024 VORTEX Shield 2.0. Built by Team VORTEX. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      className="card p-6 hover:shadow-xl transition-all duration-200"
    >
      <div className="mb-4">{icon}</div>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </motion.div>
  );
}

function StepCard({ number, title, description }: { number: string; title: string; description: string }) {
  return (
    <div className="text-center">
      <div className="w-16 h-16 bg-white text-blue-600 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
        {number}
      </div>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-blue-100">{description}</p>
    </div>
  );
}
