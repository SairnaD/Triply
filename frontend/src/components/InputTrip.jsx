import { useEffect, useRef, useState } from 'react';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import { Button, Divider, Input, Select, Space, message, Popconfirm } from 'antd';
import axios from 'axios';

function InputTrip({ onSelectTrip, onTripDeleted }) {
  const [items, setItems] = useState([]);
  const [name, setName] = useState('');
  const [selectedTrip, setSelectedTrip] = useState(null);
  const inputRef = useRef(null);

  useEffect(() => {
    loadTrips();
  }, []);

  const loadTrips = async () => {
    try {
      const res = await axios.get('http://localhost:8000/trips');
      setItems(res.data);
    } catch {
      message.error('Failed to load trips');
    }
  };

  const onNameChange = (e) => setName(e.target.value);

  const addItem = async (e) => {
    e.preventDefault();
    if (!name) return;

    try {
      const res = await axios.post('http://localhost:8000/trips', { name });
      const newTrip = res.data;
      setItems([...items, newTrip]);
      setName('');
      setSelectedTrip(newTrip.id);
      onSelectTrip(newTrip.id);
      message.success('Trip created');
      setTimeout(() => inputRef.current?.focus(), 0);
    } catch {
      message.error('Failed to create trip');
    }
  };

  const deleteTrip = async (tripId) => {
    try {
      await axios.delete(`http://localhost:8000/trips/${tripId}`);
      message.success('Trip deleted');
      if (selectedTrip === tripId) {
        setSelectedTrip(null);
        onSelectTrip(null);
        if (onTripDeleted) onTripDeleted(tripId);
      }
      loadTrips();
    } catch {
      message.error('Failed to delete trip');
    }
  };

  const handleChange = (value) => {
    setSelectedTrip(value);
    onSelectTrip(value);
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, width: 300 }}>
      <div style={{ position: 'relative', flex: 1 }}>
        <Select
          style={{ width: '100%' }}
          placeholder="Choose trip"
          value={selectedTrip}
          onChange={handleChange}
          dropdownRender={(menu) => (
            <div style={{ minWidth: 300 }}>
              {menu}
              <Divider style={{ margin: '8px 0' }} />
              <Space style={{ padding: '0 8px 4px', width: '100%' }}>
                <Input
                  placeholder="Please enter trip"
                  ref={inputRef}
                  value={name}
                  onChange={onNameChange}
                  onKeyDown={(e) => e.stopPropagation()}
                  style={{ flex: 1 }}
                />
                <Button type="text" icon={<PlusOutlined />} onClick={addItem}>
                  Add
                </Button>
              </Space>
            </div>
          )}
          options={items.map(item => ({
            label: item.name,
            value: item.id,
          }))}
        />

        {selectedTrip && (
          <Popconfirm
            title="Are you sure to delete this trip?"
            onConfirm={() => deleteTrip(selectedTrip)}
            okText="Yes"
            cancelText="No"
          >
            <Button
              danger
              icon={<DeleteOutlined />}
              style={{
                position: 'absolute',
                top: '50%',
                right: -44,
                transform: 'translateY(-50%)',
                width: 40,
                height: '100%',
              }}
            />
          </Popconfirm>
        )}
      </div>
    </div>
  );
}

export default InputTrip;