<template>
  <div class="patient-detail" v-if="patient">
    <div class="header">
      <button @click="$router.back()" class="btn btn-secondary">← Назад</button>
      <h2>{{ patient.last_name }} {{ patient.first_name }} {{ patient.middle_name }}</h2>
    </div>

    <div class="patient-info card">
      <h3>Паспорт пациента</h3>
      <div class="info-grid">
        <div><strong>ID:</strong> {{ patient.id }}</div>
        <div><strong>СНИЛС:</strong> {{ patient.snils }}</div>
        <div><strong>Дата рождения:</strong> {{ patient.date_of_birth }}</div>
        <div><strong>Пол:</strong> {{ patient.gender }}</div>
        <div><strong>Диагноз:</strong> {{ patient.diagnosis }}</div>
        <div><strong>Стадия по TNM:</strong> {{ patient.tnm_stage }}</div>
        <div><strong>Последнее обновление:</strong> {{ formatDateTime(patient.last_updated) }}</div>
      </div>
      <div v-if="patient.comment" style="margin-top: 1rem">
        <strong>Комментарий:</strong> {{ patient.comment }}
      </div>
    </div>

    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="['tab-btn', {active: activeTab === tab.id}]"
      >
        {{ tab.label }}
      </button>
    </div>

    <div class="tab-content">
      <!-- УЗИ -->
      <div v-if="activeTab === 'ultrasound'" class="section">
        <div class="section-header">
          <h3>УЗИ исследования</h3>
          <button @click="showUltrasoundModal = true" class="btn btn-primary btn-sm">Добавить</button>
        </div>
        <table class="data-table" v-if="patient.ultrasounds.length">
          <thead>
            <tr>
              <th>Дата</th>
              <th>Заключение</th>
              <th>Комментарий</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in patient.ultrasounds" :key="item.id">
              <td>{{ item.exam_date }}</td>
              <td>{{ item.findings }}</td>
              <td>{{ item.comment }}</td>
              <td><button @click="deleteUltrasound(item.id)" class="btn-sm btn-danger">Удалить</button></td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data">Нет данных</p>
      </div>

      <!-- Маммография -->
      <div v-if="activeTab === 'mammography'" class="section">
        <div class="section-header">
          <h3>Маммография</h3>
          <button @click="showMammoModal = true" class="btn btn-primary btn-sm">Добавить</button>
        </div>
        <table class="data-table" v-if="patient.mammographies.length">
          <thead>
            <tr>
              <th>Дата</th>
              <th>Этап</th>
              <th>Сторона</th>
              <th>BI-RADS</th>
              <th>ACR</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in patient.mammographies" :key="item.id">
              <td>{{ item.exam_date }}</td>
              <td>{{ item.study_stage }}</td>
              <td>{{ item.affected_side }}</td>
              <td>{{ item.birads_category }}</td>
              <td>{{ item.acr_density }}</td>
              <td><button @click="deleteMammo(item.id)" class="btn-sm btn-danger">Удалить</button></td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data">Нет данных</p>
      </div>

      <!-- Контрастная маммография -->
      <div v-if="activeTab === 'contrast'" class="section">
        <div class="section-header">
          <h3>Контрастная маммография</h3>
          <button @click="showContrastModal = true" class="btn btn-primary btn-sm">Добавить</button>
        </div>
        <table class="data-table" v-if="patient.contrast_mammographies.length">
          <thead>
            <tr>
              <th>Дата</th>
              <th>Этап</th>
              <th>Сторона</th>
              <th>BI-RADS</th>
              <th>ACR</th>
              <th>BPE</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in patient.contrast_mammographies" :key="item.id">
              <td>{{ item.exam_date }}</td>
              <td>{{ item.study_stage }}</td>
              <td>{{ item.affected_side }}</td>
              <td>{{ item.birads_category }}</td>
              <td>{{ item.acr_density }}</td>
              <td>{{ item.bpe_level }}</td>
              <td>
                <button @click="viewContrastDetails(item)" class="btn-sm btn-info">Просмотр</button>
                <button @click="deleteContrast(item.id)" class="btn-sm btn-danger">Удалить</button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data">Нет данных</p>
      </div>

      <!-- МРТ -->
      <div v-if="activeTab === 'mrt'" class="section">
        <div class="section-header">
          <h3>МРТ исследования</h3>
          <button @click="showMRTModal = true" class="btn btn-primary btn-sm">Добавить</button>
        </div>
        <table class="data-table" v-if="patient.mrts.length">
          <thead>
            <tr>
              <th>Дата</th>
              <th>Заключение</th>
              <th>Комментарий</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in patient.mrts" :key="item.id">
              <td>{{ item.exam_date }}</td>
              <td>{{ item.findings }}</td>
              <td>{{ item.comment }}</td>
              <td><button @click="deleteMRT(item.id)" class="btn-sm btn-danger">Удалить</button></td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data">Нет данных</p>
      </div>

      <!-- Гистология по биопсии -->
      <div v-if="activeTab === 'histology_biopsy'" class="section">
        <div class="section-header">
          <h3>Гистология и ИГХ (по биопсии)</h3>
          <button @click="showHistBiopsyModal = true" class="btn btn-primary btn-sm">Добавить</button>
        </div>
        <table class="data-table" v-if="patient.histology_biopsies.length">
          <thead>
            <tr>
              <th>Дата</th>
              <th>Заключение</th>
              <th>ИГХ</th>
              <th>Комментарий</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in patient.histology_biopsies" :key="item.id">
              <td>{{ item.exam_date }}</td>
              <td>{{ item.findings }}</td>
              <td>{{ item.ihc_results }}</td>
              <td>{{ item.comment }}</td>
              <td><button @click="deleteHistBiopsy(item.id)" class="btn-sm btn-danger">Удалить</button></td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data">Нет данных</p>
      </div>

      <!-- Цитология по биопсии -->
      <div v-if="activeTab === 'cytology'" class="section">
        <div class="section-header">
          <h3>Цитология (по биопсии)</h3>
          <button @click="showCytoModal = true" class="btn btn-primary btn-sm">Добавить</button>
        </div>
        <table class="data-table" v-if="patient.cytology_biopsies.length">
          <thead>
            <tr>
              <th>Дата</th>
              <th>Заключение</th>
              <th>Комментарий</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in patient.cytology_biopsies" :key="item.id">
              <td>{{ item.exam_date }}</td>
              <td>{{ item.findings }}</td>
              <td>{{ item.comment }}</td>
              <td><button @click="deleteCyto(item.id)" class="btn-sm btn-danger">Удалить</button></td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data">Нет данных</p>
      </div>

      <!-- Гистология послеоперационная -->
      <div v-if="activeTab === 'histology_postop'" class="section">
        <div class="section-header">
          <h3>Гистология и ИГХ (послеоперационная)</h3>
          <button @click="showHistPostopModal = true" class="btn btn-primary btn-sm">Добавить</button>
        </div>
        <table class="data-table" v-if="patient.histology_postops.length">
          <thead>
            <tr>
              <th>Дата</th>
              <th>Заключение</th>
              <th>ИГХ</th>
              <th>Комментарий</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in patient.histology_postops" :key="item.id">
              <td>{{ item.exam_date }}</td>
              <td>{{ item.findings }}</td>
              <td>{{ item.ihc_results }}</td>
              <td>{{ item.comment }}</td>
              <td><button @click="deleteHistPostop(item.id)" class="btn-sm btn-danger">Удалить</button></td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data">Нет данных</p>
      </div>
    </div>

    <!-- Modal УЗИ -->
    <div v-if="showUltrasoundModal" class="modal" @click.self="showUltrasoundModal = false">
      <div class="modal-content">
        <h3>Добавить УЗИ</h3>
        <form @submit.prevent="saveUltrasound">
          <div class="form-group">
            <label>Дата исследования *</label>
            <input v-model="ultrasoundForm.exam_date" type="date" required class="input">
          </div>
          <div class="form-group">
            <label>Заключение</label>
            <textarea v-model="ultrasoundForm.findings" class="input" rows="4"></textarea>
          </div>
          <div class="form-group">
            <label>Комментарий</label>
            <textarea v-model="ultrasoundForm.comment" class="input" rows="2"></textarea>
          </div>
          <div class="form-actions">
            <button type="button" @click="showUltrasoundModal = false" class="btn btn-secondary">Отмена</button>
            <button type="submit" class="btn btn-primary">Сохранить</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Маммография (упрощенная) -->
    <div v-if="showMammoModal" class="modal" @click.self="showMammoModal = false">
      <div class="modal-content">
        <h3>Добавить маммографию</h3>
        <form @submit.prevent="saveMammo">
          <div class="form-group">
            <label>Дата исследования *</label>
            <input v-model="mammoForm.exam_date" type="date" required class="input">
          </div>
          <div class="form-group">
            <label>Этап исследования (1-9)</label>
            <input v-model.number="mammoForm.study_stage" type="number" min="1" max="9" class="input">
          </div>
          <div class="form-group">
            <label>Сторона поражения</label>
            <select v-model="mammoForm.affected_side" class="input">
              <option value="">Выберите</option>
              <option value="Правая">Правая</option>
              <option value="Левая">Левая</option>
              <option value="Обе">Обе</option>
            </select>
          </div>
          <div class="form-group">
            <label>Категория BI-RADS</label>
            <select v-model="mammoForm.birads_category" class="input">
              <option value="">Выберите</option>
              <option value="0">BI-RADS 0</option>
              <option value="1">BI-RADS 1</option>
              <option value="2">BI-RADS 2</option>
              <option value="3">BI-RADS 3</option>
              <option value="4">BI-RADS 4</option>
              <option value="5">BI-RADS 5</option>
              <option value="6">BI-RADS 6</option>
            </select>
          </div>
          <div class="form-group">
            <label>Плотность по ACR</label>
            <select v-model="mammoForm.acr_density" class="input">
              <option value="">Выберите</option>
              <option value="A">ACR A</option>
              <option value="B">ACR B</option>
              <option value="C">ACR C</option>
              <option value="D">ACR D</option>
            </select>
          </div>
          <div class="form-group">
            <label>Комментарий</label>
            <textarea v-model="mammoForm.comment" class="input" rows="3"></textarea>
          </div>
          <div class="form-actions">
            <button type="button" @click="showMammoModal = false" class="btn btn-secondary">Отмена</button>
            <button type="submit" class="btn btn-primary">Сохранить</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Контрастная маммография -->
    <div v-if="showContrastModal" class="modal" @click.self="showContrastModal = false">
      <div class="modal-content modal-large">
        <h3>Добавить контрастную маммографию</h3>
        <form @submit.prevent="saveContrast">
          <div class="form-row">
            <div class="form-group">
              <label>Дата исследования *</label>
              <input v-model="contrastForm.exam_date" type="date" required class="input">
            </div>
            <div class="form-group">
              <label>Этап исследования (1-9)</label>
              <input v-model.number="contrastForm.study_stage" type="number" min="1" max="9" class="input">
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Сторона поражения</label>
              <select v-model="contrastForm.affected_side" class="input">
                <option value="">Выберите</option>
                <option value="Правая">Правая</option>
                <option value="Левая">Левая</option>
                <option value="Обе">Обе</option>
              </select>
            </div>
            <div class="form-group">
              <label>Категория BI-RADS</label>
              <select v-model="contrastForm.birads_category" class="input">
                <option value="">Выберите</option>
                <option value="0">BI-RADS 0</option>
                <option value="1">BI-RADS 1</option>
                <option value="2">BI-RADS 2</option>
                <option value="3">BI-RADS 3</option>
                <option value="4">BI-RADS 4</option>
                <option value="5">BI-RADS 5</option>
                <option value="6">BI-RADS 6</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Плотность по ACR</label>
              <select v-model="contrastForm.acr_density" class="input">
                <option value="">Выберите</option>
                <option value="A">ACR A</option>
                <option value="B">ACR B</option>
                <option value="C">ACR C</option>
                <option value="D">ACR D</option>
              </select>
            </div>
            <div class="form-group">
              <label>Степень фонового контрастирования (BPE)</label>
              <select v-model="contrastForm.bpe_level" class="input">
                <option value="">Выберите</option>
                <option value="Минимальная">Минимальная</option>
                <option value="Слабая">Слабая</option>
                <option value="Умеренная">Умеренная</option>
                <option value="Выраженная">Выраженная</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Симметрия фонового контрастирования</label>
            <select v-model="contrastForm.bpe_symmetry" class="input">
              <option value="">Выберите</option>
              <option value="Симметричная">Симметричная</option>
              <option value="Асимметричная">Асимметричная</option>
            </select>
          </div>

          <div class="form-group">
            <label>Комментарий</label>
            <textarea v-model="contrastForm.comment" class="input" rows="3"></textarea>
          </div>

          <div class="form-actions">
            <button type="button" @click="showContrastModal = false" class="btn btn-secondary">Отмена</button>
            <button type="submit" class="btn btn-primary">Сохранить</button>
          </div>
        </form>
      </div>
    </div>

    <SimpleModal
      v-if="showMRTModal"
      title="Добавить МРТ"
      :form="mrtForm"
      @close="showMRTModal = false"
      @save="saveMRT"
    />

    <HistologyModal
      v-if="showHistBiopsyModal"
      title="Добавить гистологию (биопсия)"
      :form="histBiopsyForm"
      @close="showHistBiopsyModal = false"
      @save="saveHistBiopsy"
    />

    <SimpleModal
      v-if="showCytoModal"
      title="Добавить цитологию"
      :form="cytoForm"
      @close="showCytoModal = false"
      @save="saveCyto"
    />

    <HistologyModal
      v-if="showHistPostopModal"
      title="Добавить гистологию (послеоперационная)"
      :form="histPostopForm"
      @close="showHistPostopModal = false"
      @save="saveHistPostop"
    />
  </div>
