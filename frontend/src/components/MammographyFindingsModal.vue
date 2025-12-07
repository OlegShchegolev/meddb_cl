<template>
  <div class="findings-modal modal" @click.self="$emit('close')">
    <div class="modal-content modal-xlarge">
      <div class="modal-header">
        <h3>Находки маммографии (Дата: {{ mammography.exam_date }})</h3>
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
              <th>Размеры</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="finding in findings" :key="finding.id">
              <td>{{ finding.finding_number }}</td>
              <td>{{ finding.quadrant_location }}</td>
              <td>{{ finding.depth_location }}</td>
              <td>{{ finding.finding_type }}</td>
              <td>{{ finding.size_mm }}</td>
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
      <div v-if="showAddFinding" class="modal" @click.self="closeAddModal">
        <div class="modal-content modal-large">
          <h4>{{ editingFinding ? 'Редактировать находку' : 'Добавить находку' }}</h4>
          <form @submit.prevent="saveFinding">
            <div class="form-row">
              <div class="form-group">
                <label>Номер находки (1-9) *</label>
                <input v-model.number="findingForm.finding_number" type="number" min="1" max="9" required class="input">
              </div>
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
              <div class="form-group">
                <label>Тип находки *</label>
                <select v-model="findingForm.finding_type" @change="onTypeChange" required class="input">
                  <option value="">Выберите</option>
                  <option v-for="type in findingTypes" :key="type" :value="type">{{ type }}</option>
                </select>
              </div>
            </div>

            <!-- Поля для "Объемное образование" -->
            <div v-if="findingForm.finding_type === 'Объемное образование'" class="finding-details">
              <h5>Описание объемного образования</h5>
              <div class="form-row">
                <div class="form-group">
                  <label>Форма</label>
                  <select v-model="findingForm.mass_shape" class="input">
                    <option value="">Выберите</option>
                    <option v-for="shape in massShapes" :key="shape" :value="shape">{{ shape }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Контур</label>
                  <select v-model="findingForm.mass_margin" class="input">
                    <option value="">Выберите</option>
                    <option v-for="margin in massMargins" :key="margin" :value="margin">{{ margin }}</option>
                  </select>
                </div>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>Плотность</label>
                  <select v-model="findingForm.mass_density" class="input">
                    <option value="">Выберите</option>
                    <option v-for="density in massDensities" :key="density" :value="density">{{ density }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Размеры (мм) *</label>
                  <input v-model="findingForm.size_mm" placeholder="15x16x17" required class="input">
                </div>
              </div>
            </div>

            <!-- Поля для "Асимметрия" -->
            <div v-if="findingForm.finding_type === 'Асимметрия'" class="finding-details">
              <h5>Описание асимметрии</h5>
              <div class="form-row">
                <div class="form-group">
                  <label>Вид асимметрии</label>
                  <select v-model="findingForm.asymmetry_type" class="input">
                    <option value="">Выберите</option>
                    <option v-for="type in asymmetryTypes" :key="type" :value="type">{{ type }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Размеры (мм) *</label>
                  <input v-model="findingForm.size_mm" placeholder="15x16x17" required class="input">
                </div>
              </div>
            </div>

            <!-- Поля для "Кальцинаты" -->
            <div v-if="findingForm.finding_type === 'Кальцинаты'" class="finding-details">
              <h5>Описание кальцинатов</h5>
              <div class="form-group">
                <label>Вероятность злокачественности</label>
                <select v-model="findingForm.calcification_malignancy" class="input">
                  <option value="">Выберите</option>
                  <option v-for="mal in calcificationMalignancy" :key="mal" :value="mal">{{ mal }}</option>
                </select>
              </div>
              <div class="form-group">
                <label>Морфология</label>
                <select v-model="findingForm.calcification_morphology" class="input">
                  <option value="">Выберите</option>
                  <option v-for="morph in calcificationMorphology" :key="morph" :value="morph">{{ morph }}</option>
                </select>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>Распределение</label>
                  <select v-model="findingForm.calcification_distribution" class="input">
                    <option value="">Выберите</option>
                    <option v-for="dist in calcificationDistribution" :key="dist" :value="dist">{{ dist }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Размеры зоны (мм) *</label>
                  <input v-model="findingForm.size_mm" placeholder="15x16x17" required class="input">
                </div>
              </div>
            </div>

            <!-- Поля для "Сопутствующие изменения" -->
            <div v-if="findingForm.finding_type === 'Сопутствующие изменения'" class="finding-details">
              <h5>Сопутствующие изменения</h5>
              <div class="form-group">
                <label>Вид признака (можно выбрать несколько)</label>
                <div class="checkbox-group">
                  <label v-for="feature in associatedFeatures" :key="feature" class="checkbox-label">
                    <input
                      type="checkbox"
                      :value="feature"
                      v-model="selectedFeatures"
                    >
                    {{ feature }}
                  </label>
                </div>
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
    mammography: {
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
        quadrant_location: '',
        depth_location: '',
        finding_type: '',
        mass_shape: '',
        mass_margin: '',
        mass_density: '',
        asymmetry_type: '',
        calcification_malignancy: '',
        calcification_morphology: '',
        calcification_distribution: '',
        size_mm: ''
      },
      // Справочники
      quadrantLocations: dict.QUADRANT_LOCATIONS,
      depthLocations: dict.DEPTH_LOCATIONS,
      findingTypes: dict.FINDING_TYPES,
      massShapes: dict.MASS_SHAPES,
      massMargins: dict.MASS_MARGINS,
      massDensities: dict.MASS_DENSITY,
      asymmetryTypes: dict.ASYMMETRY_TYPES,
      calcificationMalignancy: dict.CALCIFICATION_MALIGNANCY,
      calcificationMorphology: dict.CALCIFICATION_MORPHOLOGY,
      calcificationDistribution: dict.CALCIFICATION_DISTRIBUTION,
      associatedFeatures: dict.ASSOCIATED_FEATURES
    }
  },
  mounted() {
    this.loadFindings()
  },
  methods: {
    async loadFindings() {
      try {
        const response = await api.getMammographyFindings(this.mammography.id)
        this.findings = response.data
      } catch (error) {
        console.error('Error loading findings:', error)
      }
    },
    onTypeChange() {
      // Очистить поля при смене типа
      this.findingForm.mass_shape = ''
      this.findingForm.mass_margin = ''
      this.findingForm.mass_density = ''
      this.findingForm.asymmetry_type = ''
      this.findingForm.calcification_malignancy = ''
      this.findingForm.calcification_morphology = ''
      this.findingForm.calcification_distribution = ''
      this.findingForm.size_mm = ''
      this.selectedFeatures = []
    },
    editFinding(finding) {
      this.editingFinding = finding.id
      this.findingForm = { ...finding }
      if (finding.associated_feature) {
        try {
          this.selectedFeatures = JSON.parse(finding.associated_feature)
        } catch {
          this.selectedFeatures = []
        }
      }
      this.showAddFinding = true
    },
    async saveFinding() {
      try {
        const data = {
          ...this.findingForm,
          mammography_id: this.mammography.id,
          associated_feature: this.findingForm.finding_type === 'Сопутствующие изменения'
            ? JSON.stringify(this.selectedFeatures)
            : null
        }

        if (this.editingFinding) {
          await api.updateMammographyFinding(this.editingFinding, data)
        } else {
          await api.createMammographyFinding(data)
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
          await api.deleteMammographyFinding(id)
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
        quadrant_location: '',
        depth_location: '',
        finding_type: '',
        mass_shape: '',
        mass_margin: '',
        mass_density: '',
        asymmetry_type: '',
        calcification_malignancy: '',
        calcification_morphology: '',
        calcification_distribution: '',
        size_mm: ''
      }
    }
  }
}
</script>

<style scoped>
.findings-modal {
  z-index: 1001;
}

.modal-xlarge {
  max-width: 1000px;
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

.checkbox-group {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 0.5rem;
  max-height: 200px;
  overflow-y: auto;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
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
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
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
  padding-top: 1rem;
  border-top: 1px solid #dee2e6;
}
</style>