<template>
  <div class="findings-modal modal" @click.self="$emit('close')">
    <div class="modal-content modal-xlarge">
      <div class="modal-header">
        <h3>Находки послеоперационной гистологии (Дата: {{ histology_postop.exam_date }})</h3>
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
              <th>Сторона</th>
              <th>Квадрант/ЛУ</th>
              <th>Глубина</th>
              <th>Классификация ВОЗ</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="finding in findings" :key="finding.id">
              <td>{{ finding.finding_number }}</td>
              <td>{{ finding.finding_location }}</td>
              <td>{{ finding.affected_side }}</td>
              <td>{{ finding.finding_location === 'Лимфатический узел' ? finding.lymph_node_group : finding.quadrant_location }}</td>
              <td>{{ finding.depth_location }}</td>
              <td>{{ finding.who_classification ? finding.who_classification.substring(0, 50) + '...' : '' }}</td>
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

            <!-- Локализация находки -->
            <div class="form-row">
              <div class="form-group">
                <label>Локализация находки *</label>
                <select v-model="findingForm.finding_location" required class="input" @change="onFindingLocationChange">
                  <option value="">Выберите</option>
                  <option v-for="loc in findingLocations" :key="loc" :value="loc">{{ loc }}</option>
                </select>
              </div>
            </div>

            <!-- Поля для Молочной железы -->
            <div v-if="findingForm.finding_location === 'Молочная железа'">
              <div class="form-row">
                <div class="form-group">
                  <label>Сторона</label>
                  <select v-model="findingForm.affected_side" class="input">
                    <option value="">Выберите</option>
                    <option value="Правая МЖ">Правая МЖ</option>
                    <option value="Левая МЖ">Левая МЖ</option>
                  </select>
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Локализация по квадрантам</label>
                  <select v-model="findingForm.quadrant_location" class="input">
                    <option value="">Выберите</option>
                    <option v-for="loc in quadrantLocations" :key="loc" :value="loc">{{ loc }}</option>
                  </select>
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Локализация по глубине МЖ</label>
                  <select v-model="findingForm.depth_location" class="input">
                    <option value="">Выберите</option>
                    <option v-for="depth in depthLocations" :key="depth" :value="depth">{{ depth }}</option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Поля для Лимфатического узла -->
            <div v-if="findingForm.finding_location === 'Лимфатический узел'">
              <div class="form-row">
                <div class="form-group">
                  <label>Группа измененных ЛУ</label>
                  <select v-model="findingForm.lymph_node_group" class="input">
                    <option value="">Выберите</option>
                    <option v-for="group in lymphNodeGroups" :key="group" :value="group">{{ group }}</option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Размеры находки -->
            <div class="form-row form-row-3">
              <div class="form-group">
                <label>Размер 1 (мм)</label>
                <input v-model.number="findingForm.size_1_mm" @input="calculateMetrics" type="number" min="0" class="input">
              </div>
              <div class="form-group">
                <label>Размер 2 (мм)</label>
                <input v-model.number="findingForm.size_2_mm" @input="calculateMetrics" type="number" min="0" class="input">
              </div>
              <div class="form-group">
                <label>Размер 3 (мм)</label>
                <input v-model.number="findingForm.size_3_mm" @input="calculateMetrics" type="number" min="0" class="input">
              </div>
            </div>

            <!-- Рассчитанные параметры -->
            <div v-if="findingForm.volume_mm3 || findingForm.size_max_mm" class="calculated-metrics">
              <div v-if="findingForm.volume_mm3"><strong>Объем:</strong> {{ findingForm.volume_mm3 }} мм³</div>
              <div v-if="findingForm.size_max_mm"><strong>Максимальный размер:</strong> {{ findingForm.size_max_mm }} мм</div>
              <div v-if="findingForm.size_min_mm"><strong>Минимальный размер:</strong> {{ findingForm.size_min_mm }} мм</div>
            </div>

            <!-- Морфологическое заключение -->
            <div class="form-row">
              <div class="form-group">
                <label>Морфологическое заключение</label>
                <textarea
                  v-model="findingForm.morphological_conclusion"
                  class="input textarea"
                  rows="3"
                  placeholder="Введите морфологическое заключение"
                ></textarea>
              </div>
            </div>

            <!-- Классификация опухоли МЖ ВОЗ 2019 -->
            <div class="form-row">
              <div class="form-group">
                <label>Классификация опухоли МЖ ВОЗ 2019</label>
                <div class="autocomplete-wrapper">
                  <input
                    type="text"
                    v-model="findingForm.who_classification"
                    @input="filterClassifications"
                    @focus="showClassificationDropdown = true"
                    @blur="onClassificationBlur"
                    placeholder="Введите или выберите классификацию"
                    class="input"
                  />
                  <div v-if="showClassificationDropdown && filteredClassifications.length > 0" class="autocomplete-dropdown">
                    <div
                      v-for="classification in filteredClassifications"
                      :key="classification"
                      @mousedown.prevent="selectClassification(classification)"
                      class="autocomplete-item"
                    >
                      {{ classification }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Гистологическая степень злокачественности опухоли -->
            <div class="form-row">
              <div class="form-group">
                <label>Гистологическая степень злокачественности опухоли</label>
                <select v-model="findingForm.malignancy_degree" class="input">
                  <option value="">Выберите</option>
                  <option value="Gx Категория G не может быть определена">Gx Категория G не может быть определена</option>
                  <option value="G1 Низкая степень злокачественности (благоприятный вариант), 3–5 баллов по шкале SBR (Ноттингемская шкала)">
                    G1 Низкая степень злокачественности (благоприятный вариант), 3–5 баллов по шкале SBR (Ноттингемская шкала)
                  </option>
                  <option value="G2 Умеренная степень злокачественности (промежуточный вариант), 6–7 баллов по шкале SBR (Ноттингемская шкала)">
                    G2 Умеренная степень злокачественности (промежуточный вариант), 6–7 баллов по шкале SBR (Ноттингемская шкала)
                  </option>
                  <option value="G3 Высокая степень злокачественности (неблагоприятный вариант), 8–9 баллов по шкале SBR (Ноттингемская шкала)">
                    G3 Высокая степень злокачественности (неблагоприятный вариант), 8–9 баллов по шкале SBR (Ноттингемская шкала)
                  </option>
                </select>
              </div>
            </div>

            <!-- Заключение по ИГХ -->
            <div class="form-row">
              <div class="form-group">
                <label>Заключение по ИГХ</label>
                <textarea
                  v-model="findingForm.ihc_conclusion"
                  class="input textarea"
                  rows="3"
                  placeholder="Введите заключение по ИГХ"
                ></textarea>
              </div>
            </div>

            <!-- ИГХ маркеры -->
            <div class="form-row form-row-4">
              <div class="form-group">
                <label>ER</label>
                <input
                  type="text"
                  v-model="findingForm.er_value"
                  class="input"
                  placeholder="Значение ER"
                />
              </div>
              <div class="form-group">
                <label>PR</label>
                <input
                  type="text"
                  v-model="findingForm.pr_value"
                  class="input"
                  placeholder="Значение PR"
                />
              </div>
              <div class="form-group">
                <label>HER2</label>
                <input
                  type="text"
                  v-model="findingForm.her2_value"
                  class="input"
                  placeholder="Значение HER2"
                />
              </div>
              <div class="form-group">
                <label>Ki-67</label>
                <input
                  type="text"
                  v-model="findingForm.ki67_value"
                  class="input"
                  placeholder="Значение Ki-67"
                />
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
  name: 'HistologyPostopFindingsModal',
  props: {
    histology_postop: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      findings: [],
      showAddFinding: false,
      editingFinding: null,

      // Форма
      findingForm: {
        finding_number: null,
        finding_location: '',
        affected_side: '',
        quadrant_location: '',
        depth_location: '',
        lymph_node_group: '',
        morphological_conclusion: '',
        who_classification: '',
        malignancy_degree: '',
        ihc_conclusion: '',
        er_value: '',
        pr_value: '',
        her2_value: '',
        ki67_value: '',
        size_1_mm: null,
        size_2_mm: null,
        size_3_mm: null,
        volume_mm3: null,
        size_max_mm: null,
        size_min_mm: null
      },

      // Автодополнение
      showClassificationDropdown: false,
      filteredClassifications: [],
      allClassifications: [],

      // Справочники
      findingLocations: dict.HISTOLOGY_FINDING_LOCATIONS || [],
      lymphNodeGroups: dict.LYMPH_NODE_GROUPS || [],
      quadrantLocations: dict.QUADRANT_LOCATIONS || [],
      depthLocations: dict.DEPTH_LOCATIONS || [],
      whoClassifications: dict.WHO_CLASSIFICATION_2019 || []
    }
  },
  mounted() {
    this.loadFindings()
    this.initializeAutocompleteData()
  },
  methods: {
    async loadFindings() {
      try {
        const response = await api.getHistologyPostopFindings(this.histology_postop.id)
        this.findings = response.data
      } catch (error) {
        console.error('Error loading findings:', error)
      }
    },

    initializeAutocompleteData() {
      this.allClassifications = Array.isArray(this.whoClassifications)
        ? [...this.whoClassifications]
        : []
    },

    onFindingLocationChange() {
      if (this.findingForm.finding_location === 'Молочная железа') {
        this.findingForm.lymph_node_group = ''
      } else if (this.findingForm.finding_location === 'Лимфатический узел') {
        this.findingForm.quadrant_location = ''
        this.findingForm.depth_location = ''
      }
    },

    filterClassifications() {
      const searchTerm = this.findingForm.who_classification.toLowerCase().trim()
      if (!searchTerm) {
        this.filteredClassifications = this.allClassifications.slice(0, 20)
      } else {
        this.filteredClassifications = this.allClassifications.filter(classification =>
          classification.toLowerCase().includes(searchTerm)
        ).slice(0, 20)
      }
      this.showClassificationDropdown = true
    },

    selectClassification(classification) {
      this.findingForm.who_classification = classification
      this.showClassificationDropdown = false
    },

    onClassificationBlur() {
      setTimeout(() => {
        this.showClassificationDropdown = false
      }, 200)
    },

    calculateMetrics() {
      const x = this.findingForm.size_1_mm
      const y = this.findingForm.size_2_mm
      const z = this.findingForm.size_3_mm

      // Рассчитываем max и min
      if (x || y || z) {
        const sizes = [x, y, z].filter(size => size !== null && size !== undefined && size !== '' && size > 0)

        if (sizes.length > 0) {
          this.findingForm.size_max_mm = Math.max(...sizes)
          this.findingForm.size_min_mm = Math.min(...sizes)
        } else {
          this.findingForm.size_max_mm = null
          this.findingForm.size_min_mm = null
        }
      } else {
        this.findingForm.size_max_mm = null
        this.findingForm.size_min_mm = null
      }

      // Рассчитываем объем
      if (x && y && z && x > 0 && y > 0 && z > 0) {
        const volume = (4/3) * Math.PI * (x/2) * (y/2) * (z/2)
        this.findingForm.volume_mm3 = Math.round(volume)
      } else {
        this.findingForm.volume_mm3 = null
      }
    },

    editFinding(finding) {
      this.editingFinding = finding.id
      this.findingForm = {...finding}
      this.showAddFinding = true
    },

    async saveFinding() {
      try {
        const data = {
          ...this.findingForm,
          histology_postop_id: this.histology_postop.id,
        }

        if (this.editingFinding) {
          await api.updateHistologyPostopFinding(this.editingFinding, data)
        } else {
          await api.createHistologyPostopFinding(data)
        }

        this.closeAddModal()
        this.loadFindings()
        this.$emit('updated')
      } catch (error) {
        console.error('Error saving finding:', error)
        alert('Ошибка сохранения находки: ' + (error.response?.data?.detail || error.message))
      }
    },

    async deleteFinding(id) {
      if (confirm('Удалить находку?')) {
        try {
          await api.deleteHistologyPostopFinding(id)
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
      this.showClassificationDropdown = false
      this.findingForm = {
        finding_number: null,
        finding_location: '',
        affected_side: '',
        quadrant_location: '',
        depth_location: '',
        lymph_node_group: '',
        morphological_conclusion: '',
        who_classification: '',
        malignancy_degree: '',
        ihc_conclusion: '',
        er_value: '',
        pr_value: '',
        her2_value: '',
        ki67_value: '',
        size_1_mm: null,
        size_2_mm: null,
        size_3_mm: null,
        volume_mm3: null,
        size_max_mm: null,
        size_min_mm: null
      }
    }
  },
  watch: {
    showAddFinding(newVal) {
      if (newVal) {
        this.$nextTick(() => {
          if (this.$refs.modalContent) {
            this.$refs.modalContent.scrollTop = 0
          }
        })
      }
    }
  }
}
</script>

<style scoped>
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
  max-width: 1400px;
  width: 95%;
  max-height: 90vh;
  overflow-y: auto;
  padding: 2rem;
}

