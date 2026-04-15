import { Layout, message } from 'antd';
import { useState } from 'react';
import AppSider from './components/AppSider';
import AppContent from './components/AppContent';

function App() {
  const [tripId, setTripId] = useState(null);
  const [refreshFlag, setRefreshFlag] = useState(false);
  const [lastDoc, setLastDoc] = useState(null);

  const waitForProcessing = async (docId, currentTripId) => {
    message.loading({ content: 'Analyzing document...', key: 'processing', duration: 0 });
    let attempts = 0;
    const maxAttempts = 40;

    try {
      while (attempts < maxAttempts) {
        const res = await fetch(`/documents/${docId}`);
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

        const data = await res.json();
        const extracted = data.extracted_data && typeof data.extracted_data === 'object'
          ? data.extracted_data
          : { status: 'processing' };

        const status = extracted.status || 'processing';

        if (status === 'processing') {
          await new Promise(r => setTimeout(r, 2000));
          attempts++;
          continue;
        }

        message.destroy('processing');

        if (status === 'done') {
          if (currentTripId === data.trip_id) setLastDoc(data);
          setRefreshFlag(prev => !prev);
          message.success({ content: 'Document processed successfully', duration: 2 });
          return;
        }

        if (status === 'error') {
          message.error({ content: extracted.message || 'Processing failed', duration: 3 });
          return;
        }
      }

      message.destroy('processing');
      message.warning({ content: 'Processing is taking longer than expected...', duration: 3 });
    } catch (err) {
      message.destroy('processing');
      message.error({ content: 'Server error during processing', duration: 3 });
      console.error('Polling error:', err);
    }
  };

  const handleUploadSuccess = (docData) => {
    if (!docData?.id) return;
    setLastDoc(docData);
    waitForProcessing(docData.id, tripId);
  };

  const handleTripDeleted = (deletedTripId) => {
    if (tripId === deletedTripId) {
      setTripId(null);
      setLastDoc(null);
      setRefreshFlag(prev => !prev);
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <AppSider
        tripId={tripId}
        setTripId={setTripId}
        onUploadSuccess={handleUploadSuccess}
        lastDoc={lastDoc}
        onTripDeleted={handleTripDeleted}
      />
      <AppContent tripId={tripId} refreshFlag={refreshFlag} />
    </Layout>
  );
}

export default App;