import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { 
  Sparkles, 
  FileText, 
  Image, 
  Mic, 
  User, 
  Tag, 
  Zap, 
  Wand2,
  Play,
  Volume2,
  Palette,
  Brain,
  Clock,
  Shield,
  CheckCircle2,
  ArrowRight
} from 'lucide-react';

function App() {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-[#0B0C10] text-white overflow-x-hidden">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-8 py-4 bg-[#0B0C10]/80 backdrop-blur-xl border-b border-white/5">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-semibold tracking-tight">ViralLab</span>
        </div>
        <div className="hidden md:flex items-center gap-1 px-2 py-1.5 rounded-full bg-white/5 border border-white/10">
          <a href="#features" className="px-4 py-1.5 text-sm text-white/70 hover:text-white transition-colors">Product</a>
          <a href="#pricing" className="px-4 py-1.5 text-sm text-white/70 hover:text-white transition-colors">Pricing</a>
          <a href="#about" className="px-4 py-1.5 text-sm text-white/70 hover:text-white transition-colors">Company</a>
          <a href="#blog" className="px-4 py-1.5 text-sm text-white/70 hover:text-white transition-colors">Blog</a>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={() => navigate('/login')}
            className="text-sm text-white/70 hover:text-white transition-colors"
          >
            Login
          </button>
          <button 
            onClick={() => navigate('/signup')}
            className="px-4 py-2 text-sm font-medium rounded-lg bg-violet-600 hover:bg-violet-500 transition-colors"
          >
            Start free trial
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-6">
        {/* Aurora Background Effect */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-[10%] left-1/2 -translate-x-1/2 w-[800px] h-[600px]">
            {/* Black hole / Aurora effect */}
            <div className="absolute inset-0 bg-gradient-to-b from-violet-500/20 via-purple-500/10 to-transparent rounded-full blur-[100px]" />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] rounded-full bg-gradient-to-t from-violet-600/30 to-transparent blur-[60px]" />
            <div className="absolute top-[60%] left-1/2 -translate-x-1/2 w-[600px] h-[200px] bg-gradient-to-t from-violet-500/20 via-purple-400/10 to-transparent blur-[80px]" />
          </div>
        </div>

        <div className="relative z-10 max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-sm text-white/80 mb-8"
          >
            <Sparkles className="w-4 h-4 text-violet-400" />
            <span>AI-Powered Content Creation</span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-5xl md:text-7xl font-bold tracking-tight mb-6"
          >
            Create viral content<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-purple-400">with ViralLab</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-xl text-white/60 mb-10 max-w-2xl mx-auto"
          >
            Never miss a script, thumbnail or viral moment.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="flex items-center justify-center gap-4"
          >
            <button 
              onClick={() => navigate('/signup')}
              className="px-6 py-3 rounded-lg bg-violet-600 hover:bg-violet-500 font-medium transition-colors flex items-center gap-2"
            >
              Start Creating <ArrowRight className="w-4 h-4" />
            </button>
            <button className="px-6 py-3 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 font-medium transition-colors flex items-center gap-2">
              <Play className="w-4 h-4" /> Watch Demo
            </button>
          </motion.div>
        </div>

        {/* Hero Visual - Floating Result Cards */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.8 }}
          className="relative z-10 max-w-4xl mx-auto mt-16"
        >
          <div className="relative flex items-center justify-center gap-6 min-h-[300px]">
            {/* Left Card - Script */}
            <motion.div
              initial={{ opacity: 0, x: -50, rotate: -5 }}
              animate={{ opacity: 1, x: 0, rotate: -3 }}
              transition={{ delay: 0.6, duration: 0.8 }}
              className="absolute left-0 w-72"
            >
              <div className="p-6 rounded-2xl bg-gradient-to-br from-white/10 to-white/5 border border-white/10 backdrop-blur-xl shadow-2xl">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center">
                    <FileText className="w-5 h-5 text-violet-400" />
                  </div>
                  <span className="font-semibold text-white/90">Viral Script</span>
                </div>
                <div className="space-y-2">
                  <div className="h-2 bg-white/20 rounded-full w-full" />
                  <div className="h-2 bg-white/20 rounded-full w-5/6" />
                  <div className="h-2 bg-white/20 rounded-full w-4/5" />
                  <div className="h-2 bg-violet-500/40 rounded-full w-2/3 animate-pulse" />
                </div>
              </div>
            </motion.div>

            {/* Center Card - Thumbnail (Featured) */}
            <motion.div
              initial={{ opacity: 0, y: 20, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ delay: 0.7, duration: 0.8 }}
              className="relative z-10 w-80"
            >
              <div className="p-6 rounded-2xl bg-gradient-to-br from-violet-500/20 to-purple-500/20 border border-violet-500/30 backdrop-blur-xl shadow-2xl shadow-violet-500/20">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-white/20 flex items-center justify-center">
                    <Image className="w-5 h-5 text-white" />
                  </div>
                  <span className="font-semibold text-white">Eye-Catching Thumbnail</span>
                </div>
                <div className="aspect-video rounded-xl bg-gradient-to-br from-violet-600/30 to-purple-600/30 border border-white/10 flex items-center justify-center mb-3">
                  <Sparkles className="w-12 h-12 text-white/60" />
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="px-2 py-1 bg-white/10 rounded text-white/70">1920x1080</span>
                  <span className="text-white/50">With face integration</span>
                </div>
              </div>
            </motion.div>

            {/* Right Card - Audio */}
            <motion.div
              initial={{ opacity: 0, x: 50, rotate: 5 }}
              animate={{ opacity: 1, x: 0, rotate: 3 }}
              transition={{ delay: 0.8, duration: 0.8 }}
              className="absolute right-0 w-72"
            >
              <div className="p-6 rounded-2xl bg-gradient-to-br from-white/10 to-white/5 border border-white/10 backdrop-blur-xl shadow-2xl">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-cyan-500/20 flex items-center justify-center">
                    <Volume2 className="w-5 h-5 text-cyan-400" />
                  </div>
                  <span className="font-semibold text-white/90">Pro Voiceover</span>
                </div>
                <div className="flex items-end gap-1 h-16 mb-3">
                  {[...Array(16)].map((_, i) => (
                    <div
                      key={i}
                      className="flex-1 bg-cyan-500/40 rounded-sm animate-pulse"
                      style={{
                        height: `${30 + Math.random() * 70}%`,
                        animationDelay: `${i * 0.08}s`,
                      }}
                    />
                  ))}
                </div>
                <div className="flex items-center gap-2 text-xs text-white/60">
                  <Play className="w-3 h-3" />
                  <div className="flex-1 h-1 bg-white/20 rounded-full">
                    <div className="w-1/3 h-full bg-cyan-500 rounded-full" />
                  </div>
                  <span>0:45</span>
                </div>
              </div>
            </motion.div>
          </div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 px-6 relative overflow-hidden">
        {/* Ambient glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-violet-500/5 blur-[100px] rounded-full" />

        <div className="relative z-10 max-w-7xl mx-auto">
          {/* Grid Layout */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { 
                icon: FileText, 
                title: 'Script Generation', 
                desc: 'AI writes viral scripts from any topic or video',
                gradient: 'from-violet-500/10 to-purple-500/10'
              },
              { 
                icon: Image, 
                title: 'Thumbnail Studio', 
                desc: 'Eye-catching thumbnails with face integration',
                gradient: 'from-pink-500/10 to-rose-500/10'
              },
              { 
                icon: Volume2, 
                title: 'Neural Audio', 
                desc: 'Professional voiceovers with multiple voices',
                gradient: 'from-cyan-500/10 to-blue-500/10'
              },
              { 
                icon: User, 
                title: 'Face Cloning', 
                desc: 'Your face, perfectly placed in any scene',
                gradient: 'from-emerald-500/10 to-teal-500/10'
              },
              { 
                icon: Tag, 
                title: 'Smart Tags', 
                desc: 'Auto-generate SEO-optimized tags',
                gradient: 'from-orange-500/10 to-amber-500/10'
              },
              { 
                icon: FileText, 
                title: 'Descriptions', 
                desc: 'Compelling YouTube descriptions instantly',
                gradient: 'from-indigo-500/10 to-violet-500/10'
              },
              { 
                icon: Zap, 
                title: 'One-Click Workflow', 
                desc: 'From idea to content in seconds',
                gradient: 'from-yellow-500/10 to-orange-500/10'
              },
              { 
                icon: Clock, 
                title: 'Background Processing', 
                desc: 'Generate while you work on other things',
                gradient: 'from-purple-500/10 to-pink-500/10'
              },
            ].map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                className="group"
              >
                <div className={`relative h-full p-6 rounded-2xl bg-gradient-to-br ${feature.gradient} border border-white/[0.08] hover:border-white/20 transition-all duration-300 overflow-hidden`}>
                  {/* Hover glow */}
                  <div className="absolute inset-0 bg-gradient-to-t from-white/[0.05] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                  
                  <div className="relative z-10 flex flex-col h-full min-h-[200px]">
                    <div className="w-12 h-12 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center mb-4 group-hover:scale-110 group-hover:bg-white/20 transition-all duration-300">
                      <feature.icon className="w-6 h-6 text-white/80" strokeWidth={1.5} />
                    </div>
                    <h3 className="font-semibold text-white/95 mb-2 text-lg">{feature.title}</h3>
                    <p className="text-sm text-white/60 leading-relaxed">{feature.desc}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* AI Section */}
      <section className="py-24 px-6 relative">
        {/* Light beam effect */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-px h-40 bg-gradient-to-b from-transparent via-violet-500 to-violet-500/50" />
        <div className="absolute top-40 left-1/2 -translate-x-1/2 w-[400px] h-[300px] bg-violet-500/20 blur-[100px]" />

        <div className="relative z-10 max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-sm text-white/80 mb-8"
          >
            <Brain className="w-4 h-4 text-violet-400" />
            <span>ViralLab AI</span>
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-4xl md:text-5xl font-bold tracking-tight mb-6"
          >
            Content with an<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-purple-400">AI assistant</span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="text-lg text-white/60 mb-16 max-w-2xl mx-auto"
          >
            ViralLab uses GPT-4 and Gemini to analyze viral videos, generate scripts, and create thumbnails that get clicks.
          </motion.p>

          {/* AI Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { icon: Mic, title: 'Generate voiceovers', desc: 'with studio-quality voices' },
              { icon: Wand2, title: 'Create thumbnails', desc: 'from text descriptions' },
              { icon: FileText, title: 'Write viral scripts', desc: 'optimized for engagement' },
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.3 + i * 0.1 }}
                className="text-center"
              >
                <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center">
                  <item.icon className="w-5 h-5 text-white/60" />
                </div>
                <h3 className="font-medium mb-1">{item.title}</h3>
                <p className="text-sm text-white/50">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* What can you do section */}
      <section className="relative py-32 px-6 overflow-hidden">
        {/* Light beams from top */}
        <div className="absolute top-0 left-1/3 w-px h-32 bg-gradient-to-b from-violet-500/50 to-transparent" />
        <div className="absolute top-0 right-1/3 w-px h-32 bg-gradient-to-b from-violet-500/50 to-transparent" />

        {/* 3D Perspective Grid */}
        <div className="absolute inset-0 flex items-center justify-center" style={{ perspective: '1000px' }}>
          <div 
            className="absolute w-full h-64 opacity-20"
            style={{
              background: 'linear-gradient(transparent 0%, transparent 45%, rgba(139, 92, 246, 0.15) 50%, transparent 55%, transparent 100%), linear-gradient(90deg, transparent 0%, transparent 45%, rgba(139, 92, 246, 0.15) 50%, transparent 55%, transparent 100%)',
              backgroundSize: '80px 80px',
              transform: 'rotateX(60deg) translateY(-100px)',
            }}
          />
        </div>

        {/* Content Creation Flow Visualization */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="relative z-10 max-w-4xl mx-auto mb-20"
        >
          {/* Central AI Core */}
          <div className="relative flex items-center justify-center mb-12">
            {/* Pulsing core */}
            <div className="relative">
              <div className="absolute inset-0 animate-pulse">
                <div className="w-24 h-24 rounded-full bg-gradient-to-br from-violet-500/30 to-purple-500/30 blur-2xl" />
              </div>
              <div className="relative w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-600 to-purple-600 flex items-center justify-center shadow-2xl shadow-violet-500/50">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
            </div>
          </div>

          {/* Floating Content Cards */}
          <div className="relative grid grid-cols-3 gap-6">
            {/* Script Card */}
            <motion.div
              initial={{ opacity: 0, x: -20, y: 20 }}
              whileInView={{ opacity: 1, x: 0, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2, duration: 0.6 }}
              className="relative"
            >
              <div className="p-4 rounded-xl bg-white/[0.03] backdrop-blur-sm border border-white/[0.08] shadow-xl">
                <div className="w-8 h-8 rounded-lg bg-violet-500/20 flex items-center justify-center mb-3">
                  <FileText className="w-4 h-4 text-violet-400" />
                </div>
                <div className="space-y-1.5">
                  <div className="h-2 w-full bg-white/10 rounded" />
                  <div className="h-2 w-4/5 bg-white/10 rounded" />
                  <div className="h-2 w-3/5 bg-white/10 rounded" />
                </div>
                <div className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-emerald-500 flex items-center justify-center">
                  <CheckCircle2 className="w-3 h-3 text-white" />
                </div>
              </div>
              {/* Connection line */}
              <div className="absolute top-1/2 -right-3 w-6 h-px bg-gradient-to-r from-violet-500/50 to-transparent" />
            </motion.div>

            {/* Thumbnail Card */}
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3, duration: 0.6 }}
              className="relative"
            >
              <div className="p-4 rounded-xl bg-white/[0.03] backdrop-blur-sm border border-white/[0.08] shadow-xl">
                <div className="aspect-video rounded-lg bg-gradient-to-br from-violet-500/30 to-purple-500/30 mb-3 flex items-center justify-center border border-white/[0.05]">
                  <Image className="w-8 h-8 text-white/60" />
                </div>
                <div className="flex gap-1.5">
                  <div className="h-1.5 flex-1 bg-white/10 rounded" />
                  <div className="h-1.5 flex-1 bg-white/10 rounded" />
                </div>
              </div>
              {/* Connection line */}
              <div className="absolute top-1/2 -right-3 w-6 h-px bg-gradient-to-r from-violet-500/50 to-transparent" />
            </motion.div>

            {/* Audio Card */}
            <motion.div
              initial={{ opacity: 0, x: 20, y: 20 }}
              whileInView={{ opacity: 1, x: 0, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4, duration: 0.6 }}
              className="relative"
            >
              <div className="p-4 rounded-xl bg-white/[0.03] backdrop-blur-sm border border-white/[0.08] shadow-xl">
                <div className="w-8 h-8 rounded-lg bg-violet-500/20 flex items-center justify-center mb-3">
                  <Volume2 className="w-4 h-4 text-violet-400" />
                </div>
                <div className="flex items-end gap-0.5 h-12">
                  {[...Array(12)].map((_, i) => (
                    <div
                      key={i}
                      className="flex-1 bg-white/20 rounded-sm animate-pulse"
                      style={{
                        height: `${Math.random() * 100}%`,
                        animationDelay: `${i * 0.1}s`,
                      }}
                    />
                  ))}
                </div>
              </div>
            </motion.div>
          </div>

          {/* Ambient glow */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[300px] bg-gradient-to-br from-violet-600/20 via-purple-500/10 to-transparent blur-3xl pointer-events-none" />
        </motion.div>

        {/* Heading */}
        <div className="relative z-10 max-w-4xl mx-auto text-center mb-16">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-4xl md:text-5xl font-bold tracking-tight mb-4"
          >
            What can you do with ViralLab?
          </motion.h2>
        </div>

        {/* Cards Grid */}
        <div className="relative z-10 max-w-5xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-px bg-white/[0.03] rounded-2xl overflow-hidden border border-white/[0.05] mb-6">
            {[
              { icon: FileText, title: 'Analyze viral videos', desc: 'to understand what works' },
              { icon: Palette, title: 'Generate thumbnails', desc: 'with your face integrated' },
              { icon: Volume2, title: 'Create audio', desc: 'for your entire script' },
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="relative p-8 bg-[#0B0C10] hover:bg-white/[0.02] transition-all duration-300 group cursor-default overflow-hidden"
              >
                {/* Bottom glow */}
                <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none">
                  <div className="absolute inset-x-0 bottom-0 h-full bg-gradient-to-t from-violet-500/[0.08] via-violet-500/[0.02] to-transparent" />
                </div>
                
                <div className="relative flex flex-col items-center text-center space-y-4">
                  <div className="w-12 h-12 rounded-xl bg-white/[0.03] border border-white/[0.05] flex items-center justify-center group-hover:border-violet-500/30 group-hover:bg-white/[0.05] transition-all duration-300">
                    <item.icon className="w-5 h-5 text-white/50 group-hover:text-violet-400 transition-colors duration-300" strokeWidth={1.5} />
                  </div>
                  <div className="space-y-1.5">
                    <h3 className="font-semibold text-[15px] text-white/90 leading-tight">{item.title}</h3>
                    <p className="text-[13px] text-white/40 leading-relaxed">{item.desc}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-px bg-white/[0.03] rounded-2xl overflow-hidden border border-white/[0.05] max-w-3xl mx-auto">
            {[
              { icon: Tag, title: 'Auto-generate tags', desc: 'and SEO descriptions' },
              { icon: Zap, title: 'One-click workflow', desc: 'from idea to publish-ready' },
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.3 + i * 0.1 }}
                className="relative p-8 bg-[#0B0C10] hover:bg-white/[0.02] transition-all duration-300 group cursor-default overflow-hidden"
              >
                {/* Bottom glow */}
                <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none">
                  <div className="absolute inset-x-0 bottom-0 h-full bg-gradient-to-t from-violet-500/[0.08] via-violet-500/[0.02] to-transparent" />
                </div>
                
                <div className="relative flex flex-col items-center text-center space-y-4">
                  <div className="w-12 h-12 rounded-xl bg-white/[0.03] border border-white/[0.05] flex items-center justify-center group-hover:border-violet-500/30 group-hover:bg-white/[0.05] transition-all duration-300">
                    <item.icon className="w-5 h-5 text-white/50 group-hover:text-violet-400 transition-colors duration-300" strokeWidth={1.5} />
                  </div>
                  <div className="space-y-1.5">
                    <h3 className="font-semibold text-[15px] text-white/90 leading-tight">{item.title}</h3>
                    <p className="text-[13px] text-white/40 leading-relaxed">{item.desc}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Workflow Section */}
      <section className="py-32 px-6 relative overflow-hidden">
        {/* Ambient background */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-to-br from-violet-600/10 via-purple-500/5 to-transparent blur-[120px]" />

        <div className="relative z-10 max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-20">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/[0.03] border border-white/[0.08] text-sm text-white/80 mb-8"
            >
              All your content, connected
            </motion.div>

            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="text-4xl md:text-5xl font-bold tracking-tight mb-6"
            >
              Give your channel<br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-purple-400">superpowers</span>
            </motion.h2>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="text-lg text-white/50 max-w-2xl mx-auto"
            >
              Mirror the way viral creators work. ViralLab becomes your second brain for content creation.
            </motion.p>
          </div>

          {/* Central Hub Visualization */}
          <div className="relative h-[600px] flex items-center justify-center">
            {/* Central Orb */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="relative z-20"
            >
              {/* Pulse rings */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="absolute w-32 h-32 rounded-full border border-violet-500/20 animate-ping" style={{ animationDuration: '3s' }} />
                <div className="absolute w-40 h-40 rounded-full border border-violet-500/10 animate-ping" style={{ animationDuration: '4s' }} />
              </div>
              
              {/* Core sphere */}
              <div className="relative w-24 h-24 rounded-full bg-gradient-to-br from-violet-600 to-purple-600 flex items-center justify-center shadow-2xl shadow-violet-500/50">
                <div className="absolute inset-0 rounded-full bg-violet-400/50 blur-xl animate-pulse" />
                <Brain className="w-12 h-12 text-white relative z-10" />
              </div>
            </motion.div>

            {/* Connection Lines & Cards */}
            {/* Top Left - Script */}
            <motion.div
              initial={{ opacity: 0, x: 50, y: 50 }}
              whileInView={{ opacity: 1, x: 0, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3, duration: 0.6 }}
              className="absolute top-8 left-8 md:left-16"
            >
              {/* Connection line */}
              <svg className="absolute top-1/2 left-full w-32 h-32 pointer-events-none" style={{ transform: 'translate(20px, -50%)' }}>
                <line x1="0" y1="64" x2="128" y2="64" stroke="rgba(139, 92, 246, 0.2)" strokeWidth="1" />
              </svg>
              
              <div className="w-64 p-6 rounded-xl bg-[#0B0C10] border border-white/[0.08] backdrop-blur-sm hover:border-violet-500/30 transition-all duration-300 group">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center">
                    <FileText className="w-5 h-5 text-violet-400" />
                  </div>
                  <h3 className="font-semibold text-white/90">Script Generation</h3>
                </div>
                <p className="text-sm text-white/50 leading-relaxed">
                  Analyze viral videos and generate optimized scripts
                </p>
              </div>
            </motion.div>

            {/* Top Right - Thumbnails */}
            <motion.div
              initial={{ opacity: 0, x: -50, y: 50 }}
              whileInView={{ opacity: 1, x: 0, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4, duration: 0.6 }}
              className="absolute top-8 right-8 md:right-16"
            >
              {/* Connection line */}
              <svg className="absolute top-1/2 right-full w-32 h-32 pointer-events-none" style={{ transform: 'translate(-20px, -50%)' }}>
                <line x1="0" y1="64" x2="128" y2="64" stroke="rgba(139, 92, 246, 0.2)" strokeWidth="1" />
              </svg>
              
              <div className="w-64 p-6 rounded-xl bg-[#0B0C10] border border-white/[0.08] backdrop-blur-sm hover:border-violet-500/30 transition-all duration-300 group">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center">
                    <Image className="w-5 h-5 text-violet-400" />
                  </div>
                  <h3 className="font-semibold text-white/90">Thumbnail Studio</h3>
                </div>
                <p className="text-sm text-white/50 leading-relaxed">
                  Create eye-catching thumbnails with face integration
                </p>
              </div>
            </motion.div>

            {/* Bottom Left - Audio */}
            <motion.div
              initial={{ opacity: 0, x: 50, y: -50 }}
              whileInView={{ opacity: 1, x: 0, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.5, duration: 0.6 }}
              className="absolute bottom-8 left-8 md:left-16"
            >
              {/* Connection line */}
              <svg className="absolute bottom-1/2 left-full w-32 h-32 pointer-events-none" style={{ transform: 'translate(20px, 50%)' }}>
                <line x1="0" y1="64" x2="128" y2="64" stroke="rgba(139, 92, 246, 0.2)" strokeWidth="1" />
              </svg>
              
              <div className="w-64 p-6 rounded-xl bg-[#0B0C10] border border-white/[0.08] backdrop-blur-sm hover:border-violet-500/30 transition-all duration-300 group">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center">
                    <Volume2 className="w-5 h-5 text-violet-400" />
                  </div>
                  <h3 className="font-semibold text-white/90">Neural Audio</h3>
                </div>
                <p className="text-sm text-white/50 leading-relaxed">
                  Professional voiceovers in multiple voices
                </p>
              </div>
            </motion.div>

            {/* Bottom Right - Workflow */}
            <motion.div
              initial={{ opacity: 0, x: -50, y: -50 }}
              whileInView={{ opacity: 1, x: 0, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.6, duration: 0.6 }}
              className="absolute bottom-8 right-8 md:right-16"
            >
              {/* Connection line */}
              <svg className="absolute bottom-1/2 right-full w-32 h-32 pointer-events-none" style={{ transform: 'translate(-20px, 50%)' }}>
                <line x1="0" y1="64" x2="128" y2="64" stroke="rgba(139, 92, 246, 0.2)" strokeWidth="1" />
              </svg>
              
              <div className="w-64 p-6 rounded-xl bg-[#0B0C10] border border-white/[0.08] backdrop-blur-sm hover:border-violet-500/30 transition-all duration-300 group">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center">
                    <Zap className="w-5 h-5 text-violet-400" />
                  </div>
                  <h3 className="font-semibold text-white/90">One-Click Workflow</h3>
                </div>
                <p className="text-sm text-white/50 leading-relaxed">
                  From topic to publish-ready content instantly
                </p>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-24 px-6 relative">
        {/* Planet effect */}
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px]">
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] rounded-t-full bg-gradient-to-t from-violet-600/40 via-purple-500/20 to-transparent blur-sm" />
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[500px] h-[250px] rounded-t-full bg-gradient-to-t from-violet-500/30 to-transparent" />
        </div>

        <div className="relative z-10 max-w-2xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-sm text-white/80 mb-8"
          >
            Get access
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-3xl md:text-4xl font-bold tracking-tight mb-2"
          >
            We like keeping things simple
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.15 }}
            className="text-2xl md:text-3xl font-bold text-white/60 mb-12"
          >
            One plan, one price.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="mb-10"
          >
            <span className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-purple-400">$29</span>
            <span className="text-white/50 ml-2">/month (billed annually)</span>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3 }}
            className="grid grid-cols-2 gap-4 max-w-md mx-auto mb-10"
          >
            {[
              'Unlimited scripts',
              'Unlimited thumbnails',
              'Voice generation',
              'Face integration',
              'Smart tags & SEO',
              'Priority support',
            ].map((feature, i) => (
              <div key={i} className="flex items-center gap-2 text-sm text-white/70">
                <CheckCircle2 className="w-4 h-4 text-violet-400" />
                <span>{feature}</span>
              </div>
            ))}
          </motion.div>

          <motion.button
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.4 }}
            onClick={() => navigate('/signup')}
            className="px-8 py-3 rounded-lg bg-white/10 hover:bg-white/20 border border-white/20 font-medium transition-colors"
          >
            Start your 14-day trial
          </motion.button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5">
        {/* Main Footer */}
        <div className="max-w-6xl mx-auto px-6 py-16">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
            {/* Logo & Social */}
            <div className="space-y-6">
              <div className="flex items-center gap-2">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <span className="text-lg font-semibold">ViralLab</span>
              </div>
              <div className="flex items-center gap-4">
                {/* Discord */}
                <a href="#" className="text-white/40 hover:text-white transition-colors">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
                  </svg>
                </a>
                {/* Twitter/X */}
                <a href="#" className="text-white/40 hover:text-white transition-colors">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                  </svg>
                </a>
                {/* YouTube */}
                <a href="#" className="text-white/40 hover:text-white transition-colors">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                  </svg>
                </a>
              </div>
            </div>

            {/* Product Links */}
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-3">
                <li><a href="#" className="text-sm text-white/50 hover:text-white transition-colors">Features</a></li>
                <li><a href="#" className="text-sm text-white/50 hover:text-white transition-colors">Integrations</a></li>
                <li><a href="#" className="text-sm text-white/50 hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#" className="text-sm text-white/50 hover:text-white transition-colors">Changelog</a></li>
                <li><a href="#" className="text-sm text-white/50 hover:text-white transition-colors">Roadmap</a></li>
              </ul>
            </div>

            {/* Company Links */}
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-3">
                <li><a href="#" className="text-sm text-white/50 hover:text-white transition-colors">Our team</a></li>
                <li><a href="#" className="text-sm text-white/50 hover:text-white transition-colors">Our values</a></li>
                <li><a href="#" className="text-sm text-white/50 hover:text-white transition-colors">Blog</a></li>
              </ul>
            </div>

            {/* Resources Links */}
            <div>
              <h4 className="font-semibold mb-4">Resources</h4>
              <ul className="space-y-3">
                <li><a href="#" className="text-sm text-white/50 hover:text-white transition-colors">Downloads</a></li>
                <li><a href="#" className="text-sm text-white/50 hover:text-white transition-colors">Documentation</a></li>
                <li><a href="#" className="text-sm text-white/50 hover:text-white transition-colors">Contact</a></li>
              </ul>
            </div>
          </div>
        </div>

        {/* Newsletter Section */}
        <div className="border-t border-white/5">
          <div className="max-w-6xl mx-auto px-6 py-8 flex flex-col md:flex-row items-center justify-between gap-6">
            <div>
              <h4 className="font-semibold mb-1">Get free content creation tips</h4>
              <p className="text-sm text-white/50">In our weekly newsletter.</p>
            </div>
            <div className="flex items-center gap-2">
              <div className="relative">
                <input
                  type="email"
                  placeholder="Enter your email"
                  className="w-64 px-4 py-2.5 rounded-lg bg-white/5 border border-white/10 text-sm text-white placeholder-white/40 focus:outline-none focus:border-violet-500/50 transition-colors"
                />
                <Sparkles className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
              </div>
              <button className="px-5 py-2.5 rounded-lg bg-white/10 hover:bg-white/20 border border-white/10 text-sm font-medium transition-colors">
                Subscribe
              </button>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-white/5">
          <div className="max-w-6xl mx-auto px-6 py-6 flex items-center justify-between">
            <div className="flex items-center gap-4 text-sm text-white/40">
              <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
              <span>·</span>
              <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
            </div>
            <div className="text-sm text-white/40">
              ViralLab, Inc. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
