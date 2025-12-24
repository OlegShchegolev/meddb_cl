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
              <th>Размеры, мм³</th>
              <th>На RC</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="finding in leFindings" :key="finding.id">
              <td>{{ finding.finding_number }}</td>
              <td>{{ finding.quadrant_location }}</td>
              <td>{{ finding.finding_type }}</td>
              <td>{{ finding.volume_mm3 }}</td>
              <td>{{ finding.visible_on_rc }}</td>
              <td>
                <button @click="editLEFinding(finding)" class="btn-sm btn-warning">Изменить</button>
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
              <th>Размеры, мм³</th>
              <th>Интенсивность</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="finding in rcFindings" :key="finding.id">
              <td>{{ finding.finding_number }}</td>
              <td>{{ finding.quadrant_location }}</td>
              <td>{{ finding.finding_type }}</td>
              <td>{{ finding.volume_mm3 }}</td>
              <td>{{ finding.enhancement_intensity }}</td>
              <td>
                <button @click="editRCFinding(finding)" class="btn-sm btn-warning">Изменить</button>
                <button @click="deleteRCFinding(finding.id)" class="btn-sm btn-danger">Удалить</button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data">Находок RC не обнаружено</p>
      </div>

      <!-- Модал добавления/редактирования LE находки -->
      <div v-if="showAddLEFinding" class="modal inner-modal" @click.self="showAddLEFinding = false">
        <div class="modal-content modal-large">
          <h4>{{ editingLEFindingId ? 'Редактировать находку LE' : 'Добавить находку LE' }}</h4>
          <form @submit.prevent="saveLEFinding">
            <div class="form-row">
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
                  <select v-model="leFindingForm.mass_shape" @change="onLEMassShapeChange" class="input">
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
              <div v-if="leFindingForm.mass_shape === 'Округлая'" class="form-group">
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
              <button type="button" @click="closeLEFindingModal" class="btn btn-secondary">Отмена</button>
              <button type="submit" class="btn btn-primary">Сохранить</button>
            </div>
          </form>
        </div>
      </div>

      <!-- Модал добавления/редактирования RC находки -->
      <div v-if="showAddRCFinding" class="modal inner-modal" @click.self="showAddRCFinding = false">
        <div class="modal-content modal-large">
          <h4>{{ editingRCFindingId ? 'Редактировать находку RC' : 'Добавить находку RC' }}</h4>
          <form @submit.prevent="saveRCFinding">
            <div class="form-row">
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
                  <select v-model="rcFindingForm.mass_shape" @change="onRCMassShapeChange" class="input">
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

              <!-- Размеры -->
              <div v-if="rcFindingForm.mass_shape === 'Округлая'" class="form-group">
                <label>Размер (мм) *</label>
                <input v-model.number="rcFindingForm.size_x_mm" @input="copySizeForRoundMass('rc')" type="number" min="1" required class="input">
                <small class="text-muted">Для округлого образования все размеры будут одинаковыми</small>
              </div>
              <div v-else class="form-row">
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

              <div class="form-row">
                <div class="form-group">
                  <label>Характеристика контрастирования</label>
                  <select v-model="rcFindingForm.enhancement_characteristic" class="input">
                    <option value="">Выберите</option>
                    <option v-for="char in enhancementCharacteristics" :key="char" :value="char">{{ char }}</option>
                  </select>
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
            </div>

            <div class="form-group">
              <label>Интенсивность контрастирования</label>
              <select v-model="rcFindingForm.enhancement_intensity" class="input">
                <option value="">Выберите</option>
                <option v-for="intensity in enhancementIntensity" :key="intensity" :value="intensity">{{ intensity }}</option>
              </select>
            </div>

            <div class="form-actions">
              <button type="button" @click="closeRCFindingModal" class="btn btn-secondary">Отмена</button>
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
      editingLEFindingId: null,
      editingRCFindingId: null,
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
        size_x_mm: null,
        size_y_mm: null,
        size_z_mm: null,
        volume_mm3: null,
        size_max_mm: null,
        size_min_mm: null,
        enhancement_characteristic: '',
        distribution: '',
        internal_enhancement_pattern: '',
        asymmetric_enhancement_pattern: '',
        enhancement_intensity: ''
      }
    },
    calculateLEMetrics() {
      // Рассчитываем объём, максимальный и минимальный размеры
      const x = this.leFindingForm.size_x_mm;
      const y = this.leFindingForm.size_y_mm;
      const z = this.leFindingForm.size_z_mm;

      if (x && y && z) {
        // Объём для эллипсоида: V = (4/3) * π * a * b * c
        // где a, b, c - полуоси (размеры / 2)
        const volume = (4/3) * Math.PI * (x/2) * (y/2) * (z/2);
        this.leFindingForm.volume_mm3 = Math.round(volume);

        // Максимальный и минимальный размеры
        const sizes = [x, y, z];
        this.leFindingForm.size_max_mm = Math.max(...sizes);
        this.leFindingForm.size_min_mm = Math.min(...sizes);
      } else {
        // Сбрасываем значения если не все размеры заполнены
        this.leFindingForm.volume_mm3 = null;
        this.leFindingForm.size_max_mm = null;
        this.leFindingForm.size_min_mm = null;
      }
    },
    calculateRCMetrics() {
      // Рассчитываем объём, максимальный и минимальный размеры
      const x = this.rcFindingForm.size_x_mm;
      const y = this.rcFindingForm.size_y_mm;
      const z = this.rcFindingForm.size_z_mm;

      if (x && y && z) {
        // Объём для эллипсоида: V = (4/3) * π * a * b * c
        // где a, b, c - полуоси (размеры / 2)
        const volume = (4/3) * Math.PI * (x/2) * (y/2) * (z/2);
        this.rcFindingForm.volume_mm3 = Math.round(volume);

        // Максимальный и минимальный размеры
        const sizes = [x, y, z];
        this.rcFindingForm.size_max_mm = Math.max(...sizes);
        this.rcFindingForm.size_min_mm = Math.min(...sizes);
      } else {
        // Сбрасываем значения если не все размеры заполнены
        this.rcFindingForm.volume_mm3 = null;
        this.rcFindingForm.size_max_mm = null;
        this.rcFindingForm.size_min_mm = null;
      }
    },

    copySizeForRoundMass(type) {
      if (type === 'le') {
        const size = this.leFindingForm.size_x_mm;
        if (size) {
          // Для округлого образования все размеры одинаковые
          this.leFindingForm.size_y_mm = size;
          this.leFindingForm.size_z_mm = size;
          this.calculateLEMetrics();
        }
      }
      if (type === 'rc') {
        const size = this.rcFindingForm.size_x_mm;
        if (size) {
          // Для округлого образования все размеры одинаковые
          this.rcFindingForm.size_y_mm = size;
          this.rcFindingForm.size_z_mm = size;
          this.calculateRCMetrics();
        }
      }
    },

    onLEMassShapeChange() {
      // При изменении формы сбросить размеры для пересчета
      this.leFindingForm.size_x_mm = null;
      this.leFindingForm.size_y_mm = null;
      this.leFindingForm.size_z_mm = null;
      this.leFindingForm.volume_mm3 = null;
      this.leFindingForm.size_max_mm = null;
      this.leFindingForm.size_min_mm = null;
    },

    onRCMassShapeChange() {
      // При изменении формы сбросить размеры для пересчета
      this.rcFindingForm.size_x_mm = null;
      this.rcFindingForm.size_y_mm = null;
      this.rcFindingForm.size_z_mm = null;
      this.rcFindingForm.volume_mm3 = null;
      this.rcFindingForm.size_max_mm = null;
      this.rcFindingForm.size_min_mm = null;
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
        quadrant_location: this.leFindingForm.quadrant_location,
        depth_location: this.leFindingForm.depth_location,
        finding_type: this.leFindingForm.finding_type
      }
    },
    onRCTypeChange() {
      this.rcFindingForm = { ...this.getEmptyRCForm(),
        quadrant_location: this.rcFindingForm.quadrant_location,
        depth_location: this.rcFindingForm.depth_location,
        finding_type: this.rcFindingForm.finding_type
      }
    },

    editLEFinding(finding) {
      this.editingLEFindingId = finding.id;
      this.leFindingForm = { ...finding };

      // Пересчитать метрики если это объемное образование
      if (this.leFindingForm.finding_type === 'Объемное образование' &&
          this.leFindingForm.size_x_mm &&
          this.leFindingForm.size_y_mm &&
          this.leFindingForm.size_z_mm) {
        this.calculateLEMetrics();
      }

      this.showAddLEFinding = true;
    },

    editRCFinding(finding) {
      this.editingRCFindingId = finding.id;
      this.rcFindingForm = { ...finding };

      // Пересчитать метрики если это объемное образование
      if (this.rcFindingForm.finding_type === 'Объемное образование' &&
          this.rcFindingForm.size_x_mm &&
          this.rcFindingForm.size_y_mm &&
          this.rcFindingForm.size_z_mm) {
        this.calculateRCMetrics();
      }

      this.showAddRCFinding = true;
    },

    async saveLEFinding() {
      try {
        const data = {
          ...this.leFindingForm,
          contrast_mammo_id: this.contrastMammo.id
        }

        if (this.editingLEFindingId) {
          await api.updateContrastMammoLEFinding(this.editingLEFindingId, data)
        } else {
          await api.createContrastMammoLEFinding(data)
        }

        this.closeLEFindingModal()
        this.loadFindings()
        this.$emit('updated')
      } catch (error) {
        alert('Ошибка сохранения: ' + (error.response?.data?.detail || error.message))
      }
    },

    async saveRCFinding() {
      try {
        const data = {
          ...this.rcFindingForm,
          contrast_mammo_id: this.contrastMammo.id
        }

        if (this.editingRCFindingId) {
          await api.updateContrastMammoRCFinding(this.editingRCFindingId, data)
        } else {
          await api.createContrastMammoRCFinding(data)
        }

        this.closeRCFindingModal()
        this.loadFindings()
        this.$emit('updated')
      } catch (error) {
        alert('Ошибка сохранения: ' + (error.response?.data?.detail || error.message))
      }
    },

    closeLEFindingModal() {
      this.showAddLEFinding = false
      this.editingLEFindingId = null
      this.leFindingForm = this.getEmptyLEForm()
    },

    closeRCFindingModal() {
      this.showAddRCFinding = false
      this.editingRCFindingId = null
      this.rcFindingForm = this.getEmptyRCForm()
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

.calculated-metrics {
  background: #e9ecef;
  padding: 0.75rem;
  border-radius: 4px;
  margin-top: 1rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.5rem;
}

.text-muted {
  color: #6c757d;
  font-size: 0.8rem;
  display: block;
  margin-top: 0.25rem;
}
</style>