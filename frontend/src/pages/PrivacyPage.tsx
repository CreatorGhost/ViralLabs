import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Sparkles, ArrowLeft } from 'lucide-react';

export default function PrivacyPage() {
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
          <h1 className="text-4xl font-bold mb-2">Privacy Policy</h1>
          <p className="text-white/50 mb-12">Last updated: December 11, 2024</p>

          <div className="prose prose-invert prose-violet max-w-none space-y-8">
            {/* Introduction */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">1. Introduction</h2>
              <p className="text-white/70 leading-relaxed">
                ViralLab ("we", "our", or "us") is committed to protecting your privacy. This Privacy Policy explains 
                how we collect, use, disclose, and safeguard your information when you visit our website virallab.arkyon.dev 
                and use our services.
              </p>
              <p className="text-white/70 leading-relaxed mt-4">
                Please read this privacy policy carefully. If you do not agree with the terms of this privacy policy, 
                please do not access the site or use our services.
              </p>
            </section>

            {/* Information We Collect */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">2. Information We Collect</h2>
              
              <h3 className="text-lg font-medium text-white/90 mt-6 mb-3">Personal Data</h3>
              <p className="text-white/70 leading-relaxed">
                We may collect personally identifiable information that you voluntarily provide to us when you:
              </p>
              <ul className="list-disc list-inside text-white/70 space-y-2 mt-4">
                <li>Register for an account</li>
                <li>Subscribe to our services</li>
                <li>Make a purchase</li>
                <li>Contact us with inquiries</li>
                <li>Participate in surveys or promotions</li>
              </ul>
              <p className="text-white/70 leading-relaxed mt-4">
                This information may include:
              </p>
              <ul className="list-disc list-inside text-white/70 space-y-2 mt-4">
                <li>Name and email address</li>
                <li>Phone number</li>
                <li>Billing and payment information</li>
                <li>Profile information (including uploaded photos)</li>
              </ul>

              <h3 className="text-lg font-medium text-white/90 mt-6 mb-3">Usage Data</h3>
              <p className="text-white/70 leading-relaxed">
                We automatically collect certain information when you visit, use, or navigate our services. This includes:
              </p>
              <ul className="list-disc list-inside text-white/70 space-y-2 mt-4">
                <li>IP address and browser type</li>
                <li>Device information</li>
                <li>Pages visited and time spent</li>
                <li>Referring website addresses</li>
                <li>Actions taken on our platform</li>
              </ul>
            </section>

            {/* How We Use Your Information */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">3. How We Use Your Information</h2>
              <p className="text-white/70 leading-relaxed mb-4">
                We use the information we collect for various purposes, including to:
              </p>
              <ul className="list-disc list-inside text-white/70 space-y-2">
                <li>Provide, operate, and maintain our services</li>
                <li>Process your transactions and send related information</li>
                <li>Send you technical notices, updates, and support messages</li>
                <li>Respond to your comments, questions, and customer service requests</li>
                <li>Communicate with you about products, services, and events</li>
                <li>Monitor and analyze trends, usage, and activities</li>
                <li>Detect, investigate, and prevent fraudulent transactions</li>
                <li>Personalize and improve your experience</li>
              </ul>
            </section>

            {/* AI-Generated Content */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">4. AI-Generated Content & Your Data</h2>
              <p className="text-white/70 leading-relaxed">
                Our service uses artificial intelligence to generate content including scripts, thumbnails, and audio. 
                When you use these features:
              </p>
              <ul className="list-disc list-inside text-white/70 space-y-2 mt-4">
                <li>Your input prompts and preferences are processed to generate content</li>
                <li>Uploaded face images are used solely for the purpose of generating thumbnails with your likeness</li>
                <li>We do not use your uploaded images to train our AI models without explicit consent</li>
                <li>Generated content is stored in your account and can be deleted at any time</li>
              </ul>
            </section>

            {/* Payment Information */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">5. Payment Information</h2>
              <p className="text-white/70 leading-relaxed">
                We use third-party payment processors (including PhonePe, UPI, and card networks) to process payments. 
                We do not store your complete payment card details on our servers. Payment information is:
              </p>
              <ul className="list-disc list-inside text-white/70 space-y-2 mt-4">
                <li>Transmitted directly to our payment processor via secure, encrypted connections</li>
                <li>Processed in compliance with Payment Card Industry Data Security Standards (PCI-DSS)</li>
                <li>Protected by our payment partners' security measures</li>
              </ul>
            </section>

            {/* Data Sharing */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">6. Sharing Your Information</h2>
              <p className="text-white/70 leading-relaxed mb-4">
                We may share your information in the following situations:
              </p>
              <ul className="list-disc list-inside text-white/70 space-y-2">
                <li><strong className="text-white/90">Service Providers:</strong> With third parties who perform services for us (payment processing, data analysis, email delivery)</li>
                <li><strong className="text-white/90">Business Transfers:</strong> In connection with any merger, sale of company assets, or acquisition</li>
                <li><strong className="text-white/90">Legal Requirements:</strong> When required by law or to respond to legal process</li>
                <li><strong className="text-white/90">Protection:</strong> To protect the rights, property, or safety of ViralLab, our users, or others</li>
              </ul>
              <p className="text-white/70 leading-relaxed mt-4">
                We do not sell, rent, or trade your personal information to third parties for their marketing purposes.
              </p>
            </section>

            {/* Data Storage */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">7. Data Storage & Security</h2>
              <p className="text-white/70 leading-relaxed">
                Your data is stored on secure cloud servers. We implement appropriate technical and organizational security 
                measures to protect your personal information, including:
              </p>
              <ul className="list-disc list-inside text-white/70 space-y-2 mt-4">
                <li>Encryption of data in transit and at rest</li>
                <li>Regular security assessments</li>
                <li>Access controls and authentication</li>
                <li>Secure coding practices</li>
              </ul>
              <p className="text-white/70 leading-relaxed mt-4">
                However, no method of transmission over the Internet or electronic storage is 100% secure. While we strive 
                to use commercially acceptable means to protect your personal information, we cannot guarantee absolute security.
              </p>
            </section>

            {/* Data Retention */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">8. Data Retention</h2>
              <p className="text-white/70 leading-relaxed">
                We retain your personal information only for as long as necessary to fulfill the purposes outlined in this 
                Privacy Policy, unless a longer retention period is required or permitted by law.
              </p>
              <p className="text-white/70 leading-relaxed mt-4">
                When you delete your account, we will delete or anonymize your personal information within 30 days, except 
                for data we are required to retain for legal, accounting, or compliance purposes.
              </p>
            </section>

            {/* Your Rights */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">9. Your Rights</h2>
              <p className="text-white/70 leading-relaxed mb-4">
                Depending on your location, you may have certain rights regarding your personal information:
              </p>
              <ul className="list-disc list-inside text-white/70 space-y-2">
                <li><strong className="text-white/90">Access:</strong> Request a copy of your personal data</li>
                <li><strong className="text-white/90">Correction:</strong> Request correction of inaccurate data</li>
                <li><strong className="text-white/90">Deletion:</strong> Request deletion of your personal data</li>
                <li><strong className="text-white/90">Portability:</strong> Request transfer of your data to another service</li>
                <li><strong className="text-white/90">Objection:</strong> Object to processing of your personal data</li>
                <li><strong className="text-white/90">Withdrawal:</strong> Withdraw consent where we rely on consent to process your data</li>
              </ul>
              <p className="text-white/70 leading-relaxed mt-4">
                To exercise these rights, please contact us at <a href="mailto:privacy@arkyon.dev" className="text-violet-400 hover:underline">privacy@arkyon.dev</a>.
              </p>
            </section>

            {/* Cookies */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">10. Cookies & Tracking Technologies</h2>
              <p className="text-white/70 leading-relaxed">
                We use cookies and similar tracking technologies to track activity on our Service and hold certain information. 
                Cookies are files with a small amount of data that may include an anonymous unique identifier.
              </p>
              <p className="text-white/70 leading-relaxed mt-4">
                You can instruct your browser to refuse all cookies or to indicate when a cookie is being sent. However, 
                if you do not accept cookies, you may not be able to use some portions of our Service.
              </p>
            </section>

            {/* Children's Privacy */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">11. Children's Privacy</h2>
              <p className="text-white/70 leading-relaxed">
                Our Service is not intended for use by children under the age of 18. We do not knowingly collect personally 
                identifiable information from children under 18. If you become aware that a child has provided us with 
                personal data, please contact us immediately.
              </p>
            </section>

            {/* Changes */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">12. Changes to This Privacy Policy</h2>
              <p className="text-white/70 leading-relaxed">
                We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new 
                Privacy Policy on this page and updating the "Last updated" date.
              </p>
              <p className="text-white/70 leading-relaxed mt-4">
                You are advised to review this Privacy Policy periodically for any changes. Changes to this Privacy Policy 
                are effective when they are posted on this page.
              </p>
            </section>

            {/* Contact */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">13. Contact Us</h2>
              <p className="text-white/70 leading-relaxed">
                If you have any questions about this Privacy Policy, please contact us:
              </p>
              <ul className="mt-4 text-white/70 space-y-2">
                <li>By email: <a href="mailto:privacy@arkyon.dev" className="text-violet-400 hover:underline">privacy@arkyon.dev</a></li>
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
            <Link to="/terms" className="hover:text-white transition-colors">Terms of Service</Link>
            <span>·</span>
            <Link to="/refund" className="hover:text-white transition-colors">Refund Policy</Link>
          </div>
          <div>© 2024 ViralLab. All rights reserved.</div>
        </div>
      </footer>
    </div>
  );
}
