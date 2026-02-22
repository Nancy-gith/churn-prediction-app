import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Wrench, CheckCircle2, AlertTriangle, ArrowRight, ChevronRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { cleanDataset, getCleaningReport } from '../services/api'

export default function CleaningPage() {
    const [loading, setLoading] = useState(false)
    const [report, setReport] = useState(null)
    const [error, setError] = useState(null)
    const navigate = useNavigate()

    const handleClean = async () => {
        setLoading(true)
        setError(null)
        try {
            const res = await cleanDataset()
            setReport(res.data.report)
        } catch (err) {
            setError(err.response?.data?.detail || 'Cleaning failed')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        getCleaningReport()
            .then(res => {
                if (res.data.before && !res.data.cleaned) {
                    // Pre-cleaning preview available
                }
            })
            .catch(() => { })
    }, [])

    return (
        <div className="space-y-8">
            {/* ── Header ── */}
            <div className="flex items-center justify-between flex-wrap gap-4">
                <div>
                    <h1 className="text-3xl font-black tracking-tight flex items-center gap-3">
                        <Wrench size={28} style={{ color: '#8b5cf6' }} />
                        Data Cleaning Pipeline
                    </h1>
                    <p className="mt-2" style={{ color: 'var(--text-secondary)' }}>
                        Fix missing values, correct data types, detect outliers, and prepare data for ML.
                    </p>
                </div>
                <div className="flex gap-3">
                    <button className="btn-primary flex items-center gap-2" onClick={handleClean} disabled={loading}>
                        {loading ? (
                            <>
                                <div className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
                                Cleaning...
                            </>
                        ) : (
                            <>
                                <Wrench size={16} />
                                Run Cleaning Pipeline
                            </>
                        )}
                    </button>
                    {report && (
                        <button className="btn-secondary flex items-center gap-2" onClick={() => navigate('/eda')}>
                            Next: EDA
                            <ChevronRight size={16} />
                        </button>
                    )}
                </div>
            </div>

            {error && (
                <div className="glass-card p-4 flex items-center gap-3" style={{ borderColor: 'rgba(239, 68, 68, 0.3)' }}>
                    <AlertTriangle size={20} style={{ color: '#ef4444' }} />
                    <span style={{ color: '#ef4444' }}>{error}</span>
                </div>
            )}

            {loading && (
                <div className="flex flex-col items-center gap-4 py-12">
                    <div className="spinner" style={{ width: 48, height: 48 }} />
                    <p style={{ color: 'var(--text-secondary)' }}>Running cleaning pipeline...</p>
                    <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                        Fixing types → Imputing missing → Removing outliers → Encoding target
                    </p>
                </div>
            )}

            {report && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-8"
                >
                    {/* ── Shape Before/After ── */}
                    <div className="grid sm:grid-cols-3 gap-4">
                        <div className="glass-card p-6">
                            <div className="text-xs font-semibold mb-2 uppercase" style={{ color: 'var(--text-muted)' }}>Before</div>
                            <div className="text-2xl font-bold">{report.shape_before.rows.toLocaleString()} × {report.shape_before.columns}</div>
                            <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>rows × columns</div>
                        </div>
                        <div className="flex items-center justify-center">
                            <ArrowRight size={32} style={{ color: '#8b5cf6' }} />
                        </div>
                        <div className="glass-card p-6">
                            <div className="text-xs font-semibold mb-2 uppercase" style={{ color: 'var(--text-muted)' }}>After</div>
                            <div className="text-2xl font-bold"
                                style={{ background: 'var(--gradient-success)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                                {report.shape_after.rows.toLocaleString()} × {report.shape_after.columns}
                            </div>
                            <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>rows × columns</div>
                        </div>
                    </div>

                    {/* ── Transformations Applied ── */}
                    <div className="glass-card overflow-hidden">
                        <div className="px-6 py-4" style={{ borderBottom: '1px solid var(--glass-border)' }}>
                            <h3 className="font-semibold flex items-center gap-2">
                                <CheckCircle2 size={18} style={{ color: '#22c55e' }} />
                                Transformations Applied ({report.transformations.length} steps)
                            </h3>
                        </div>
                        <div className="divide-y" style={{ borderColor: 'rgba(255,255,255,0.03)' }}>
                            {report.transformations.map((t, i) => (
                                <motion.div
                                    key={i}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: i * 0.05 }}
                                    className="px-6 py-4 flex flex-col sm:flex-row sm:items-center gap-2"
                                >
                                    <div className="flex items-center gap-3 min-w-[200px]">
                                        <span className="w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold"
                                            style={{ background: 'rgba(139,92,246,0.15)', color: '#a78bfa' }}>
                                            {i + 1}
                                        </span>
                                        <span className="font-semibold text-sm">{t.step}</span>
                                    </div>
                                    {t.action && (
                                        <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                                            {t.action}
                                        </span>
                                    )}
                                    {t.reason && (
                                        <span className="text-xs px-3 py-1 rounded-full ml-auto whitespace-nowrap"
                                            style={{ background: 'rgba(6,182,212,0.1)', color: '#06b6d4' }}>
                                            {t.reason}
                                        </span>
                                    )}
                                </motion.div>
                            ))}
                        </div>
                    </div>

                    {/* ── Missing Values Before ── */}
                    {report.before && Object.keys(report.before.missing_values || {}).length > 0 && (
                        <div className="glass-card overflow-hidden">
                            <div className="px-6 py-4" style={{ borderBottom: '1px solid var(--glass-border)' }}>
                                <h3 className="font-semibold">Missing Values (Before Cleaning)</h3>
                            </div>
                            <div className="p-6">
                                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                                    {Object.entries(report.before.missing_values).map(([col, info]) => (
                                        <div key={col} className="flex items-center justify-between p-3 rounded-lg"
                                            style={{ background: 'rgba(239,68,68,0.05)', border: '1px solid rgba(239,68,68,0.1)' }}>
                                            <div>
                                                <div className="font-semibold text-sm">{col}</div>
                                                <div className="text-xs" style={{ color: 'var(--text-muted)' }}>
                                                    {info.percentage}% missing
                                                </div>
                                            </div>
                                            <div className="badge badge-danger">{info.count}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* ── Outlier Details ── */}
                    {Object.keys(report.outlier_details || {}).length > 0 && (
                        <div className="glass-card overflow-hidden">
                            <div className="px-6 py-4" style={{ borderBottom: '1px solid var(--glass-border)' }}>
                                <h3 className="font-semibold flex items-center gap-2">
                                    <AlertTriangle size={18} style={{ color: '#eab308' }} />
                                    Outlier Detection & Treatment
                                </h3>
                            </div>
                            <div className="p-6">
                                <div className="grid sm:grid-cols-2 gap-4">
                                    {Object.entries(report.outlier_details).map(([col, info]) => (
                                        <div key={col} className="p-4 rounded-lg"
                                            style={{ background: 'rgba(234,179,8,0.05)', border: '1px solid rgba(234,179,8,0.1)' }}>
                                            <div className="font-semibold mb-2">{col}</div>
                                            <div className="space-y-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
                                                <div>{info.outliers_found} outliers found</div>
                                                <div>Range: [{info.lower_bound}, {info.upper_bound}]</div>
                                                <div className="text-xs" style={{ color: 'var(--text-muted)' }}>{info.treatment}</div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* ── Data Type Changes ── */}
                    {report.before && report.before.data_type_issues?.length > 0 && (
                        <div className="glass-card overflow-hidden">
                            <div className="px-6 py-4" style={{ borderBottom: '1px solid var(--glass-border)' }}>
                                <h3 className="font-semibold">Data Type Corrections</h3>
                            </div>
                            <div className="p-6">
                                <table className="data-table">
                                    <thead>
                                        <tr>
                                            <th>Column</th>
                                            <th>Original Type</th>
                                            <th>Corrected To</th>
                                            <th>Reason</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {report.before.data_type_issues.map((issue, i) => (
                                            <tr key={i}>
                                                <td className="font-semibold">{issue.column}</td>
                                                <td><span className="badge badge-danger">{issue.current_type}</span></td>
                                                <td><span className="badge badge-success">{issue.expected_type}</span></td>
                                                <td>{issue.reason}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}
                </motion.div>
            )}

            {!report && !loading && (
                <div className="text-center py-16">
                    <Wrench size={48} className="mx-auto mb-4" style={{ color: 'var(--text-muted)' }} />
                    <h3 className="text-lg font-semibold mb-2">Ready to Clean</h3>
                    <p style={{ color: 'var(--text-muted)' }}>
                        Load a dataset first, then click "Run Cleaning Pipeline" to start.
                    </p>
                </div>
            )}
        </div>
    )
}
