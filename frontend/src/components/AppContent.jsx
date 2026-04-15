import { Layout, Button } from 'antd';
import FrameCanva from './FrameCanva';
import TotalCard from './TotalCard';
import ExportButton from './ExportButton';
import DocumentsDrawer from './DocumentsDrawer';
import EditDocModal from './EditDocModal';

import { useEffect, useState } from 'react';
import axios from 'axios';

const contentStyle = {
  textAlign: 'center',
  color: '#fff',
  backgroundColor: '#111214',
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  flexDirection: 'column'
};

function AppContent({ tripId, refreshFlag }) {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);

  const [documents, setDocuments] = useState([]);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editingDoc, setEditingDoc] = useState(null);

  // Fetch functions
  const fetchSummary = async () => {
    if (!tripId) return;

    try {
      const res = await axios.get(`http://localhost:8000/trips/${tripId}/summary`);
      setSummary(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchDocuments = async () => {
    if (!tripId) return;

    try {
      const res = await axios.get(`http://localhost:8000/trips/${tripId}/documents`);
      setDocuments(res.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  // Universal refresh
  const refreshAll = async () => {
    setLoading(true);
    try {
      await Promise.all([fetchSummary(), fetchDocuments()]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshAll();
  }, [tripId, refreshFlag]);

  const pieData = summary?.categories
    ? Object.entries(summary.categories).map(([name, value]) => ({
        name,
        value
      }))
    : [];

  // Save edited document
  const handleSave = async (updated) => {
    try {
      await axios.patch(`http://localhost:8000/documents/${updated.id}`, updated);

      setEditingDoc(null);
      refreshAll();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <Layout.Content style={contentStyle}>
      <div style={{ marginBottom: '1rem', display: 'flex', gap: '1rem' }}>
        <ExportButton tripId={tripId} />

        <Button
          type="primary"
          onClick={() => setDrawerOpen(true)}
          style={{
            marginBottom: 20,
            background: '#1F0827',
            border: 'none',
            height: 40,
            padding: '0 20px',
            fontWeight: 500
          }}
          onMouseEnter={(e) => { e.currentTarget.style.background = '#2a0f36'; }}
          onMouseLeave={(e) => { e.currentTarget.style.background = '#1F0827'; }}
        >
          Show Receipts
        </Button>
      </div>

      <FrameCanva 
        data={pieData}
        loading={loading}
        onRefresh={refreshAll}
      />

      <TotalCard 
        total={summary?.total || 0}
        count={summary?.count || 0}
      />

      <DocumentsDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        documents={documents}
        onEdit={(doc) => setEditingDoc(doc)}
      />

      <EditDocModal
        open={!!editingDoc}
        doc={editingDoc}
        onClose={() => setEditingDoc(null)}
        onSave={handleSave}
        onDelete={() => refreshAll()}
      />
    </Layout.Content>
  );
}

export default AppContent;