import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Zap, Send, AlertCircle, TrendingUp, TrendingDown, Info, ArrowLeft, CheckCircle2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { quickPredict, getQuickPredictStatus } from '../services/api'

const FORM_FIELDS = [
    { name: 'gender', label: 'Gender', type: 'select', options: ['Male', 'Female'] },
    { name: 'SeniorCitizen', label: 'Senior Citizen', type: 'select', options: ['0', '1'] },
    { name: 'Partner', label: 'Partner', type: 'select', options: ['Yes', 'No'] },
    { name: 'Dependents', label: 'Dependents', type: 'select', options: ['Yes', 'No'] },
    { name: 'tenure', label: 'Tenure (months)', type: 'number', min: 0, max: 72 },
    { name: 'PhoneService', label: 'Phone Service', type: 'select', options: ['Yes', 'No'] },
    {
        name: 'MultipleLines', label: 'Multiple Lines', type: 'select',
        options: ['Yes', 'No', 'No phone service']
    },
    {
        name: 'InternetService', label: 'Internet Service', type: 'select',
        options: ['DSL', 'Fiber optic', 'No']
    },
    {
        name: 'OnlineSecurity', label: 'Online Security', type: 'select',
        options: ['Yes', 'No', 'No internet service']
    },
    {
        name: 'OnlineBackup', label: 'Online Backup', type: 'select',
        options: ['Yes', 'No', 'No internet service']
    },
    {
        name: 'DeviceProtection', label: 'Device Protection', type: 'select',
        options: ['Yes', 'No', 'No internet service']
    },
    {
        name: 'TechSupport', label: 'Tech Support', type: 'select',
        options: ['Yes', 'No', 'No internet service']
    },
    {
        name: 'StreamingTV', label: 'Streaming TV', type: 'select',
        options: ['Yes', 'No', 'No internet service']
    },
    {
        name: 'StreamingMovies', label: 'Streaming Movies', type: 'select',
        options: ['Yes', 'No', 'No internet service']
    },
    {
        name: 'Contract', label: 'Contract', type: 'select',
        options: ['Month-to-month', 'One year', 'Two year']
    },
    { name: 'PaperlessBilling', label: 'Paperless Billing', type: 'select', options: ['Yes', 'No'] },
    {
        name: 'PaymentMethod', label: 'Payment Method', type: 'select',
        options: ['Electronic check', 'Mailed check', 'Bank transfer (automatic)', 'Credit card (automatic)']
    },
    { name: 'MonthlyCharges', label: 'Monthly Charges ($)', type: 'number', min: 0, max: 200 },
    { name: 'TotalCharges', label: 'Total Charges ($)', type: 'number', min: 0, max: 10000 },
    { name: 'SupportCalls', label: 'Support Calls', type: 'number', min: 0, max: 10 },
]

const DEFAULT_VALUES = {
    gender: 'Male', SeniorCitizen: '0', Partner: 'No', Dependents: 'No',
    tenure: '24', PhoneService: 'Yes', MultipleLines: 'No',
    InternetService: 'Fiber optic', OnlineSecurity: 'No', OnlineBackup: 'No',
    DeviceProtection: 'No', TechSupport: 'No', StreamingTV: 'No',
    StreamingMovies: 'No', Contract: 'Month-to-month', PaperlessBilling: 'Yes',
    PaymentMethod: 'Electronic check', MonthlyCharges: '75',
    TotalCharges: '1800', SupportCalls: '2',
}

