import { Button, message } from 'antd';
import { FileExcelOutlined } from '@ant-design/icons';
import axios from 'axios';

function ExportButton({ tripId }) {
  const handleExport = async () => {
    if (!tripId) {
      message.warning("Choose trip to export the summary");
      return;
    }

    try {
      const res = await axios.get(`http://localhost:8000/trips/${tripId}/export`, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');

      const contentDisposition = res.headers['content-disposition'];
      let fileName = 'trip_report.xlsx';

      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?(.+)"?/);
        if (match && match[1]) fileName = match[1];
      }

      link.href = url;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      message.success("Summary is downloaded");
    } catch (err) {
      console.error(err);
      message.error("Error exporting the summary");
    }
  };

  return (
    <Button
      type="primary"
      icon={<FileExcelOutlined />}
      onClick={handleExport}
      style={{
        marginBottom: 20,
        background: '#1F0827',
        border: 'none',
        height: 40,
        padding: '0 20px',
        fontWeight: 500
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = '#2a0f36';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = '#1F0827';
      }}
    >
      Export Excel
    </Button>
  );
}

export default ExportButton;