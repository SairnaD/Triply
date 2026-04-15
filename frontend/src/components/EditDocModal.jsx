import { Modal, Input, Select, DatePicker, Button, Space, message } from 'antd';
import { useState, useEffect } from 'react';
import dayjs from 'dayjs';
import axios from 'axios';

function EditDocModal({ open, onClose, doc, onSave, onDelete }) {
  const [form, setForm] = useState({});

  useEffect(() => {
    if (doc) {
      setForm({
        ...doc,
        date: doc.date ? dayjs(doc.date, 'DD/MM/YYYY') : null
      });
    }
  }, [doc]);

  const handleSave = () => {
    const payload = {
      ...form,
      date: form.date ? form.date.format('DD/MM/YYYY') : null
    };
    onSave(payload);
  };

  const handleDelete = async () => {
    if (!doc?.id) return;

    try {
      await axios.delete(`http://localhost:8000/documents/${doc.id}`);
      message.success('Document deleted successfully');
      onClose();
      if (onDelete) onDelete(doc.id);
    } catch (err) {
      console.error(err);
      message.error('Failed to delete document');
    }
  };

  return (
    <Modal
      title="Edit Receipt"
      open={open}
      onOk={handleSave}
      onCancel={onClose}
      footer={[
        <Button key="delete" danger onClick={handleDelete}>
          Delete
        </Button>,
        <Button key="cancel" onClick={onClose}>
          Cancel
        </Button>,
        <Button key="save" type="primary" onClick={handleSave}>
          Save
        </Button>,
      ]}
    >
      <Input
        placeholder="Amount"
        value={form.amount}
        onChange={(e) => setForm({ ...form, amount: e.target.value })}
        style={{ marginBottom: 10 }}
      />

      <DatePicker
        placeholder="Select Date"
        value={form.date}
        onChange={(date) => setForm({ ...form, date })}
        format="DD/MM/YYYY"
        style={{ marginBottom: 10, width: '100%' }}
      />

      <Select
        value={form.category}
        style={{ width: '100%' }}
        onChange={(value) => setForm({ ...form, category: value })}
        options={[
          { value: 'Food' },
          { value: 'Transport' },
          { value: 'Hotel' },
          { value: 'Other' }
        ]}
      />
    </Modal>
  );
}

export default EditDocModal;