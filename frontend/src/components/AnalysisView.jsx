import React, { useEffect } from 'react';
import { Sparkles, AlertTriangle, CheckCircle2, HelpCircle, TrendingUp, Loader2 } from 'lucide-react';
import { useDataStore } from '../store/useDataStore';

function AnalysisView() {
    const {
        analysis, isAnalyzing, analysisError, analyzeDataset,
        cleanDataset, isCleaning, cleaningResult,
        engineerFeatures, isEngineeringFeatures, featureEngineering,
        generateReport, isGeneratingReport, report
    } = useDataStore();

    useEffect(() => {
        // Auto-trigger analysis if not already done
        if (!analysis && !isAnalyzing && !analysisError) {
            analyzeDataset();
        }
    }, []);

    const handleAnalyze = () => {
        analyzeDataset();
    };

    if (isAnalyzing) {
        return (
            <div className="card">
                <div className="text-center py-12">
                    <div className="w-16 h-16 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mx-auto mb-4"></div>
                    <h3 className="text-xl font-semibold text-slate-800 mb-2">Analyzing Your Dataset</h3>
                    <p className="text-slate-600">
                        Our AI is examining your data structure, detecting patterns, and generating insights...
                    </p>
                </div>
            </div>
        );
    }

    if (analysisError) {
        return (
            <div className="card">
                <div className="text-center py-12">
                    <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <AlertTriangle className="w-8 h-8 text-red-600" />
                    </div>
                    <h3 className="text-xl font-semibold text-slate-800 mb-2">Analysis Failed</h3>
                    <p className="text-slate-600 mb-4">{analysisError}</p>
                    <button onClick={handleAnalyze} className="btn-primary">
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    if (!analysis) {
        return (
            <div className="card">
                <div className="text-center py-12">
                    <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Sparkles className="w-8 h-8 text-primary-600" />
                    </div>
                    <h3 className="text-xl font-semibold text-slate-800 mb-2">Ready to Analyze</h3>
                    <p className="text-slate-600 mb-4">
                        Click the button below to start AI-powered analysis of your dataset
                    </p>
                    <button onClick={handleAnalyze} className="btn-primary">
                        <Sparkles className="w-4 h-4 inline mr-2" />
                        Start Analysis
                    </button>
                </div>
            </div>
        );
    }

    const getDataTypeBadge = (dataType) => {
        const badges = {
            numeric: 'badge-info',
            categorical: 'badge-warning',
            datetime: 'badge-success',
            text: 'badge bg-purple-100 text-purple-800',
            boolean: 'badge bg-indigo-100 text-indigo-800',
            unknown: 'badge bg-slate-100 text-slate-800',
        };
        return badges[dataType] || 'badge';
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="card bg-gradient-to-br from-primary-50 to-secondary-50 border-primary-200">
                <div className="flex items-start justify-between">
                    <div>
                        <h2 className="text-2xl font-bold text-slate-800 mb-2">
                            <Sparkles className="w-6 h-6 inline mr-2 text-primary-600" />
                            Dataset Analysis
                        </h2>
                        <p className="text-slate-600">
                            AI-powered insights about your data structure and quality
                        </p>
                    </div>
                    <div className="text-right">
                        <div className="text-3xl font-bold text-primary-600">
                            {analysis.overall_quality_score}
                            <span className="text-lg text-slate-500">/100</span>
                        </div>
                        <p className="text-sm text-slate-600">Quality Score</p>
                    </div>
                </div>
            </div>

            {/* Warnings */}
            {analysis.warnings && analysis.warnings.length > 0 && (
                <div className="card bg-yellow-50 border-yellow-200">
                    <h3 className="font-semibold text-yellow-900 mb-3 flex items-center">
                        <AlertTriangle className="w-5 h-5 mr-2" />
                        Warnings & Issues
                    </h3>
                    <ul className="space-y-2">
                        {analysis.warnings.map((warning, idx) => (
                            <li key={idx} className="text-sm text-yellow-800 flex items-start">
                                <span className="w-1.5 h-1.5 bg-yellow-600 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                                <span>{warning}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Domain Insights */}
            {analysis.domain_insights && analysis.domain_insights.length > 0 && (
                <div className="card bg-blue-50 border-blue-200">
                    <h3 className="font-semibold text-blue-900 mb-3 flex items-center">
                        <TrendingUp className="w-5 h-5 mr-2" />
                        Domain Insights
                    </h3>
                    <ul className="space-y-2">
                        {analysis.domain_insights.map((insight, idx) => (
                            <li key={idx} className="text-sm text-blue-800 flex items-start">
                                <span className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                                <span>{insight}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Suggested Target */}
            {analysis.suggested_target && (
                <div className="card bg-green-50 border-green-200">
                    <h3 className="font-semibold text-green-900 mb-2 flex items-center">
                        <CheckCircle2 className="w-5 h-5 mr-2" />
                        Suggested Target Variable
                    </h3>
                    <p className="text-sm text-green-800">
                        For machine learning tasks, we recommend using <strong className="font-mono">{analysis.suggested_target}</strong> as your target variable.
                    </p>
                </div>
            )}

            {/* Questions for User */}
            {analysis.questions_for_user && analysis.questions_for_user.length > 0 && (
                <div className="card bg-purple-50 border-purple-200">
                    <h3 className="font-semibold text-purple-900 mb-3 flex items-center">
                        <HelpCircle className="w-5 h-5 mr-2" />
                        Questions to Clarify
                    </h3>
                    <ul className="space-y-2">
                        {analysis.questions_for_user.map((question, idx) => (
                            <li key={idx} className="text-sm text-purple-800 flex items-start">
                                <span className="font-bold mr-2">{idx + 1}.</span>
                                <span>{question}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Column Details */}
            <div className="card">
                <h3 className="text-xl font-bold text-slate-800 mb-4">Column Analysis</h3>
                <div className="space-y-4">
                    {analysis.columns && analysis.columns.map((col, idx) => (
                        <div
                            key={idx}
                            className="p-4 bg-slate-50 rounded-lg border border-slate-200 hover:border-primary-300 transition-colors"
                        >
                            <div className="flex items-start justify-between mb-2">
                                <div className="flex-1">
                                    <div className="flex-1">
                                        <div className="flex items-center space-x-2 mb-1">
                                            <h4 className="font-mono font-semibold text-slate-800">{col.name}</h4>
                                            <span className={`badge ${getDataTypeBadge(col.data_type)}`}>
                                                {col.data_type}
                                            </span>
                                            {col.is_primary_key && (
                                                <span className="badge bg-amber-100 text-amber-800">Primary Key</span>
                                            )}
                                        </div>
                                        <p className="text-sm text-slate-600">{col.inferred_meaning}</p>
                                    </div>
                                </div>
                            </div>

                            <div className="grid grid-cols-3 gap-4 mt-3 text-sm">
                                <div>
                                    <span className="text-slate-500">Null Values:</span>
                                    <span className={`ml-2 font-semibold ${col.null_percentage > 50 ? 'text-red-600' :
                                        col.null_percentage > 20 ? 'text-yellow-600' :
                                            'text-green-600'
                                        }`}>
                                        {col.null_count} ({col.null_percentage.toFixed(1)}%)
                                    </span>
                                </div>
                                <div>
                                    <span className="text-slate-500">Unique:</span>
                                    <span className="ml-2 font-semibold text-slate-700">{col.unique_count}</span>
                                </div>
                                <div>
                                    <span className="text-slate-500">Samples:</span>
                                    <span className="ml-2 font-mono text-xs text-slate-600">
                                        {col.sample_values.slice(0, 3).join(', ')}
                                    </span>
                                </div>
                            </div>

                            {col.detected_issues && col.detected_issues.length > 0 && (
                                <div className="mt-3 p-2 bg-red-50 rounded border border-red-200">
                                    <p className="text-xs font-semibold text-red-900 mb-1">Issues Detected:</p>
                                    <ul className="text-xs text-red-700 space-y-0.5">
                                        {col.detected_issues.map((issue, i) => (
                                            <li key={i}>• {issue}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {col.suggested_action && (
                                <div className="mt-3 p-2 bg-blue-50 rounded border border-blue-200">
                                    <p className="text-xs font-semibold text-blue-900 mb-1">Suggested Action:</p>
                                    <p className="text-xs text-blue-700">{col.suggested_action}</p>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Action Buttons */}
            <div className="card bg-gradient-to-r from-primary-50 to-secondary-50 border-primary-200">
                <h3 className="font-semibold text-slate-800 mb-3">Next Steps</h3>
                <div className="flex space-x-3">
                    <button
                        className="btn-primary flex-1"
                        onClick={() => cleanDataset()}
                        disabled={isCleaning}
                    >
                        {isCleaning ? <Loader2 className="w-4 h-4 inline mr-2 animate-spin" /> : <Sparkles className="w-4 h-4 inline mr-2" />}
                        {isCleaning ? 'Cleaning...' : 'Clean Dataset'}
                    </button>
                    <button
                        className="btn-secondary flex-1"
                        onClick={() => engineerFeatures()}
                        disabled={isEngineeringFeatures}
                    >
                        {isEngineeringFeatures ? <Loader2 className="w-4 h-4 inline mr-2 animate-spin" /> : <TrendingUp className="w-4 h-4 inline mr-2" />}
                        {isEngineeringFeatures ? 'Engineering...' : 'Feature Engineering'}
                    </button>
                    <button
                        className="btn-secondary flex-1"
                        onClick={() => generateReport()}
                        disabled={isGeneratingReport}
                    >
                        {isGeneratingReport ? <Loader2 className="w-4 h-4 inline mr-2 animate-spin" /> : <TrendingUp className="w-4 h-4 inline mr-2" />}
                        {isGeneratingReport ? 'Generating...' : 'Generate Report'}
                    </button>
                </div>

                {/* Results Feedback */}
                {cleaningResult && (
                    <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                        <div className="flex items-center text-green-800 font-medium mb-1">
                            <CheckCircle2 className="w-4 h-4 mr-2" />
                            Dataset Cleaned Successfully
                        </div>
                        <p className="text-sm text-green-700">{cleaningResult.summary}</p>
                    </div>
                )}

                {featureEngineering && (
                    <div className="mt-4 p-3 bg-purple-50 border border-purple-200 rounded-lg">
                        <div className="flex items-center text-purple-800 font-medium mb-1">
                            <CheckCircle2 className="w-4 h-4 mr-2" />
                            Features Engineered Successfully
                        </div>
                        <p className="text-sm text-purple-700">{featureEngineering.summary}</p>
                    </div>
                )}

                {report && (
                    <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                        <div className="flex items-center justify-between">
                            <div>
                                <div className="flex items-center text-blue-800 font-medium mb-1">
                                    <CheckCircle2 className="w-4 h-4 mr-2" />
                                    Report Generated Successfully
                                </div>
                                <p className="text-sm text-blue-700">Your comprehensive analysis report is ready.</p>
                            </div>
                            <a
                                href={report.report_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="btn-primary text-sm py-1.5 px-3"
                            >
                                Download PDF
                            </a>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default AnalysisView;