</template>

<script>
import api from '../api'

export default {
  data() {
    return {
      patient: null,
      activeTab: 'ultrasound',
      tabs: [
        { id: 'ultrasound', label: 'УЗИ' },
        { id: 'mammography', label: 'Маммография' },
        { id: 'contrast', label: 'Контрастная маммография' },
        { id: 'mrt', label: 'МРТ' },
        { id: 'histology_biopsy', label: 'Гистология (биопсия)' },
        { id: 'cytology', label: 'Цитология' },
        { id: 'histology_postop', label: 'Гистология (послеоп.)' }
      ],
      showUltrasoundModal: false,
      showMammoModal: false,
      showContrastModal: false,
      showMRTModal: false,
      showHistBiopsyModal: false,
      showCytoModal: false,
      showHistPostopModal: false,
      ultrasoundForm: { exam_date: '', findings: '', comment: '' },
      mammoForm: {
        exam_date: '',
        study_stage: null,
        affected_side: '',
        birads_category: '',
        acr_density: '',
        comment: ''
      },
      contrastForm: {
        exam_date: '',
        study_stage: null,
        affected_side: '',
        birads_category: '',
        acr_density: '',
        bpe_level: '',
        bpe_symmetry: '',
        comparison_available: false,
        dynamics: '',
        comment: ''
      },
      mrtForm: { exam_date: '', findings: '', comment: '' },
      histBiopsyForm: { exam_date: '', findings: '', ihc_results: '', comment: '' },
      cytoForm: { exam_date: '', findings: '', comment: '' },
      histPostopForm: { exam_date: '', findings: '', ihc_results: '', comment: '' }
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
        alert('Ошибка загрузки данных пациента')
        this.$router.push('/patients')
      }
    },
    formatDateTime(dt) {
      if (!dt) return ''
      return new Date(dt).toLocaleString('ru-RU')
    },
    async saveUltrasound() {
      try {
        await api.createUltrasound({ ...this.ultrasoundForm, patient_id: this.patient.id })
        this.showUltrasoundModal = false
        this.ultrasoundForm = { exam_date: '', findings: '', comment: '' }
        this.loadPatient()
      } catch (error) {
        alert('Ошибка сохранения')
      }
    },
    async deleteUltrasound(id) {
      if (confirm('Удалить запись?')) {
        await api.deleteUltrasound(id)
        this.loadPatient()
      }
    },
    async saveMammo() {
      try {
        await api.createMammography({ ...this.mammoForm, patient_id: this.patient.id })
        this.showMammoModal = false
        this.mammoForm = { exam_date: '', study_stage: null, affected_side: '', birads_category: '', acr_density: '', comment: '' }
        this.loadPatient()
      } catch (error) {
        alert('Ошибка сохранения')
      }
    },
    async deleteMammo(id) {
      if (confirm('Удалить запись?')) {
        await api.deleteMammography(id)
        this.loadPatient()
      }
    },
    async saveContrast() {
      try {
        await api.createContrastMammography({ ...this.contrastForm, patient_id: this.patient.id })
        this.showContrastModal = false
        this.contrastForm = {
          exam_date: '',
          study_stage: null,
          affected_side: '',
          birads_category: '',
          acr_density: '',
          bpe_level: '',
          bpe_symmetry: '',
          comparison_available: false,
          dynamics: '',
          comment: ''
        }
        this.loadPatient()
      } catch (error) {
        alert('Ошибка сохранения')
      }
    },
    viewContrastDetails(item) {
      alert('Детальный просмотр с находками будет реализован в следующей версии')
    },
    async deleteContrast(id) {
      if (confirm('Удалить запись?')) {
        await api.deleteContrastMammography(id)
        this.loadPatient()
      }
    },
    async saveMRT() {
      await api.createMRT({ ...this.mrtForm, patient_id: this.patient.id })
      this.showMRTModal = false
      this.loadPatient()
    },
    async deleteMRT(id) {
      if (confirm('Удалить запись?')) {
        await api.deleteMRT(id)
        this.loadPatient()
      }
    },
    async saveHistBiopsy() {
      await api.createHistologyBiopsy({ ...this.histBiopsyForm, patient_id: this.patient.id })
      this.showHistBiopsyModal = false
      this.loadPatient()
    },
    async deleteHistBiopsy(id) {
      if (confirm('Удалить запись?')) {
        await api.deleteHistologyBiopsy(id)
        this.loadPatient()
      }
    },
    async saveCyto() {
      await api.createCytologyBiopsy({ ...this.cytoForm, patient_id: this.patient.id })
      this.showCytoModal = false
      this.loadPatient()
    },
    async deleteCyto(id) {
      if (confirm('Удалить запись?')) {
        await api.deleteCytologyBiopsy(id)
        this.loadPatient()
      }
    },
    async saveHistPostop() {
      await api.createHistologyPostop({ ...this.histPostopForm, patient_id: this.patient.id })
      this.showHistPostopModal = false
      this.loadPatient()
    },
    async deleteHistPostop(id) {
      if (confirm('Удалить запись?')) {
        await api.deleteHistologyPostop(id)
        this.loadPatient()
      }
    }
  }
}
</script>

