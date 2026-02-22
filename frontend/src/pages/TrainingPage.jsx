import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
    Brain, Zap, Trophy, Clock, Info, ChevronDown, ChevronUp, BarChart
} from 'lucide-react'
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, Legend, BarChart as RBarChart, Bar
} from 'recharts'
import { trainModels, getEvaluation, getSHAP, getModels } from '../services/api'

const MODEL_COLORS = {
    'XGBoost': '#f59e0b',
    'LightGBM': '#06b6d4',
    'CatBoost': '#ec4899',
}

const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null
    return (
        <div style={{
            background: 'rgba(15, 15, 35, 0.95)',
            border: '1px solid rgba(139, 92, 246, 0.3)',
            borderRadius: 10,
            padding: '12px 16px',
            fontSize: 13,
        }}>
            <div style={{ color: '#f1f5f9', fontWeight: 600, marginBottom: 6 }}>{label}</div>
            {payload.map((p, i) => (
                <div key={i} style={{ color: p.color, display: 'flex', gap: 8 }}>
                    <span style={{ width: 8, height: 8, borderRadius: '50%', background: p.color, display: 'inline-block', marginTop: 5 }} />
                    {p.name}: <strong style={{ color: '#f1f5f9' }}>{p.value?.toFixed ? p.value.toFixed(4) : p.value}</strong>
                </div>
            ))}
        </div>
    )
}

