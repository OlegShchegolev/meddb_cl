<template>
  <div class="findings-modal modal" @click.self="$emit('close')">
    <div class="modal-content modal-xlarge">
      <div class="modal-header">
        <h3>Находки гистологии по биопсии (Дата: {{ histology_biopsy.exam_date }})</h3>
        <button @click="$emit('close')" class="btn-close">×</button>
      </div>

      <div class="findings-list">
        <div class="section-header">
          <h4>Список находок</h4>
          <button @click="showAddFinding = true" class="btn btn-primary btn-sm">Добавить находку</button>
        </div>

        <table class="data-table" v-if="findings.length">
          <thead>
            <tr>
              <th>№</th>
              <th>Локализация</th>
              <th>Глубина</th>
              <th>Тип</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="finding in findings" :key="finding.id">
              <td>{{ finding.finding_number }}</td>
              <td>{{ finding.quadrant_location }}</td>
              <td>{{ finding.depth_location }}</td>
              <td>{{ finding.finding_type }}</td>
              <td>
                <button @click="editFinding(finding)" class="btn-sm btn-warning">Изменить</button>
                <button @click="deleteFinding(finding.id)" class="btn-sm btn-danger">Удалить</button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data">Находок не обнаружено</p>
      </div>

      <!-- Модальное окно добавления/редактирования находки -->
      <div v-if="showAddFinding" class="inner-modal-wrapper">
        <div class="inner-modal-backdrop" @click.self="closeAddModal"></div>
        <div ref="modalContent" class="inner-modal-content modal-large">
          <h4>{{ editingFinding ? 'Редактировать находку' : 'Добавить находку' }}</h4>
          <form @submit.prevent="saveFinding">
            <div class="form-row">
              <div class="form-group">
                <label>Локализация по квадрантам *</label>
                <select v-model="findingForm.quadrant_location" required class="input">
                  <option value="">Выберите</option>
                  <option v-for="loc in quadrantLocations" :key="loc" :value="loc">{{ loc }}</option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Локализация по глубине МЖ *</label>
                <select v-model="findingForm.depth_location" required class="input">
                  <option value="">Выберите</option>
                  <option v-for="depth in depthLocations" :key="depth" :value="depth">{{ depth }}</option>
                </select>
              </div>
              <!-- Классификация опухоли МЖ ВОЗ 2019 (группа) -->
              <div class="form-group">
                <label>Классификация опухоли МЖ ВОЗ 2019 (группа) *</label>
                <select v-model="findingForm.classification_group" @change="onGroupChange" required class="input">
                  <option value="">Выберите</option>
                  <option v-for="group in findingClassificationGroups" :key="group" :value="group">{{ group }}</option>
                </select>
              </div>
            </div>

            <!-- Классификация опухоли МЖ ВОЗ 2019 (dbl) -->
            <div class="form-row">
              <div class="form-group">
                <label>Классификация опухоли МЖ ВОЗ 2019 (вид)</label>
                <select v-model="findingForm.classification_type" required class="input">
                  <option value="">Выберите</option>
                  <option v-for="type in findingClassificationTypes[findingForm.classification_group.split('.')[0]]" :key="type" :value="type">{{ type }}</option>
                </select>
              </div>

              <!-- Гистологическая степень злокачественности опухоли -->
              <div class="form-group" v-if="findingForm.malignancy_degree">
                <label>Гистологическая степень злокачественности опухоли</label>
                <select v-model="findingForm.malignancy_degree" class="input">
                  <option value="">Выберите</option>
                  <option value="Gx Категория G не может быть определена">Gx Категория G не может быть определена</option>
                  <option value="G1 Низкая степень злокачественности (благоприятный вариант), 3–5 баллов по шкале SBR (Ноттингемская шкала)">G1 Низкая степень злокачественности (благоприятный вариант), 3–5 баллов по шкале SBR (Ноттингемская шкала)</option>
                  <option value="G2 Умеренная степень злокачественности (промежуточный вариант), 6–7 баллов по шкале SBR (Ноттингемская шкала)">G2 Умеренная степень злокачественности (промежуточный вариант), 6–7 баллов по шкале SBR (Ноттингемская шкала)</option>
                  <option value="G3 Высокая степень злокачественности (неблагоприятный вариант), 8–9 баллов по шкале SBR (Ноттингемская шкала)">G3 Высокая степень злокачественности (неблагоприятный вариант), 8–9 баллов по шкале SBR (Ноттингемская шкала)</option>
                </select>
              </div>
            </div>

            <div class="form-actions">
              <button type="button" @click="closeAddModal" class="btn btn-secondary">Отмена</button>
              <button type="submit" class="btn btn-primary">Сохранить</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api'
import * as dict from '../dictionaries'

