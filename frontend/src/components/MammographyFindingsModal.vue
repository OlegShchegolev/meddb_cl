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
              <th>Размеры (мм)</th>
              <th>Объём (мм³)</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="finding in findings" :key="finding.id">
              <td>{{ finding.finding_number }}</td>
              <td>{{ finding.affected_side }}</td>
              <td>{{ finding.quadrant_location }}</td>
              <td>{{ finding.depth_location }}</td>
              <td>{{ finding.finding_type }}</td>
              <td>
                <template v-if="finding.size_x_mm && finding.size_y_mm && finding.size_z_mm">
                  {{ finding.size_x_mm }}×{{ finding.size_y_mm }}×{{ finding.size_z_mm }}
                </template>
                <template v-else>-</template>
              </td>
              <td>{{ finding.volume_mm3 || '-' }}</td>
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
                <label>Сторона поражения *</label>
                <select v-model="findingForm.affected_side" required class="input">
                  <option value="">Выберите</option>
                  <option value="Правая МЖ">Правая МЖ</option>
                  <option value="Левая МЖ">Левая МЖ</option>
                </select>
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
            <div v-if="findingForm.finding_type === 'Объемное образование'  || findingForm.finding_type === 'Кальцинаты' || findingForm.finding_type === 'Асимметрия'" class="finding-details">
              <h5>Описание объемного образования</h5>
              <div class="form-row">
                <div class="form-group">
                  <label>Форма</label>
                  <select v-model="findingForm.mass_shape" @change="onMassShapeChange" class="input">
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
              </div>
              <div class="form-group">
                <label>Кальцинаты в структуре</label>
                <select v-model="findingForm.calcification_in_structure" class="input">
                  <option value="">Выберите</option>
                    <option v-for="morph in calcificationInStructure" :key="morph" :value="morph">{{ morph }}</option>
                </select>
              </div>

              <!-- Размеры для объемного образования -->
              <div v-if="findingForm.mass_shape === 'Округлая'" class="form-group">
                <label>Размер (мм)</label>
                <input
                  v-model.number="findingForm.size_x_mm"
                  @input="copySizeForRoundMass"
                  type="number"
                  min="1"
                  class="input"
                  placeholder="Введите размер"
                >
                <small class="text-muted">Для округлого образования все размеры будут одинаковыми</small>
              </div>
              <div v-else class="form-row">
                <div class="form-group">
                  <label>Размер X (мм)</label>
                  <input
                    v-model.number="findingForm.size_x_mm"
                    @input="calculateMetrics"
                    type="number"
                    min="1"
                    class="input"
                    placeholder="X размер"
                  >
                </div>
                <div class="form-group">
                  <label>Размер Y (мм)</label>
                  <input
                    v-model.number="findingForm.size_y_mm"
                    @input="calculateMetrics"
                    type="number"
                    min="1"
                    class="input"
                    placeholder="Y размер"
                  >
                </div>
                <div class="form-group">
                  <label>Размер Z (мм)</label>
                  <input
                    v-model.number="findingForm.size_z_mm"
                    @input="calculateMetrics"
                    type="number"
                    min="1"
                    class="input"
                    placeholder="Z размер"
                  >
                </div>
              </div>

              <!-- Рассчитанные параметры -->
              <div v-if="findingForm.size_x_mm && findingForm.size_y_mm && findingForm.size_z_mm" class="calculated-metrics">
                <div><strong>Объём:</strong> {{ findingForm.volume_mm3 }} мм³</div>
              </div>
              <div v-if="findingForm.size_max_mm && findingForm.size_min_mm" class="calculated-metrics">
                <div><strong>Макс. размер:</strong> {{ findingForm.size_max_mm }} мм</div>
                <div><strong>Мин. размер:</strong> {{ findingForm.size_min_mm }} мм</div>
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
              </div>
            </div>

            <!-- Поля для "Сопутствующие изменения" -->
            <div v-if="findingForm.finding_type === 'Сопутствующие признаки'" class="finding-details">
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

            <!-- Сравнение с предыдущими -->
            <div class="form-row">
              <div class="form-group">
                <label>Сравнение с предыдущими исследованиями</label>
                <select v-model="findingForm.comparison_available" class="input">
                  <option :value="false">Нет</option>
                  <option :value="true">Да</option>
                </select>
              </div>
              <div class="form-group" v-if="findingForm.comparison_available">
                <label>Динамика</label>
                <select v-model="findingForm.dynamics" class="input">
                  <option value="">Выберите</option>
                  <option value="Без динамики">Без динамики</option>
                  <option value="Положительная динамика">Положительная динамика</option>
                  <option value="Отрицательная динамика">Отрицательная динамика</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Комментарий</label>
              <textarea v-model="findingForm.comment" class="input" rows="3"></textarea>
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
        affected_side: '',
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
        asymmetry_type: '',
        calcification_in_structure: '',
        calcification_malignancy: '',
        calcification_morphology: '',
        calcification_distribution: '',
        associated_feature: '',
        comparison_available: false,
        dynamics: '',
        comment: ''
      },
      // Справочники
      quadrantLocations: dict.QUADRANT_LOCATIONS,
      depthLocations: dict.DEPTH_LOCATIONS,
      findingTypes: dict.FINDING_TYPES,
      massShapes: dict.MASS_SHAPES,
      massMargins: dict.MASS_MARGINS,
      massDensities: dict.MASS_DENSITY,
      asymmetryTypes: dict.ASYMMETRY_TYPES,
      calcificationInStructure: dict.CALCIFICATION_MORPHOLOGY,
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
      this.findingForm = {
        ...this.findingForm,
        mass_shape: '',
        mass_margin: '',
        mass_density: '',
        size_x_mm: null,
        size_y_mm: null,
        size_z_mm: null,
        volume_mm3: null,
        size_max_mm: null,
        size_min_mm: null,
        asymmetry_type: '',
        calcification_malignancy: '',
        calcification_morphology: '',
        calcification_distribution: ''
      }
      this.selectedFeatures = []

      // Прокрутить к началу формы при смене типа
      this.$nextTick(() => {
        this.scrollToFormBottom();
      });
    },

    onMassShapeChange() {
      // При изменении формы сбросить размеры для пересчета
      this.findingForm.size_x_mm = null
      this.findingForm.size_y_mm = null
      this.findingForm.size_z_mm = null
      this.findingForm.volume_mm3 = null
      this.findingForm.size_max_mm = null
      this.findingForm.size_min_mm = null
    },

    calculateMetrics() {
      // Рассчитываем объём, максимальный и минимальный размеры
      const x = this.findingForm.size_x_mm;
      const y = this.findingForm.size_y_mm;
      const z = this.findingForm.size_z_mm;

        // Рассчитываем max и min даже если введен только один размер
        // Рассчитываем max и min даже если введен только один размер
      if (x || y || z) {
        // Фильтруем только заполненные значения
        const sizes = [x, y, z].filter(size => size !== null && size !== undefined && size !== '');

        if (sizes.length > 0) {
          this.findingForm.size_max_mm = Math.max(...sizes);
          this.findingForm.size_min_mm = Math.min(...sizes);
        } else {
          this.findingForm.size_max_mm = null;
          this.findingForm.size_min_mm = null;
        }
      } else {
        this.findingForm.size_max_mm = null;
        this.findingForm.size_min_mm = null;
      }

      if (x && y && z) {
        // Объём для эллипсоида: V = (4/3) * π * a * b * c
        // где a, b, c - полуоси (размеры / 2)
        const volume = (4 / 3) * Math.PI * (x / 2) * (y / 2) * (z / 2);
        this.findingForm.volume_mm3 = Math.round(volume);

        // Прокрутить к рассчитанным метрикам
        this.$nextTick(() => {
          this.scrollToFormBottom();
        });
      } else {
        // Сбрасываем значения если не все размеры заполнены
        this.findingForm.volume_mm3 = null;
      }
    },

    copySizeForRoundMass() {
      const size = this.findingForm.size_x_mm;
      if (size) {
        // Для округлого образования все размеры одинаковые
        this.findingForm.size_y_mm = size;
        this.findingForm.size_z_mm = size;
        this.calculateMetrics();
      }
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

      if (finding.associated_feature) {
        try {
          this.selectedFeatures = JSON.parse(finding.associated_feature)
        } catch {
          this.selectedFeatures = []
        }
      }
      this.showAddFinding = true

      // Пересчитать метрики если это объемное образование
      if (this.findingForm.finding_type === 'Объемное образование' &&
          this.findingForm.size_x_mm &&
          this.findingForm.size_y_mm &&
          this.findingForm.size_z_mm) {
        this.calculateMetrics();
      }
    },
    async saveFinding() {
      try {
        // Формируем данные для отправки
        const data = {
          ...this.findingForm,
          mammography_id: this.mammography.id,
          associated_feature: this.findingForm.finding_type === 'Сопутствующие признаки'
              ? JSON.stringify(this.selectedFeatures)
              : null
        }

        // Для не-объемных образований очищаем отдельные размеры
        if (this.findingForm.finding_type !== 'Объемное образование') {
          data.size_x_mm = null;
          data.size_y_mm = null;
          data.size_z_mm = null;
          data.volume_mm3 = null;
          data.size_max_mm = null;
          data.size_min_mm = null;
        }

        if (!this.findingForm.affected_side) {
          alert('Необходимо выбрать сторону поражения');
          return;
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
        size_x_mm: null,
        size_y_mm: null,
        size_z_mm: null,
        volume_mm3: null,
        size_max_mm: null,
        size_min_mm: null,
        asymmetry_type: '',
        calcification_malignancy: '',
        calcification_morphology: '',
        calcification_distribution: '',
        associated_feature: '',
        comparison_available: false,
        dynamics: '',
        comment: ''
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