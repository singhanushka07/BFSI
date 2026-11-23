import { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, FileText, Trash2, Search, Loader2, CheckCircle, X } from 'lucide-react'
import { ragAPI } from '../../api/client'
import toast from 'react-hot-toast'

export default function PDFUpload({ onDocumentUploaded }) {
  const [uploading, setUploading] = useState(false)
  const [documents, setDocuments] = useState([])
  const [loadingDocs, setLoadingDocs] = useState(false)
  const [query, setQuery] = useState('')
  const [queryCollection, setQueryCollection] = useState('')
  const [queryResults, setQueryResults] = useState(null)
  const [querying, setQuerying] = useState(false)
  const [company, setCompany] = useState('')
  const [docType, setDocType] = useState('annual_report')
  const [dragOver, setDragOver] = useState(false)
  const fileRef = useRef()

  const loadDocs = async () => {
    setLoadingDocs(true)
    try {
      const res = await ragAPI.documents()
      setDocuments(res.data)
    } catch {
      toast.error('Could not load documents')
    } finally {
      setLoadingDocs(false)
    }
  }

  useState(() => { loadDocs() }, [])

  const handleUpload = async (file) => {
    if (!file || !file.name.toLowerCase().endsWith('.pdf')) {
      toast.error('Please select a PDF file')
      return
    }
    const fd = new FormData()
    fd.append('file', file)
    fd.append('company', company || 'Unknown Company')
    fd.append('doc_type', docType)
    setUploading(true)
    try {
      const res = await ragAPI.upload(fd)
      toast.success(`Indexed ${res.data.chunks_indexed} chunks from ${file.name}`)
      await loadDocs()
      if (onDocumentUploaded) onDocumentUploaded(res.data.collection)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (id) => {
    try {
      await ragAPI.deleteDoc(id)
      setDocuments((d) => d.filter((doc) => doc.id !== id))
      toast.success('Document removed')
    } catch {
      toast.error('Delete failed')
    }
  }

  const handleQuery = async () => {
    if (!queryCollection || !query.trim()) return
    setQuerying(true)
    try {
      const res = await ragAPI.query({ collection: queryCollection, query, n_results: 4 })
      setQueryResults(res.data.results)
    } catch {
      toast.error('Query failed')
    } finally {
      setQuerying(false)
    }
  }

  return (
    <div className="space-y-5">
      {/* Upload Area */}
      <div className="glass-card p-5">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 rounded-lg bg-pink-500/15 border border-pink-500/30 flex items-center justify-center">
            <Upload className="w-4 h-4 text-pink-400" />
          </div>
          <div>
            <p className="text-white font-semibold text-sm">Upload Financial PDF</p>
            <p className="text-slate-500 text-xs">ChromaDB vectorizes and indexes your document</p>
          </div>
        </div>

        <div className="grid sm:grid-cols-2 gap-3 mb-4">
          <input
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            placeholder="Company name (e.g. Apple Inc)"
            className="input-field text-sm"
          />
          <select
            value={docType}
            onChange={(e) => setDocType(e.target.value)}
            className="input-field text-sm"
          >
            <option value="annual_report">Annual Report</option>
            <option value="10k">10-K Filing</option>
            <option value="earnings">Earnings Report</option>
            <option value="prospectus">Prospectus</option>
            <option value="risk_report">Risk Report</option>
          </select>
        </div>

        <div
          onClick={() => fileRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => { e.preventDefault(); setDragOver(false); const f = e.dataTransfer.files[0]; if (f) handleUpload(f) }}
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200
            ${dragOver ? 'border-pink-500/60 bg-pink-500/10' : 'border-white/10 hover:border-pink-500/40 hover:bg-pink-500/5'}`}
        >
          {uploading ? (
            <div className="flex flex-col items-center gap-2">
              <Loader2 className="w-8 h-8 text-pink-400 animate-spin" />
              <p className="text-pink-400 text-sm">Indexing PDF into ChromaDB...</p>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2">
              <Upload className="w-8 h-8 text-slate-500" />
              <p className="text-slate-300 text-sm font-medium">Drop PDF here or click to browse</p>
              <p className="text-slate-500 text-xs">Annual reports, 10-K filings, earnings PDFs</p>
            </div>
          )}
        </div>
        <input ref={fileRef} type="file" accept=".pdf" className="hidden" onChange={(e) => handleUpload(e.target.files[0])} />
      </div>

      {/* Document Library */}
      <div className="glass-card p-5">
        <p className="text-white font-semibold text-sm mb-4">
          Indexed Documents
          <span className="ml-2 px-2 py-0.5 rounded-full bg-pink-500/15 text-pink-400 text-xs">{documents.length}</span>
        </p>
        {documents.length === 0 ? (
          <p className="text-slate-500 text-sm text-center py-4">No documents uploaded yet</p>
        ) : (
          <div className="space-y-2">
            {documents.map((doc) => (
              <div key={doc.id} className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/5">
                <FileText className="w-4 h-4 text-pink-400 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-white text-xs font-medium truncate">{doc.filename}</p>
                  <p className="text-slate-500 text-xs">{doc.company} · {doc.pages} chunks · {doc.doc_type}</p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setQueryCollection(doc.collection)}
                    className={`p-1.5 rounded-lg transition-colors ${queryCollection === doc.collection ? 'bg-cyan-500/20 text-cyan-400' : 'hover:bg-white/10 text-slate-400'}`}
                    title="Query this document"
                  >
                    <Search className="w-3.5 h-3.5" />
                  </button>
                  <button onClick={() => handleDelete(doc.id)} className="p-1.5 rounded-lg hover:bg-red-500/10 text-slate-400 hover:text-red-400 transition-colors">
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* RAG Query */}
      <div className="glass-card p-5">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 rounded-lg bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center">
            <Search className="w-4 h-4 text-cyan-400" />
          </div>
          <div>
            <p className="text-white font-semibold text-sm">RAG Query</p>
            <p className="text-slate-500 text-xs">Semantic search over indexed documents</p>
          </div>
        </div>

        <div className="space-y-3">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. What are the main risk factors disclosed?"
            className="input-field text-sm"
            onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
          />
          <button
            onClick={handleQuery}
            disabled={!queryCollection || !query.trim() || querying}
            className="btn-primary w-full text-sm py-2.5 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {querying && <Loader2 className="w-4 h-4 animate-spin" />}
            {queryCollection ? `Query: ${queryCollection.split('_').slice(-1)[0]}` : 'Select a document above to query'}
          </button>
        </div>

        {queryResults && (
          <div className="mt-4 space-y-2">
            <p className="text-xs text-slate-500 font-medium uppercase tracking-wider">Retrieved Chunks ({queryResults.length})</p>
            {queryResults.map((r, i) => (
              <motion.div key={i} initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
                className="p-3 rounded-xl bg-white/5 border border-cyan-500/10">
                <p className="text-slate-300 text-xs leading-relaxed mb-2">{r.text}</p>
                <p className="text-slate-600 text-xs">Page {r.metadata?.page} · similarity {(1 - r.distance).toFixed(3)}</p>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