.modal-large {
  max-width: 900px;
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
  max-width: 900px;
}

.autocomplete-wrapper {
  position: relative;
}

.autocomplete-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 200px;
  overflow-y: auto;
  background: white;
  border: 1px solid #ced4da;
  border-top: none;
  border-radius: 0 0 4px 4px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.autocomplete-item {
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 0.9rem;
}

.autocomplete-item:hover {
  background-color: #f8f9fa;
}

.autocomplete-item:active {
  background-color: #e9ecef;
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
  font-size: 0.9rem;
}

.data-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #dee2e6;
  font-size: 0.85rem;
}

.no-data {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
  font-style: italic;
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

.form-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-row-3 {
  grid-template-columns: repeat(3, 1fr);
}

.form-row-4 {
  grid-template-columns: repeat(4, 1fr);
}

.form-group {
  margin-bottom: 1rem;
  position: relative;
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

.textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.input:focus {
  border-color: #667eea;
  outline: none;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.calculated-metrics {
  background: #e9ecef;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.5rem;
}

.calculated-metrics div {
  font-size: 0.9rem;
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

@media (max-width: 768px) {
  .form-row,
  .form-row-3,
  .form-row-4 {
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

  .data-table th,
  .data-table td {
    padding: 0.5rem;
    font-size: 0.8rem;
  }
}
</style>