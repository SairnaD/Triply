import { Layout } from 'antd';
import InputTrip from './InputTrip';
import UploadFile from './UploadFile';
import DocCard from './DocCard';

function AppSider({ tripId, setTripId, onUploadSuccess, lastDoc, onTripDeleted }) {
  return (
    <Layout.Sider
      width="25%"
      style={{
        height: '100vh',
        backgroundColor: '#191a1c',
        color: '#fff'
      }}
    >
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100%',
          gap: '1.5rem',
          padding: '0 1rem',
          boxSizing: 'border-box',
          textAlign: 'center',
        }}
      >
        <InputTrip 
          onSelectTrip={setTripId} 
          onTripDeleted={onTripDeleted}
        />

        <UploadFile
          tripId={tripId}
          onUploadSuccess={(data) => {
            if (onUploadSuccess) onUploadSuccess(data);
          }}
        />

        <DocCard data={lastDoc} />
      </div>
    </Layout.Sider>
  );
}

export default AppSider;