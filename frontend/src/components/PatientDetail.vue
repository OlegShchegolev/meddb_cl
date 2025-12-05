<template>
  <div class="patient-detail" v-if="patient">
    <div class="header">
      <button @click="$router.back()" class="btn btn-secondary">← Back</button>
      <h2>{{ patient.first_name }} {{ patient.last_name }}</h2>
    </div>

    <div class="patient-info card">
      <h3>Patient Information</h3>
      <div class="info-grid">
        <div><strong>ID:</strong> {{ patient.id }}</div>
        <div><strong>Дата рождения:</strong> {{ patient.date_of_birth }}</div>
        <div><strong>Пол:</strong> {{ patient.gender }}</div>
        <div><strong>Email:</strong> {{ patient.email }}</div>
        <div><strong>Телефон:</strong> {{ patient.phone }}</div>
        <div><strong>Адрес:</strong> {{ patient.address }}</div>
      </div>
    </div>

    <div class="section">
      <div class="section-header">
        <h3>Mammographies</h3>
        <button @click="showMammoModal = true" class="btn btn-primary btn-sm">Add</button>
      </div>
      <table class="data-table" v-if="patient.mammographies.length">
        <thead>
          <tr>
            <th>Дата</th>
            <th>Breast Density</th>
            <th>BIRADS Score</th>
            <th>Обнаружения</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="mammo in patient.mammographies" :key="mammo.id">
            <td>{{ mammo.exam_date }}</td>
            <td>{{ mammo.breast_density }}</td>
            <td>{{ mammo.birads_score }}</td>
            <td>{{ mammo.findings }}</td>
            <td>
              <button @click="deleteMammo(mammo.id)" class="btn-sm btn-danger">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else class="no-data">No mammographies recorded</p>
    </div>

    <div class="section">
      <div class="section-header">
        <h3>Ultrasounds</h3>
        <button @click="showUltrasoundModal = true" class="btn btn-primary btn-sm">Add</button>
      </div>
      <table class="data-table" v-if="patient.ultrasounds.length">
        <thead>
          <tr>
            <th>Дата</th>
            <th>Орган</th>
            <th>Измерения</th>
            <th>Обнаружения</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="us in patient.ultrasounds" :key="us.id">
            <td>{{ us.exam_date }}</td>
            <td>{{ us.organ }}</td>
            <td>{{ us.measurements }}</td>
            <td>{{ us.findings }}</td>
            <td>
              <button @click="deleteUltrasound(us.id)" class="btn-sm btn-danger">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else class="no-data">No ultrasounds recorded</p>
    </div>

    <div class="section">
      <div class="section-header">
        <h3>MRTs</h3>
        <button @click="showMRTModal = true" class="btn btn-primary btn-sm">Add</button>
      </div>
      <table class="data-table" v-if="patient.mrts.length">
        <thead>
          <tr>
            <th>Дата</th>
            <th>Часть тела</th>
            <th>Контраст</th>
            <th>Обнаружения</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="mrt in patient.mrts" :key="mrt.id">
            <td>{{ mrt.exam_date }}</td>
            <td>{{ mrt.body_part }}</td>
            <td>{{ mrt.contrast_used }}</td>
            <td>{{ mrt.findings }}</td>
            <td>
              <button @click="deleteMRT(mrt.id)" class="btn-sm btn-danger">Удалить</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else class="no-data">Нет МРТ записей</p>
    </div>

    <!-- Mammography Modal -->
    <div v-if="showMammoModal" class="modal" @click.self="showMammoModal = false">
      <div class="modal-content">
        <h3>Добавить маммографию</h3>
        <form @submit.prevent="saveMammo">
          <div class="form-group">
            <label>Exam Date *</label>
            <input v-model="mammoForm.exam_date" type="date" required class="input">
          </div>
          <div class="form-group">
            <label>Breast Density</label>
            <input v-model="mammoForm.breast_density" class="input">
          </div>
          <div class="form-group">
            <label>BIRADS Score</label>
            <input v-model.number="mammoForm.birads_score" type="number" class="input">
          </div>
          <div class="form-group">
            <label>Обнаружения</label>
            <textarea v-model="mammoForm.findings" class="input" rows="3"></textarea>
          </div>
          <div class="form-group">
            <label>Комментарии</label>
            <textarea v-model="mammoForm.notes" class="input" rows="3"></textarea>
          </div>
          <div class="form-actions">
            <button type="button" @click="showMammoModal = false" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary">Save</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Ultrasound Modal -->
    <div v-if="showUltrasoundModal" class="modal" @click.self="showUltrasoundModal = false">
      <div class="modal-content">
        <h3>Добавить УЗИ</h3>
        <form @submit.prevent="saveUltrasound">
          <div class="form-group">
            <label>Дата исследования *</label>
            <input v-model="ultrasoundForm.exam_date" type="date" required class="input">
          </div>
          <div class="form-group">
            <label>Орган</label>
            <input v-model="ultrasoundForm.organ" class="input">
          </div>
          <div class="form-group">
            <label>Измерения</label>
            <input v-model="ultrasoundForm.measurements" class="input">
          </div>
          <div class="form-group">
            <label>Обнаружения</label>
            <textarea v-model="ultrasoundForm.findings" class="input" rows="3"></textarea>
          </div>
          <div class="form-group">
            <label>Комментарии</label>
            <textarea v-model="ultrasoundForm.notes" class="input" rows="3"></textarea>
          </div>
          <div class="form-actions">
            <button type="button" @click="showUltrasoundModal = false" class="btn btn-secondary">Отмена</button>
            <button type="submit" class="btn btn-primary">Сохранить</button>
          </div>
        </form>
      </div>
    </div>

    <!-- MRT Modal -->
    <div v-if="showMRTModal" class="modal" @click.self="showMRTModal = false">
      <div class="modal-content">
        <h3>Добавить МРТ</h3>
        <form @submit.prevent="saveMRT">
          <div class="form-group">
            <label>Дата исследования *</label>
            <input v-model="mrtForm.exam_date" type="date" required class="input">
          </div>
          <div class="form-group">
            <label>Часть тела</label>
            <input v-model="mrtForm.body_part" class="input">
          </div>
          <div class="form-group">
            <label>Использование контраста</label>
            <input v-model="mrtForm.contrast_used" class="input">
          </div>
          <div class="form-group">
            <label>Обнаружения</label>
            <textarea v-model="mrtForm.findings" class="input" rows="3"></textarea>
          </div>
          <div class="form-group">
            <label>Impression</label>
            <textarea v-model="mrtForm.impression" class="input" rows="3"></textarea>
          </div>
          <div class="form-group">
            <label>Комментарии</label>
            <textarea v-model="mrtForm.notes" class="input" rows="3"></textarea>
          </div>
          <div class="form-actions">
            <button type="button" @click="showMRTModal = false" class="btn btn-secondary">Отмена</button>
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
      patient: null,
      showMammoModal: false,
      showUltrasoundModal: false,
      showMRTModal: false,
      mammoForm: {
        exam_date: '',
        breast_density: '',
        birads_score: null,
        findings: '',
        notes: ''
      },
      ultrasoundForm: {
        exam_date: '',
        organ: '',
        measurements: '',
        findings: '',
        notes: ''
      },
      mrtForm: {
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
    this.loadPatient()
  },
  methods: {
    async loadPatient() {
      try {
        const response = await api.getPatient(this.$route.params.id)
        this.patient = response.data
      } catch (error) {
        alert('Ошибка загрузки пациента')
        this.$router.push('/patients')
      }
    },
    async saveMammo() {
      try {
        await api.createMammography({
          ...this.mammoForm,
          patient_id: this.patient.id
        })
        this.showMammoModal = false
        this.loadPatient()
        this.mammoForm = {
          exam_date: '',
          breast_density: '',
          birads_score: null,
          findings: '',
          notes: ''
        }
      } catch (error) {
        alert('Ошибка сохранения маммографии')
      }
    },
    async deleteMammo(id) {
      if (confirm('Удалить запись маммографии?')) {
        try {
          await api.deleteMammography(id)
          this.loadPatient()
        } catch (error) {
          alert('Ошибка удаления записи маммографии')
        }
      }
    },
    async saveUltrasound() {
      try {
        await api.createUltrasound({
          ...this.ultrasoundForm,
          patient_id: this.patient.id
        })
        this.showUltrasoundModal = false
        this.loadPatient()
        this.ultrasoundForm = {
          exam_date: '',
          organ: '',
          measurements: '',
          findings: '',
          notes: ''
        }
      } catch (error) {
        alert('Ошибка сохранения УЗИ')
      }
    },
    async deleteUltrasound(id) {
      if (confirm('Удалить запись УЗИ?')) {
        try {
          await api.deleteUltrasound(id)
          this.loadPatient()
        } catch (error) {
          alert('Ошибка удаления записи УЗИ')
        }
      }
    },
    async saveMRT() {
      try {
        await api.createMRT({
          ...this.mrtForm,
          patient_id: this.patient.id
        })
        this.showMRTModal = false
        this.loadPatient()
        this.mrtForm = {
          exam_date: '',
          body_part: '',
          contrast_used: '',
          findings: '',
          impression: '',
          notes: ''
        }
      } catch (error) {
        alert('Ошибка сохранения МРТ')
      }
    },
    async deleteMRT(id) {
      if (confirm('Удалить запись МРТ?')) {
        try {
          await api.deleteMRT(id)
          this.loadPatient()
        } catch (error) {
          alert('Ошибка удаления записи МРТ')
        }
      }
    }
  }
}
</script>

<style scoped>
.patient-detail {
  padding: 1rem;
}

.header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.section {
  margin-bottom: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.no-data {
  color: #6c757d;
  font-style: italic;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 4px;
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

.btn-primary {
  background: #667eea;
  color: white;
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

.input {
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  width: 100%;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}
</style>