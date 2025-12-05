<template>
  <div class="ultrasounds">
    <div class="header">
      <h2>Ultrasounds</h2>
      <button @click="showAddModal = true" class="btn btn-primary">Add Ultrasound</button>
    </div>

    <div class="filters">
      <input v-model="filters.patient_id" @input="loadData" type="number" placeholder="Patient ID" class="input">
      <input v-model="filters.date_from" @input="loadData" type="date" placeholder="From date" class="input">
      <input v-model="filters.date_to" @input="loadData" type="date" placeholder="To date" class="input">
      <input v-model="filters.organ" @input="loadData" placeholder="Filter by organ" class="input">
      <button @click="exportData" class="btn btn-secondary">Export to Excel</button>
    </div>

    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Patient ID</th>
          <th>Exam Date</th>
          <th>Organ</th>
          <th>Measurements</th>
          <th>Findings</th>
          <th>Notes</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.id }}</td>
          <td>{{ item.patient_id }}</td>
          <td>{{ item.exam_date }}</td>
          <td>{{ item.organ }}</td>
          <td>{{ item.measurements }}</td>
          <td>{{ item.findings }}</td>
          <td>{{ item.notes }}</td>
          <td>
            <button @click="editItem(item)" class="btn-sm btn-warning">Edit</button>
            <button @click="deleteItem(item.id)" class="btn-sm btn-danger">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Add/Edit Modal -->
    <div v-if="showAddModal || editingItem" class="modal" @click.self="closeModal">
      <div class="modal-content">
        <h3>{{ editingItem ? 'Edit Ultrasound' : 'Add Ultrasound' }}</h3>
        <form @submit.prevent="saveItem">
          <div class="form-group">
            <label>Patient ID *</label>
            <input v-model.number="form.patient_id" type="number" required class="input">
          </div>
          <div class="form-group">
            <label>Exam Date *</label>
            <input v-model="form.exam_date" type="date" required class="input">
          </div>
          <div class="form-group">
            <label>Organ</label>
            <input v-model="form.organ" class="input">
          </div>
          <div class="form-group">
            <label>Measurements</label>
            <input v-model="form.measurements" class="input">
          </div>
          <div class="form-group">
            <label>Findings</label>
            <textarea v-model="form.findings" class="input" rows="3"></textarea>
          </div>
          <div class="form-group">
            <label>Notes</label>
            <textarea v-model="form.notes" class="input" rows="3"></textarea>
          </div>
          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary">Save</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api'

export default {
  data() {
    return {
      items: [],
      filters: {
        patient_id: '',
        date_from: '',
        date_to: '',
        organ: ''
      },
      showAddModal: false,
      editingItem: null,
      form: {
        patient_id: '',
        exam_date: '',
        organ: '',
        measurements: '',
        findings: '',
        notes: ''
      }
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    async loadData() {
      try {
        const params = {}
        if (this.filters.patient_id) params.patient_id = this.filters.patient_id
        if (this.filters.date_from) params.date_from = this.filters.date_from
        if (this.filters.date_to) params.date_to = this.filters.date_to
        if (this.filters.organ) params.organ = this.filters.organ

        const response = await api.getUltrasounds(params)
        this.items = response.data
      } catch (error) {
        alert('Error loading data')
      }
    },
    async deleteItem(id) {
      if (confirm('Delete this ultrasound?')) {
        try {
          await api.deleteUltrasound(id)
          this.loadData()
        } catch (error) {
          alert('Error deleting ultrasound')
        }
      }
    },
    editItem(item) {
      this.editingItem = item.id
      this.form = { ...item }
    },
    async saveItem() {
      try {
        if (this.editingItem) {
          await api.updateUltrasound(this.editingItem, this.form)
        } else {
          await api.createUltrasound(this.form)
        }
        this.closeModal()
        this.loadData()
      } catch (error) {
        alert('Error saving ultrasound: ' + (error.response?.data?.detail || error.message))
      }
    },
    closeModal() {
      this.showAddModal = false
      this.editingItem = null
      this.form = {
        patient_id: '',
        exam_date: '',
        organ: '',
        measurements: '',
        findings: '',
        notes: ''
      }
    },
    async exportData() {
      try {
        const params = {}
        if (this.filters.patient_id) params.patient_id = this.filters.patient_id
        if (this.filters.date_from) params.date_from = this.filters.date_from
        if (this.filters.date_to) params.date_to = this.filters.date_to
        if (this.filters.organ) params.organ = this.filters.organ

        const response = await api.exportData('ultrasounds', params)
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', 'ultrasounds.xlsx')
        document.body.appendChild(link)
        link.click()
        link.remove()
      } catch (error) {
        alert('Error exporting data')
      }
    }
  }
}
</script>

<style scoped>
.ultrasounds {
  padding: 1rem;
}

.header {
  margin-bottom: 2rem;
}

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.input {
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  flex: 1;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border-radius: 8px;
  overflow: hidden;
}

.data-table th {
  background: #f8f9fa;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #495057;
}

.data-table td {
  padding: 1rem;
  border-top: 1px solid #dee2e6;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-sm {
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-warning {
  background: #ffc107;
  color: #212529;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}
</style>