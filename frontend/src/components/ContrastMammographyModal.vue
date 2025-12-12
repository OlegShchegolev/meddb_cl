<template>
  <div class="findings-modal modal" @click.self="$emit('close')">
    <div class="modal-content modal-xlarge">
      <div class="modal-header">
        <h3>Контрастная маммография (Дата: {{ contrastMammo.exam_date }})</h3>
        <button @click="$emit('close')" class="btn-close">×</button>
      </div>

      <!-- Общая информация -->
      <div class="info-section">
        <div class="info-grid">
          <div><strong>Этап:</strong> {{ contrastMammo.study_stage }}</div>
          <div><strong>Сторона:</strong> {{ contrastMammo.affected_side }}</div>
          <div><strong>BI-RADS:</strong> {{ contrastMammo.birads_category }}</div>
          <div><strong>ACR:</strong> {{ contrastMammo.acr_density }}</div>
          <div><strong>BPE уровень:</strong> {{ contrastMammo.bpe_level }}</div>
          <div><strong>BPE симметрия:</strong> {{ contrastMammo.bpe_symmetry }}</div>
        </div>
      </div>

      <!-- Вкладки для LE и RC находок -->
      <div class="tabs-section">
        <button
          @click="activeTab = 'le'"
          :class="['tab-btn', {active: activeTab === 'le'}]"
        >
          Находки LE
        </button>
        <button
          @click="activeTab = 'rc'"
          :class="['tab-btn', {active: activeTab === 'rc'}]"
        >
          Находки RC
        </button>
      </div>

      <!-- LE находки -->
      <div v-if="activeTab === 'le'" class="findings-section">
        <div class="section-header">
          <h4>Находки на LE (Low Energy)</h4>
          <button @click="showAddLEFinding = true" class="btn btn-primary btn-sm">Добавить находку LE</button>
        </div>

        <table class="data-table" v-if="leFindings.length">
          <thead>
            <tr>
              <th>№</th>
              <th>Локализация</th>
              <th>Тип</th>
              <th>Размеры</th>
              <th>На RC</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="finding in leFindings" :key="finding.id">
              <td>{{ finding.finding_number }}</td>
              <td>{{ finding.quadrant_location }}</td>
              <td>{{ finding.finding_type }}</td>
              <td>{{ finding.size_mm }}</td>
              <td>{{ finding.visible_on_rc }}</td>
              <td>
                <button @click="deleteLEFinding(finding.id)" class="btn-sm btn-danger">Удалить</button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data">Находок LE не обнаружено</p>
      </div>

      <!-- RC находки -->
      <div v-if="activeTab === 'rc'" class="findings-section">
        <div class="section-header">
          <h4>Находки на RC (не определяющиеся на LE)</h4>
          <button @click="showAddRCFinding = true" class="btn btn-primary btn-sm">Добавить находку RC</button>
        </div>

        <table class="data-table" v-if="rcFindings.length">
          <thead>
            <tr>
              <th>№</th>
              <th>Локализация</th>
              <th>Тип</th>
              <th>Размеры</th>
              <th>Интенсивность</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="finding in rcFindings" :key="finding.id">
              <td>{{ finding.finding_number }}</td>
              <td>{{ finding.quadrant_location }}</td>
              <td>{{ finding.finding_type }}</td>
              <td>{{ finding.size_mm }}</td>
              <td>{{ finding.enhancement_intensity }}</td>
              <td>
                <button @click="deleteRCFinding(finding.id)" class="btn-sm btn-danger">Удалить</button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data">Находок RC не обнаружено</p>
      </div>

      <!-- Модал добавления LE находки -->
      <div v-if="showAddLEFinding" class="modal inner-modal" @click.self="showAddLEFinding = false">
        <div class="modal-content modal-large">
          <h4>Добавить находку LE</h4>
          <form @submit.prevent="saveLEFinding">
            <div class="form-row">
              <div class="form-group">
                <label>Номер находки (1-9) *</label>
                <input v-model.number="leFindingForm.finding_number" type="number" min="1" max="9" required class="input">
              </div>
              <div class="form-group">
                <label>Локализация по квадрантам *</label>
                <select v-model="leFindingForm.quadrant_location" required class="input">
                  <option value="">Выберите</option>
                  <option v-for="loc in quadrantLocations" :key="loc" :value="loc">{{ loc }}</option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Локализация по глубине МЖ *</label>
                <select v-model="leFindingForm.depth_location" required class="input">
                  <option value="">Выберите</option>
                  <option v-for="depth in depthLocations" :key="depth" :value="depth">{{ depth }}</option>
                </select>
              </div>
              <div class="form-group">
                <label>Тип находки *</label>
                <select v-model="leFindingForm.finding_type" @change="onLETypeChange" required class="input">
                  <option value="">Выберите</option>
                  <option v-for="type in findingTypes" :key="type" :value="type">{{ type }}</option>
                </select>
              </div>
            </div>

            <!-- Динамические поля аналогично обычной маммографии -->
            <div v-if="leFindingForm.finding_type === 'Объемное образование'" class="finding-details">
              <h5>Описание объемного образования</h5>
              <div class="form-row">
                <div class="form-group">
                  <label>Форма</label>
                  <select v-model="leFindingForm.mass_shape" class="input">
                    <option value="">Выберите</option>
                    <option v-for="shape in massShapes" :key="shape" :value="shape">{{ shape }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Контур</label>
                  <select v-model="leFindingForm.mass_margin" class="input">
                    <option value="">Выберите</option>
                    <option v-for="margin in massMargins" :key="margin" :value="margin">{{ margin }}</option>
                  </select>
                </div>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>Плотность</label>
                  <select v-model="leFindingForm.mass_density" class="input">
                    <option value="">Выберите</option>
                    <option v-for="density in massDensities" :key="density" :value="density">{{ density }}</option>
                  </select>
                </div>
              </div>

              <!-- Размеры -->
              <div v-if="shouldShowSingleSizeField('le')" class="form-group">
                <label>Размер (мм) *</label>
                <input v-model.number="leFindingForm.size_x_mm" @input="copySizeForRoundMass('le')" type="number" min="1" required class="input">
                <small class="text-muted">Для округлого образования все размеры будут одинаковыми</small>
              </div>
              <div v-else class="form-row">
                <div class="form-group">
                  <label>Размер X (мм) *</label>
                  <input v-model.number="leFindingForm.size_x_mm" @input="calculateLEMetrics" type="number" min="1" required class="input">
                </div>
                <div class="form-group">
                  <label>Размер Y (мм) *</label>
                  <input v-model.number="leFindingForm.size_y_mm" @input="calculateLEMetrics" type="number" min="1" required class="input">
                </div>
                <div class="form-group">
                  <label>Размер Z (мм) *</label>
                  <input v-model.number="leFindingForm.size_z_mm" @input="calculateLEMetrics" type="number" min="1" required class="input">
                </div>
              </div>

              <!-- Рассчитанные параметры -->
              <div v-if="leFindingForm.size_x_mm && leFindingForm.size_y_mm && leFindingForm.size_z_mm" class="calculated-metrics">
                <div><strong>Объём:</strong> {{ leFindingForm.volume_mm3 }} мм³</div>
                <div><strong>Макс. размер:</strong> {{ leFindingForm.size_max_mm }} мм</div>
                <div><strong>Мин. размер:</strong> {{ leFindingForm.size_min_mm }} мм</div>
              </div>
            </div>

            <!-- Определяется ли на RC -->
            <div class="form-group">
              <label>Находка определяется на RC?</label>
              <select v-model="leFindingForm.visible_on_rc" class="input">
                <option value="">Выберите</option>
                <option value="Да">Да</option>
                <option value="Нет">Нет</option>
              </select>
            </div>

            <!-- Поля если "Да" -->
            <div v-if="leFindingForm.visible_on_rc === 'Да'" class="finding-details">
              <h5>Характеристики на RC</h5>
              <div class="form-group">
                <label>Паттерн внутреннего контрастирования</label>
                <select v-model="leFindingForm.rc_internal_enhancement" class="input">
                  <option value="">Выберите</option>
                  <option v-for="pattern in enhancementPatterns" :key="pattern" :value="pattern">{{ pattern }}</option>
                </select>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>Степень контрастирования</label>
                  <select v-model="leFindingForm.rc_enhancement_degree" class="input">
                    <option value="">Выберите</option>
                    <option v-for="degree in enhancementDegrees" :key="degree" :value="degree">{{ degree }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Интенсивность контрастирования</label>
                  <select v-model="leFindingForm.rc_enhancement_intensity" class="input">
                    <option value="">Выберите</option>
                    <option v-for="intensity in enhancementIntensity" :key="intensity" :value="intensity">{{ intensity }}</option>
                  </select>
                </div>
              </div>
            </div>

            <div class="form-actions">
              <button type="button" @click="showAddLEFinding = false" class="btn btn-secondary">Отмена</button>
              <button type="submit" class="btn btn-primary">Сохранить</button>
            </div>
          </form>
        </div>
      </div>

      <!-- Модал добавления RC находки -->
      <div v-if="showAddRCFinding" class="modal inner-modal" @click.self="showAddRCFinding = false">
        <div class="modal-content modal-large">
          <h4>Добавить находку RC</h4>
          <form @submit.prevent="saveRCFinding">
            <div class="form-row">
              <div class="form-group">
                <label>Номер находки (1-9) *</label>
                <input v-model.number="rcFindingForm.finding_number" type="number" min="1" max="9" required class="input">
              </div>
              <div class="form-group">
                <label>Локализация по квадрантам *</label>
                <select v-model="rcFindingForm.quadrant_location" required class="input">
                  <option value="">Выберите</option>
                  <option v-for="loc in quadrantLocations" :key="loc" :value="loc">{{ loc }}</option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Локализация по глубине МЖ *</label>
                <select v-model="rcFindingForm.depth_location" required class="input">
                  <option value="">Выберите</option>
                  <option v-for="depth in depthLocations" :key="depth" :value="depth">{{ depth }}</option>
                </select>
              </div>
              <div class="form-group">
                <label>Тип находки на RC *</label>
                <select v-model="rcFindingForm.finding_type" @change="onRCTypeChange" required class="input">
                  <option value="">Выберите</option>
                  <option v-for="type in rcFindingTypes" :key="type" :value="type">{{ type }}</option>
                </select>
              </div>
            </div>

            <!-- Объемное образование -->
            <div v-if="rcFindingForm.finding_type === 'Объемное образование'" class="finding-details">
              <h5>Описание объемного образования</h5>
              <div class="form-row">
                <div class="form-group">
                  <label>Форма</label>
                  <select v-model="rcFindingForm.mass_shape" class="input">
                    <option value="">Выберите</option>
                    <option v-for="shape in massShapes" :key="shape" :value="shape">{{ shape }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Контур</label>
                  <select v-model="rcFindingForm.mass_margin" class="input">
                    <option value="">Выберите</option>
                    <option v-for="margin in massMargins" :key="margin" :value="margin">{{ margin }}</option>
                  </select>
                </div>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>Характеристика контрастирования</label>
                  <select v-model="rcFindingForm.enhancement_characteristic" class="input">
                    <option value="">Выберите</option>
                    <option v-for="char in enhancementCharacteristics" :key="char" :value="char">{{ char }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Размеры (мм) *</label>
                  <input v-model="rcFindingForm.size_mm" placeholder="15x16x17" required class="input">
                </div>
              </div>
            </div>

            <!-- Зона контрастирования без образования -->
            <div v-if="rcFindingForm.finding_type === 'Зона контрастирования без образования'" class="finding-details">
              <h5>Зона контрастирования</h5>
              <div class="form-row">
                <div class="form-group">
                  <label>Распределение</label>
                  <select v-model="rcFindingForm.distribution" class="input">
                    <option value="">Выберите</option>
                    <option v-for="dist in enhancementDistribution" :key="dist" :value="dist">{{ dist }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Паттерн внутреннего усиления</label>
                  <select v-model="rcFindingForm.internal_enhancement_pattern" class="input">
                    <option value="">Выберите</option>
                    <option v-for="pattern in enhancementPatterns" :key="pattern" :value="pattern">{{ pattern }}</option>
                  </select>
                </div>
              </div>
              <div class="form-group">
                <label>Размеры (мм) *</label>
                <input v-model="rcFindingForm.size_mm" placeholder="15x16x17" required class="input">
              </div>
            </div>

            <!-- Зона асимметричного контрастирования -->
            <div v-if="rcFindingForm.finding_type === 'Зона асимметричного контрастирования'" class="finding-details">
              <h5>Асимметричное контрастирование</h5>
              <div class="form-row">
                <div class="form-group">
                  <label>Паттерн внутреннего усиления</label>
                  <select v-model="rcFindingForm.asymmetric_enhancement_pattern" class="input">
                    <option value="">Выберите</option>
                    <option v-for="pattern in enhancementPatterns" :key="pattern" :value="pattern">{{ pattern }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Размеры зоны (мм) *</label>
                  <input v-model="rcFindingForm.size_mm" placeholder="15x16x17" required class="input">
                </div>
              </div>
            </div>

            <div class="form-group">
              <label>Интенсивность контрастирования</label>
              <select v-model="rcFindingForm.enhancement_intensity" class="input">
                <option value="">Выберите</option>
                <option v-for="intensity in enhancementIntensity" :key="intensity" :value="intensity">{{ intensity }}</option>
              </select>
            </div>

            <div class="form-actions">
              <button type="button" @click="showAddRCFinding = false" class="btn btn-secondary">Отмена</button>
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
    contrastMammo: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      activeTab: 'le',
      leFindings: [],
      rcFindings: [],
      showAddLEFinding: false,
      showAddRCFinding: false,
      leFindingForm: this.getEmptyLEForm(),
      rcFindingForm: this.getEmptyRCForm(),
      // Справочники
      quadrantLocations: dict.QUADRANT_LOCATIONS,
      depthLocations: dict.DEPTH_LOCATIONS,
      findingTypes: dict.FINDING_TYPES,
      rcFindingTypes: dict.RC_FINDING_TYPES,
      massShapes: dict.MASS_SHAPES,
      massMargins: dict.MASS_MARGINS,
      massDensities: dict.MASS_DENSITY,
      enhancementPatterns: dict.ENHANCEMENT_PATTERNS,
      enhancementDegrees: dict.ENHANCEMENT_DEGREES,
      enhancementIntensity: dict.ENHANCEMENT_INTENSITY,
      enhancementCharacteristics: dict.ENHANCEMENT_CHARACTERISTICS,
      enhancementDistribution: dict.ENHANCEMENT_DISTRIBUTION
    }
  },
  mounted() {
    this.loadFindings()
  },
  methods: {
    getEmptyLEForm() {
      return {
        finding_number: null,
        quadrant_location: '',
        depth_location: '',
        finding_type: '',
        mass_shape: '',
        mass_margin: '',
        mass_density: '',
        size_mm: '',
        visible_on_rc: '',
        rc_internal_enhancement: '',
        rc_enhancement_degree: '',
        rc_enhancement_intensity: ''
      }
    },
    getEmptyRCForm() {
      return {
        finding_number: null,
        quadrant_location: '',
        depth_location: '',
        finding_type: '',
        mass_shape: '',
        mass_margin: '',
        enhancement_characteristic: '',
        distribution: '',
        internal_enhancement_pattern: '',
        asymmetric_enhancement_pattern: '',
        size_mm: '',
        enhancement_intensity: ''
      }
    },
    async loadFindings() {
      try {
        const leResponse = await api.getContrastMammoLEFindings(this.contrastMammo.id)
        this.leFindings = leResponse.data

        const rcResponse = await api.getContrastMammoRCFindings(this.contrastMammo.id)
        this.rcFindings = rcResponse.data
      } catch (error) {
        console.error('Error loading findings:', error)
      }
    },
    onLETypeChange() {
      this.leFindingForm = { ...this.getEmptyLEForm(),
        finding_number: this.leFindingForm.finding_number,
        quadrant_location: this.leFindingForm.quadrant_location,
        depth_location: this.leFindingForm.depth_location,
        finding_type: this.leFindingForm.finding_type
      }
    },
    onRCTypeChange() {
      this.rcFindingForm = { ...this.getEmptyRCForm(),
        finding_number: this.rcFindingForm.finding_number,
        quadrant_location: this.rcFindingForm.quadrant_location,
        depth_location: this.rcFindingForm.depth_location,
        finding_type: this.rcFindingForm.finding_type
      }
    },
    async saveLEFinding() {
      try {
        await api.createContrastMammoLEFinding({
          ...this.leFindingForm,
          contrast_mammo_id: this.contrastMammo.id
        })
        this.showAddLEFinding = false
        this.leFindingForm = this.getEmptyLEForm()
        this.loadFindings()
        this.$emit('updated')
      } catch (error) {
        alert('Ошибка сохранения: ' + (error.response?.data?.detail || error.message))
      }
    },
    async saveRCFinding() {
      try {
        await api.createContrastMammoRCFinding({
          ...this.rcFindingForm,
          contrast_mammo_id: this.contrastMammo.id
        })
        this.showAddRCFinding = false
        this.rcFindingForm = this.getEmptyRCForm()
        this.loadFindings()
        this.$emit('updated')
      } catch (error) {
        alert('Ошибка сохранения: ' + (error.response?.data?.detail || error.message))
      }
    },
    async deleteLEFinding(id) {
      if (confirm('Удалить находку LE?')) {
        try {
          await api.deleteContrastMammoLEFinding(id)
          this.loadFindings()
          this.$emit('updated')
        } catch (error) {
          alert('Ошибка удаления')
        }
      }
    },
    async deleteRCFinding(id) {
      if (confirm('Удалить находку RC?')) {
        try {
          await api.deleteContrastMammoRCFinding(id)
          this.loadFindings()
          this.$emit('updated')
        } catch (error) {
          alert('Ошибка удаления')
        }
      }
    }
  }
}
</script>

<style scoped>
.findings-modal {
  z-index: 1001;
}

.inner-modal {
  z-index: 1002 !important;
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

.modal-xlarge {
  max-width: 1000px;
}

.modal-large {
  max-width: 800px;
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

.info-section {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem;
}

.tabs-section {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #e9ecef;
}

.tab-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  background: none;
  cursor: pointer;
  font-weight: 500;
  border-bottom: 3px solid transparent;
  transition: all 0.3s;
}

.tab-btn.active {
  color: #667eea;
  border-bottom-color: #667eea;
}

.findings-section {
  margin-top: 1rem;
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