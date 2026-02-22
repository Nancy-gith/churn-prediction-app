import React, { useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import { Upload, Database, FileSpreadsheet, CheckCircle2, AlertCircle, ChevronRight, Zap } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { loadDefaultDataset, uploadDataset } from '../services/api'

export default function LandingPage() {
    const [loading, setLoading] = useState(false)
    const [dragActive, setDragActive] = useState(false)
    const [preview, setPreview] = useState(null)
    const [error, setError] = useState(null)
    const [loadType, setLoadType] = useState(null) // 'default' or 'upload'
    const navigate = useNavigate()

    const handleLoadDefault = async () => {
        setLoading(true)
        setError(null)
        setLoadType('default')
        try {
            const res = await loadDefaultDataset()
            setPreview(res.data.preview)
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to load dataset')
        } finally {
            setLoading(false)
        }
    }

    const handleFileUpload = async (file) => {
        if (!file || !file.name.endsWith('.csv')) {
            setError('Please upload a CSV file')
            return
        }
        setLoading(true)
        setError(null)
        setLoadType('upload')
        try {
            const res = await uploadDataset(file)
            setPreview(res.data.preview)
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to upload file')
        } finally {
            setLoading(false)
        }
    }

    const handleDrop = useCallback((e) => {
        e.preventDefault()
        setDragActive(false)
        const file = e.dataTransfer.files[0]
        handleFileUpload(file)
    }, [])

    const handleDrag = useCallback((e) => {
        e.preventDefault()
        if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true)
        else if (e.type === 'dragleave') setDragActive(false)
    }, [])

    return (
        <div className="space-y-8">
            {/* ── Hero Section ── */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center py-8"
            >
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-semibold mb-6"
                    style={{ background: 'rgba(139,92,246,0.1)', color: '#a78bfa', border: '1px solid rgba(139,92,246,0.2)' }}>
                    <Database size={14} />
                    POWERED BY 6 ML MODELS
                </div>
                <h1 className="text-4xl sm:text-5xl font-black tracking-tight mb-4"
                    style={{ background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                    Predict Customer Churn
                </h1>
                <p className="text-lg max-w-2xl mx-auto" style={{ color: 'var(--text-secondary)' }}>
                    Upload your telecom dataset or use the built-in IBM Telco dataset.
                    Train industry-standard ML models and predict which customers are at risk of leaving.
                </p>
            </motion.div>

            {/* ── Upload Area ── */}
            <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
                {/* Drag & Drop */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 }}
                >
                    <div
                        className={`dropzone ${dragActive ? 'active' : ''}`}
                        onDragEnter={handleDrag}
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={handleDrop}
                        onClick={() => document.getElementById('file-input').click()}
                    >
                        <input
                            id="file-input"
                            type="file"
                            accept=".csv"
                            className="hidden"
                            onChange={(e) => handleFileUpload(e.target.files[0])}
                        />
                        <Upload size={40} style={{ color: '#8b5cf6' }} className="mx-auto mb-4" />
                        <h3 className="text-lg font-bold mb-2">Upload Your Dataset</h3>
                        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
                            Drag & drop a CSV file here, or click to browse
                        </p>
                        <p className="text-xs mt-3" style={{ color: 'var(--text-muted)' }}>
                            Supports: .csv files with churn data
                        </p>
                    </div>
                </motion.div>

                {/* Default Dataset */}
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 }}
                >
                    <div className="glass-card p-8 h-full flex flex-col items-center justify-center text-center">
                        <FileSpreadsheet size={40} style={{ color: '#06b6d4' }} className="mb-4" />
                        <h3 className="text-lg font-bold mb-2">Use Default Dataset</h3>
                        <p className="text-sm mb-6" style={{ color: 'var(--text-muted)' }}>
                            IBM Telco Customer Churn dataset with 7,043 rows and 21 features. Perfect for getting started.
                        </p>
                        <button
                            className="btn-primary flex items-center gap-2"
                            onClick={handleLoadDefault}
                            disabled={loading}
                        >
                            {loading && loadType === 'default' ? (
                                <>
                                    <div className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
                                    Loading...
                                </>
                            ) : (
                                <>
                                    <Database size={16} />
                                    Load Default Dataset
                                </>
                            )}
                        </button>
                    </div>
                </motion.div>
            </div>

            {/* ── Error ── */}
            {error && (
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="max-w-4xl mx-auto glass-card p-4 flex items-center gap-3"
                    style={{ borderColor: 'rgba(239, 68, 68, 0.3)' }}
                >
                    <AlertCircle size={20} style={{ color: '#ef4444' }} />
                    <span style={{ color: '#ef4444' }}>{error}</span>
                </motion.div>
            )}

            {/* ── Loading ── */}
            {loading && (
                <div className="flex items-center justify-center gap-3 py-8">
                    <div className="spinner" />
                    <span style={{ color: 'var(--text-secondary)' }}>Loading dataset...</span>
                </div>
            )}

            {/* ── Dataset Preview ── */}
            {preview && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-6"
                >
                    {/* Summary Cards */}
                    <div className="flex items-center gap-3 mb-4">
                        <CheckCircle2 size={24} style={{ color: '#22c55e' }} />
                        <h2 className="text-xl font-bold">Dataset Loaded Successfully</h2>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                        <div className="glass-card metric-card">
                            <div className="metric-value">{preview.shape.rows.toLocaleString()}</div>
                            <div className="metric-label">Rows</div>
                        </div>
                        <div className="glass-card metric-card">
                            <div className="metric-value">{preview.shape.columns}</div>
                            <div className="metric-label">Columns</div>
                        </div>
                        <div className="glass-card metric-card">
                            <div className="metric-value">
                                {Object.values(preview.missing_values).reduce((a, b) => a + b, 0)}
                            </div>
                            <div className="metric-label">Missing Values</div>
                        </div>
                        <div className="glass-card metric-card">
                            <div className="metric-value">
                                {Object.values(preview.dtypes).filter(d => d.includes('object')).length}
                            </div>
                            <div className="metric-label">Categoricals</div>
                        </div>
                    </div>

                    {/* Data Table */}
                    <div className="glass-card overflow-hidden">
                        <div className="px-6 py-4 flex items-center justify-between"
                            style={{ borderBottom: '1px solid var(--glass-border)' }}>
                            <h3 className="font-semibold">Data Preview (First 20 Rows)</h3>
                            <div className="flex items-center gap-3">
                                <button
                                    className="flex items-center gap-2 text-sm px-4 py-2 rounded-lg font-semibold transition-all"
                                    style={{ background: 'linear-gradient(135deg, #f59e0b, #ef4444)', color: '#fff', border: 'none' }}
                                    onClick={() => navigate('/quick-predict')}
                                >
                                    <Zap size={16} />
                                    ⚡ Quick Predict
                                </button>
                                <button
                                    className="btn-primary flex items-center gap-2 text-sm"
                                    onClick={() => navigate('/cleaning')}
                                >
                                    Next: Clean Data
                                    <ChevronRight size={16} />
                                </button>
                            </div>
                        </div>
                        <div className="overflow-x-auto max-h-96">
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        {preview.columns.map(col => (
                                            <th key={col}>{col}</th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {preview.head.map((row, i) => (
                                        <tr key={i}>
                                            {preview.columns.map(col => (
                                                <td key={col} className="whitespace-nowrap">{String(row[col] ?? '')}</td>
                                            ))}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </motion.div>
            )}
        </div>
    )
}
