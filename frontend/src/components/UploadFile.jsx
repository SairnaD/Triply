import { InboxOutlined } from '@ant-design/icons';
import { message, Upload, Spin } from 'antd';
import { useState } from 'react';
import axios from 'axios';

const { Dragger } = Upload;

function UploadFile({ tripId, onUploadSuccess }) {
  const [loading, setLoading] = useState(false);

  const pollDocument = async (docId) => {
    try {
      let status = "processing";
      while (status === "processing") {
        const res = await axios.get(`http://localhost:8000/documents/${docId}`);
        status = res.data.extracted_data?.status || "processing";
        if (status === "processing") await new Promise(r => setTimeout(r, 1500));
        else return res.data.extracted_data;
      }
    } catch (err) {
      console.error("Polling error:", err);
      return { status: "error", message: "Polling failed" };
    }
  };

  const props = {
    name: 'file',
    multiple: false,
    beforeUpload: () => {
      if (!tripId) {
        message.error("Please select a trip first");
        return Upload.LIST_IGNORE;
      }
      return true;
    },
    customRequest: async ({ file, onSuccess, onError }) => {
      setLoading(true);
      const formData = new FormData();
      formData.append('file', file);

      try {
        const res = await axios.post(`http://localhost:8000/upload?trip_id=${tripId}`, formData);
        onSuccess(res.data, file);

        const extractedData = await pollDocument(res.data.id);

        if (onUploadSuccess) onUploadSuccess(extractedData);
        message.success(`${file.name} uploaded and processed successfully`);
      } catch (err) {
        console.error(err);
        message.error(`${file.name} upload failed`);
        onError(err);
      } finally {
        setLoading(false);
      }
    },
    onDrop(e) {
      console.log('Dropped files', e.dataTransfer.files);
    },
  };

  return (
    <div style={{ width: '100%' }}>
      <Dragger {...props}>
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text" style={{ color: 'white' }}>
          Click or drag file to this area to upload
        </p>
      </Dragger>

      {loading && (
        <Spin
          style={{ marginTop: 20 }}
          tip="Analyzing document..."
        />
      )}
    </div>
  );
}

export default UploadFile;