<template>
  <div class="mrts">
    <div class="header">
      <h2>MRTs</h2>
      <button @click="showAddModal = true" class="btn btn-primary">Добавить МРТ</button>
    </div>

    <div class="filters">
      <input v-model="filters.patient_id" @input="loadData" type="number" placeholder="ID пациента" class="input">
      <input v-model="filters.date_from" @input="loadData" type="date" placeholder="Дата от" class="input">
      <input v-model="filters.date_to" @input="loadData" type="date" placeholder="Дата по" class="input">
      <input v-model="filters.body_part" @input="loadData" placeholder="Фильтр по части тела" class="input">
      <button @click="exportData" class="btn btn-secondary">Export to Excel</button>
    </div>

    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Patient ID</th>
          <th>Exam Date</th>
          <th>Body Part</th>
          <th>Contrast Used</th>
          <th>Findings</th>
          <th>Impression</th>
          <th>Notes</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.id }}</td>
          <td>{{ item.patient_id }}</td>
          <td>{{ item.exam_date }}</td>
          <td>{{ item.body_part }}</td>
          <td>{{ item.contrast_used }}</td>
          <td>{{ item.findings }}</td>
          <td>{{ item.impression }}</td>
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
        <h3>{{ editingItem ? 'Edit MRT' : 'Add MRT' }}</h3>
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
            <label>Body Part</label>
            <input v-model="form.body_part" class="input">
          </div>
          <div class="form-group">
            <label>Contrast Used</label>
            <input v-model="form.contrast_used" class="input">
          </div>
          <div class="form-group">
            <label>Findings</label>
            <textarea v-model="form.findings" class="input" rows="3"></textarea>
          </div>
          <div class="form-group">
            <label>Impression</label>
            <textarea v-model="form.impression" class="input" rows="3"></textarea>
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
        body_part: ''
      },
      showAddModal: false,
      editingItem: null,
      form: {
        patient_id: '',
        exam_date: '',
        body_part: '',
        contrast_used: '',
        findings: '',
        impression: '',
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
        if (this.filters.body_part) params.body_part = this.filters.body_part

        const response = await api.getMRTs(params)
        this.items = response.data
      } catch (error) {
        alert('Error loading data')
      }
    },
    async deleteItem(id) {
      if (confirm('Delete this MRT?')) {
        try {
          await api.deleteMRT(id)
          this.loadData()
        } catch (error) {
          alert('Error deleting MRT')
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
          await api.updateMRT(this.editingItem, this.form)
        } else {
          await api.createMRT(this.form)
        }
        this.closeModal()
        this.loadData()
      } catch (error) {
        alert('Error saving MRT: ' + (error.response?.data?.detail || error.message))
      }
    },
    closeModal() {
      this.showAddModal = false
      this.editingItem = null
      this.form = {
        patient_id: '',
        exam_date: '',
        body_part: '',
        contrast_used: '',
        findings: '',
        impression: '',
        notes: ''
      }
    },
    async exportData() {
      try {
        const params = {}
        if (this.filters.patient_id) params.patient_id = this.filters.patient_id
        if (this.filters.date_from) params.date_from = this.filters.date_from
        if (this.filters.date_to) params.date_to = this.filters.date_to
        if (this.filters.body_part) params.body_part = this.filters.body_part

        const response = await api.exportData('mrts', params)
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', 'mrts.xlsx')
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
.mrts {
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