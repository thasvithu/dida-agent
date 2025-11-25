import React from 'react';
import { useDataStore } from '../store/useDataStore';

function DataPreview() {
    const { preview, columnNames, rows, columns } = useDataStore();

    if (!preview || preview.length === 0) {
        return null;
    }

    return (
        <div className="card">
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h2 className="text-xl font-bold text-slate-800">Data Preview</h2>
                    <p className="text-sm text-slate-500 mt-1">
                        Showing first {preview.length} of {rows?.toLocaleString()} rows
                    </p>
                </div>
                <div className="flex space-x-4 text-sm">
                    <div className="px-4 py-2 bg-primary-50 rounded-lg">
                        <span className="text-slate-600">Rows:</span>
                        <span className="ml-2 font-bold text-primary-700">{rows?.toLocaleString()}</span>
                    </div>
                    <div className="px-4 py-2 bg-secondary-50 rounded-lg">
                        <span className="text-slate-600">Columns:</span>
                        <span className="ml-2 font-bold text-secondary-700">{columns}</span>
                    </div>
                </div>
            </div>

            <div className="overflow-x-auto rounded-lg border border-slate-200">
                <table className="w-full text-sm">
                    <thead className="bg-gradient-to-r from-slate-50 to-slate-100 border-b-2 border-slate-200">
                        <tr>
                            <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider sticky left-0 bg-slate-100">
                                #
                            </th>
                            {columnNames.map((col, idx) => (
                                <th
                                    key={idx}
                                    className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider whitespace-nowrap"
                                >
                                    {col}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-slate-100">
                        {preview.map((row, rowIdx) => (
                            <tr
                                key={rowIdx}
                                className="hover:bg-slate-50 transition-colors"
                            >
                                <td className="px-4 py-3 text-slate-400 font-medium sticky left-0 bg-white">
                                    {rowIdx + 1}
                                </td>
                                {columnNames.map((col, colIdx) => {
                                    const value = row[col];
                                    const displayValue = value === null || value === undefined ? (
                                        <span className="text-slate-400 italic">null</span>
                                    ) : typeof value === 'number' ? (
                                        <span className="text-blue-700 font-mono">{value}</span>
                                    ) : typeof value === 'boolean' ? (
                                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${value ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                                            }`}>
                                            {value.toString()}
                                        </span>
                                    ) : (
                                        <span className="text-slate-700">{String(value)}</span>
                                    );

                                    return (
                                        <td
                                            key={colIdx}
                                            className="px-4 py-3 whitespace-nowrap"
                                        >
                                            {displayValue}
                                        </td>
                                    );
                                })}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-sm text-blue-800">
                    💡 <strong>Tip:</strong> This is a preview of your data. Click on the "Analysis" tab to get AI-powered insights about your dataset.
                </p>
            </div>
        </div>
    );
}

export default DataPreview;