export default {
  props: {
    histology_biopsy: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      findings: [],
      showAddFinding: false,
      editingFinding: null,
      selectedFeatures: [],
      findingForm: {
        finding_number: null,
        affected_side: '',
        quadrant_location: '',
        depth_location: '',
        classification_group: '',
        classification_type: '',
        malignancy_degree: '',
      },
      // Справочники
      quadrantLocations: dict.QUADRANT_LOCATIONS,
      depthLocations: dict.DEPTH_LOCATIONS,
      findingTypes: dict.FINDING_TYPES,
      findingClassificationGroups: dict.CLASSIFICATION_GROUPS,
      findingClassificationTypes: dict.CLASSIFICATION_TYPES
    }
  },
  mounted() {
    this.loadFindings()
  },
  methods: {
    async loadFindings() {
      try {
        const response = await api.getHistologyBiopsyFindings(this.histology_biopsy.id)
        this.findings = response.data
      } catch (error) {
        console.error('Error loading findings:', error)
      }
    },
    onGroupChange() {
      // Очистить поля при смене типа
      this.findingForm = {
        ...this.findingForm,
        classification_type: ''
      }
      this.selectedFeatures = []

      // Прокрутить к началу формы при смене типа
      this.$nextTick(() => {
        this.scrollToFormBottom();
      });
    },

    scrollToFormBottom() {
      // Прокрутить к нижней части формы (к кнопкам)
      this.$nextTick(() => {
        if (this.$refs.modalContent) {
          const formActions = this.$refs.modalContent.querySelector('.form-actions');
          if (formActions) {
            formActions.scrollIntoView({behavior: 'smooth', block: 'end'});
          }
        }
      });
    },
    editFinding(finding) {
      this.editingFinding = finding.id

      this.findingForm = {...finding}

      this.showAddFinding = true
    },
    async saveFinding() {
      try {
        // Формируем данные для отправки
        const data = {
          ...this.findingForm,
          histology_biopsy_id: this.histology_biopsy.id,
        }


        if (this.editingFinding) {
          await api.updateHistologyBiopsyFinding(this.editingFinding, data)
        } else {
          await api.createHistologyBiopsyFinding(data)
        }

        this.closeAddModal()
        this.loadFindings()
        this.$emit('updated')
      } catch (error) {
        alert('Ошибка сохранения находки: ' + (error.response?.data?.detail || error.message))
      }
    },
    async deleteFinding(id) {
      if (confirm('Удалить находку?')) {
        try {
          await api.deleteHistologyBiopsyFinding(id)
          this.loadFindings()
          this.$emit('updated')
        } catch (error) {
          alert('Ошибка удаления')
        }
      }
    },
    closeAddModal() {
      this.showAddFinding = false
      this.editingFinding = null
      this.selectedFeatures = []
      this.findingForm = {
        finding_number: null,
        affected_side: '',
        quadrant_location: '',
        depth_location: '',
        classification_group: '',
        classification_type: '',
        malignancy_degree: '',
      }
    }
  },
  watch: {
    showAddFinding(newVal) {
      if (newVal) {
        // При открытии формы прокрутить к началу
        this.$nextTick(() => {
          if (this.$refs.modalContent) {
            this.$refs.modalContent.scrollTop = 0;
          }
        });
      }
    }
  }
}
</script>

<style scoped>
/* Основные стили модального окна */
.findings-modal.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.findings-modal .modal-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.modal-xlarge {
  max-width: 1000px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  padding: 2rem;
}

.modal-large {
  max-width: 800px;
  width: 90%;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e9ecef;
}

.btn-close {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #6c757d;
  padding: 0;
  width: 2rem;
  height: 2rem;
  line-height: 1;
}

.btn-close:hover {
  color: #000;
}

.findings-list {
  margin-bottom: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

/* Внутреннее модальное окно */
.inner-modal-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1002;
  display: flex;
  justify-content: center;
  align-items: center;
}

.inner-modal-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
}

.inner-modal-content {
  position: relative;
  z-index: 1003;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  max-height: 85vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  padding: 2rem;
  width: 90%;
  max-width: 800px;
}

/* Стили формы */
.finding-details {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  margin-top: 1rem;
}

.finding-details h5 {
  margin-bottom: 1rem;
  color: #495057;
}

.calculated-metrics {
  background: #e9ecef;
  padding: 0.75rem;
  border-radius: 4px;
  margin-top: 1rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.5rem;
}

.calculated-metrics div {
  font-size: 0.9rem;
}

.text-muted {
  color: #6c757d;
  font-size: 0.8rem;
  display: block;
  margin-top: 0.25rem;
}

.checkbox-group {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 0.5rem;
  max-height: 200px;
  overflow-y: auto;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  background: white;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  padding: 0.25rem;
}

.checkbox-label input[type="checkbox"] {
  cursor: pointer;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 4px;
  overflow: hidden;
}

.data-table th {
  background: #f8f9fa;
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid #dee2e6;
}

.data-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #dee2e6;
}

.no-data {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
  font-style: italic;
}

/* Кнопки */
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
  margin-right: 0.5rem;
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

/* Форма */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #212529;
}

.input {
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  width: 100%;
  background: white;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.input:focus {
  border-color: #667eea;
  outline: none;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #dee2e6;
  position: sticky;
  bottom: 0;
  background: white;
  padding-bottom: 1rem;
  margin-bottom: -1rem;
}

/* Адаптивность */
@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }

  .inner-modal-content {
    width: 95%;
    max-height: 90vh;
    padding: 1rem;
  }

  .modal-xlarge {
    width: 95%;
    padding: 1rem;
  }
}

@media (max-height: 700px) {
  .inner-modal-content {
    max-height: 90vh;
  }

  .finding-details {
    max-height: 300px;
    overflow-y: auto;
  }
}
</style>