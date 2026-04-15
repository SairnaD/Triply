import { Card, Spin, FloatButton } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import { PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

function FrameCanva({ data, onRefresh, loading }) {
  return (
    <div style={{ position: 'relative' }}>
      
      <FloatButton
        icon={<ReloadOutlined />}
        onClick={onRefresh}
        shape="square"
        style={{
          position: 'absolute',
          right: 20,
          top: 20,
          width: 40,
          height: 40
        }}
      />

      <Card style={{ 
        width: '100vh', 
        height: '60vh', 
        backgroundColor: "#222", 
        marginBottom: '1rem', 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
      }}>

        {loading ? (
          <Spin size="large" tip="Updating..." />
        ) : data && data.length > 0 ? (
          <PieChart width={500} height={400}>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={120}
              fill="#8884d8"
              label
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        ) : (
          <p style={{ color: 'white' }}>No data to display</p>
        )}

      </Card>
    </div>
  );
}

export default FrameCanva;