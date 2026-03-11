import React, { useState, useEffect, useRef } from 'react';
import { Table, Play, Plus, Trash2, Save, Database, Search, Globe, User, RefreshCw, AlertCircle, Zap, Download, Upload } from 'lucide-react';
import { BackendService } from '../../services/backendService';
import { useToast } from './Toast';

export interface ClayColumn {
  id: string;
  label: string;
  type: 'text' | 'url' | 'enrichment';
  width: number;
  enrichmentPrompt?: string;
}

export interface ClayRow {
  id: string;
  data: Record<string, any>;
}

export interface ClayTableData {
  columns: ClayColumn[];
  rows: ClayRow[];
}

// Initial State — Clean Slate for User
const INITIAL_DATA: ClayTableData = {
  columns: [
    { id: 'c1', label: 'Company Name', type: 'text', width: 200 },
    { id: 'c2', label: 'Website', type: 'url', width: 200 },
    { id: 'c3', label: 'Enrich: CEO Name', type: 'enrichment', width: 200, enrichmentPrompt: "Find the CEO's full name for this company." },
    { id: 'c4', label: 'Enrich: Latest News', type: 'enrichment', width: 300, enrichmentPrompt: "Find the most recent news headline or press release for this company." }
  ],
  rows: []
};

const MarketingClay: React.FC = () => {
  const [tableData, setTableData] = useState<ClayTableData>(INITIAL_DATA);
  const [isEnriching, setIsEnriching] = useState(false);
  const [enrichmentQueue, setEnrichmentQueue] = useState<{ rowId: string, colId: string }[]>([]);
  const [newColumnName, setNewColumnName] = useState('');
  const [newColumnPrompt, setNewColumnPrompt] = useState('');
  const [showAddCol, setShowAddCol] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { addToast } = useToast();

  // Load from LocalStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('clay_table_v1');
    if (saved) {
      try {
        setTableData(JSON.parse(saved));
      } catch (e) {
        console.error("Failed to load saved table");
      }
    }
  }, []);

  // Save to LocalStorage on change
  useEffect(() => {
    localStorage.setItem('clay_table_v1', JSON.stringify(tableData));
  }, [tableData]);

  // Queue Processor (Simulating BullMQ Worker)
  useEffect(() => {
    const processQueue = async () => {
      if (enrichmentQueue.length === 0 || isEnriching) return;

      setIsEnriching(true);
      const job = enrichmentQueue[0]; // FIFO

      // Find context
      const row = tableData.rows.find(r => r.id === job.rowId);
      const col = tableData.columns.find(c => c.id === job.colId);

      if (row && col && col.enrichmentPrompt) {
        try {
          // Update Status to Loading
          updateCell(job.rowId, job.colId, "Thinking...");

          // Call Backend
          const result = await BackendService.enrichData(row.data, col.enrichmentPrompt);

          // Update Result (Backend returns { enrichedData: ... })
          updateCell(job.rowId, job.colId, result.enrichedData);
        } catch (e) {
          updateCell(job.rowId, job.colId, "Error");
        }
      }

      // Remove job and continue
      setEnrichmentQueue(prev => prev.slice(1));
      setIsEnriching(false);
    };

    processQueue();
  }, [enrichmentQueue, isEnriching, tableData]);

  const updateCell = (rowId: string, colId: string, value: any) => {
    setTableData(prev => ({
      ...prev,
      rows: prev.rows.map(r => r.id === rowId ? { ...r, data: { ...r.data, [colId]: value } } : r)
    }));
  };

  const addRow = () => {
    const newRow: ClayRow = {
      id: Date.now().toString(),
      data: {}
    };
    setTableData(prev => ({ ...prev, rows: [...prev.rows, newRow] }));
    addToast('Row added', 'success');
  };

  const addColumn = (type: 'text' | 'enrichment') => {
    if (!newColumnName) return;
    const newCol: ClayColumn = {
      id: `c${Date.now()}`,
      label: newColumnName,
      type: type,
      width: 200,
      enrichmentPrompt: type === 'enrichment' ? newColumnPrompt : undefined
    };
    setTableData(prev => ({ ...prev, columns: [...prev.columns, newCol] }));
    setNewColumnName('');
    setNewColumnPrompt('');
    setShowAddCol(false);
    addToast('Column added', 'success');
  };

  const runEnrichmentForColumn = (colId: string) => {
    // Add all rows to queue for this column
    const jobs = tableData.rows.map(row => ({ rowId: row.id, colId }));
    setEnrichmentQueue(prev => [...prev, ...jobs]);
    addToast(`Queued enrichment for ${jobs.length} rows`, 'success');
  };

  const clearStorage = () => {
    if (confirm("Reset table to default? This cannot be undone.")) {
      setTableData(INITIAL_DATA);
      addToast('Table reset to defaults', 'info');
    }
  };

  // --- CSV Handlers ---
  const handleExportCSV = () => {
    const headers = tableData.columns.map(c => c.label).join(',');
    const rows = tableData.rows.map(r => {
      return tableData.columns.map(c => {
        const cell = r.data[c.id] || '';
        // Escape quotes and wrap in quotes if contains comma
        const escaped = cell.toString().replace(/"/g, '""');
        return `"${escaped}"`;
      }).join(',');
    }).join('\n');

    const csvContent = `${headers}\n${rows}`;
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'yokaizen_export.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    addToast('CSV Exported Successfully', 'success');
  };

  const handleImportCSV = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (evt) => {
      const text = evt.target?.result as string;
      const lines = text.split('\n');
      if (lines.length < 2) return;

      const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));

      // Create columns from CSV headers
      const newColumns: ClayColumn[] = headers.map((h, i) => ({
        id: `c_imp_${i}`,
        label: h,
        type: h.toLowerCase().includes('url') || h.toLowerCase().includes('website') ? 'url' : 'text',
        width: 200
      }));

      // Create rows
      const newRows: ClayRow[] = lines.slice(1).filter(l => l.trim()).map((line, idx) => {
        // Simple split handling quotes roughly (production needs robust parser)
        // For now assuming simple CSV without complex nested quotes
        const values = line.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/).map(v => v.trim().replace(/^"|"$/g, '').replace(/""/g, '"'));
        const rowData: Record<string, string> = {};
        newColumns.forEach((col, i) => {
          rowData[col.id] = values[i] || '';
        });
        return {
          id: `r_imp_${idx}`,
          data: rowData
        };
      });

      if (confirm(`Importing ${newRows.length} rows and ${newColumns.length} columns. This will replace current data.`)) {
        setTableData({ columns: newColumns, rows: newRows });
        addToast(`Imported ${newRows.length} rows`, 'success');
      }

      // Reset input
      if (fileInputRef.current) fileInputRef.current.value = '';
    };
    reader.readAsText(file);
  };

  return (
    <div className="p-6 max-w-[1600px] mx-auto animate-fade-in h-full flex flex-col">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-6 gap-4">
        <div>
          <h2 className="text-3xl font-bold text-white flex items-center gap-3">
            <Database className="w-8 h-8 text-violet-500" />
            Agent F: Growth Engine
          </h2>
          <p className="text-slate-400 mt-2">Vertical Build Strategy. No n8n. No NocoDB. Pure Code.</p>
        </div>

        <div className="flex items-center gap-3">
          <div className="px-3 py-1 bg-slate-800 rounded text-xs text-slate-400 border border-slate-700 flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isEnriching ? 'bg-emerald-400 animate-pulse' : 'bg-slate-600'}`}></div>
            {isEnriching ? `Enriching (${enrichmentQueue.length} in queue)` : 'Worker Idle'}
          </div>
          <button onClick={clearStorage} className="text-xs text-rose-400 hover:text-rose-300 flex items-center gap-1">
            <Trash2 className="w-3 h-3" /> Reset Data
          </button>
        </div>
      </div>

      {/* Toolbar */}
      <div className="bg-slate-800/50 border-x border-t border-slate-700 rounded-t-xl p-4 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 backdrop-blur-sm">
        <div className="flex flex-wrap items-center gap-2 w-full lg:w-auto">
          <button onClick={addRow} className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors whitespace-nowrap">
            <Plus className="w-4 h-4 shrink-0" /> Add Company
          </button>
          <div className="hidden sm:block h-8 w-px bg-slate-700 mx-2"></div>
          <button onClick={() => setShowAddCol(true)} className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors whitespace-nowrap">
            <Plus className="w-4 h-4 shrink-0" /> Add Column
          </button>
        </div>

        <div className="flex flex-wrap items-center gap-2 w-full lg:w-auto mt-2 lg:mt-0">
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            onChange={handleImportCSV}
            className="hidden"
          />
          <button onClick={() => fileInputRef.current?.click()} className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white px-3 py-2 rounded-lg text-xs font-medium border border-slate-600 transition-colors whitespace-nowrap flex-1 sm:flex-none justify-center">
            <Upload className="w-3 h-3 shrink-0" /> Import CSV
          </button>
          <button onClick={handleExportCSV} className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white px-3 py-2 rounded-lg text-xs font-medium border border-slate-600 transition-colors whitespace-nowrap flex-1 sm:flex-none justify-center">
            <Download className="w-3 h-3 shrink-0" /> Export CSV
          </button>
        </div>
      </div>

      {/* The Grid (Fake Table) */}
      <div className="flex-1 overflow-x-auto bg-slate-900 border border-slate-700 rounded-b-xl shadow-2xl relative scrollbar-thin scrollbar-thumb-slate-700">
        <table className="w-full border-collapse text-sm text-left min-w-[800px]">
          <thead className="bg-slate-800 text-slate-400 sticky top-0 z-10 shadow-md">
            <tr>
              <th className="p-4 border-b border-r border-slate-700 font-medium w-12 text-center">#</th>
              {tableData.columns.map(col => (
                <th key={col.id} className="p-3 border-b border-r border-slate-700 font-medium min-w-[200px] group relative" style={{ width: col.width }}>
                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-2">
                      {col.type === 'text' && <User className="w-3 h-3" />}
                      {col.type === 'url' && <Globe className="w-3 h-3" />}
                      {col.type === 'enrichment' && <Zap className="w-3 h-3 text-violet-400" />}
                      {col.label}
                    </span>
                    {col.type === 'enrichment' && (
                      <button
                        onClick={() => runEnrichmentForColumn(col.id)}
                        className="opacity-0 group-hover:opacity-100 text-violet-400 hover:text-white bg-violet-500/20 hover:bg-violet-500 p-1 rounded transition-all"
                        title="Run Enrichment"
                      >
                        <Play className="w-3 h-3 fill-current" />
                      </button>
                    )}
                  </div>
                  {col.enrichmentPrompt && (
                    <div className="text-[10px] text-slate-500 truncate mt-1 font-mono opacity-0 group-hover:opacity-100 transition-opacity">
                      AI: {col.enrichmentPrompt}
                    </div>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {tableData.rows.map((row, idx) => (
              <tr key={row.id} className="hover:bg-slate-800/30 transition-colors group">
                <td className="p-3 border-r border-slate-700/50 text-center text-slate-600 font-mono text-xs">{idx + 1}</td>
                {tableData.columns.map(col => (
                  <td key={`${row.id}-${col.id}`} className="border-r border-slate-700/50 p-0 relative">
                    {col.type === 'enrichment' ? (
                      <div className="w-full h-full p-3 flex items-center justify-between text-violet-200 bg-violet-500/5">
                        <span className="truncate">{row.data[col.id]}</span>
                        {!row.data[col.id] && (
                          <button
                            onClick={() => {
                              setEnrichmentQueue(prev => [...prev, { rowId: row.id, colId: col.id }]);
                              addToast('Enrichment queued', 'info');
                            }}
                            className="text-xs bg-violet-500/20 hover:bg-violet-500 text-violet-300 hover:text-white px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-all"
                          >
                            Enrich
                          </button>
                        )}
                      </div>
                    ) : (
                      <input
                        type="text"
                        value={row.data[col.id] || ''}
                        onChange={(e) => updateCell(row.id, col.id, e.target.value)}
                        className="w-full h-full bg-transparent p-3 outline-none text-slate-300 focus:bg-indigo-500/10 transition-colors"
                      />
                    )}
                  </td>
                ))}
              </tr>
            ))}

            {/* Add Row Button at bottom */}
            <tr>
              <td colSpan={tableData.columns.length + 1} className="p-2">
                <button onClick={addRow} className="w-full py-2 border-2 border-dashed border-slate-700 hover:border-slate-600 text-slate-500 hover:text-slate-300 rounded text-sm font-medium transition-all">
                  + New Row
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Add Column Modal */}
      {showAddCol && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm">
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 w-96 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-4">Add New Column</h3>

            <div className="mb-4">
              <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Column Name</label>
              <input
                autoFocus
                className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white focus:ring-2 focus:ring-indigo-500 outline-none"
                value={newColumnName}
                onChange={(e) => setNewColumnName(e.target.value)}
                placeholder="e.g. LinkedIn URL"
              />
            </div>

            <div className="mb-6">
              <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Enrichment Instruction (Optional)</label>
              <textarea
                className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white focus:ring-2 focus:ring-indigo-500 outline-none h-24 text-sm"
                value={newColumnPrompt}
                onChange={(e) => setNewColumnPrompt(e.target.value)}
                placeholder="Leave empty for standard text column.&#10;Or enter instruction: 'Find the company's estimated annual revenue'."
              />
            </div>

            <div className="flex gap-2 justify-end">
              <button onClick={() => setShowAddCol(false)} className="px-4 py-2 text-slate-400 hover:text-white">Cancel</button>
              <button onClick={() => addColumn('text')} className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg">Text Column</button>
              <button onClick={() => addColumn('enrichment')} disabled={!newColumnPrompt} className="px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white rounded-lg disabled:opacity-50">
                AI Column
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MarketingClay;