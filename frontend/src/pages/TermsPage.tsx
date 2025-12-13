import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Sparkles, ArrowLeft } from 'lucide-react';

export default function TermsPage() {
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
          <h1 className="text-4xl font-bold mb-2">Terms of Service</h1>
          <p className="text-white/50 mb-12">Last updated: December 11, 2024</p>

          <div className="prose prose-invert prose-violet max-w-none space-y-8">
            {/* Introduction */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">1. Introduction</h2>
              <p className="text-white/70 leading-relaxed">
                Welcome to ViralLab ("Company", "we", "our", "us"). These Terms of Service ("Terms", "Terms of Service") 
                govern your use of our website located at virallab.arkyon.dev (together or individually "Service") operated by ViralLab.
              </p>
              <p className="text-white/70 leading-relaxed mt-4">
                Our Privacy Policy also governs your use of our Service and explains how we collect, safeguard, and disclose 
                information that results from your use of our web pages.
              </p>
              <p className="text-white/70 leading-relaxed mt-4">
                Your agreement with us includes these Terms and our Privacy Policy ("Agreements"). You acknowledge that you 
                have read and understood Agreements, and agree to be bound by them.
              </p>
              <p className="text-white/70 leading-relaxed mt-4">
                If you do not agree with (or cannot comply with) Agreements, then you may not use the Service. These Terms 
                apply to all visitors, users, and others who wish to access or use the Service.
              </p>
            </section>

            {/* Communications */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">2. Communications</h2>
              <p className="text-white/70 leading-relaxed">
                By creating an Account on our Service, you agree to subscribe to newsletters, marketing or promotional 
                materials, and other information we may send. However, you may opt out of receiving any, or all, of these 
                communications from us by following the unsubscribe link or by emailing us at support@arkyon.dev.
              </p>
            </section>

            {/* Purchases */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">3. Purchases & Subscriptions</h2>
              <p className="text-white/70 leading-relaxed">
                If you wish to purchase any product or service made available through the Service ("Purchase"), you may be 
                asked to supply certain information relevant to your Purchase including, without limitation, your payment 
                details, billing address, and other relevant information.
              </p>
              <p className="text-white/70 leading-relaxed mt-4">
                You represent and warrant that: (i) you have the legal right to use any payment method(s) in connection 
                with any Purchase; and (ii) the information you supply to us is true, correct, and complete.
              </p>
              <p className="text-white/70 leading-relaxed mt-4">
                We reserve the right to refuse or cancel your order at any time for reasons including but not limited to: 
                product or service availability, errors in the description or price of the product or service, error in 
                your order, or other reasons.
              </p>
            </section>

            {/* Subscription Terms */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">4. Subscription Terms</h2>
              <p className="text-white/70 leading-relaxed">
                Some parts of the Service are billed on a subscription basis ("Subscription(s)"). You will be billed in 
                advance on a recurring and periodic basis ("Billing Cycle"). Billing cycles are set on a monthly basis.
              </p>
              <p className="text-white/70 leading-relaxed mt-4">
                At the end of each Billing Cycle, your Subscription will automatically renew under the exact same conditions 
                unless you cancel it or ViralLab cancels it. You may cancel your Subscription renewal either through your 
                online account management page or by contacting our customer support team.
              </p>
              <p className="text-white/70 leading-relaxed mt-4">
                A valid payment method, including UPI, credit card, or debit card, is required to process the payment for 
                your Subscription. You shall provide ViralLab with accurate and complete billing information.
              </p>
            </section>

            {/* Free Trial */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">5. Free Trial</h2>
              <p className="text-white/70 leading-relaxed">
                ViralLab may, at its sole discretion, offer a Subscription with a free trial for a limited period of time 
                ("Free Trial"). You may be required to enter your billing information in order to sign up for the Free Trial.
              </p>
              <p className="text-white/70 leading-relaxed mt-4">
                If you do enter your billing information when signing up for the Free Trial, you will not be charged by 
                ViralLab until the Free Trial has expired. On the last day of the Free Trial period, unless you cancelled 
                your Subscription, you will be automatically charged the applicable Subscription fees for the type of 
                Subscription you have selected.
              </p>
              <p className="text-white/70 leading-relaxed mt-4">
                At any time and without notice, ViralLab reserves the right to (i) modify the terms and conditions of the 
                Free Trial offer, or (ii) cancel such Free Trial offer.
              </p>
            </section>

            {/* Fee Changes */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">6. Fee Changes</h2>
              <p className="text-white/70 leading-relaxed">
                ViralLab, in its sole discretion and at any time, may modify the Subscription fees for the Subscriptions. 
                Any Subscription fee change will become effective at the end of the then-current Billing Cycle.
              </p>
              <p className="text-white/70 leading-relaxed mt-4">
                ViralLab will provide you with reasonable prior notice of any change in Subscription fees to give you an 
                opportunity to terminate your Subscription before such change becomes effective.
              </p>
              <p className="text-white/70 leading-relaxed mt-4">
                Your continued use of the Service after the Subscription fee change comes into effect constitutes your 
                agreement to pay the modified Subscription fee amount.
              </p>
            </section>

            {/* No Refunds */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">7. No Refund Policy</h2>
              <p className="text-white/70 leading-relaxed">
                All subscription payments are final and non-refundable. We provide a 14-day free trial so you can 
                fully evaluate our service before making any payment. By subscribing after the trial period, you 
                acknowledge and agree that no refunds will be provided. Please refer to our{' '}
                <Link to="/refund" className="text-violet-400 hover:underline">Refund Policy</Link> for detailed information.
              </p>
            </section>

            {/* Content */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">8. Content</h2>
              <p className="text-white/70 leading-relaxed">
                Our Service allows you to post, link, store, share, and otherwise make available certain information, 
                text, graphics, videos, or other material ("Content"). You are responsible for the Content that you post 
                on or through the Service, including its legality, reliability, and appropriateness.
              </p>
              <p className="text-white/70 leading-relaxed mt-4">
                By posting Content on or through the Service, you represent and warrant that: (i) the Content is yours 
                (you own it) and/or you have the right to use it and the right to grant us the rights and license as 
                provided in these Terms, and (ii) that the posting of your Content on or through the Service does not 
                violate the privacy rights, publicity rights, copyrights, contract rights, or any other rights of any person.
              </p>
            </section>

            {/* Prohibited Uses */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">9. Prohibited Uses</h2>
              <p className="text-white/70 leading-relaxed mb-4">
                You may use the Service only for lawful purposes and in accordance with Terms. You agree not to use the Service:
              </p>
              <ul className="list-disc list-inside text-white/70 space-y-2">
                <li>In any way that violates any applicable national or international law or regulation.</li>
                <li>For the purpose of exploiting, harming, or attempting to exploit or harm minors in any way.</li>
                <li>To transmit, or procure the sending of, any advertising or promotional material without our prior written consent.</li>
                <li>To impersonate or attempt to impersonate the Company, a Company employee, another user, or any other person or entity.</li>
                <li>In any way that infringes upon the rights of others, or in any way is illegal, threatening, fraudulent, or harmful.</li>
                <li>To engage in any other conduct that restricts or inhibits anyone's use or enjoyment of the Service.</li>
              </ul>
            </section>

            {/* Intellectual Property */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">10. Intellectual Property</h2>
              <p className="text-white/70 leading-relaxed">
                The Service and its original content (excluding Content provided by users), features, and functionality 
                are and will remain the exclusive property of ViralLab and its licensors. The Service is protected by 
                copyright, trademark, and other laws of both India and foreign countries. Our trademarks and trade dress 
                may not be used in connection with any product or service without the prior written consent of ViralLab.
              </p>
            </section>

            {/* Termination */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">11. Termination</h2>
              <p className="text-white/70 leading-relaxed">
                We may terminate or suspend your account and bar access to the Service immediately, without prior notice 
                or liability, under our sole discretion, for any reason whatsoever and without limitation, including but 
                not limited to a breach of Terms.
              </p>
              <p className="text-white/70 leading-relaxed mt-4">
                If you wish to terminate your account, you may simply discontinue using the Service or contact us to 
                delete your account.
              </p>
            </section>

            {/* Governing Law */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">12. Governing Law</h2>
              <p className="text-white/70 leading-relaxed">
                These Terms shall be governed and construed in accordance with the laws of India, without regard to its 
                conflict of law provisions. Any disputes arising from these Terms will be subject to the exclusive 
                jurisdiction of the courts in Bangalore, Karnataka, India.
              </p>
            </section>

            {/* Changes */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">13. Changes to Terms</h2>
              <p className="text-white/70 leading-relaxed">
                We reserve the right, at our sole discretion, to modify or replace these Terms at any time. If a revision 
                is material, we will provide at least 30 days' notice prior to any new terms taking effect. What constitutes 
                a material change will be determined at our sole discretion.
              </p>
              <p className="text-white/70 leading-relaxed mt-4">
                By continuing to access or use our Service after any revisions become effective, you agree to be bound by 
                the revised terms. If you do not agree to the new terms, you are no longer authorized to use the Service.
              </p>
            </section>

            {/* Grievance Redressal */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">14. Grievance Redressal</h2>
              <p className="text-white/70 leading-relaxed">
                In accordance with the Information Technology Act 2000 and Consumer Protection Act 2019, 
                we have appointed a Grievance Officer to address your concerns:
              </p>
              <div className="mt-4 p-4 rounded-lg bg-white/[0.03] border border-white/[0.08]">
                <p className="text-white/70"><strong className="text-white">Grievance Officer:</strong> Aditya Pratap Singh</p>
                <p className="text-white/70"><strong className="text-white">Email:</strong> <a href="mailto:grievance@arkyon.dev" className="text-violet-400 hover:underline">grievance@arkyon.dev</a></p>
                <p className="text-white/70 mt-2 text-sm">
                  Complaints will be acknowledged within 48 hours and resolved within 30 days of receipt.
                </p>
              </div>
            </section>

            {/* Contact */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">15. Contact Us</h2>
              <p className="text-white/70 leading-relaxed">
                If you have any questions about these Terms, please contact us:
              </p>
              <ul className="mt-4 text-white/70 space-y-2">
                <li>By email: <a href="mailto:support@arkyon.dev" className="text-violet-400 hover:underline">support@arkyon.dev</a></li>
                <li>By visiting our website: <Link to="/contact" className="text-violet-400 hover:underline">Contact Page</Link></li>
              </ul>
            </section>
          </div>
        </motion.div>
      </div>

      {/* Footer */}
      <footer className="border-t border-white/5 py-8">
        <div className="max-w-3xl mx-auto px-6 flex items-center justify-between text-sm text-white/40">
          <div className="flex items-center gap-4">
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
