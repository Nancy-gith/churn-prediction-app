import React from 'react'
import { Routes, Route, NavLink, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Shield, Upload, BarChart3, Brain, UserSearch, Database, Sparkles, Zap } from 'lucide-react'
import LandingPage from './pages/LandingPage'
import CleaningPage from './pages/CleaningPage'
import EDAPage from './pages/EDAPage'
import TrainingPage from './pages/TrainingPage'
import PredictPage from './pages/PredictPage'
import QuickPredictPage from './pages/QuickPredictPage'

const navItems = [
    { path: '/', label: 'Upload', icon: Upload },
    { path: '/cleaning', label: 'Cleaning', icon: Database },
    { path: '/eda', label: 'EDA', icon: BarChart3 },
    { path: '/training', label: 'Models', icon: Brain },
    { path: '/predict', label: 'Predict', icon: UserSearch },
    { path: '/quick-predict', label: 'Quick Predict', icon: Zap },
]

export default function App() {
    const location = useLocation()

    return (
        <div className="min-h-screen flex flex-col">
            {/* ── NAVBAR ── */}
            <nav className="sticky top-0 z-50 glass-card border-t-0 border-x-0 rounded-none"
                style={{ borderRadius: 0 }}>
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        {/* Logo */}
                        <NavLink to="/" className="flex items-center gap-3 no-underline">
                            <div className="w-9 h-9 rounded-lg flex items-center justify-center"
                                style={{ background: 'var(--gradient-primary)' }}>
                                <Shield size={20} className="text-white" />
                            </div>
                            <div>
                                <span className="text-lg font-bold tracking-tight"
                                    style={{ background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                                    ChurnGuard
                                </span>
                                <span className="text-xs ml-1.5 font-medium" style={{ color: 'var(--text-muted)' }}>AI</span>
                            </div>
                        </NavLink>

                        {/* Nav Links */}
                        <div className="flex items-center gap-1">
                            {navItems.map(({ path, label, icon: Icon }) => (
                                <NavLink
                                    key={path}
                                    to={path}
                                    className={({ isActive }) =>
                                        `nav-link flex items-center gap-2 ${isActive ? 'active' : ''}`
                                    }
                                >
                                    <Icon size={16} />
                                    <span className="hidden sm:inline">{label}</span>
                                </NavLink>
                            ))}
                        </div>
                    </div>
                </div>
            </nav>

            {/* ── MAIN CONTENT ── */}
            <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={location.pathname}
                        initial={{ opacity: 0, y: 12 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -12 }}
                        transition={{ duration: 0.25, ease: 'easeOut' }}
                    >
                        <Routes location={location}>
                            <Route path="/" element={<LandingPage />} />
                            <Route path="/cleaning" element={<CleaningPage />} />
                            <Route path="/eda" element={<EDAPage />} />
                            <Route path="/training" element={<TrainingPage />} />
                            <Route path="/predict" element={<PredictPage />} />
                            <Route path="/quick-predict" element={<QuickPredictPage />} />
                        </Routes>
                    </motion.div>
                </AnimatePresence>
            </main>

            {/* ── FOOTER ── */}
            <footer className="text-center py-6" style={{ color: 'var(--text-muted)' }}>
                <div className="flex items-center justify-center gap-2 text-xs">
                    <Sparkles size={12} />
                    <span>ChurnGuard AI — Telecom Churn Prediction Platform</span>
                    <Sparkles size={12} />
                </div>
            </footer>
        </div>
    )
}
