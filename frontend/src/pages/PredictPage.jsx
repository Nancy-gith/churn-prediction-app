import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { UserSearch, Send, AlertCircle, TrendingUp, TrendingDown, Info } from 'lucide-react'
import { predictChurn, getModels } from '../services/api'

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

export default function PredictPage() {
    const [formData, setFormData] = useState(DEFAULT_VALUES)
    const [selectedModel, setSelectedModel] = useState('xgboost')
    const [models, setModels] = useState(null)
    const [prediction, setPrediction] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    useEffect(() => {
        getModels()
            .then(res => {
                setModels(res.data)
                if (res.data.best_model) setSelectedModel(res.data.best_model)
            })
            .catch(() => { })
    }, [])

    const handleChange = (name, value) => {
        setFormData(prev => ({ ...prev, [name]: value }))
    }

    const handlePredict = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError(null)
        setPrediction(null)
        try {
            // Convert numeric fields
            const data = { ...formData }
            data.tenure = parseInt(data.tenure) || 0
            data.MonthlyCharges = parseFloat(data.MonthlyCharges) || 0
            data.TotalCharges = parseFloat(data.TotalCharges) || 0
            data.SupportCalls = parseInt(data.SupportCalls) || 0
            data.SeniorCitizen = parseInt(data.SeniorCitizen)

            const res = await predictChurn(selectedModel, data)
            setPrediction(res.data)
        } catch (err) {
            setError(err.response?.data?.detail || 'Prediction failed')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="space-y-8">
            {/* ── Header ── */}
            <div>
                <h1 className="text-3xl font-black tracking-tight flex items-center gap-3">
                    <UserSearch size={28} style={{ color: '#8b5cf6' }} />
                    Predict Customer Churn
                </h1>
                <p className="mt-2" style={{ color: 'var(--text-secondary)' }}>
                    Enter customer details to predict their churn probability. SHAP explains why.
                </p>
            </div>

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
                                {['logistic_regression', 'random_forest', 'xgboost', 'lightgbm', 'catboost', 'neural_network'].map(m => (
                                    <option key={m} value={m}>
                                        {m.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                                        {models?.best_model === m ? ' ⭐ (Best)' : ''}
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
                            disabled={loading || !models?.trained}
                        >
                            {loading ? (
                                <>
                                    <div className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
                                    Predicting...
                                </>
                            ) : (
                                <>
                                    <Send size={16} />
                                    Predict Churn
                                </>
                            )}
                        </button>

                        {!models?.trained && (
                            <p className="text-center text-sm" style={{ color: 'var(--text-muted)' }}>
                                ⚠️ Train models first on the Models page before predicting.
                            </p>
                        )}
                    </form>
                </div>

                {/* ── Prediction Result ── */}
                <div className="space-y-6">
                    {error && (
                        <div className="glass-card p-4 flex items-center gap-3" style={{ borderColor: 'rgba(239,68,68,0.3)' }}>
                            <AlertCircle size={18} style={{ color: '#ef4444' }} />
                            <span className="text-sm" style={{ color: '#ef4444' }}>{error}</span>
                        </div>
                    )}

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
                            </div>

                            {/* SHAP Explanation */}
                            {prediction.shap_explanation?.top_reasons && (
                                <div className="glass-card overflow-hidden">
                                    <div className="px-5 py-3" style={{ borderBottom: '1px solid var(--glass-border)' }}>
                                        <h4 className="font-semibold text-sm flex items-center gap-2">
                                            <Info size={14} style={{ color: '#06b6d4' }} />
                                            Why This Prediction (SHAP)
                                        </h4>
                                    </div>
                                    <div className="divide-y" style={{ borderColor: 'rgba(255,255,255,0.03)' }}>
                                        {prediction.shap_explanation.top_reasons.slice(0, 8).map((reason, i) => (
                                            <div key={i} className="px-5 py-3 flex items-center justify-between">
                                                <div className="flex items-center gap-3">
                                                    {reason.shap_value > 0 ? (
                                                        <TrendingUp size={14} style={{ color: '#ef4444' }} />
                                                    ) : (
                                                        <TrendingDown size={14} style={{ color: '#22c55e' }} />
                                                    )}
                                                    <span className="text-sm font-medium">{reason.feature}</span>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <span className={`text-xs ${reason.shap_value > 0 ? 'text-red-400' : 'text-green-400'
                                                        }`}>
                                                        {reason.direction}
                                                    </span>
                                                    <span className="font-mono text-xs" style={{ color: 'var(--text-muted)' }}>
                                                        {reason.shap_value > 0 ? '+' : ''}{reason.shap_value.toFixed(4)}
                                                    </span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

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

                    {!prediction && !error && (
                        <div className="glass-card p-8 text-center">
                            <UserSearch size={40} className="mx-auto mb-4" style={{ color: 'var(--text-muted)' }} />
                            <p style={{ color: 'var(--text-muted)' }} className="text-sm">
                                Fill in the customer details and click "Predict" to see results.
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
