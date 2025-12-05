<template>
  <div class="mammographies">
    <div class="header">
      <h2>Mammographies</h2>
      <button @click="showAddModal = true" class="btn btn-primary">Add Mammography</button>
    </div>

    <div class="filters">
      <input v-model="filters.patient_id" @input="loadData" type="number" placeholder="ID Пациента" class="input">
      <input v-model="filters.date_from" @input="loadData" type="date" placeholder="Дата от" class="input">
      <input v-model="filters.date_to" @input="loadData" type="date" placeholder="Дата по" class="input">
      <button @click="exportData" class="btn btn-secondary">Export to Excel</button>
    </div>

    <table class="data-table">
      <thead>
        <tr>
          <th>ID исследования</th>
          <th>ID пациента</th>
          <th>Дата исследования</th>
          <th>Breast Density</th>
          <th>BIRADS Score</th>
          <th>Обнаружения</th>
          <th>Комментарии</th>
          <th>Действия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.id }}</td>
          <td>{{ item.patient_id }}</td>
          <td>{{ item.exam_date }}</td>
          <td>{{ item.breast_density }}</td>
          <td>{{ item.birads_score }}</td>
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
        <h3>{{ editingItem ? 'Редактировать маммографию' : 'Добавить маммографию' }}</h3>
        <form @submit.prevent="saveItem">
          <div class="form-group">
            <label>ID Пациента*</label>
            <input v-model.number="form.patient_id" type="number" required class="input">
          </div>
          <div class="form-group">
            <label>Дата исследования *</label>
            <input v-model="form.exam_date" type="date" required class="input">
          </div>
          <div class="form-group">
            <label>Breast Density</label>
            <input v-model="form.breast_density" class="input">
          </div>
          <div class="form-group">
            <label>BIRADS Score</label>
            <input v-model.number="form.birads_score" type="number" class="input">
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
            <button type="button" @click="closeModal" class="btn btn-secondary">Отмена</button>
            <button type="submit" class="btn btn-primary">Сохранить</button>
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
        date_to: ''
      },
      showAddModal: false,
      editingItem: null,
      form: {
        patient_id: '',
        exam_date: '',
        breast_density: '',
        birads_score: null,
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

        const response = await api.getMammographies(params)
        this.items = response.data
      } catch (error) {
        alert('Error loading data')
      }
    },
    async deleteItem(id) {
      if (confirm('Удалить данную запись маммографии?')) {
        try {
          await api.deleteMammography(id)
          this.loadData()
        } catch (error) {
          alert('Ошибка при удалении маммографии')
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
          await api.updateMammography(this.editingItem, this.form)
        } else {
          await api.createMammography(this.form)
        }
        this.closeModal()
        this.loadData()
      } catch (error) {
        alert('Ошибка удаления маммографии: ' + (error.response?.data?.detail || error.message))
      }
    },
    closeModal() {
      this.showAddModal = false
      this.editingItem = null
      this.form = {
        patient_id: '',
        exam_date: '',
        breast_density: '',
        birads_score: null,
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

        const response = await api.exportData('mammographies', params)
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', 'mammographies.xlsx')
        document.body.appendChild(link)
        link.click()
        link.remove()
      } catch (error) {
        alert('Ошибка экспорта данных')
      }
    }
  }
}
</script>

<style scoped>
.mammographies {
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