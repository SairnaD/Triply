import { Card, Space } from 'antd';

function TotalCard({ total, count }) {
  return (
    <Space vertical size={16}>
      <Card size="small" title="Trip Summary" style={{ width: 300 }}>
        <p><b>Total Expenses:</b> ${total.toFixed(2)}</p>
        <p><b>Documents:</b> {count}</p>
      </Card>
    </Space>
  );
}

export default TotalCard;