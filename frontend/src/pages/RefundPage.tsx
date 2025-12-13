import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Sparkles, ArrowLeft, CheckCircle2, XCircle, AlertCircle, Info } from 'lucide-react';

export default function RefundPage() {
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
        <Link 
          to="/"
          className="flex items-center gap-2 text-sm text-white/70 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Home
        </Link>
      </nav>

      {/* Content */}
      <div className="pt-32 pb-20 px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-3xl mx-auto"
        >
          <h1 className="text-4xl font-bold mb-2">Refund & Cancellation Policy</h1>
          <p className="text-white/50 mb-12">Last updated: December 11, 2024</p>

          {/* Quick Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
              <CheckCircle2 className="w-6 h-6 text-emerald-400 mb-2" />
              <h3 className="font-semibold text-white mb-1">14-Day Free Trial</h3>
              <p className="text-sm text-white/60">Try before you pay</p>
            </div>
            <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20">
              <AlertCircle className="w-6 h-6 text-amber-400 mb-2" />
              <h3 className="font-semibold text-white mb-1">No Refunds</h3>
              <p className="text-sm text-white/60">All payments are final</p>
            </div>
            <div className="p-4 rounded-xl bg-violet-500/10 border border-violet-500/20">
              <XCircle className="w-6 h-6 text-violet-400 mb-2" />
              <h3 className="font-semibold text-white mb-1">Cancel Anytime</h3>
              <p className="text-sm text-white/60">Stop future charges</p>
            </div>
          </div>

          {/* Important Notice */}
          <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-6 mb-12">
            <div className="flex items-start gap-4">
              <Info className="w-6 h-6 text-amber-400 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-amber-400 mb-2">Important: No Refund Policy</h3>
                <p className="text-white/70 leading-relaxed">
                  ViralLab operates on a <strong className="text-white">strict no-refund policy</strong> for all subscription payments. 
                  We provide a generous <strong className="text-white">14-day free trial</strong> so you can fully evaluate our service 
                  before making any payment. Please use this trial period to ensure ViralLab meets your needs.
                </p>
              </div>
            </div>
          </div>

          <div className="prose prose-invert prose-violet max-w-none space-y-8">
            {/* Overview */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">1. Overview</h2>
              <p className="text-white/70 leading-relaxed">
                ViralLab is a digital service that provides AI-powered content creation tools. Due to the nature of 
                digital services and the immediate access provided upon subscription, all payments made to ViralLab 
                are <strong className="text-white">final and non-refundable</strong>.
              </p>
            </section>

            {/* Free Trial */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">2. Free Trial Period</h2>
              <p className="text-white/70 leading-relaxed">
                We offer a <strong className="text-white">14-day free trial</strong> for all new users. During the trial period:
              </p>
              <ul className="list-disc list-inside text-white/70 space-y-2 mt-4">
                <li>You have <strong className="text-white">full access</strong> to all premium features</li>
                <li><strong className="text-white">No payment</strong> is charged during the trial</li>
                <li>You can <strong className="text-white">cancel at any time</strong> before the trial ends without any charge</li>
                <li>If you don't cancel, your subscription will automatically begin at the end of the trial</li>
              </ul>
              <p className="text-white/70 leading-relaxed mt-4">
                We strongly encourage you to thoroughly test all features during your free trial to ensure our 
                service meets your requirements before your subscription begins.
              </p>
            </section>

            {/* No Refund Policy */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">3. No Refund Policy</h2>
              <p className="text-white/70 leading-relaxed">
                Once your subscription payment is processed (after the free trial or upon renewal):
              </p>
              <ul className="list-disc list-inside text-white/70 space-y-2 mt-4">
                <li><strong className="text-white">No refunds</strong> will be provided under any circumstances</li>
                <li>This applies to monthly subscription fees</li>
                <li>Partial month refunds are not available</li>
                <li>Unused credits or features cannot be refunded</li>
              </ul>
              <p className="text-white/70 leading-relaxed mt-4">
                This policy exists because:
              </p>
              <ul className="list-disc list-inside text-white/70 space-y-2 mt-4">
                <li>Digital services are consumed immediately upon access</li>
                <li>We provide a generous free trial to evaluate the service</li>
                <li>AI generation costs are incurred in real-time</li>
              </ul>
            </section>

            {/* Cancellation Policy */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">4. Cancellation Policy</h2>
              <p className="text-white/70 leading-relaxed">
                While we do not offer refunds, you can <strong className="text-white">cancel your subscription at any time</strong>:
              </p>
              
              <h3 className="text-lg font-medium text-white/90 mt-6 mb-3">How to Cancel</h3>
              <ul className="list-disc list-inside text-white/70 space-y-2">
                <li>Through your account settings under "Subscription Management"</li>
                <li>By contacting our support team at <a href="mailto:support@arkyon.dev" className="text-violet-400 hover:underline">support@arkyon.dev</a></li>
              </ul>

              <h3 className="text-lg font-medium text-white/90 mt-6 mb-3">What Happens When You Cancel</h3>
              <ul className="list-disc list-inside text-white/70 space-y-2">
                <li>Your subscription remains <strong className="text-white">active until the end</strong> of your current billing period</li>
                <li>You will <strong className="text-white">not be charged</strong> for the next billing cycle</li>
                <li>You retain access to premium features until your subscription expires</li>
                <li>Your account and content are preserved (you can resubscribe anytime)</li>
              </ul>

              <h3 className="text-lg font-medium text-white/90 mt-6 mb-3">UPI AutoPay Mandate</h3>
              <p className="text-white/70 leading-relaxed">
                If you subscribed using UPI AutoPay, canceling your subscription will also revoke the autopay mandate. 
                No further automatic deductions will be made from your account.
              </p>
            </section>

            {/* Exceptions */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">5. Exceptional Circumstances</h2>
              <p className="text-white/70 leading-relaxed">
                In rare cases, we may consider exceptions to our no-refund policy at our sole discretion:
              </p>
              <ul className="list-disc list-inside text-white/70 space-y-2 mt-4">
                <li><strong className="text-white">Duplicate charges:</strong> If you were accidentally charged twice for the same period</li>
                <li><strong className="text-white">Technical errors:</strong> If a payment processing error occurred on our end</li>
                <li><strong className="text-white">Extended outage:</strong> If our service was unavailable for an extended period (more than 7 consecutive days)</li>
              </ul>
              <p className="text-white/70 leading-relaxed mt-4">
                To report any of these issues, contact us at <a href="mailto:billing@arkyon.dev" className="text-violet-400 hover:underline">billing@arkyon.dev</a> with 
                details and any relevant transaction information.
              </p>
            </section>

            {/* Before You Subscribe */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">6. Before You Subscribe</h2>
              <p className="text-white/70 leading-relaxed">
                To avoid any dissatisfaction, we recommend:
              </p>
              <ul className="list-disc list-inside text-white/70 space-y-2 mt-4">
                <li><strong className="text-white">Use the full 14-day trial</strong> to test all features</li>
                <li>Check that the service meets your specific requirements</li>
                <li>Review our <Link to="/terms" className="text-violet-400 hover:underline">Terms of Service</Link> and this policy</li>
                <li>Contact <a href="mailto:support@arkyon.dev" className="text-violet-400 hover:underline">support@arkyon.dev</a> if you have any questions before subscribing</li>
              </ul>
            </section>

            {/* Contact */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">7. Contact Us</h2>
              <p className="text-white/70 leading-relaxed">
                If you have any questions about this policy, please contact us:
              </p>
              <ul className="mt-4 text-white/70 space-y-2">
                <li>Billing inquiries: <a href="mailto:billing@arkyon.dev" className="text-violet-400 hover:underline">billing@arkyon.dev</a></li>
                <li>General support: <a href="mailto:support@arkyon.dev" className="text-violet-400 hover:underline">support@arkyon.dev</a></li>
                <li>Visit our <Link to="/contact" className="text-violet-400 hover:underline">Contact Page</Link></li>
              </ul>
            </section>
          </div>
        </motion.div>
      </div>

      {/* Footer */}
      <footer className="border-t border-white/5 py-8">
        <div className="max-w-3xl mx-auto px-6 flex items-center justify-between text-sm text-white/40">
          <div className="flex items-center gap-4">
            <Link to="/terms" className="hover:text-white transition-colors">Terms of Service</Link>
            <span>·</span>
            <Link to="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link>
          </div>
          <div>© 2024 ViralLab. All rights reserved.</div>
        </div>
      </footer>
    </div>
  );
}