export default function QuickPredictPage() {
    const [formData, setFormData] = useState(DEFAULT_VALUES)
    const [selectedModel, setSelectedModel] = useState('xgboost')
    const [availableModels, setAvailableModels] = useState([])
    const [prediction, setPrediction] = useState(null)
    const [loading, setLoading] = useState(false)
    const [statusLoading, setStatusLoading] = useState(true)
    const [error, setError] = useState(null)
    const [pipelineSteps, setPipelineSteps] = useState([])
    const navigate = useNavigate()

    useEffect(() => {
        getQuickPredictStatus()
            .then(res => {
                setAvailableModels(res.data.models || [])
                if (res.data.models?.length > 0) {
                    setSelectedModel(res.data.models[0])
                }
            })
            .catch(() => { })
            .finally(() => setStatusLoading(false))
    }, [])

    const handleChange = (name, value) => {
        setFormData(prev => ({ ...prev, [name]: value }))
    }

    const handlePredict = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError(null)
        setPrediction(null)
        setPipelineSteps([])

        // Show pipeline steps with delays for effect
        const steps = [
            { label: 'Loading dataset...', icon: '📊' },
            { label: 'Cleaning data...', icon: '🧹' },
            { label: 'Preparing features...', icon: '⚙️' },
            { label: 'Running prediction...', icon: '🔮' },
        ]

        for (let i = 0; i < steps.length; i++) {
            setPipelineSteps(prev => [...prev, { ...steps[i], status: 'running' }])
            await new Promise(r => setTimeout(r, 400))
            setPipelineSteps(prev =>
                prev.map((s, idx) => idx === i ? { ...s, status: 'done' } : s)
            )
        }

        try {
            const data = { ...formData }
            data.tenure = parseInt(data.tenure) || 0
            data.MonthlyCharges = parseFloat(data.MonthlyCharges) || 0
            data.TotalCharges = parseFloat(data.TotalCharges) || 0
            data.SupportCalls = parseInt(data.SupportCalls) || 0
            data.SeniorCitizen = parseInt(data.SeniorCitizen)

            const res = await quickPredict(selectedModel, data)
            setPrediction(res.data)
        } catch (err) {
            setError(err.response?.data?.detail || 'Quick prediction failed. Make sure models have been trained at least once.')
        } finally {
            setLoading(false)
        }
    }

    if (statusLoading) {
        return (
            <div className="flex items-center justify-center py-20">
                <div className="spinner" style={{ width: 48, height: 48 }} />
            </div>
        )
    }

    return (
        <div className="space-y-8">
            {/* ── Header ── */}
            <div className="flex items-center justify-between flex-wrap gap-4">
                <div>
                    <h1 className="text-3xl font-black tracking-tight flex items-center gap-3">
                        <div className="w-9 h-9 rounded-lg flex items-center justify-center"
                            style={{ background: 'linear-gradient(135deg, #f59e0b, #ef4444)' }}>
                            <Zap size={20} className="text-white" />
                        </div>
                        Quick Predict
                    </h1>
                    <p className="mt-2" style={{ color: 'var(--text-secondary)' }}>
                        Skip the full pipeline — predict churn instantly using pre-trained models.
                    </p>
                </div>
                <button
                    className="btn-secondary flex items-center gap-2 text-sm"
                    onClick={() => navigate('/')}
                >
                    <ArrowLeft size={16} />
                    Back to Upload
                </button>
            </div>

            {/* ── Info Banner ── */}
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card p-4 flex items-start gap-3"
                style={{ borderColor: 'rgba(245, 158, 11, 0.3)' }}
            >
                <Zap size={18} style={{ color: '#f59e0b', marginTop: 2, flexShrink: 0 }} />
                <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                    <strong style={{ color: '#f59e0b' }}>How Quick Predict works:</strong> The system automatically
                    loads the dataset, cleans it, and uses <strong>pre-trained saved models</strong> to predict — no
                    manual cleaning or training needed. Just fill in the customer details and hit predict!
                </div>
            </motion.div>

            {availableModels.length === 0 && (
                <div className="glass-card p-8 text-center" style={{ borderColor: 'rgba(239,68,68,0.3)' }}>
                    <AlertCircle size={40} className="mx-auto mb-4" style={{ color: '#ef4444' }} />
                    <h3 className="text-lg font-bold mb-2">No Saved Models Found</h3>
                    <p style={{ color: 'var(--text-secondary)' }} className="mb-4">
                        Quick Predict requires models to be trained at least once. Go through the full pipeline first
                        (Upload → Clean → Train), then you can use Quick Predict next time.
                    </p>
                    <button className="btn-primary" onClick={() => navigate('/')}>
                        Go to Upload
                    </button>
                </div>
            )}

            {availableModels.length > 0 && (
                <div className="grid lg:grid-cols-3 gap-8">
                    {/* ── Form ── */}
                    <div className="lg:col-span-2">
                        <form onSubmit={handlePredict} className="space-y-6">
                            {/* Model Selector */}
                            <div className="glass-card p-5">
                                <label className="block text-sm font-semibold mb-2">Select Model</label>
                                <select
                                    className="input-field"
                                    value={selectedModel}
                                    onChange={(e) => setSelectedModel(e.target.value)}
                                >
                                    {availableModels.map(m => (
                                        <option key={m} value={m}>
                                            {m.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {/* Customer Fields */}
                            <div className="glass-card p-6">
                                <h3 className="font-semibold mb-4">Customer Information</h3>
                                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                                    {FORM_FIELDS.map(field => (
                                        <div key={field.name}>
                                            <label className="block text-xs font-semibold mb-1.5" style={{ color: 'var(--text-muted)' }}>
                                                {field.label}
                                            </label>
                                            {field.type === 'select' ? (
                                                <select
                                                    className="input-field"
                                                    value={formData[field.name]}
                                                    onChange={(e) => handleChange(field.name, e.target.value)}
                                                >
                                                    {field.options.map(opt => (
                                                        <option key={opt} value={opt}>{opt}</option>
                                                    ))}
                                                </select>
                                            ) : (
                                                <input
                                                    type="number"
                                                    className="input-field"
                                                    value={formData[field.name]}
                                                    onChange={(e) => handleChange(field.name, e.target.value)}
                                                    min={field.min}
                                                    max={field.max}
                                                />
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <button
                                type="submit"
                                className="btn-primary w-full py-3 text-center flex items-center justify-center gap-2"
                                disabled={loading}
                                style={!loading ? { background: 'linear-gradient(135deg, #f59e0b, #ef4444)' } : {}}
                            >
                                {loading ? (
                                    <>
                                        <div className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
                                        Processing...
                                    </>
                                ) : (
                                    <>
                                        <Zap size={16} />
                                        ⚡ Quick Predict
                                    </>
                                )}
                            </button>
                        </form>
                    </div>

                    {/* ── Right Column: Pipeline + Results ── */}
                    <div className="space-y-6">
                        {/* Pipeline Steps */}
                        {pipelineSteps.length > 0 && (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="glass-card p-5"
                            >
                                <h4 className="text-sm font-semibold mb-3" style={{ color: 'var(--text-muted)' }}>
                                    PIPELINE
                                </h4>
                                <div className="space-y-3">
                                    {pipelineSteps.map((step, i) => (
                                        <motion.div
                                            key={i}
                                            initial={{ opacity: 0, x: -10 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            className="flex items-center gap-3"
                                        >
                                            {step.status === 'done' ? (
                                                <CheckCircle2 size={16} style={{ color: '#22c55e' }} />
                                            ) : (
                                                <div className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
                                            )}
                                            <span className="text-sm" style={{
                                                color: step.status === 'done' ? 'var(--text-secondary)' : 'var(--text-primary)'
                                            }}>
                                                {step.icon} {step.label}
                                            </span>
                                        </motion.div>
                                    ))}
                                </div>
                            </motion.div>
                        )}

                        {/* Error */}
                        {error && (
                            <div className="glass-card p-4 flex items-center gap-3" style={{ borderColor: 'rgba(239,68,68,0.3)' }}>
                                <AlertCircle size={18} style={{ color: '#ef4444' }} />
                                <span className="text-sm" style={{ color: '#ef4444' }}>{error}</span>
                            </div>
                        )}

                        {/* Prediction Result */}
                        {prediction && (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="space-y-6"
                            >
                                {/* Risk Gauge */}
                                <div className="glass-card p-8 text-center"
                                    style={{ borderColor: `${prediction.risk_color}30` }}>
                                    <div className="risk-gauge mx-auto mb-4"
                                        style={{
                                            background: `conic-gradient(${prediction.risk_color} ${prediction.probability_percentage * 3.6}deg, rgba(255,255,255,0.05) 0deg)`,
                                        }}>
                                        <div className="relative z-10 text-center">
                                            <div className="text-3xl font-black" style={{ color: prediction.risk_color }}>
                                                {prediction.probability_percentage}%
                                            </div>
                                            <div className="text-xs font-semibold" style={{ color: 'var(--text-muted)' }}>
                                                CHURN RISK
                                            </div>
                                        </div>
                                    </div>

                                    <div className="text-2xl font-bold mb-2" style={{ color: prediction.risk_color }}>
                                        {prediction.prediction}
                                    </div>
                                    <div className={`badge ${prediction.risk_level === 'low' ? 'badge-success' :
                                        prediction.risk_level === 'medium' ? 'badge-warning' : 'badge-danger'
                                        }`}>
                                        {prediction.risk_label}
                                    </div>

                                    {/* Quick Predict badge */}
                                    <div className="mt-3 inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold"
                                        style={{ background: 'rgba(245,158,11,0.1)', color: '#f59e0b', border: '1px solid rgba(245,158,11,0.2)' }}>
                                        <Zap size={12} />
                                        Quick Predict
                                    </div>
                                </div>

                                {/* Model Info */}
                                <div className="glass-card p-5">
                                    <div className="text-xs" style={{ color: 'var(--text-muted)' }}>
                                        Model: <span className="font-semibold" style={{ color: 'var(--text-secondary)' }}>
                                            {prediction.model_used.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                                        </span>
                                    </div>
                                    <div className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
                                        Raw probability: <span className="font-mono">{prediction.probability}</span>
                                    </div>
                                </div>
                            </motion.div>
                        )}

                        {!prediction && !error && pipelineSteps.length === 0 && (
                            <div className="glass-card p-8 text-center">
                                <Zap size={40} className="mx-auto mb-4" style={{ color: 'var(--text-muted)' }} />
                                <p style={{ color: 'var(--text-muted)' }} className="text-sm">
                                    Fill in the customer details and click "Quick Predict" to see instant results.
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    )
}
