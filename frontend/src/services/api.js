import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '';

const api = axios.create({
    baseURL: `${API_BASE}/api`,
    timeout: 300000, // 5 min for model training
    headers: { 'Content-Type': 'application/json' },
});

// ── Dataset ──
export const loadDefaultDataset = () => api.get('/load-default');
export const uploadDataset = (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
};
export const getDatasetPreview = () => api.get('/dataset-preview');

// ── Cleaning ──
export const getCleaningReport = () => api.get('/cleaning-report');
export const cleanDataset = () => api.post('/clean');

// ── EDA ──
export const getEDA = () => api.get('/eda');

// ── Training ──
export const trainModels = (tuneHyperparameters = false) =>
    api.post('/train', { tune_hyperparameters: tuneHyperparameters });
export const getModels = () => api.get('/models');
export const getEvaluation = () => api.get('/evaluation');

// ── SHAP ──
export const getSHAP = (modelName) => api.get(`/shap/${modelName}`);

// ── Prediction ──
export const predictChurn = (modelName, customerData) =>
    api.post('/predict', { model_name: modelName, customer_data: customerData });

// ── Quick Predict ──
export const getQuickPredictStatus = () => api.get('/quick-predict/status');
export const quickPredict = (modelName, customerData) =>
    api.post('/quick-predict', { model_name: modelName, customer_data: customerData });

// ── Health ──
export const getHealth = () => api.get('/health');

export default api;