export default function TrainingPage() {
    const [training, setTraining] = useState(false)
    const [evaluation, setEvaluation] = useState(null)
    const [tuning, setTuning] = useState(false)
    const [shapData, setShapData] = useState(null)
    const [shapLoading, setShapLoading] = useState(false)
    const [expandedModel, setExpandedModel] = useState(null)
    const [error, setError] = useState(null)
    const [smoteInfo, setSMOTEInfo] = useState(null)

    useEffect(() => {
        getEvaluation()
            .then(res => setEvaluation(res.data))
            .catch(() => { })
    }, [])

    const handleTrain = async () => {
        setTraining(true)
        setError(null)
        setEvaluation(null)
        setShapData(null)
        try {
            const res = await trainModels(tuning)
            setEvaluation(res.data.evaluation)
            setSMOTEInfo(res.data.smote_info)
        } catch (err) {
            setError(err.response?.data?.detail || 'Training failed')
        } finally {
            setTraining(false)
        }
    }

    const handleSHAP = async (modelName) => {
        setShapLoading(true)
        try {
            const res = await getSHAP(modelName)
            setShapData(res.data)
        } catch (err) {
            console.error('SHAP failed:', err)
        } finally {
            setShapLoading(false)
        }
    }

    return (
        <div className="space-y-8">
            {/* ── Header ── */}
            <div className="flex items-center justify-between flex-wrap gap-4">
                <div>
                    <h1 className="text-3xl font-black tracking-tight flex items-center gap-3">
                        <Brain size={28} style={{ color: '#8b5cf6' }} />
                        Model Training & Evaluation
                    </h1>
                    <p className="mt-2" style={{ color: 'var(--text-secondary)' }}>
                        Train 3 industry-leading gradient boosting models and compare their performance.
                    </p>
                </div>
                <div className="flex items-center gap-4">
                    <label className="flex items-center gap-2 text-sm cursor-pointer"
                        style={{ color: 'var(--text-secondary)' }}>
                        <input
                            type="checkbox"
                            checked={tuning}
                            onChange={() => setTuning(!tuning)}
                            className="w-4 h-4 accent-purple-500"
                        />
                        Hyperparameter Tuning (Optuna)
                    </label>
                    <button className="btn-primary flex items-center gap-2" onClick={handleTrain} disabled={training}>
                        {training ? (
                            <>
                                <div className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
                                Training {tuning ? '(with tuning)' : ''}...
                            </>
                        ) : (
                            <>
                                <Zap size={16} />
                                Train All Models
                            </>
                        )}
                    </button>
                </div>
            </div>

            {error && (
                <div className="glass-card p-4 flex items-center gap-3" style={{ borderColor: 'rgba(239,68,68,0.3)' }}>
                    <Info size={20} style={{ color: '#ef4444' }} />
                    <span style={{ color: '#ef4444' }}>{error}</span>
                </div>
            )}

            {training && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="glass-card p-8 text-center"
                >
                    <div className="spinner mx-auto mb-4" style={{ width: 48, height: 48 }} />
                    <h3 className="text-lg font-bold mb-2">Training Models...</h3>
                    <p style={{ color: 'var(--text-secondary)' }}>
                        Training 3 models{tuning ? ' with Optuna hyperparameter tuning' : ''}.<br />
                        This may take 15-45 seconds.
                    </p>
                    <div className="progress-bar mt-6 max-w-md mx-auto">
                        <div className="progress-fill" style={{ width: '60%', animation: 'pulse 2s infinite' }} />
                    </div>
                </motion.div>
            )}

            {/* ── SMOTE Info ── */}
            {smoteInfo && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5">
                    <h4 className="font-semibold mb-3 flex items-center gap-2">
                        <Info size={16} style={{ color: '#06b6d4' }} />
                        Class Imbalance Handling (SMOTE)
                    </h4>
                    <div className="grid sm:grid-cols-3 gap-4 text-sm">
                        <div className="p-3 rounded-lg" style={{ background: 'rgba(239,68,68,0.05)' }}>
                            <div className="font-semibold">Before SMOTE</div>
                            <div style={{ color: 'var(--text-secondary)' }}>
                                {Object.entries(smoteInfo.class_distribution_before).map(([k, v]) => (
                                    <div key={k}>Class {k}: {v.toLocaleString()}</div>
                                ))}
                            </div>
                        </div>
                        <div className="flex items-center justify-center">
                            <span className="text-2xl">→</span>
                        </div>
                        <div className="p-3 rounded-lg" style={{ background: 'rgba(34,197,94,0.05)' }}>
                            <div className="font-semibold">After SMOTE</div>
                            <div style={{ color: 'var(--text-secondary)' }}>
                                {Object.entries(smoteInfo.class_distribution_after).map(([k, v]) => (
                                    <div key={k}>Class {k}: {v.toLocaleString()}</div>
                                ))}
                            </div>
                        </div>
                    </div>
                    <p className="text-xs mt-3" style={{ color: 'var(--text-muted)' }}>
                        +{smoteInfo.samples_added.toLocaleString()} synthetic samples added via {smoteInfo.technique}
                    </p>
                </motion.div>
            )}

            {/* ── Results ── */}
            {evaluation && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
                    {/* Best Model Callout */}
                    <div className="glass-card p-6 animate-glow"
                        style={{ borderColor: 'rgba(34,197,94,0.3)' }}>
                        <div className="flex items-center gap-3 mb-3">
                            <Trophy size={24} style={{ color: '#eab308' }} />
                            <h3 className="text-lg font-bold">Best Model: {evaluation.best_model_name}</h3>
                        </div>
                        <p style={{ color: 'var(--text-secondary)' }}>{evaluation.recommendation}</p>
                    </div>

                    {/* Comparison Table */}
                    <div className="glass-card overflow-hidden">
                        <div className="px-6 py-4" style={{ borderBottom: '1px solid var(--glass-border)' }}>
                            <h3 className="font-semibold">Model Comparison</h3>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        <th></th>
                                        <th>Model</th>
                                        <th>Accuracy</th>
                                        <th>Precision</th>
                                        <th>Recall ⭐</th>
                                        <th>F1-Score</th>
                                        <th>ROC-AUC</th>
                                        <th>Time</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {evaluation.comparison_table.map((row, i) => (
                                        <tr key={row.model_key}
                                            style={row.model_key === evaluation.best_model
                                                ? { background: 'rgba(34,197,94,0.05)' } : {}}>
                                            <td>
                                                {i === 0 && <Trophy size={16} style={{ color: '#eab308' }} />}
                                            </td>
                                            <td>
                                                <div className="flex items-center gap-2">
                                                    <span className="w-3 h-3 rounded-full"
                                                        style={{ background: MODEL_COLORS[row.model] || '#8b5cf6', display: 'inline-block' }} />
                                                    <span className="font-semibold">{row.model}</span>
                                                </div>
                                            </td>
                                            <td className="font-mono">{(row.accuracy * 100).toFixed(1)}%</td>
                                            <td className="font-mono">{(row.precision * 100).toFixed(1)}%</td>
                                            <td className="font-mono font-bold" style={{ color: '#f1f5f9' }}>
                                                {(row.recall * 100).toFixed(1)}%
                                            </td>
                                            <td className="font-mono">{(row.f1_score * 100).toFixed(1)}%</td>
                                            <td className="font-mono">{(row.roc_auc * 100).toFixed(1)}%</td>
                                            <td className="font-mono flex items-center gap-1">
                                                <Clock size={12} style={{ color: 'var(--text-muted)' }} />
                                                {row.train_time}s
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* ROC Curves */}
                    <div className="glass-card p-6">
                        <h3 className="font-semibold mb-4">ROC Curves (All Models)</h3>
                        <ResponsiveContainer width="100%" height={400}>
                            <LineChart>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                                <XAxis
                                    dataKey="fpr" type="number" domain={[0, 1]}
                                    label={{ value: 'False Positive Rate', position: 'bottom', fill: '#64748b', fontSize: 12 }}
                                    stroke="#64748b" fontSize={11}
                                />
                                <YAxis
                                    dataKey="tpr" type="number" domain={[0, 1]}
                                    label={{ value: 'True Positive Rate', angle: -90, position: 'left', fill: '#64748b', fontSize: 12 }}
                                    stroke="#64748b" fontSize={11}
                                />
                                <Tooltip content={<CustomTooltip />} />
                                <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
                                {/* Diagonal reference line */}
                                <Line
                                    data={[{ fpr: 0, tpr: 0 }, { fpr: 1, tpr: 1 }]}
                                    dataKey="tpr" stroke="#334155" strokeDasharray="5 5"
                                    dot={false} name="Random" strokeWidth={1}
                                />
                                {Object.entries(evaluation.evaluations).map(([key, ev]) => (
                                    <Line
                                        key={key}
                                        data={ev.roc_curve}
                                        dataKey="tpr"
                                        stroke={MODEL_COLORS[ev.info.name] || '#8b5cf6'}
                                        strokeWidth={2}
                                        dot={false}
                                        name={`${ev.info.name} (AUC=${ev.metrics.roc_auc.toFixed(3)})`}
                                    />
                                ))}
                            </LineChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Confusion Matrices */}
                    <div className="glass-card overflow-hidden">
                        <div className="px-6 py-4" style={{ borderBottom: '1px solid var(--glass-border)' }}>
                            <h3 className="font-semibold">Confusion Matrices</h3>
                        </div>
                        <div className="p-6 grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
                            {Object.entries(evaluation.evaluations).map(([key, ev]) => (
                                <div key={key} className="p-4 rounded-xl" style={{ background: 'rgba(255,255,255,0.02)' }}>
                                    <div className="text-sm font-semibold mb-3 flex items-center gap-2">
                                        <span className="w-3 h-3 rounded-full"
                                            style={{ background: MODEL_COLORS[ev.info.name] || '#8b5cf6' }} />
                                        {ev.info.name}
                                    </div>
                                    <div className="grid grid-cols-2 gap-1 text-center text-xs">
                                        <div className="p-3 rounded-lg" style={{ background: 'rgba(34,197,94,0.1)' }}>
                                            <div className="text-lg font-bold">{ev.confusion_matrix.tn}</div>
                                            <div style={{ color: 'var(--text-muted)' }}>True Neg</div>
                                        </div>
                                        <div className="p-3 rounded-lg" style={{ background: 'rgba(239,68,68,0.1)' }}>
                                            <div className="text-lg font-bold">{ev.confusion_matrix.fp}</div>
                                            <div style={{ color: 'var(--text-muted)' }}>False Pos</div>
                                        </div>
                                        <div className="p-3 rounded-lg" style={{ background: 'rgba(234,179,8,0.1)' }}>
                                            <div className="text-lg font-bold">{ev.confusion_matrix.fn}</div>
                                            <div style={{ color: 'var(--text-muted)' }}>False Neg</div>
                                        </div>
                                        <div className="p-3 rounded-lg" style={{ background: 'rgba(34,197,94,0.1)' }}>
                                            <div className="text-lg font-bold">{ev.confusion_matrix.tp}</div>
                                            <div style={{ color: 'var(--text-muted)' }}>True Pos</div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Model Details (expandable) */}
                    <div className="space-y-3">
                        <h3 className="font-semibold px-1">Model Details & Explanations</h3>
                        {Object.entries(evaluation.evaluations).map(([key, ev]) => (
                            <motion.div key={key} className="glass-card overflow-hidden">
                                <button
                                    className="w-full px-6 py-4 flex items-center justify-between text-left"
                                    onClick={() => setExpandedModel(expandedModel === key ? null : key)}
                                >
                                    <div className="flex items-center gap-3">
                                        <span className="w-3 h-3 rounded-full"
                                            style={{ background: MODEL_COLORS[ev.info.name] || '#8b5cf6' }} />
                                        <span className="font-semibold">{ev.info.name}</span>
                                        <span className="badge badge-success text-xs">
                                            F1: {(ev.metrics.f1_score * 100).toFixed(1)}%
                                        </span>
                                    </div>
                                    {expandedModel === key ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                                </button>
                                {expandedModel === key && (
                                    <motion.div
                                        initial={{ height: 0, opacity: 0 }}
                                        animate={{ height: 'auto', opacity: 1 }}
                                        className="px-6 pb-6 space-y-4"
                                    >
                                        <div className="grid sm:grid-cols-2 gap-4">
                                            <div>
                                                <div className="text-xs font-semibold uppercase mb-1" style={{ color: 'var(--text-muted)' }}>
                                                    How It Works
                                                </div>
                                                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                                                    {ev.info.how_it_works}
                                                </p>
                                            </div>
                                            <div>
                                                <div className="text-xs font-semibold uppercase mb-1" style={{ color: 'var(--text-muted)' }}>
                                                    Why For Churn
                                                </div>
                                                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                                                    {ev.info.why_for_churn}
                                                </p>
                                            </div>
                                        </div>
                                        <div className="grid sm:grid-cols-2 gap-4">
                                            <div className="p-3 rounded-lg" style={{ background: 'rgba(34,197,94,0.05)' }}>
                                                <div className="text-xs font-semibold mb-1" style={{ color: '#22c55e' }}>Strengths</div>
                                                <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>{ev.info.strengths}</div>
                                            </div>
                                            <div className="p-3 rounded-lg" style={{ background: 'rgba(239,68,68,0.05)' }}>
                                                <div className="text-xs font-semibold mb-1" style={{ color: '#ef4444' }}>Weaknesses</div>
                                                <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>{ev.info.weaknesses}</div>
                                            </div>
                                        </div>
                                        <button
                                            className="btn-secondary text-sm flex items-center gap-2"
                                            onClick={() => handleSHAP(key)}
                                            disabled={shapLoading}
                                        >
                                            <BarChart size={14} />
                                            {shapLoading ? 'Computing SHAP...' : 'View SHAP Feature Importance'}
                                        </button>
                                    </motion.div>
                                )}
                            </motion.div>
                        ))}
                    </div>

                    {/* SHAP Chart */}
                    {shapData && shapData.feature_importance && (
                        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                            className="glass-card p-6">
                            <h3 className="font-semibold mb-4">
                                SHAP Feature Importance — {shapData.model_name}
                            </h3>
                            <ResponsiveContainer width="100%" height={Math.max(300, shapData.feature_importance.length * 28)}>
                                <RBarChart
                                    data={shapData.feature_importance.slice(0, 15).reverse()}
                                    layout="vertical"
                                    margin={{ left: 120 }}
                                >
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                                    <XAxis type="number" stroke="#64748b" fontSize={11} />
                                    <YAxis type="category" dataKey="feature" stroke="#64748b" fontSize={11} width={120} />
                                    <Tooltip content={<CustomTooltip />} />
                                    <Bar dataKey="importance" fill="#8b5cf6" radius={[0, 6, 6, 0]} name="Mean |SHAP|" />
                                </RBarChart>
                            </ResponsiveContainer>
                            <p className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>
                                SHAP values show each feature's average contribution to predictions. Higher = more important.
                            </p>
                        </motion.div>
                    )}
                </motion.div>
            )}

            {!evaluation && !training && (
                <div className="text-center py-16">
                    <Brain size={48} className="mx-auto mb-4" style={{ color: 'var(--text-muted)' }} />
                    <h3 className="text-lg font-semibold mb-2">Ready to Train</h3>
                    <p style={{ color: 'var(--text-muted)' }}>
                        Clean your dataset first, then click "Train All Models" to begin.
                    </p>
                </div>
            )}
        </div>
    )
}
