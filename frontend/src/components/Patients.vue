<template>
  <div class="patients">
    <div class="header">
      <h2>Пациенты</h2>
      <button @click="showAddModal = true" class="btn btn-primary">Добавить пациента</button>
    </div>

    <div class="filters">
      <input v-model="filters.last_name" @input="loadPatients" placeholder="Фамилия" class="input">
      <input v-model="filters.first_name" @input="loadPatients" placeholder="Имя" class="input">
      <input v-model="filters.snils" @input="loadPatients" placeholder="СНИЛС" class="input">
    </div>

    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>СНИЛС</th>
          <th>ФИО</th>
          <th>Пол</th>
          <th>Дата рождения</th>
          <th>Диагноз</th>
          <th>Последнее обновление</th>
          <th>Действия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="patient in patients" :key="patient.id">
          <td>{{ patient.id }}</td>
          <td>{{ patient.snils }}</td>
          <td>{{ patient.last_name }} {{ patient.first_name }} {{ patient.middle_name }}</td>
          <td>{{ patient.gender }}</td>
          <td>{{ patient.date_of_birth }}</td>
          <td>{{ patient.diagnosis }}</td>
          <td>{{ formatDateTime(patient.last_updated) }}</td>
          <td class="actions">
            <button @click="viewPatient(patient.id)" class="btn-sm btn-info">Просмотр</button>
            <button @click="editPatient(patient)" class="btn-sm btn-warning">Редактировать</button>
            <button @click="deletePatientConfirm(patient.id)" class="btn-sm btn-danger">Удалить</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="showAddModal || editingPatient" class="modal" @click.self="closeModal">
      <div class="modal-content">
        <h3>{{ editingPatient ? 'Редактировать пациента' : 'Добавить пациента' }}</h3>
        <form @submit.prevent="savePatient">
          <div class="form-group" v-if="!editingPatient">
            <label>ID пациента *</label>
            <input v-model="form.id" required class="input" placeholder="Например: P001">
          </div>
          <div class="form-group">
            <label>СНИЛС</label>
            <input v-model="form.snils" class="input" placeholder="XXX-XXX-XXX XX">
          </div>
          <div class="form-group">
            <label>Фамилия *</label>
            <input v-model="form.last_name" required class="input">
          </div>
          <div class="form-group">
            <label>Имя *</label>
            <input v-model="form.first_name" required class="input">
          </div>
          <div class="form-group">
            <label>Отчество</label>
            <input v-model="form.middle_name" class="input">
          </div>
          <div class="form-group">
            <label>Пол *</label>
            <select v-model="form.gender" required class="input">
              <option value="">Выберите</option>
              <option value="Мужской">Мужской</option>
              <option value="Женский">Женский</option>
            </select>
          </div>
          <div class="form-group">
            <label>Дата рождения *</label>
            <input v-model="form.date_of_birth" type="date" required class="input">
          </div>
          <div class="form-group">
            <label>Диагноз</label>
            <textarea v-model="form.diagnosis" class="input" rows="3"></textarea>
          </div>
          <div class="form-group">
            <label>Стадия по TNM</label>
            <input v-model="form.tnm_stage" class="input" placeholder="Например: T2N1M0">
          </div>
          <div class="form-group">
            <label>Комментарий</label>
            <textarea v-model="form.comment" class="input" rows="3"></textarea>
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
      patients: [],
      filters: {
        last_name: '',
        first_name: '',
        snils: ''
      },
      showAddModal: false,
      editingPatient: null,
      form: {
        id: '',
        snils: '',
        last_name: '',
        first_name: '',
        middle_name: '',
        gender: '',
        date_of_birth: '',
        diagnosis: '',
        tnm_stage: '',
        comment: ''
      }
    }
  },
  mounted() {
    this.loadPatients()
  },
  methods: {
    async loadPatients() {
      try {
        const response = await api.getPatients(this.filters)
        this.patients = response.data
      } catch (error) {
        alert('Ошибка загрузки пациентов')
      }
    },
    viewPatient(id) {
      this.$router.push(`/patients/${id}`)
    },
    editPatient(patient) {
      this.editingPatient = patient.id
      this.form = { ...patient }
    },
    async savePatient() {
      try {
        if (this.editingPatient) {
          await api.updatePatient(this.editingPatient, this.form)
        } else {
          await api.createPatient(this.form)
        }
        this.closeModal()
        this.loadPatients()
      } catch (error) {
        alert('Ошибка сохранения: ' + (error.response?.data?.detail || error.message))
      }
    },
    async deletePatientConfirm(id) {
      if (confirm('Удалить пациента и все связанные данные?')) {
        try {
          await api.deletePatient(id)
          this.loadPatients()
        } catch (error) {
          alert('Ошибка удаления')
        }
      }
    },
    closeModal() {
      this.showAddModal = false
      this.editingPatient = null
      this.form = {
        id: '',
        snils: '',
        last_name: '',
        first_name: '',
        middle_name: '',
        gender: '',
        date_of_birth: '',
        diagnosis: '',
        tnm_stage: '',
        comment: ''
      }
    },
    formatDateTime(dt) {
      if (!dt) return ''
      return new Date(dt).toLocaleString('ru-RU')
    }
  }
}
</script>

<style scoped>
.patients {
  padding: 1rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
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

.actions {
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5568d3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}

.btn-sm {
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
}

.btn-info {
  background: #17a2b8;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-warning {
  background: #ffc107;
  color: #212529;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-danger {
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.input {
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  width: 100%;
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
  max-width: 600px;
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