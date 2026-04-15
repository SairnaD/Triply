import { Drawer, List, Button } from 'antd';

function DocumentsDrawer({ open, onClose, documents, onEdit }) {
  return (
    <Drawer
      title="Receipts"
      placement="right"
      onClose={onClose}
      open={open}
      width={350}
    >
      <List
        dataSource={documents}
        renderItem={(doc) => (
          <List.Item
            actions={[
              <Button type="link" onClick={() => onEdit(doc)}>
                Edit
              </Button>
            ]}
          >
            <div>
              <b>{doc.category}</b> — ${doc.amount}
              <br />
              <small>{doc.date}</small>
            </div>
          </List.Item>
        )}
      />
    </Drawer>
  );
}

export default DocumentsDrawer;