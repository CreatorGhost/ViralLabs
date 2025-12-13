import React from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Sparkles, 
  ArrowLeft, 
  Target,
  Heart,
  Rocket,
  Users,
  Globe,
  Award,
  ArrowRight
} from 'lucide-react';

export default function AboutPage() {
  const navigate = useNavigate();

  const values = [
    {
      icon: Target,
      title: 'Creator-First',
      description: 'Everything we build is designed with content creators in mind. We understand the challenges of growing a YouTube channel.',
    },
    {
      icon: Heart,
      title: 'Simplicity',
      description: 'Powerful AI shouldn\'t be complicated. We make advanced technology accessible to everyone, regardless of technical skill.',
    },
    {
      icon: Rocket,
      title: 'Innovation',
      description: 'We\'re constantly pushing the boundaries of what AI can do for content creation, staying ahead of the curve.',
    },
    {
      icon: Users,
      title: 'Community',
      description: 'We\'re building more than a tool – we\'re building a community of creators who support and inspire each other.',
    },
  ];

  const stats = [
    { value: '10,000+', label: 'Creators' },
    { value: '500K+', label: 'Scripts Generated' },
    { value: '1M+', label: 'Thumbnails Created' },
    { value: '99.9%', label: 'Uptime' },
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
        <Link 
          to="/"
          className="flex items-center gap-2 text-sm text-white/70 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Home
        </Link>
      </nav>

      {/* Hero */}
      <div className="pt-32 pb-20 px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center max-w-3xl mx-auto"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-violet-500/10 border border-violet-500/20 text-sm text-violet-300 mb-6">
            <Globe className="w-4 h-4" />
            Our Story
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-6">
            Empowering creators to go viral
          </h1>
          <p className="text-xl text-white/60 leading-relaxed">
            We're on a mission to democratize content creation by giving every creator access 
            to the same AI-powered tools that the biggest YouTube channels use.
          </p>
        </motion.div>
      </div>

      {/* Stats */}
      <div className="px-6 pb-20">
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {stats.map((stat, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * i }}
                className="text-center p-6 rounded-2xl bg-white/[0.02] border border-white/[0.06]"
              >
                <div className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-purple-400 mb-1">
                  {stat.value}
                </div>
                <div className="text-sm text-white/50">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Story Section */}
      <div className="px-6 pb-20">
        <div className="max-w-3xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="bg-white/[0.02] border border-white/[0.06] rounded-2xl p-8 md:p-12"
          >
            <h2 className="text-2xl font-bold mb-6">The Story Behind ViralLab</h2>
            
            <div className="space-y-6 text-white/70 leading-relaxed">
              <p>
                ViralLab was born out of frustration. As content creators ourselves, we spent countless 
                hours writing scripts, designing thumbnails, and trying to figure out what makes content 
                go viral. We knew there had to be a better way.
              </p>
              
              <p>
                In 2024, we set out to build the tool we wished existed – an AI-powered platform that 
                could analyze successful content, generate engaging scripts, create eye-catching thumbnails, 
                and produce professional voiceovers, all in one place.
              </p>
              
              <p>
                Today, ViralLab helps thousands of creators around the world produce more content in less 
                time, without sacrificing quality. Whether you're just starting out or you're an established 
                creator looking to scale, we're here to help you succeed.
              </p>
              
              <p>
                We're based in Bangalore, India, and we're proud to be building for the global creator 
                economy from right here.
              </p>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Values */}
      <div className="px-6 pb-20">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-2xl font-bold mb-4">Our Values</h2>
            <p className="text-white/60">The principles that guide everything we do</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {values.map((value, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 * i }}
                className="bg-white/[0.02] border border-white/[0.06] rounded-2xl p-8 hover:border-violet-500/30 transition-colors"
              >
                <div className="w-12 h-12 rounded-xl bg-violet-500/20 flex items-center justify-center mb-4">
                  <value.icon className="w-6 h-6 text-violet-400" />
                </div>
                <h3 className="text-xl font-semibold mb-2">{value.title}</h3>
                <p className="text-white/60 leading-relaxed">{value.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Team Section */}
      <div className="px-6 pb-20">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-2xl font-bold mb-4">Meet the Team</h2>
            <p className="text-white/60">The people behind ViralLab</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { name: 'Aditya Singh', role: 'Founder & CEO', image: null },
              { name: 'Coming Soon', role: 'CTO', image: null },
              { name: 'Coming Soon', role: 'Head of Product', image: null },
            ].map((member, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 * i }}
                className="text-center"
              >
                <div className="w-24 h-24 mx-auto mb-4 rounded-full bg-gradient-to-br from-violet-500/20 to-purple-500/20 border border-white/10 flex items-center justify-center">
                  {member.image ? (
                    <img src={member.image} alt={member.name} className="w-full h-full rounded-full object-cover" />
                  ) : (
                    <span className="text-2xl font-bold text-white/30">{member.name.charAt(0)}</span>
                  )}
                </div>
                <h3 className="font-semibold">{member.name}</h3>
                <p className="text-sm text-white/50">{member.role}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Location */}
      <div className="px-6 pb-20">
        <div className="max-w-3xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="bg-gradient-to-br from-violet-500/10 to-purple-500/10 border border-violet-500/20 rounded-2xl p-8 md:p-12"
          >
            <div className="flex items-start gap-6">
              <div className="w-12 h-12 rounded-xl bg-violet-500/20 flex items-center justify-center flex-shrink-0">
                <Award className="w-6 h-6 text-violet-400" />
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2">Made in India 🇮🇳</h3>
                <p className="text-white/60 leading-relaxed mb-4">
                  ViralLab is proudly built in Bangalore, the startup capital of India. We're committed 
                  to building world-class products right here, serving creators globally.
                </p>
                <p className="text-white/70">
                  <strong>Office:</strong><br />
                  ViralLab<br />
                  Bangalore, Karnataka<br />
                  India
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* CTA */}
      <div className="px-6 pb-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-3xl mx-auto text-center"
        >
          <h2 className="text-3xl font-bold mb-4">Join us on this journey</h2>
          <p className="text-white/60 mb-8">
            We're always looking for talented people and passionate creators to join our community.
          </p>
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <button
              onClick={() => navigate('/signup')}
              className="px-8 py-3 rounded-xl bg-violet-600 hover:bg-violet-500 font-medium transition-colors flex items-center gap-2"
            >
              Start Creating <ArrowRight className="w-4 h-4" />
            </button>
            <Link
              to="/contact"
              className="px-8 py-3 rounded-xl bg-white/10 hover:bg-white/15 border border-white/10 font-medium transition-colors"
            >
              Get in Touch
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
            <Link to="/contact" className="hover:text-white transition-colors">Contact</Link>
          </div>
          <div>© 2024 ViralLab. All rights reserved.</div>
        </div>
      </footer>
    </div>
  );
}
