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
              <td>{{ finding.size_x_mm }}×{{ finding.size_y_mm }}×{{ finding.size_z_mm }}</td>
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
              <td>{{ finding.size_x_mm }}×{{ finding.size_y_mm }}×{{ finding.size_z_mm }}</td>
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
              <div v-else>
                <div class="form-row">
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
              </div>

              <!-- Размеры -->
              <div v-if="shouldShowSingleSizeField('rc')" class="form-group">
                <label>Размер (мм) *</label>
                <input v-model.number="rcFindingForm.size_x_mm" @input="copySizeForRoundMass('rc')" type="number" min="1" required class="input">
                <small class="text-muted">Для округлого образования все размеры будут одинаковыми</small>
              </div>
              <div v-else>
                <div class="form-row">
                  <div class="form-group">
                    <label>Размер X (мм) *</label>
                    <input v-model.number="rcFindingForm.size_x_mm" @input="calculateRCMetrics" type="number" min="1" required class="input">
                  </div>
                  <div class="form-group">
                    <label>Размер Y (мм) *</label>
                    <input v-model.number="rcFindingForm.size_y_mm" @input="calculateRCMetrics" type="number" min="1" required class="input">
                  </div>
                  <div class="form-group">
                    <label>Размер Z (мм) *</label>
                    <input v-model.number="rcFindingForm.size_z_mm" @input="calculateRCMetrics" type="number" min="1" required class="input">
                  </div>
                </div>
              </div>

              <!-- Рассчитанные параметры -->
              <div v-if="rcFindingForm.size_x_mm && rcFindingForm.size_y_mm && rcFindingForm.size_z_mm" class="calculated-metrics">
                <div><strong>Объём:</strong> {{ rcFindingForm.volume_mm3 }} мм³</div>
                <div><strong>Макс. размер:</strong> {{ rcFindingForm.size_max_mm }} мм</div>
                <div><strong>Мин. размер:</strong> {{ rcFindingForm.size_min_mm }} мм</div>
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
              <div class="form-row">
                <div class="form-group">
                  <label>Размер X (мм) *</label>
                  <input v-model.number="rcFindingForm.size_x_mm" @input="calculateRCMetrics" type="number" min="1" required class="input">
                </div>
                <div class="form-group">
                  <label>Размер Y (мм) *</label>
                  <input v-model.number="rcFindingForm.size_y_mm" @input="calculateRCMetrics" type="number" min="1" required class="input">
                </div>
                <div class="form-group">
                  <label>Размер Z (мм) *</label>
                  <input v-model.number="rcFindingForm.size_z_mm" @input="calculateRCMetrics" type="number" min="1" required class="input">
                </div>
              </div>

              <!-- Рассчитанные параметры -->
              <div v-if="rcFindingForm.size_x_mm && rcFindingForm.size_y_mm && rcFindingForm.size_z_mm" class="calculated-metrics">
                <div><strong>Объём:</strong> {{ rcFindingForm.volume_mm3 }} мм³</div>
                <div><strong>Макс. размер:</strong> {{ rcFindingForm.size_max_mm }} мм</div>
                <div><strong>Мин. размер:</strong> {{ rcFindingForm.size_min_mm }} мм</div>
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
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>Размер X (мм) *</label>
                  <input v-model.number="rcFindingForm.size_x_mm" @input="calculateRCMetrics" type="number" min="1" required class="input">
                </div>
                <div class="form-group">
                  <label>Размер Y (мм) *</label>
                  <input v-model.number="rcFindingForm.size_y_mm" @input="calculateRCMetrics" type="number" min="1" required class="input">
                </div>
                <div class="form-group">
                  <label>Размер Z (мм) *</label>
                  <input v-model.number="rcFindingForm.size_z_mm" @input="calculateRCMetrics" type="number" min="1" required class="input">
                </div>
              </div>

              <!-- Рассчитанные параметры -->
              <div v-if="rcFindingForm.size_x_mm && rcFindingForm.size_y_mm && rcFindingForm.size_z_mm" class="calculated-metrics">
                <div><strong>Объём:</strong> {{ rcFindingForm.volume_mm3 }} мм³</div>
                <div><strong>Макс. размер:</strong> {{ rcFindingForm.size_max_mm }} мм</div>
                <div><strong>Мин. размер:</strong> {{ rcFindingForm.size_min_mm }} мм</div>
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
        size_x_mm: null,
        size_y_mm: null,
        size_z_mm: null,
        volume_mm3: null,
        size_max_mm: null,
        size_min_mm: null,
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
        size_x_mm: null,
        size_y_mm: null,
        size_z_mm: null,
        volume_mm3: null,
        size_max_mm: null,
        size_min_mm: null,
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
    shouldShowSingleSizeField(type) {
      const form = type === 'le' ? this.leFindingForm : this.rcFindingForm
      return form.finding_type === 'Объемное образование' && form.mass_shape === 'Округлая'
    },
    copySizeForRoundMass(type) {
      const form = type === 'le' ? this.leFindingForm : this.rcFindingForm
      if (this.shouldShowSingleSizeField(type) && form.size_x_mm) {
        form.size_y_mm = form.size_x_mm
        form.size_z_mm = form.size_x_mm
        if (type === 'le') {
          this.calculateLEMetrics()
        } else {
          this.calculateRCMetrics()
        }
      }
    },
    calculateLEMetrics() {
      const form = this.leFindingForm
      if (form.size_x_mm && form.size_y_mm && form.size_z_mm) {
        form.volume_mm3 = form.size_x_mm * form.size_y_mm * form.size_z_mm
        const sizes = [form.size_x_mm, form.size_y_mm, form.size_z_mm]
        form.size_max_mm = Math.max(...sizes)
        form.size_min_mm = Math.min(...sizes)
      }
    },
    calculateRCMetrics() {
      const form = this.rcFindingForm
      if (form.size_x_mm && form.size_y_mm && form.size_z_mm) {
        form.volume_mm3 = form.size_x_mm * form.size_y_mm * form.size_z_mm
        const sizes = [form.size_x_