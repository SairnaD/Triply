import { Card, Space } from 'antd';

function DocCard({ data }) {

  if (!data) return null;

  if (data.status === "processing") {
    return (
      <Card size="small" title="Document Info" style={{ width: 300 }}>
        <p>Analyzing document...</p>
      </Card>
    );
  }

  if (data.status === "error") {
    return (
      <Card size="small" title="Document Info" style={{ width: 300 }}>
        <p style={{ color: 'red' }}>
          {data.message || "Processing error"}
        </p>
      </Card>
    );
  }

  if (!data.amount && !data.date && !data.category) {
    return null;
  }

  return (
    <Space direction="vertical" size={16}>
      <Card
        size="small"
        title="Document Info"
        style={{ width: 300 }}
      >
        <p><b>Amount:</b> {data.amount}</p>
        <p><b>Date:</b> {data.date}</p>
        <p><b>Category:</b> {data.category}</p>
      </Card>
    </Space>
  );
}

export default DocCard;