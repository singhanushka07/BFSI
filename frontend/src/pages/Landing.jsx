import Navbar from '../components/common/Navbar'
import Hero from '../components/landing/Hero'
import Features from '../components/landing/Features'
import ArchitectureDiagram from '../components/landing/ArchitectureDiagram'
import TechStack from '../components/landing/TechStack'
import Footer from '../components/common/Footer'
import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { motion } from 'framer-motion'

export default function Landing() {
  return (
    <div className="min-h-screen bg-navy-950">
      <Navbar transparent />
      <Hero />
      <Features />
      <ArchitectureDiagram />
      <TechStack />

      {/* CTA Section */}
      <section className="py-24 px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-3xl mx-auto text-center"
        >
          <div className="glass-card glow-border p-12">
            <h2 className="text-4xl font-extrabold text-white mb-4">
              Ready to Assess Risk with AI?
            </h2>
            <p className="text-slate-400 text-lg mb-8 max-w-xl mx-auto">
              Create an account and run your first multi-agent risk analysis in under 60 seconds.
            </p>
            <div className="flex flex-wrap gap-4 justify-center">
              <Link to="/login?mode=register" className="btn-primary flex items-center gap-2 text-base px-8 py-4">
                Start Free Analysis
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link to="/login" className="btn-secondary text-base px-8 py-4">
                Sign In
              </Link>
            </div>
          </div>
        </motion.div>
      </section>

      <Footer />
    </div>
  )
}
