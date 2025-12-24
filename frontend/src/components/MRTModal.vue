<template>
  <div class="mrt-modal modal" @click.self="$emit('close')">
    <div class="modal-content modal-xlarge">
      <div class="modal-header">
        <h3>МРТ молочных желез (Дата: {{ mrt.exam_date }})</h3>
        <button @click="$emit('close')" class="btn-close">×</button>
      </div>

      <!-- Общая информация -->
      <div class="info-section">
        <div class="info-grid">
          <div><strong>Этап:</strong> {{ mrt.study_stage }}</div>
          <div><strong>День МЦ:</strong> {{ mrt.menstrual_cycle_day }}</div>
          <div><strong>BI-RADS справа:</strong> {{ mrt.birads_right }}</div>
          <div><strong>BI-RADS слева:</strong> {{ mrt.birads_left }}</div>
          <div><strong>ACR справа:</strong> {{ mrt.acr_density_right }}</div>
          <div><strong>ACR слева:</strong> {{ mrt.acr_density_left }}</div>
          <div><strong>BPE:</strong> {{ mrt.bpe_level }}</div>
          <div><strong>Симметрия BPE:</strong> {{ mrt.bpe_symmetry }}</div>
        </div>
      </div>

      <!-- Вкладки для находок и лимфоузлов -->
      <div class="tabs-section">
        <button
          @click="activeTab = 'findings'"
          :class="['tab-btn', {active: activeTab === 'findings'}]"
        >
          Находки
        </button>
        <button
          @click="activeTab = 'lymphNodes'"
          :class="['tab-btn', {active: activeTab === 'lymphNodes'}]"
        >
          Лимфоузлы
        </button>
      </div>

      <!-- Находки -->
      <div v-if="activeTab === 'findings'" class="findings-section">
        <div class="section-header">
          <h4>Находки при МРТ</h4>
          <button @click="showAddFinding = true" class="btn btn-primary btn-sm">Добавить находку</button>
        </div>

        <table class="data-table" v-if="findings.length">
          <thead>
            <tr>
              <th>№</th>
              <th>Сторона</th>
              <th>Локализация</th>
              <th>Тип</th>
              <th>Размеры, мм³</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in findings" :key="item.id">
              <td>{{ item.finding_number }}</td>
              <td>{{ item.side }}</td>
              <td>{{ item.quadrant_location }}</td>
              <td>{{ item.finding_type }}</td>
              <td>{{ item.volume_mm3 }}</td>
              <td>
                <button @click="editFinding(item)" class="btn-sm btn-warning">Изменить</button>
                <button @click="deleteFinding(item.id)" class="btn-sm btn-danger">Удалить</button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data">Находок не обнаружено</p>
      </div>

      <!-- Лимфоузлы -->
      <div v-if="activeTab === 'lymphNodes'" class="findings-section">
        <div class="section-header">
          <h4>Лимфоузлы</h4>
          <button @click="showAddLymphNode = true" class="btn btn-primary btn-sm">Добавить лимфоузел</button>
        </div>

        <table class="data-table" v-if="lymphNodes.length">
          <thead>
            <tr>
              <th>№</th>
              <th>Сторона</th>
              <th>Изменен</th>
              <th>Группа ЛУ</th>
              <th>Размеры</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ln in lymphNodes" :key="ln.id">
              <td>{{ ln.finding_number }}</td>
              <td>{{ ln.side }}</td>
              <td>{{ ln.has_changes }}</td>
              <td>{{ ln.lymph_node_group }}</td>
              <td>{{ ln.size_cortical_mm }}</td>
              <td>
                <button @click="editLymphNode(ln)" class="btn-sm btn-warning">Изменить</button>
                <button @click="deleteLymphNode(ln.id)" class="btn-sm btn-danger">Удалить</button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data">Лимфоузлов не обнаружено</p>
      </div>

      <!-- Модал добавления/редактирования находки -->
      <div v-if="showAddFinding" class="modal inner-modal" @click.self="showAddFinding = false">
        <div class="modal-content modal-large">
          <h4>{{ editingFindingId ? 'Редактировать находку' : 'Добавить находку' }}</h4>
          <form @submit.prevent="saveFinding">
            <div class="form-row">
              <div class="form-group">
                <label>Сторона *</label>
                <select v-model="findingForm.side" required class="input">
                  <option value="">Выберите</option>
                  <option value="Правая МЖ">Правая МЖ</option>
                  <option value="Левая МЖ">Левая МЖ</option>
                </select>
              </div>
              <div class="form-group">
                <label>Тип находки *</label>
                <select v-model="findingForm.finding_type" @change="onFindingTypeChange" required class="input">
                  <option value="">Выберите</option>
                  <option value="Образование">Образование</option>
                  <option value="Очаг">Очаг</option>
                  <option value="Зона неопухолевого контрастирования (NME)">Зона неопухолевого контрастирования (NME)</option>
                  <option value="Сопутствующие признаки">Сопутствующие признаки</option>
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
              <div class="form-group">
                <label>Локализация по глубине МЖ</label>
                <select v-model="findingForm.depth_location" class="input">
                  <option value="">Выберите</option>
                  <option v-for="depth in depthLocations" :key="depth" :value="depth">{{ depth }}</option>
                </select>
              </div>
            </div>

            <!-- Для Образования или Очага -->
            <div v-if="findingForm.finding_type === 'Образование' || findingForm.finding_type === 'Очаг'" class="finding-details">
              <h5>Описание {{ findingForm.finding_type === 'Образование' ? 'образования' : 'очага' }}</h5>

              <div class="form-row">
                <div class="form-group">
                  <label>Форма</label>
                  <select v-model="findingForm.mass_shape" class="input">
                    <option value="">Выберите</option>
                    <option v-for="shape in massShapes" :key="shape" :value="shape">{{ shape }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Края</label>
                  <select v-model="findingForm.mass_margin" class="input">
                    <option value="">Выберите</option>
                    <option v-for="margin in massMargins" :key="margin" :value="margin">{{ margin }}</option>
                  </select>
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Размер X (мм)</label>
                  <input v-model.number="findingForm.size_x_mm" @input="calculateVolume" type="number" min="1" class="input">
                </div>
                <div class="form-group">
                  <label>Размер Y (мм)</label>
                  <input v-model.number="findingForm.size_y_mm" @input="calculateVolume" type="number" min="1" class="input">
                </div>
                <div class="form-group">
                  <label>Размер Z (мм)</label>
                  <input v-model.number="findingForm.size_z_mm" @input="calculateVolume" type="number" min="1" class="input">
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Сигнал T2</label>
                  <select v-model="findingForm.t2_signal" class="input">
                    <option value="">Выберите</option>
                    <option v-for="signal in t2Signals" :key="signal" :value="signal">{{ signal }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Характеристики усиления</label>
                  <select v-model="findingForm.enhancement_characteristics" class="input">
                    <option value="">Выберите</option>
                    <option v-for="char in enhancementCharacteristics" :key="char" :value="char">{{ char }}</option>
                  </select>
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Кинетика контрастирования</label>
                  <select v-model="findingForm.kinetics" class="input">
                    <option value="">Выберите</option>
                    <option v-for="kin in kinetics" :key="kin" :value="kin">{{ kin }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Сигнал на DWI (высокий b-value)</label>
                  <select v-model="findingForm.dwi_signal" class="input">
                    <option value="">Выберите</option>
                    <option v-for="dwi in dwiSignals" :key="dwi" :value="dwi">{{ dwi }}</option>
                  </select>
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Сигнал на карте ADC</label>
                  <select v-model="findingForm.adc_signal" class="input">
                    <option value="">Выберите</option>
                    <option v-for="adc in adcSignals" :key="adc" :value="adc">{{ adc }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Значение ADC</label>
                  <input v-model.number="findingForm.adc_value" type="number" step="0.01" class="input">
                </div>
              </div>

              <div class="form-group">
                <label>Признаки инвазии</label>
                <select v-model="findingForm.invasion_signs" class="input">
                  <option value="">Выберите</option>
                  <option value="Вовлечение">Вовлечение</option>
                  <option value="перифокальный отёк">перифокальный отёк</option>
                </select>
              </div>

              <div v-if="findingForm.volume_mm3" class="calculated-metrics">
                <div><strong>Объём:</strong> {{ findingForm.volume_mm3 }} мм³</div>
              </div>
            </div>

            <!-- Для зоны неопухолевого контрастирования (NME) -->
            <div v-if="findingForm.finding_type === 'Зона неопухолевого контрастирования (NME)'" class="finding-details">
              <h5>Описание зоны неопухолевого контрастирования</h5>

              <div class="form-row">
                <div class="form-group">
                  <label>Распределение</label>
                  <select v-model="findingForm.nme_distribution" class="input">
                    <option value="">Выберите</option>
                    <option v-for="dist in nmeDistributions" :key="dist" :value="dist">{{ dist }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Характеристики усиления</label>
                  <select v-model="findingForm.nme_enhancement" class="input">
                    <option value="">Выберите</option>
                    <option v-for="enh in nmeEnhancements" :key="enh" :value="enh">{{ enh }}</option>
                  </select>
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Размер X (мм)</label>
                  <input v-model.number="findingForm.size_x_mm" @input="calculateVolume" type="number" min="1" class="input">
                </div>
                <div class="form-group">
                  <label>Размер Y (мм)</label>
                  <input v-model.number="findingForm.size_y_mm" @input="calculateVolume" type="number" min="1" class="input">
                </div>
                <div class="form-group">
                  <label>Размер Z (мм)</label>
                  <input v-model.number="findingForm.size_z_mm" @input="calculateVolume" type="number" min="1" class="input">
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Кинетика контрастирования</label>
                  <select v-model="findingForm.kinetics" class="input">
                    <option value="">Выберите</option>
                    <option v-for="kin in kinetics" :key="kin" :value="kin">{{ kin }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Сигнал на DWI</label>
                  <select v-model="findingForm.dwi_signal" class="input">
                    <option value="">Выберите</option>
                    <option v-for="dwi in dwiSignals" :key="dwi" :value="dwi">{{ dwi }}</option>
                  </select>
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Сигнал на карте ADC</label>
                  <select v-model="findingForm.adc_signal" class="input">
                    <option value="">Выберите</option>
                    <option v-for="adc in adcSignals" :key="adc" :value="adc">{{ adc }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Значение ADC</label>
                  <input v-model.number="findingForm.adc_value" type="number" step="0.01" class="input">
                </div>
              </div>

              <div v-if="findingForm.volume_mm3" class="calculated-metrics">
                <div><strong>Объём:</strong> {{ findingForm.volume_mm3 }} мм³</div>
              </div>
            </div>

            <div class="form-actions">
              <button type="button" @click="closeFindingModal" class="btn btn-secondary">Отмена</button>
              <button type="submit" class="btn btn-primary">Сохранить</button>
            </div>
          </form>
        </div>
      </div>

      <!-- Модал добавления/редактирования лимфоузла -->
      <div v-if="showAddLymphNode" class="modal inner-modal" @click.self="showAddLymphNode = false">
        <div class="modal-content modal-large">
          <h4>{{ editingLymphNodeId ? 'Редактировать лимфоузел' : 'Добавить лимфоузел' }}</h4>
          <form @submit.prevent="saveLymphNode">
            <div class="form-row">
              <div class="form-group">
                <label>Сторона *</label>
                <select v-model="lymphNodeForm.side" required class="input">
                  <option value="">Выберите</option>
                  <option value="Правая МЖ">Правая МЖ</option>
                  <option value="Левая МЖ">Левая МЖ</option>
                </select>
              </div>
              <div class="form-group">
                <label>Наличие изменений *</label>
                <select v-model="lymphNodeForm.has_changes" required class="input">
                  <option value="">Выберите</option>
                  <option value="Да">Да</option>
                  <option value="Нет">Нет</option>
                </select>
              </div>
            </div>

            <div v-if="lymphNodeForm.has_changes === 'Да'" class="finding-details">
              <h5>Характеристики лимфоузла</h5>

              <div class="form-group">
                <label>Группа ЛУ</label>
                <select v-model="lymphNodeForm.lymph_node_group" class="input">
                  <option value="">Выберите</option>
                  <option v-for="group in lymphNodeGroups" :key="group" :value="group">{{ group }}</option>
                </select>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Форма ЛУ</label>
                  <select v-model="lymphNodeForm.shape" class="input">
                    <option value="">Выберите</option>
                    <option v-for="shape in lymphNodeShapes" :key="shape" :value="shape">{{ shape }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Контур и форма</label>
                  <select v-model="lymphNodeForm.contour" class="input">
                    <option value="">Выберите</option>
                    <option v-for="contour in lymphNodeContours" :key="contour" :value="contour">{{ contour }}</option>
                  </select>
                </div>
              </div>

              <div class="form-group">
                <label>Размер (наибольший кортикальный), мм</label>
                <input v-model.number="lymphNodeForm.size_cortical_mm" type="number" min="1" class="input">
              </div>

              <div class="form-group">
                <label>Структура ЛУ</label>
                <select v-model="lymphNodeForm.structure" class="input">
                  <option value="">Выберите</option>
                  <option v-for="struct in lymphNodeStructures" :key="struct" :value="struct">{{ struct }}</option>
                </select>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Интенсивность и характер контрастирования</label>
                  <select v-model="lymphNodeForm.enhancement_intensity" class="input">
                    <option value="">Выберите</option>
                    <option v-for="int in lymphNodeEnhancements" :key="int" :value="int">{{ int }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Кинетика контрастирования</label>
                  <select v-model="lymphNodeForm.kinetics" class="input">
                    <option value="">Выберите</option>
                    <option v-for="kin in kinetics" :key="kin" :value="kin">{{ kin }}</option>
                  </select>
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Сигнал на DWI</label>
                  <select v-model="lymphNodeForm.dwi_signal" class="input">
                    <option value="">Выберите</option>
                    <option v-for="dwi in dwiSignals" :key="dwi" :value="dwi">{{ dwi }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Сигнал на карте ADC</label>
                  <select v-model="lymphNodeForm.adc_signal" class="input">
                    <option value="">Выберите</option>
                    <option v-for="adc in adcSignals" :key="adc" :value="adc">{{ adc }}</option>
                  </select>
                </div>
              </div>

              <div class="form-group">
                <label>Значение ADC</label>
                <input v-model.number="lymphNodeForm.adc_value" type="number" step="0.01" class="input">
              </div>
            </div>

            <div class="form-actions">
              <button type="button" @click="closeLymphNodeModal" class="btn btn-secondary">Отмена</button>
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

export default {
  props: {
    mrt: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      activeTab: 'findings',
      findings: [],
      lymphNodes: [],
      showAddFinding: false,
      showAddLymphNode: false,
      editingFindingId: null,
      editingLymphNodeId: null,
      findingForm: this.getEmptyFindingForm(),
      lymphNodeForm: this.getEmptyLymphNodeForm(),

      // Справочники из таблицы МРТ
      quadrantLocations: [
        'Верхне-наружный квадрант',
        'Верхне-внутренний квадрант',
        'Нижне-наружный квадрант',
        'Нижне-внутренний квадрант',
        'Субареолярная зона',
        'Центральная зона',
        'Граница верхних квадрантов',
        'Граница нижних квадрантов',
        'Граница наружных квадрантов',
        'Граница внутренних квадрантов'
      ],
      depthLocations: [
        'Передняя треть',
        'Средняя треть',
        'Задяя треть',
        'Субареолярно',
        'в проекции большой грудной мышцы',
        'в проекции аксиллярной зоны',
        'в зоне Зоргиуса'
      ],
      massShapes: [
        'Округлая',
        'Овальная',
        'Полициклическая',
        'Неправильная'
      ],
      massMargins: [
        'Четкие',
        'Нечеткие',
        'Спикулообразные',
        'Микродольчатые'
      ],
      t2Signals: [
        'Гиперинтенсивный',
        'негиперинтенсивный',
        'Изоинтенсивный'
      ],
      enhancementCharacteristics: [
        'Гомогенное',
        'Гетерогенное',
        'Кольцевое (выраженное периферическое усиление)',
        'Имеет внутренние перегородки'
      ],
      kinetics: [
        '1й тип кривой',
        '2й тип кривой',
        '3й тип кривой'
      ],
      dwiSignals: [
        'Высокий',
        'Низкий',
        'Изоинтенсивный'
      ],
      adcSignals: [
        'Низкий (светлый на ADC = темный на карте)',
        'Высокий'
      ],
      nmeDistributions: [
        'Фокальное',
        'Линейное',
        'Сегментарное',
        'Регионарное',
        'Множественные регионы',
        'Диффузное'
      ],
      nmeEnhancements: [
        'Гомогенное',
        'Гетерогенное',
        'Сливное (кластеризованное)',
        'Сгруппированные кольца'
      ],
      lymphNodeGroups: [
        'Надключичные ЛУ',
        'Подключичные ЛУ',
        'Медиастинальные ЛУ',
        'Парастернальные ЛУ',
        'Верхние подмышечные ЛУ',
        'Средние подмышечные ЛУ',
        'Нижние подмышечные ЛУ',
        'Медиальные надчревные ЛУ',
        'Латеральные надчревные ЛУ'
      ],
      lymphNodeShapes: [
        'Округлая / выпуклая',
        'Овальная / бобовидная с дифференцированными воротами',
        'Неправильная / Спикулообразный, нечеткий контур'
      ],
      lymphNodeContours: [
        'Ровные',
        'Неровные: волнистые',
        'Неровные: полициклические',
        'Неровные: звездчатые',
        'Неровные: спикулообразные',
        'Неровные: лучистые'
      ],
      lymphNodeStructures: [
        'Сохраненные ворота (жировая ткань + сосудистая ножка) – признак нормы',
        'Диффузное или неравномерное утолщение кортикального слоя (> 3 мм) – подозрительный признак',
        'Полная потеря жировых ворот, гомогенное усиление – высокоподозрительный признак',
        'Очаговое кортикальное образование/выбухание – высокоподозрительный признак'
      ],
      lymphNodeEnhancements: [
        'Умеренное, гомогенное (реактивное изменение)',
        'Интенсивное, гомогенное (подозрительно)',
        'Гетерогенное, периферическое/кольцевое – высокоподозрительный признак, может указывать на'
      ]
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    getEmptyFindingForm() {
      return {
        finding_number: null,
        side: '',
        quadrant_location: '',
        depth_location: '',
        finding_type: '',
        mass_shape: '',
        mass_margin: '',
        size_x_mm: null,
        size_y_mm: null,
        size_z_mm: null,
        volume_mm3: null,
        t2_signal: '',
        enhancement_characteristics: '',
        kinetics: '',
        dwi_signal: '',
        adc_signal: '',
        adc_value: null,
        invasion_signs: '',
        nme_distribution: '',
        nme_enhancement: ''
      }
    },
    getEmptyLymphNodeForm() {
      return {
        finding_number: null,
        side: '',
        has_changes: '',
        lymph_node_group: '',
        shape: '',
        contour: '',
        size_cortical_mm: null,
        structure: '',
        enhancement_intensity: '',
        kinetics: '',
        dwi_signal: '',
        adc_signal: '',
        adc_value: null
      }
    },
    calculateVolume() {
      const x = this.findingForm.size_x_mm
      const y = this.findingForm.size_y_mm
      const z = this.findingForm.size_z_mm

      if (x && y && z) {
        const volume = (4 / 3) * Math.PI * (x / 2) * (y / 2) * (z / 2)
        this.findingForm.volume_mm3 = Math.round(volume)
      } else {
        this.findingForm.volume_mm3 = null
      }
    },
    onFindingTypeChange() {
      const side = this.findingForm.side
      const quadrant = this.findingForm.quadrant_location
      const depth = this.findingForm.depth_location
      const type = this.findingForm.finding_type

      this.findingForm = this.getEmptyFindingForm()
      this.findingForm.side = side
      this.findingForm.quadrant_location = quadrant
      this.findingForm.depth_location = depth
      this.findingForm.finding_type = type
    },
    async loadData() {
      try {
        const findingsResponse = await api.getMRTFindings(this.mrt.id)
        this.findings = findingsResponse.data

        const lymphNodesResponse = await api.getMRTLymphNodes(this.mrt.id)
        this.lymphNodes = lymphNodesResponse.data
      } catch (error) {
        console.error('Error loading data:', error)
      }
    },
    editFinding(finding) {
      this.editingFindingId = finding.id
      this.findingForm = {...finding}
      this.showAddFinding = true
    },
    editLymphNode(lymphNode) {
      this.editingLymphNodeId = lymphNode.id
      this.lymphNodeForm = {...lymphNode}
      this.showAddLymphNode = true
    },
    async saveFinding() {
      try {
        const data = {
          ...this.findingForm,
          mrt_id: this.mrt.id
        }

        if (this.editingFindingId) {
          await api.updateMRTFinding(this.editingFindingId, data)
        } else {
          await api.createMRTFinding(data)
        }

        this.closeFindingModal()
        this.loadData()
        this.$emit('updated')
      } catch (error) {
        alert('Ошибка сохранения: ' + (error.response?.data?.detail || error.message))
      }
    },
    async saveLymphNode() {
      try {
        const data = {
          ...this.lymphNodeForm,
          mrt_id: this.mrt.id
        }

        if (this.editingLymphNodeId) {
          await api.updateMRTLymphNode(this.editingLymphNodeId, data)
        } else {
          await api.createMRTLymphNode(data)
        }

        this.closeLymphNodeModal()
        this.loadData()
        this.$emit('updated')
      } catch (error) {
        alert('Ошибка сохранения: ' + (error.response?.data?.detail || error.message))
      }
    },
    closeFindingModal() {
      this.showAddFinding = false
      this.editingFindingId = null
      this.findingForm = this.getEmptyFindingForm()
    },
    closeLymphNodeModal() {
      this.showAddLymphNode = false
      this.editingLymphNodeId = null
      this.lymphNodeForm = this.getEmptyLymphNodeForm()
    },
    async deleteFinding(id) {
      if (confirm('Удалить находку?')) {
        try {
          await api.deleteMRTFinding(id)
          this.loadData()
          this.$emit('updated')
        } catch (error) {
          alert('Ошибка удаления')
        }
      }
    },
    async deleteLymphNode(id) {
      if (confirm('Удалить лимфоузел?')) {
        try {
          await api.deleteMRTLymphNode(id)
          this.loadData()
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
.mrt-modal {
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
  background: rgba(0, 0, 0, 0.5);
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
}
</style>