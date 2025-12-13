import React from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Sparkles, 
  ArrowLeft, 
  Check,
  X,
  Zap,
  Crown,
  HelpCircle
} from 'lucide-react';

export default function PricingPage() {
  const navigate = useNavigate();

  const features = [
    { name: 'AI Script Generation', free: '3 per day', pro: 'Unlimited' },
    { name: 'Thumbnail Generation', free: '2 per day', pro: 'Unlimited' },
    { name: 'Image Generation', free: '2 per day', pro: 'Unlimited' },
    { name: 'Audio Voiceover', free: false, pro: 'Unlimited' },
    { name: 'Face Integration', free: false, pro: true },
    { name: 'HD Exports', free: false, pro: true },
    { name: 'YouTube Analysis', free: '5 videos', pro: 'Unlimited' },
    { name: 'One-Click Workflow', free: false, pro: true },
    { name: 'Priority Processing', free: false, pro: true },
    { name: 'Email Support', free: true, pro: true },
    { name: 'Priority Support', free: false, pro: true },
  ];

  const faqs = [
    {
      question: 'How does the 14-day free trial work?',
      answer: 'When you sign up, you get full access to all Pro features for 14 days completely free. No credit card required to start. You can cancel anytime during the trial.',
    },
    {
      question: 'What payment methods do you accept?',
      answer: 'We accept UPI (PhonePe, GPay, Paytm), all major credit/debit cards, and net banking through our secure payment partner.',
    },
    {
      question: 'Can I cancel my subscription anytime?',
      answer: 'Yes! You can cancel your subscription at any time from your account settings. Your access will continue until the end of your current billing period.',
    },
    {
      question: 'Is there a refund policy?',
      answer: 'We have a no-refund policy for all subscription payments. This is why we offer a generous 14-day free trial - so you can fully evaluate our service before paying. You can cancel anytime to stop future charges.',
    },
    {
      question: 'What happens to my content if I cancel?',
      answer: 'Your account and all generated content remain accessible even after cancellation. You can resubscribe anytime to regain Pro features.',
    },
    {
      question: 'Do you offer annual billing?',
      answer: 'Currently we offer monthly billing at ₹2,499/month. Annual plans with additional discounts will be available soon.',
    },
  ];

  return (
    <div className="min-h-screen bg-[#0B0C10] text-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-8 py-4 bg-[#0B0C10]/80 backdrop-blur-xl border-b border-white/5">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-semibold tracking-tight">ViralLab</span>
        </Link>
        <div className="flex items-center gap-4">
          <Link 
            to="/"
            className="flex items-center gap-2 text-sm text-white/70 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Link>
          <button
            onClick={() => navigate('/login')}
            className="text-sm text-white/70 hover:text-white transition-colors"
          >
            Login
          </button>
        </div>
      </nav>

      {/* Hero */}
      <div className="pt-32 pb-16 px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center max-w-3xl mx-auto"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-violet-500/10 border border-violet-500/20 text-sm text-violet-300 mb-6">
            <Zap className="w-4 h-4" />
            Simple, transparent pricing
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Choose the right plan for you
          </h1>
          <p className="text-xl text-white/60">
            Start free, upgrade when you're ready. No hidden fees.
          </p>
        </motion.div>
      </div>

      {/* Pricing Cards */}
      <div className="px-6 pb-20">
        <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Free Plan */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white/[0.02] border border-white/[0.06] rounded-2xl p-8"
          >
            <div className="mb-6">
              <h2 className="text-xl font-semibold mb-1">Free</h2>
              <p className="text-white/50 text-sm">Perfect for trying out</p>
            </div>

            <div className="mb-6">
              <span className="text-4xl font-bold">₹0</span>
              <span className="text-white/50 ml-2">/ forever</span>
            </div>

            <button
              onClick={() => navigate('/signup')}
              className="w-full py-3 rounded-xl bg-white/10 hover:bg-white/15 border border-white/10 font-medium transition-colors mb-8"
            >
              Get Started Free
            </button>

            <div className="space-y-4">
              <p className="text-sm font-medium text-white/70">What's included:</p>
              {features.map((feature, i) => (
                <div key={i} className="flex items-center gap-3 text-sm">
                  {feature.free ? (
                    <Check className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  ) : (
                    <X className="w-4 h-4 text-white/20 flex-shrink-0" />
                  )}
                  <span className={feature.free ? 'text-white/70' : 'text-white/30'}>
                    {feature.name}
                    {typeof feature.free === 'string' && (
                      <span className="text-white/40 ml-1">({feature.free})</span>
                    )}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Pro Plan */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="relative bg-gradient-to-br from-violet-500/10 to-purple-500/10 border border-violet-500/30 rounded-2xl p-8"
          >
            {/* Popular Badge */}
            <div className="absolute -top-3 left-1/2 -translate-x-1/2">
              <div className="flex items-center gap-1.5 px-4 py-1.5 rounded-full bg-violet-500 text-sm font-medium">
                <Crown className="w-4 h-4" />
                Most Popular
              </div>
            </div>

            <div className="mb-6">
              <h2 className="text-xl font-semibold mb-1">Pro</h2>
              <p className="text-white/50 text-sm">For serious content creators</p>
            </div>

            <div className="mb-6">
              <span className="text-4xl font-bold">₹2,499</span>
              <span className="text-white/50 ml-2">/ month</span>
              <p className="text-sm text-violet-400 mt-1">14-day free trial included</p>
            </div>

            <button
              onClick={() => navigate('/signup')}
              className="w-full py-3 rounded-xl bg-violet-600 hover:bg-violet-500 font-medium transition-colors mb-8"
            >
              Start Free Trial
            </button>

            <div className="space-y-4">
              <p className="text-sm font-medium text-white/70">Everything in Free, plus:</p>
              {features.map((feature, i) => (
                <div key={i} className="flex items-center gap-3 text-sm">
                  <Check className="w-4 h-4 text-violet-400 flex-shrink-0" />
                  <span className="text-white/80">
                    {feature.name}
                    {typeof feature.pro === 'string' && feature.pro !== 'Unlimited' && (
                      <span className="text-white/50 ml-1">({feature.pro})</span>
                    )}
                    {feature.pro === 'Unlimited' && (
                      <span className="text-violet-400 ml-1">(Unlimited)</span>
                    )}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>

      {/* Features Comparison Table */}
      <div className="px-6 pb-20">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-12">Feature Comparison</h2>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-4 font-medium text-white/70">Feature</th>
                  <th className="text-center py-4 font-medium text-white/70 w-32">Free</th>
                  <th className="text-center py-4 font-medium text-violet-400 w-32">Pro</th>
                </tr>
              </thead>
              <tbody>
                {features.map((feature, i) => (
                  <tr key={i} className="border-b border-white/5">
                    <td className="py-4 text-white/80">{feature.name}</td>
                    <td className="py-4 text-center">
                      {typeof feature.free === 'string' ? (
                        <span className="text-white/60 text-sm">{feature.free}</span>
                      ) : feature.free ? (
                        <Check className="w-5 h-5 text-emerald-400 mx-auto" />
                      ) : (
                        <X className="w-5 h-5 text-white/20 mx-auto" />
                      )}
                    </td>
                    <td className="py-4 text-center">
                      {typeof feature.pro === 'string' ? (
                        <span className="text-violet-400 text-sm font-medium">{feature.pro}</span>
                      ) : (
                        <Check className="w-5 h-5 text-violet-400 mx-auto" />
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Payment Methods */}
      <div className="px-6 pb-20">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-2xl font-bold mb-4">Secure Payment Methods</h2>
          <p className="text-white/60 mb-8">Pay securely with your preferred method</p>
          
          <div className="flex items-center justify-center gap-6 flex-wrap">
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 border border-white/10">
              <img src="https://upload.wikimedia.org/wikipedia/commons/7/71/PhonePe_Logo.svg" alt="PhonePe" className="h-6 w-auto" />
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white/70">
              UPI
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white/70">
              Visa / Mastercard
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white/70">
              Net Banking
            </div>
          </div>
          
          <p className="text-white/40 text-sm mt-6">
            All transactions are encrypted and secure. We never store your payment details.
          </p>
        </div>
      </div>

      {/* FAQ */}
      <div className="px-6 pb-20">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-2xl font-bold mb-4">Frequently Asked Questions</h2>
            <p className="text-white/60">Everything you need to know about our pricing</p>
          </div>

          <div className="space-y-4">
            {faqs.map((faq, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * i }}
                className="bg-white/[0.02] border border-white/[0.06] rounded-xl p-6"
              >
                <div className="flex items-start gap-4">
                  <HelpCircle className="w-5 h-5 text-violet-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-medium mb-2">{faq.question}</h3>
                    <p className="text-white/60 text-sm leading-relaxed">{faq.answer}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA */}
      <div className="px-6 pb-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-3xl mx-auto text-center bg-gradient-to-br from-violet-500/20 to-purple-500/20 border border-violet-500/30 rounded-2xl p-12"
        >
          <h2 className="text-3xl font-bold mb-4">Ready to create viral content?</h2>
          <p className="text-white/60 mb-8">
            Start your 14-day free trial today. No credit card required.
          </p>
          <div className="flex items-center justify-center gap-4">
            <button
              onClick={() => navigate('/signup')}
              className="px-8 py-3 rounded-xl bg-violet-600 hover:bg-violet-500 font-medium transition-colors"
            >
              Start Free Trial
            </button>
            <Link
              to="/contact"
              className="px-8 py-3 rounded-xl bg-white/10 hover:bg-white/15 border border-white/10 font-medium transition-colors"
            >
              Contact Sales
            </Link>
          </div>
        </motion.div>
      </div>

      {/* Footer */}
      <footer className="border-t border-white/5 py-8">
        <div className="max-w-5xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-white/40">
          <div className="flex items-center gap-4">
            <Link to="/terms" className="hover:text-white transition-colors">Terms of Service</Link>
            <span>·</span>
            <Link to="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link>
            <span>·</span>
            <Link to="/refund" className="hover:text-white transition-colors">Refund Policy</Link>
          </div>
          <div>© 2024 ViralLab. All rights reserved.</div>
        </div>
      </footer>
    </div>
  );
}