<style scoped>
.patient-detail { padding: 1rem; }
.header { display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem; }
.card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 2rem; }
.info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 1rem; }
.tabs { display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap; }
.tab-btn { padding: 0.75rem 1.5rem; border: none; background: #e9ecef; cursor: pointer; border-radius: 4px 4px 0 0; font-weight: 500; }
.tab-btn.active { background: #667eea; color: white; }
.tab-content { background: white; padding: 1.5rem; border-radius: 0 4px 4px 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { background: #f8f9fa; padding: 0.75rem; text-align: left; font-weight: 600; }
.data-table td { padding: 0.75rem; border-top: 1px solid #dee2e6; }
.no-data { color: #6c757d; font-style: italic; padding: 1rem; }
.btn { padding: 0.5rem 1rem; border: none; border-radius: 4px; cursor: pointer; font-weight: 500; }
.btn-primary { background: #667eea; color: white; }
.btn-secondary { background: #6c757d; color: white; }
.btn-sm { padding: 0.25rem 0.75rem; font-size: 0.875rem; }
.btn-danger { background: #dc3545; color: white; }
.modal { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-content { background: white; padding: 2rem; border-radius: 8px; max-width: 600px; width: 90%; max-height: 90vh; overflow-y: auto; }
.modal-large { max-width: 800px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
.input { padding: 0.5rem; border: 1px solid #ced4da; border-radius: 4px; width: 100%; }
.form-actions { display: flex; gap: 1rem; justify-content: flex-end; margin-top: 1.5rem; }
</style>