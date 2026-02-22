import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { BarChart3, RefreshCw, Users, TrendingDown, DollarSign, Phone } from 'lucide-react'
import {
    PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid,
    Tooltip, Legend, ResponsiveContainer, ComposedChart, Line, Area
} from 'recharts'
import { getEDA } from '../services/api'

const COLORS = {
    primary: '#8b5cf6',
    secondary: '#06b6d4',
    danger: '#ef4444',
    success: '#22c55e',
    warning: '#eab308',
    muted: '#64748b',
    churn: '#ef4444',
    noChurn: '#22c55e',
}

const DONUT_COLORS = ['#22c55e', '#ef4444']

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
            {label && <div style={{ color: '#f1f5f9', fontWeight: 600, marginBottom: 6 }}>{label}</div>}
            {payload.map((p, i) => (
                <div key={i} style={{ color: p.color || '#94a3b8', display: 'flex', gap: 8, alignItems: 'center' }}>
                    <span style={{ width: 8, height: 8, borderRadius: '50%', background: p.color, display: 'inline-block' }} />
                    {p.name}: <strong style={{ color: '#f1f5f9' }}>{typeof p.value === 'number' ? p.value.toLocaleString() : p.value}</strong>
                </div>
            ))}
        </div>
    )
}

export default function EDAPage() {
    const [eda, setEda] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const fetchEDA = async () => {
        setLoading(true)
        setError(null)
        try {
            const res = await getEDA()
            setEda(res.data)
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to compute EDA')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => { fetchEDA() }, [])

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center py-20 gap-4">
                <div className="spinner" style={{ width: 48, height: 48 }} />
                <p style={{ color: 'var(--text-secondary)' }}>Computing EDA visualizations...</p>
            </div>
        )
    }

    if (error) {
        return (
            <div className="text-center py-16">
                <BarChart3 size={48} className="mx-auto mb-4" style={{ color: 'var(--text-muted)' }} />
                <h3 className="text-lg font-semibold mb-2">EDA Unavailable</h3>
                <p style={{ color: 'var(--text-muted)' }} className="mb-4">{error}</p>
                <button className="btn-primary" onClick={fetchEDA}>Retry</button>
            </div>
        )
    }

    if (!eda) return null

    const { summary_stats: stats } = eda

    return (
        <div className="space-y-8">
            {/* ── Header ── */}
            <div className="flex items-center justify-between flex-wrap gap-4">
                <div>
                    <h1 className="text-3xl font-black tracking-tight flex items-center gap-3">
                        <BarChart3 size={28} style={{ color: '#8b5cf6' }} />
                        Exploratory Data Analysis
                    </h1>
                    <p className="mt-2" style={{ color: 'var(--text-secondary)' }}>
                        Interactive charts to explore patterns in the telco churn data.
                    </p>
                </div>
                <button className="btn-secondary flex items-center gap-2" onClick={fetchEDA}>
                    <RefreshCw size={16} /> Refresh
                </button>
            </div>

            {/* ── Summary Stats ── */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                {[
                    { label: 'Total Customers', value: stats.total_customers?.toLocaleString(), icon: Users, color: '#8b5cf6' },
                    { label: 'Churn Rate', value: `${stats.churn_rate}%`, icon: TrendingDown, color: '#ef4444' },
                    { label: 'Avg Tenure', value: `${stats.avg_tenure} mo`, icon: Phone, color: '#06b6d4' },
                    { label: 'Avg Monthly', value: `$${stats.avg_monthly_charges}`, icon: DollarSign, color: '#22c55e' },
                ].map(({ label, value, icon: Icon, color }, i) => (
                    <motion.div
                        key={label}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.05 }}
                        className="glass-card p-5 flex items-center gap-4"
                    >
                        <div className="w-10 h-10 rounded-lg flex items-center justify-center"
                            style={{ background: `${color}20`, color }}>
                            <Icon size={20} />
                        </div>
                        <div>
                            <div className="text-xl font-bold">{value}</div>
                            <div className="text-xs" style={{ color: 'var(--text-muted)' }}>{label}</div>
                        </div>
                    </motion.div>
                ))}
            </div>

            {/* ── Charts Grid ── */}
            <div className="grid lg:grid-cols-2 gap-6">
                {/* Churn Distribution (Donut) */}
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
                    className="glass-card p-6">
                    <h3 className="font-semibold mb-4">Churn Distribution</h3>
                    <ResponsiveContainer width="100%" height={280}>
                        <PieChart>
                            <Pie
                                data={eda.churn_distribution.data}
                                cx="50%" cy="50%"
                                innerRadius={70} outerRadius={110}
                                dataKey="value" nameKey="name"
                                stroke="none"
                            >
                                {eda.churn_distribution.data.map((_, i) => (
                                    <Cell key={i} fill={DONUT_COLORS[i]} />
                                ))}
                            </Pie>
                            <Tooltip content={<CustomTooltip />} />
                            <Legend
                                iconType="circle"
                                wrapperStyle={{ color: 'var(--text-secondary)', fontSize: 13 }}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </motion.div>

                {/* Tenure vs Churn (Histogram) */}
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
                    className="glass-card p-6">
                    <h3 className="font-semibold mb-4">Tenure vs Churn Status</h3>
                    <ResponsiveContainer width="100%" height={280}>
                        <BarChart data={eda.tenure_vs_churn.data}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                            <XAxis dataKey="bin" stroke="#64748b" fontSize={11} />
                            <YAxis stroke="#64748b" fontSize={11} />
                            <Tooltip content={<CustomTooltip />} />
                            <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
                            <Bar dataKey="No Churn" fill={COLORS.noChurn} radius={[4, 4, 0, 0]} />
                            <Bar dataKey="Churn" fill={COLORS.churn} radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </motion.div>

                {/* Churn by Category Charts */}
                {Object.entries(eda.churn_by_category || {}).map(([col, chart], idx) => (
                    <motion.div key={col}
                        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 + idx * 0.05 }}
                        className="glass-card p-6"
                    >
                        <h3 className="font-semibold mb-4">{chart.title}</h3>
                        <ResponsiveContainer width="100%" height={280}>
                            <ComposedChart data={chart.data}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                                <XAxis dataKey="category" stroke="#64748b" fontSize={11} />
                                <YAxis yAxisId="left" stroke="#64748b" fontSize={11} />
                                <YAxis yAxisId="right" orientation="right" stroke={COLORS.warning} fontSize={11}
                                    tickFormatter={(v) => `${v}%`} />
                                <Tooltip content={<CustomTooltip />} />
                                <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
                                <Bar yAxisId="left" dataKey="No Churn" fill={COLORS.noChurn} radius={[4, 4, 0, 0]} />
                                <Bar yAxisId="left" dataKey="Churn" fill={COLORS.churn} radius={[4, 4, 0, 0]} />
                                <Line yAxisId="right" type="monotone" dataKey="Churn Rate" stroke={COLORS.warning}
                                    strokeWidth={2} dot={{ fill: COLORS.warning, r: 4 }} />
                            </ComposedChart>
                        </ResponsiveContainer>
                    </motion.div>
                ))}

                {/* Monthly Charges Box Plot (as stats) */}
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
                    className="glass-card p-6">
                    <h3 className="font-semibold mb-4">Monthly Charges by Churn Status</h3>
                    <div className="grid grid-cols-2 gap-6 mt-4">
                        {eda.monthly_charges_boxplot.data.map((d) => (
                            <div key={d.category} className="p-4 rounded-xl"
                                style={{
                                    background: d.category === 'Churn' ? 'rgba(239,68,68,0.06)' : 'rgba(34,197,94,0.06)',
                                    border: `1px solid ${d.category === 'Churn' ? 'rgba(239,68,68,0.15)' : 'rgba(34,197,94,0.15)'}`
                                }}>
                                <div className="text-sm font-semibold mb-3" style={{ color: d.category === 'Churn' ? '#ef4444' : '#22c55e' }}>
                                    {d.category}
                                </div>
                                {[
                                    ['Min', d.min], ['Q1', d.q1], ['Median', d.median],
                                    ['Mean', d.mean], ['Q3', d.q3], ['Max', d.max]
                                ].map(([label, val]) => (
                                    <div key={label} className="flex justify-between text-sm py-1"
                                        style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                                        <span style={{ color: 'var(--text-muted)' }}>{label}</span>
                                        <span className="font-mono font-semibold">${val}</span>
                                    </div>
                                ))}
                            </div>
                        ))}
                    </div>
                </motion.div>

                {/* Support Calls vs Churn */}
                {eda.support_calls_vs_churn?.data?.length > 0 && (
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}
                        className="glass-card p-6">
                        <h3 className="font-semibold mb-4">Support Calls vs Churn Rate</h3>
                        <ResponsiveContainer width="100%" height={280}>
                            <ComposedChart data={eda.support_calls_vs_churn.data}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                                <XAxis dataKey="support_calls" stroke="#64748b" fontSize={11} />
                                <YAxis yAxisId="left" stroke="#64748b" fontSize={11} />
                                <YAxis yAxisId="right" orientation="right" stroke={COLORS.warning} fontSize={11}
                                    tickFormatter={(v) => `${v}%`} />
                                <Tooltip content={<CustomTooltip />} />
                                <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
                                <Bar yAxisId="left" dataKey="total_customers" fill={COLORS.primary} radius={[4, 4, 0, 0]} name="Total Customers" />
                                <Line yAxisId="right" type="monotone" dataKey="churn_rate" stroke={COLORS.danger}
                                    strokeWidth={2} dot={{ fill: COLORS.danger, r: 4 }} name="Churn Rate %" />
                            </ComposedChart>
                        </ResponsiveContainer>
                    </motion.div>
                )}

                {/* Correlation Heatmap (as table) */}
                {eda.correlation_heatmap?.columns && (
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
                        className="glass-card p-6 lg:col-span-2">
                        <h3 className="font-semibold mb-4">Feature Correlation Heatmap</h3>
                        <div className="overflow-x-auto">
                            <table style={{ fontSize: 11, borderCollapse: 'collapse', width: '100%' }}>
                                <thead>
                                    <tr>
                                        <th style={{ padding: '6px 8px', textAlign: 'left', color: 'var(--text-muted)', fontSize: 10 }}></th>
                                        {eda.correlation_heatmap.columns.map(col => (
                                            <th key={col} style={{
                                                padding: '6px 4px', textAlign: 'center', color: 'var(--text-muted)',
                                                fontSize: 9, maxWidth: 60, overflow: 'hidden', textOverflow: 'ellipsis',
                                                whiteSpace: 'nowrap', writingMode: 'vertical-lr', transform: 'rotate(180deg)', height: 80,
                                            }}>
                                                {col}
                                            </th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {eda.correlation_heatmap.columns.map(row => (
                                        <tr key={row}>
                                            <td style={{ padding: '4px 8px', color: 'var(--text-secondary)', fontSize: 10, whiteSpace: 'nowrap', fontWeight: 600 }}>
                                                {row}
                                            </td>
                                            {eda.correlation_heatmap.columns.map(col => {
                                                const cell = eda.correlation_heatmap.data.find(d => d.x === col && d.y === row)
                                                const val = cell?.value ?? 0
                                                const absVal = Math.abs(val)
                                                const bg = val > 0
                                                    ? `rgba(139, 92, 246, ${absVal * 0.6})`
                                                    : `rgba(239, 68, 68, ${absVal * 0.6})`
                                                return (
                                                    <td key={col} style={{
                                                        padding: '4px', textAlign: 'center',
                                                        background: bg,
                                                        color: absVal > 0.3 ? '#f1f5f9' : 'var(--text-muted)',
                                                        fontSize: 10, fontWeight: absVal > 0.3 ? 600 : 400,
                                                        borderRadius: 2,
                                                    }}>
                                                        {val.toFixed(2)}
                                                    </td>
                                                )
                                            })}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </motion.div>
                )}
            </div>
        </div>
    )
}
