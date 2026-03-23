<template>
  <div class="modal rb-overlay" @click.self="$emit('close')">
    <div class="rb-modal">
      <div class="rb-header">
        <h3>Конструктор вариативного отчёта</h3>
        <button @click="$emit('close')" class="rb-close">&times;</button>
      </div>

      <div class="rb-body">
        <!-- 1. Пациенты -->
        <div class="rb-section">
          <h4 class="rb-section-title">1. Пациенты</h4>
          <div class="rb-row">
            <input v-model="patientSearch" class="input rb-search" placeholder="Поиск по ФИО или ИД">
            <button @click="selectAllPatients" class="btn btn-sm btn-outline-secondary">Выбрать всех</button>
            <button @click="selectedPatientIds = []" class="btn btn-sm btn-outline-secondary">Снять всех</button>
          </div>
          <div class="rb-patient-list">
            <label v-for="p in displayedPatients" :key="p.id" class="rb-patient-item">
              <input type="checkbox" :value="p.id" v-model="selectedPatientIds">
              <span>{{ p.last_name }} {{ p.first_name }} {{ p.middle_name }} <em>({{ p.id }})</em></span>
            </label>
            <div v-if="isLoading" class="rb-loading">Загрузка...</div>
            <div v-if="!isLoading && displayedPatients.length === 0" class="rb-empty">Пациенты не найдены</div>
          </div>
          <div class="rb-count">Выбрано: {{ selectedPatientIds.length }} из {{ allPatients.length }}</div>

          <div class="rb-subsection">
            <div class="rb-subsection-header">
              <strong>Поля паспорта в отчёте</strong>
              <button @click="selectedPatientFields = PATIENT_FIELDS.map(f => f.key)" class="btn btn-xs">Все</button>
              <button @click="selectedPatientFields = []" class="btn btn-xs">Снять</button>
            </div>
            <div class="rb-checkboxes">
              <label v-for="f in PATIENT_FIELDS" :key="f.key" class="rb-cb-item">
                <input type="checkbox" :value="f.key" v-model="selectedPatientFields">
                {{ f.label }}
              </label>
            </div>
          </div>
        </div>

        <!-- 2. Исследования -->
        <div class="rb-section">
          <h4 class="rb-section-title">2. Исследования и параметры</h4>
          <div class="rb-modality-grid">
            <label v-for="m in MODALITIES" :key="m.key" class="rb-mod-item">
              <input type="checkbox" :value="m.key" v-model="selectedModalities">
              {{ m.label }}
            </label>
          </div>

          <div v-for="m in selectedModalityDefs" :key="'fp-' + m.key" class="rb-filter-panel">
            <div class="rb-fp-header" @click="togglePanel(m.key)">
              <strong>{{ m.label }}</strong>
              <span v-if="activeFilterCount(m.key) > 0" class="rb-badge">{{ activeFilterCount(m.key) }}</span>
              <span class="rb-chevron">{{ expandedPanels[m.key] ? '▲' : '▼' }}</span>
            </div>
            <div v-show="expandedPanels[m.key]" class="rb-fp-body">
              <div v-for="field in m.filterFields" :key="field.key" class="rb-ff">
                <div class="rb-ff-header" @click="toggleField(m.key, field.key)">
                  <span>{{ field.label }}</span>
                  <span v-if="(modalityFilters[m.key][field.key] || []).length > 0" class="rb-badge-sm">
                    {{ modalityFilters[m.key][field.key].length }}
                  </span>
                  <span class="rb-chevron-sm">{{ isFieldExpanded(m.key, field.key) ? '▲' : '▼' }}</span>
                </div>
                <div v-show="isFieldExpanded(m.key, field.key)" class="rb-ff-options">
                  <div class="rb-ff-actions">
                    <button @click="selectAllFilter(m.key, field.key, field.options)" class="btn btn-xs">Все</button>
                    <button @click="clearFilter(m.key, field.key)" class="btn btn-xs">Снять</button>
                  </div>
                  <label v-for="opt in field.options" :key="opt" class="rb-opt">
                    <input type="checkbox" :value="opt" v-model="modalityFilters[m.key][field.key]">
                    {{ opt }}
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="rb-footer">
        <span v-if="selectedPatientIds.length === 0" class="rb-warn">Выберите пациентов</span>
        <span v-else-if="selectedModalities.length === 0" class="rb-warn">Выберите методы исследований</span>
        <span v-else class="rb-ok">Готово к формированию</span>
        <div class="rb-footer-btns">
          <button @click="$emit('close')" class="btn btn-secondary">Закрыть</button>
          <button @click="generateReport" class="btn btn-primary"
            :disabled="isGenerating || selectedPatientIds.length === 0 || selectedModalities.length === 0">
            <span v-if="isGenerating">⏳ Формируется...</span>
            <span v-else>📊 Сформировать Excel</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api'
import * as XLSX from 'xlsx'

const NA = 'N/A'

const QUADRANT_LOCATIONS = [
  'Верхне-наружный квадрант', 'Верхне-внутренний квадрант',
  'Нижне-наружный квадрант', 'Нижне-внутренний квадрант',
  'Субареолярная зона', 'Центральная зона',
  'Граница верхних квадрантов', 'Граница нижних квадрантов',
  'Граница наружных квадрантов', 'Граница внутренних квадрантов'
]

const DEPTH_LOCATIONS = [
  'Передняя треть', 'Средняя треть', 'Задняя треть',
  'Субареолярно', 'В проекции большой грудной мышцы',
  'В проекции аксиллярной зоны', 'в зоне Зоргиуса'
]

const LYMPH_NODE_GROUPS = [
  'Надключичные ЛУ', 'Подключичные ЛУ', 'Медиастинальные ЛУ',
  'Парастернальные ЛУ', 'Верхние подмышечные ЛУ',
  'Средние подмышечные ЛУ', 'Нижние подмышечные ЛУ',
  'Медиальные надчревные ЛУ', 'Латеральные надчревные ЛУ'
]

const PATIENT_FIELDS = [
  { key: 'id', label: 'ИД' },
  { key: 'last_name', label: 'Фамилия' },
  { key: 'first_name', label: 'Имя' },
  { key: 'middle_name', label: 'Отчество' },
  { key: 'snils', label: 'СНИЛС' },
  { key: 'gender', label: 'Пол' },
  { key: 'date_of_birth', label: 'Дата рождения' },
  { key: 'diagnosis', label: 'Диагноз' },
  { key: 'tnm_stage', label: 'Стадия TNM' },
  { key: 'mkb_code', label: 'Код МКБ' },
  { key: 'comment', label: 'Комментарий' }
]

const MALIGNANCY_DEGREES = [
  'Gx Категория G не может быть определена',
  'G1 Низкая степень злокачественности (благоприятный вариант), 3–5 баллов по шкале SBR (Ноттингемская шкала)',
  'G2 Умеренная степень злокачественности (промежуточный вариант), 6–7 баллов по шкале SBR (Ноттингемская шкала)',
  'G3 Высокая степень злокачественности (неблагоприятный вариант), 8–9 баллов по шкале SBR (Ноттингемская шкала)'
]

const MODALITIES = [
  {
    key: 'mammo', label: 'Маммография',
    dataKey: 'mammographies', findingsKey: 'findings',
    sideField: 'affected_side', quadrantField: 'quadrant_location',
    depthField: 'depth_location', lymphGroupField: null,
    hasVolume: true,
    filterFields: [
      { key: 'finding_type', label: 'Тип находки', options: ['Объемное образование', 'Асимметрия', 'Кальцинаты', 'Сопутствующие изменения'] },
      { key: 'affected_side', label: 'Сторона', options: ['Правая МЖ', 'Левая МЖ'] },
      { key: 'quadrant_location', label: 'Квадрант', options: QUADRANT_LOCATIONS },
      { key: 'depth_location', label: 'Глубина', options: DEPTH_LOCATIONS },
      { key: 'mass_shape', label: 'Форма', options: ['Округлая', 'Овальная', 'Неправильная'] },
      { key: 'mass_margin', label: 'Контур', options: ['Четкий ровный', 'Микролобулированный', 'Нечеткий', 'Спикулообразный'] },
      { key: 'mass_density', label: 'Плотность', options: ['Высокая плотность', 'Изоденсная', 'Низкая плотность', 'Содержит жир'] },
      { key: 'asymmetry_type', label: 'Тип асимметрии', options: ['Асимметрия', 'Глобальная асимметрия', 'Фокальная асимметрия', 'Развивающаяся асимметрия'] },
      { key: 'calcification_malignancy', label: 'Характер кальцинатов', options: ['Доброкачественные', 'Подозрительные'] },
      { key: 'dynamics', label: 'Динамика', options: ['Улучшение', 'Без динамики', 'Ухудшение'] }
    ],
    detailFields: [
      { key: 'finding_type', label: 'Тип находки' }, { key: 'mass_shape', label: 'Форма' },
      { key: 'mass_margin', label: 'Контур' }, { key: 'mass_density', label: 'Плотность' },
      { key: 'asymmetry_type', label: 'Тип асимметрии' }, { key: 'calcification_in_structure', label: 'Кальцинаты в структуре' },
      { key: 'calcification_malignancy', label: 'Характер кальцинатов' },
      { key: 'calcification_morphology', label: 'Морфология кальцинатов' },
      { key: 'calcification_distribution', label: 'Распределение кальцинатов' },
      { key: 'associated_feature', label: 'Сопутствующие признаки' }, { key: 'dynamics', label: 'Динамика' },
      { key: 'comparison_available', label: 'Сравнение доступно' }, { key: 'comment', label: 'Комментарий' }
    ]
  },
  {
    key: 'uzi_mzh', label: 'УЗИ МЖ',
    dataKey: 'ultrasounds', findingsKey: 'findings',
    sideField: 'side', quadrantField: 'quadrant_location',
    depthField: 'depth_location', lymphGroupField: null,
    hasVolume: true,
    filterFields: [
      { key: 'finding_type', label: 'Тип находки', options: ['Объемное образование', 'Сопутствующие признаки'] },
      { key: 'side', label: 'Сторона', options: ['Правая МЖ', 'Левая МЖ'] },
      { key: 'quadrant_location', label: 'Квадрант', options: QUADRANT_LOCATIONS },
      { key: 'depth_location', label: 'Глубина', options: DEPTH_LOCATIONS },
      { key: 'mass_shape', label: 'Форма', options: ['Округлая', 'Овальная', 'Полициклическая', 'Неправильная'] },
      { key: 'spatial_orientation', label: 'Ориентация', options: ['горизонтальная', 'вертикальная', 'неопределенная (шаровидная)'] },
      { key: 'echogenicity', label: 'Эхогенность', options: ['анэхогенное', 'гипоэхогенное', 'гиперэхогенное', 'изоэхогенное'] },
      { key: 'vascularization_type', label: 'Васкуляризация', options: ['Аваскулярный', 'Васкуляризация внутри образования', 'Периферическая васкуляризация'] }
    ],
    detailFields: [
      { key: 'finding_type', label: 'Тип находки' }, { key: 'mass_shape', label: 'Форма' },
      { key: 'spatial_orientation', label: 'Ориентация' }, { key: 'mass_margin', label: 'Контур' },
      { key: 'mass_boundary', label: 'Граница' }, { key: 'echogenicity', label: 'Эхогенность' },
      { key: 'structure', label: 'Структура' }, { key: 'acoustic_effects', label: 'Акустические эффекты' },
      { key: 'vascularization_type', label: 'Васкуляризация' }, { key: 'surrounding_tissue', label: 'Окружающие ткани' },
      { key: 'associated_feature_type', label: 'Сопутствующие признаки' }
    ]
  },
  {
    key: 'uzi_lu', label: 'УЗИ ЛУ',
    dataKey: 'ultrasounds', findingsKey: 'lymph_nodes',
    sideField: 'side', quadrantField: null,
    depthField: null, lymphGroupField: 'lymph_node_group',
    hasVolume: true,
    filterFields: [
      { key: 'side', label: 'Сторона', options: ['Правая МЖ', 'Левая МЖ'] },
      { key: 'has_changes', label: 'Изменения', options: ['Да', 'Нет'] },
      { key: 'lymph_node_group', label: 'Группа ЛУ', options: LYMPH_NODE_GROUPS },
      { key: 'shape', label: 'Форма', options: ['Округлая', 'Овальная', 'Неправильная'] },
      { key: 'vascularization_type', label: 'Васкуляризация', options: ['Аваскулярный', 'Васкуляризация внутри ЛУ', 'Периферическая васкуляризация'] },
      { key: 'hyperplasia_type', label: 'Тип гиперплазии', options: ['Доброкачественная', 'Злокачественная'] }
    ],
    detailFields: [
      { key: 'has_changes', label: 'Изменения' }, { key: 'shape', label: 'Форма ЛУ' },
      { key: 'margin', label: 'Контур ЛУ' }, { key: 'boundary', label: 'Граница ЛУ' },
      { key: 'medulla_echogenicity', label: 'Эхогенность мозгового слоя' },
      { key: 'cortex_echogenicity', label: 'Эхогенность коркового слоя' },
      { key: 'has_widened_cortex', label: 'Расширение коркового слоя' },
      { key: 'vascularization_type', label: 'Васкуляризация ЛУ' }, { key: 'hyperplasia_type', label: 'Тип гиперплазии' }
    ]
  },
  {
    key: 'km_le', label: 'КМ LE',
    dataKey: 'contrast_mammographies', findingsKey: 'le_findings',
    sideField: 'affected_side', quadrantField: 'quadrant_location',
    depthField: 'depth_location', lymphGroupField: null,
    hasVolume: true,
    filterFields: [
      { key: 'finding_type', label: 'Тип находки', options: ['Объемное образование', 'Асимметрия', 'Кальцинаты', 'Сопутствующие изменения'] },
      { key: 'affected_side', label: 'Сторона', options: ['Правая МЖ', 'Левая МЖ'] },
      { key: 'quadrant_location', label: 'Квадрант', options: QUADRANT_LOCATIONS },
      { key: 'depth_location', label: 'Глубина', options: DEPTH_LOCATIONS },
      { key: 'mass_shape', label: 'Форма', options: ['Округлая', 'Овальная', 'Неправильная'] },
      { key: 'rc_enhancement_degree', label: 'Степень контрастирования', options: ['Слабая', 'Умеренная', 'Выраженная'] }
    ],
    detailFields: [
      { key: 'finding_type', label: 'Тип находки' }, { key: 'mass_shape', label: 'Форма' },
      { key: 'mass_margin', label: 'Контур' }, { key: 'mass_density', label: 'Плотность' },
      { key: 'contrast_type', label: 'Тип контрастирования' }, { key: 'visible_on_rc', label: 'Видимость на RC' },
      { key: 'rc_internal_enhancement', label: 'Внутреннее контрастирование RC' },
      { key: 'rc_enhancement_degree', label: 'Степень контрастирования' },
      { key: 'rc_enhancement_intensity', label: 'Интенсивность контрастирования' }, { key: 'dynamics', label: 'Динамика' }
    ]
  },
  {
    key: 'km_rc', label: 'КМ RC',
    dataKey: 'contrast_mammographies', findingsKey: 'rc_findings',
    sideField: 'affected_side', quadrantField: 'quadrant_location',
    depthField: 'depth_location', lymphGroupField: null,
    hasVolume: true,
    filterFields: [
      { key: 'finding_type', label: 'Тип находки', options: ['Объемное образование', 'Зона контрастирования без образования', 'Зона асимметричного контрастирования'] },
      { key: 'affected_side', label: 'Сторона', options: ['Правая МЖ', 'Левая МЖ'] },
      { key: 'quadrant_location', label: 'Квадрант', options: QUADRANT_LOCATIONS },
      { key: 'depth_location', label: 'Глубина', options: DEPTH_LOCATIONS },
      { key: 'enhancement_characteristic', label: 'Характеристика контрастирования', options: ['Однородное', 'Гетерогенное', 'Кольцевидное', 'Темная внутренняя перегородка'] },
      { key: 'enhancement_intensity', label: 'Интенсивность', options: ['Слабая', 'Умеренная', 'Выраженная'] }
    ],
    detailFields: [
      { key: 'finding_type', label: 'Тип находки' }, { key: 'mass_shape', label: 'Форма' },
      { key: 'mass_margin', label: 'Контур' }, { key: 'enhancement_characteristic', label: 'Характеристика контрастирования' },
      { key: 'distribution', label: 'Распределение' }, { key: 'internal_enhancement_pattern', label: 'Внутренний паттерн' },
      { key: 'asymmetric_enhancement_pattern', label: 'Асимметричный паттерн' },
      { key: 'enhancement_intensity', label: 'Интенсивность' }, { key: 'dynamics', label: 'Динамика' }
    ]
  },
  {
    key: 'mrt_mzh', label: 'МРТ МЖ',
    dataKey: 'mrts', findingsKey: 'findings',
    sideField: 'side', quadrantField: 'quadrant_location',
    depthField: 'depth_location', lymphGroupField: null,
    hasVolume: true,
    filterFields: [
      { key: 'finding_type', label: 'Тип находки', options: ['Образование', 'Очаг', 'Зона неопухолевого контрастирования (NME)', 'Сопутствующие признаки'] },
      { key: 'side', label: 'Сторона', options: ['Правая МЖ', 'Левая МЖ'] },
      { key: 'quadrant_location', label: 'Квадрант', options: QUADRANT_LOCATIONS },
      { key: 'depth_location', label: 'Глубина', options: DEPTH_LOCATIONS },
      { key: 't2_signal', label: 'T2 сигнал', options: ['Гиперинтенсивный', 'негиперинтенсивный', 'Изоинтенсивный'] },
      { key: 'kinetics', label: 'Кинетика', options: ['1й тип кривой', '2й тип кривой', '3й тип кривой'] },
      { key: 'dwi_signal', label: 'DWI сигнал', options: ['Высокий', 'Низкий', 'Изоинтенсивный'] }
    ],
    detailFields: [
      { key: 'finding_type', label: 'Тип находки' }, { key: 'mass_shape', label: 'Форма' },
      { key: 'mass_margin', label: 'Контур' }, { key: 't2_signal', label: 'T2 сигнал' },
      { key: 'enhancement_characteristics', label: 'Характер контрастирования' }, { key: 'kinetics', label: 'Кинетика' },
      { key: 'dwi_signal', label: 'DWI сигнал' }, { key: 'adc_signal', label: 'ADC сигнал' },
      { key: 'adc_value', label: 'ADC значение' }, { key: 'invasion_signs', label: 'Признаки инвазии' },
      { key: 'nme_distribution', label: 'NME распределение' }, { key: 'nme_enhancement', label: 'NME контрастирование' }
    ]
  },
  {
    key: 'mrt_lu', label: 'МРТ ЛУ',
    dataKey: 'mrts', findingsKey: 'lymph_nodes',
    sideField: 'side', quadrantField: null,
    depthField: null, lymphGroupField: 'lymph_node_group',
    hasVolume: false,
    filterFields: [
      { key: 'side', label: 'Сторона', options: ['Правая МЖ', 'Левая МЖ'] },
      { key: 'has_changes', label: 'Изменения', options: ['Да', 'Нет'] },
      { key: 'lymph_node_group', label: 'Группа ЛУ', options: LYMPH_NODE_GROUPS },
      { key: 'kinetics', label: 'Кинетика', options: ['1й тип кривой', '2й тип кривой', '3й тип кривой'] },
      { key: 'dwi_signal', label: 'DWI сигнал', options: ['Высокий', 'Низкий', 'Изоинтенсивный'] }
    ],
    detailFields: [
      { key: 'has_changes', label: 'Изменения' }, { key: 'shape', label: 'Форма ЛУ' },
      { key: 'contour', label: 'Контур ЛУ' }, { key: 'size_cortical_mm', label: 'Размер кортикального слоя (мм)' },
      { key: 'structure', label: 'Структура' }, { key: 'enhancement_intensity', label: 'Интенсивность контрастирования' },
      { key: 'kinetics', label: 'Кинетика' }, { key: 'dwi_signal', label: 'DWI сигнал' },
      { key: 'adc_signal', label: 'ADC сигнал' }, { key: 'adc_value', label: 'ADC значение' }
    ]
  },
  {
    key: 'hist_bio', label: 'Гистология (биопсия)',
    dataKey: 'histology_biopsies', findingsKey: 'findings',
    sideField: 'affected_side', quadrantField: 'quadrant_location',
    depthField: 'depth_location', lymphGroupField: 'lymph_node_group',
    hasVolume: false,
    filterFields: [
      { key: 'finding_location', label: 'Локализация', options: ['Молочная железа', 'Лимфатический узел'] },
      { key: 'affected_side', label: 'Сторона', options: ['Правая МЖ', 'Левая МЖ'] },
      { key: 'quadrant_location', label: 'Квадрант', options: QUADRANT_LOCATIONS },
      { key: 'lymph_node_group', label: 'Группа ЛУ', options: LYMPH_NODE_GROUPS },
      { key: 'malignancy_degree', label: 'Степень злокачественности', options: MALIGNANCY_DEGREES },
      { key: 'er_value', label: 'ER', options: ['Позитивный', 'Негативный', 'Сомнительный'] },
      { key: 'pr_value', label: 'PR', options: ['Позитивный', 'Негативный', 'Сомнительный'] },
      { key: 'her2_value', label: 'HER2', options: ['0', '1+', '2+', '3+'] },
      { key: 'ki67_value', label: 'Ki67', options: ['Низкий (≤20%)', 'Высокий (>20%)'] }
    ],
    detailFields: [
      { key: 'finding_location', label: 'Тип локализации' },
      { key: 'morphological_conclusion', label: 'Морфологическое заключение' },
      { key: 'who_classification', label: 'Классификация ВОЗ' }, { key: 'malignancy_degree', label: 'Степень злокачественности' },
      { key: 'ihc_conclusion', label: 'ИГХ заключение' }, { key: 'er_value', label: 'ER' },
      { key: 'pr_value', label: 'PR' }, { key: 'her2_value', label: 'HER2' }, { key: 'ki67_value', label: 'Ki67' }
    ]
  },
  {
    key: 'cyto', label: 'Цитология (биопсия)',
    dataKey: 'cytology_biopsies', findingsKey: 'findings',
    sideField: 'affected_side', quadrantField: 'quadrant_location',
    depthField: 'depth_location', lymphGroupField: 'lymph_node_group',
    hasVolume: false,
    filterFields: [
      { key: 'cytology_body_part', label: 'Орган', options: ['Молочная железа', 'Лимфатический узел'] },
      { key: 'affected_side', label: 'Сторона', options: ['Правая МЖ', 'Левая МЖ'] },
      { key: 'quadrant_location', label: 'Квадрант', options: QUADRANT_LOCATIONS },
      { key: 'lymph_node_group', label: 'Группа ЛУ', options: LYMPH_NODE_GROUPS },
      { key: 'diagnostic_category', label: 'Диагностическая категория', options: ['С1 — неинформативный материал.', 'С2 — доброкачественный процесс.', 'С3 — атипия неясного значения.', 'С4 — подозрение на злокачественный процесс.', 'С5 — злокачественное новообразование.'] },
      { key: 'cytology_report', label: 'Заключение', options: ['Наличие злокачественных клеток в пределах предоставленного материала', 'Отсутствие злокачественных клеток в пределах предоставленного материала'] }
    ],
    detailFields: [
      { key: 'cytology_body_part', label: 'Орган' },
      { key: 'diagnostic_category', label: 'Диагностическая категория' },
      { key: 'cytology_report', label: 'Заключение' }
    ]
  },
  {
    key: 'hist_postop', label: 'Гистология (послеоп)',
    dataKey: 'histology_postops', findingsKey: 'findings',
    sideField: 'affected_side', quadrantField: 'quadrant_location',
    depthField: 'depth_location', lymphGroupField: 'lymph_node_group',
    hasVolume: true,
    filterFields: [
      { key: 'finding_location', label: 'Локализация', options: ['Молочная железа', 'Лимфатический узел'] },
      { key: 'affected_side', label: 'Сторона', options: ['Правая МЖ', 'Левая МЖ'] },
      { key: 'quadrant_location', label: 'Квадрант', options: QUADRANT_LOCATIONS },
      { key: 'lymph_node_group', label: 'Группа ЛУ', options: LYMPH_NODE_GROUPS },
      { key: 'malignancy_degree', label: 'Степень злокачественности', options: MALIGNANCY_DEGREES },
      { key: 'er_value', label: 'ER', options: ['Позитивный', 'Негативный', 'Сомнительный'] },
      { key: 'pr_value', label: 'PR', options: ['Позитивный', 'Негативный', 'Сомнительный'] },
      { key: 'her2_value', label: 'HER2', options: ['0', '1+', '2+', '3+'] },
      { key: 'ki67_value', label: 'Ki67', options: ['Низкий (≤20%)', 'Высокий (>20%)'] }
    ],
    detailFields: [
      { key: 'finding_location', label: 'Тип локализации' },
      { key: 'morphological_conclusion', label: 'Морфологическое заключение' },
      { key: 'who_classification', label: 'Классификация ВОЗ' }, { key: 'malignancy_degree', label: 'Степень злокачественности' },
      { key: 'ihc_conclusion', label: 'ИГХ заключение' }, { key: 'er_value', label: 'ER' },
      { key: 'pr_value', label: 'PR' }, { key: 'her2_value', label: 'HER2' }, { key: 'ki67_value', label: 'Ki67' },
      { key: 'size_1_mm', label: 'Размер 1 (мм)' }, { key: 'size_2_mm', label: 'Размер 2 (мм)' },
      { key: 'size_3_mm', label: 'Размер 3 (мм)' }
    ]
  }
]

function initFilterState() {
  const state = {}
  MODALITIES.forEach(m => {
    state[m.key] = {}
    m.filterFields.forEach(f => { state[m.key][f.key] = [] })
  })
  return state
}

export default {
  name: 'ReportBuilderModal',
  emits: ['close'],
  data() {
    return {
      allPatients: [],
      patientSearch: '',
      selectedPatientIds: [],
      selectedPatientFields: ['id', 'last_name', 'first_name', 'middle_name', 'diagnosis', 'tnm_stage'],
      selectedModalities: [],
      modalityFilters: initFilterState(),
      expandedPanels: {},
      expandedFields: {},
      isLoading: false,
      isGenerating: false,
      PATIENT_FIELDS,
      MODALITIES
    }
  },
  computed: {
    displayedPatients() {
      if (!this.patientSearch.trim()) return this.allPatients
      const q = this.patientSearch.toLowerCase()
      return this.allPatients.filter(p =>
        `${p.last_name} ${p.first_name} ${p.middle_name} ${p.id}`.toLowerCase().includes(q)
      )
    },
    selectedModalityDefs() {
      return MODALITIES.filter(m => this.selectedModalities.includes(m.key))
    }
  },
  mounted() {
    this.loadPatients()
  },
  methods: {
    async loadPatients() {
      this.isLoading = true
      try {
        const resp = await api.getPatients({})
        this.allPatients = resp.data
      } finally {
        this.isLoading = false
      }
    },
    selectAllPatients() {
      this.selectedPatientIds = this.displayedPatients.map(p => p.id)
    },
    togglePanel(key) {
      this.expandedPanels[key] = !this.expandedPanels[key]
    },
    toggleField(modKey, fieldKey) {
      const k = `${modKey}|${fieldKey}`
      this.expandedFields[k] = !this.expandedFields[k]
    },
    isFieldExpanded(modKey, fieldKey) {
      return !!this.expandedFields[`${modKey}|${fieldKey}`]
    },
    activeFilterCount(modKey) {
      return Object.values(this.modalityFilters[modKey] || {}).filter(v => v && v.length > 0).length
    },
    selectAllFilter(modKey, fieldKey, options) {
      this.modalityFilters[modKey][fieldKey] = [...options]
    },
    clearFilter(modKey, fieldKey) {
      this.modalityFilters[modKey][fieldKey] = []
    },

    passesFilter(finding, filters) {
      for (const [fieldKey, selected] of Object.entries(filters)) {
        if (!selected || selected.length === 0) continue
        if (!selected.includes(finding[fieldKey])) return false
      }
      return true
    },

    collectFindings(patientFull, modDef) {
      const studies = patientFull[modDef.dataKey] || []
      const filters = this.modalityFilters[modDef.key] || {}
      const result = []
      studies.forEach(study => {
        const findings = study[modDef.findingsKey] || []
        findings.forEach(f => {
          if (this.passesFilter(f, filters)) {
            result.push({
              ...f,
              _studyId: study.id,
              _studyDate: study.exam_date || '',
              _studyStage: study.study_stage || '',
              _patientId: patientFull.id,
              _modKey: modDef.key,
              _modLabel: modDef.label
            })
          }
        })
      })
      return result
    },

    getSizeMax(f, m) {
      if (m.key === 'mrt_lu') return f.size_cortical_mm || null
      return f.size_max_mm || f.size_z_mm || null
    },
    getSizeMin(f, m) {
      if (m.key === 'mrt_lu') return f.size_cortical_mm || null
      return f.size_min_mm || f.size_x_mm || null
    },
    getVolume(f, m) {
      if (!m.hasVolume) return null
      return f.volume_mm3 || null
    },

    computeStats(findings, modDef) {
      const studyIds = new Set(findings.map(f => f._studyId))
      const patientIds = new Set(findings.map(f => f._patientId))
      const sides = {}, quadrants = {}, depths = {}, lymphGroups = {}
      const volumes = [], maxSizes = [], minSizes = []

      findings.forEach(f => {
        const side = f[modDef.sideField]; if (side) sides[side] = (sides[side] || 0) + 1
        if (modDef.quadrantField) { const q = f[modDef.quadrantField]; if (q) quadrants[q] = (quadrants[q] || 0) + 1 }
        if (modDef.depthField) { const d = f[modDef.depthField]; if (d) depths[d] = (depths[d] || 0) + 1 }
        if (modDef.lymphGroupField) { const lg = f[modDef.lymphGroupField]; if (lg) lymphGroups[lg] = (lymphGroups[lg] || 0) + 1 }
        const vol = this.getVolume(f, modDef); if (vol) volumes.push(vol)
        const sMax = this.getSizeMax(f, modDef); if (sMax) maxSizes.push(sMax)
        const sMin = this.getSizeMin(f, modDef); if (sMin) minSizes.push(sMin)
      })

      const sumVol = volumes.length > 0 ? volumes.reduce((a, b) => a + b, 0) : null
      return {
        studiesCount: studyIds.size, patientsCount: patientIds.size, findingsCount: findings.length,
        rightCount: sides['Правая МЖ'] || 0, leftCount: sides['Левая МЖ'] || 0,
        quadrants, depths, lymphGroups,
        sumVol, avgVol: sumVol !== null ? Math.round(sumVol / volumes.length) : null,
        minSize: minSizes.length > 0 ? Math.min(...minSizes) : null,
        maxSize: maxSizes.length > 0 ? Math.max(...maxSizes) : null
      }
    },

    async generateReport() {
      this.isGenerating = true
      try {
        const selectedPatients = []
        for (const pid of this.selectedPatientIds) {
          const resp = await api.getPatient(pid)
          selectedPatients.push(resp.data)
        }

        const selModDefs = MODALITIES.filter(m => this.selectedModalities.includes(m.key))

        const allData = selectedPatients.map(pFull => {
          const findings = {}
          selModDefs.forEach(m => { findings[m.key] = this.collectFindings(pFull, m) })
          return { patientFull: pFull, findings }
        })

        const wb = XLSX.utils.book_new()
        XLSX.utils.book_append_sheet(wb, this.buildSheet1(allData, selModDefs), 'Общая сводная статистика')
        XLSX.utils.book_append_sheet(wb, this.buildSheet2(allData, selModDefs), 'Свод по пациентам')
        XLSX.utils.book_append_sheet(wb, this.buildSheet3(allData, selModDefs), 'Детализация по пациентам')

        const date = new Date().toLocaleDateString('ru-RU').replace(/\./g, '_')
        XLSX.writeFile(wb, `Вариативный_отчёт_${date}.xlsx`)
      } catch (err) {
        alert('Ошибка генерации отчёта: ' + err.message)
        console.error(err)
      } finally {
        this.isGenerating = false
      }
    },

    buildSheet1(allData, selModDefs) {
      // Aggregate all findings per modality across all selected patients
      const modFindings = {}
      selModDefs.forEach(m => {
        modFindings[m.key] = []
        allData.forEach(d => modFindings[m.key].push(...d.findings[m.key]))
      })

      const headers = [
        'Метод', 'Кол-во исследований', 'Кол-во пациентов', 'Кол-во образований',
        'Правая МЖ', 'Левая МЖ',
        ...QUADRANT_LOCATIONS,
        ...LYMPH_NODE_GROUPS,
        ...DEPTH_LOCATIONS,
        'Суммарный объём (мм³)', 'Средний объём на 1 образование (мм³)',
        'Минимальный размер (мм)', 'Максимальный размер (мм)'
      ]

      const rows = [headers]
      const totals = {
        studiesCount: 0, patientsSet: new Set(), findingsCount: 0,
        rightCount: 0, leftCount: 0,
        quadrants: {}, lymphGroups: {}, depths: {},
        volumes: [], maxSizes: [], minSizes: []
      }

      selModDefs.forEach(m => {
        const findings = modFindings[m.key]
        const s = this.computeStats(findings, m)

        rows.push([
          m.label, s.studiesCount, s.patientsCount, s.findingsCount,
          s.rightCount, s.leftCount,
          ...QUADRANT_LOCATIONS.map(q => s.quadrants[q] || 0),
          ...LYMPH_NODE_GROUPS.map(g => s.lymphGroups[g] || 0),
          ...DEPTH_LOCATIONS.map(d => s.depths[d] || 0),
          s.sumVol !== null ? s.sumVol : NA,
          s.avgVol !== null ? s.avgVol : NA,
          s.minSize !== null ? s.minSize : NA,
          s.maxSize !== null ? s.maxSize : NA
        ])

        totals.studiesCount += s.studiesCount
        totals.findingsCount += s.findingsCount
        totals.rightCount += s.rightCount
        totals.leftCount += s.leftCount
        findings.forEach(f => {
          totals.patientsSet.add(f._patientId)
          QUADRANT_LOCATIONS.forEach(q => { if (f[m.quadrantField] === q) totals.quadrants[q] = (totals.quadrants[q] || 0) + 1 })
          LYMPH_NODE_GROUPS.forEach(g => { if (m.lymphGroupField && f[m.lymphGroupField] === g) totals.lymphGroups[g] = (totals.lymphGroups[g] || 0) + 1 })
          DEPTH_LOCATIONS.forEach(d => { if (m.depthField && f[m.depthField] === d) totals.depths[d] = (totals.depths[d] || 0) + 1 })
          const vol = this.getVolume(f, m); if (vol) totals.volumes.push(vol)
          const sMax = this.getSizeMax(f, m); if (sMax) totals.maxSizes.push(sMax)
          const sMin = this.getSizeMin(f, m); if (sMin) totals.minSizes.push(sMin)
        })
      })

      const tSumVol = totals.volumes.length > 0 ? totals.volumes.reduce((a, b) => a + b, 0) : null
      rows.push([
        'ИТОГО', totals.studiesCount, totals.patientsSet.size, totals.findingsCount,
        totals.rightCount, totals.leftCount,
        ...QUADRANT_LOCATIONS.map(q => totals.quadrants[q] || 0),
        ...LYMPH_NODE_GROUPS.map(g => totals.lymphGroups[g] || 0),
        ...DEPTH_LOCATIONS.map(d => totals.depths[d] || 0),
        tSumVol !== null ? tSumVol : NA,
        tSumVol !== null ? Math.round(tSumVol / totals.volumes.length) : NA,
        totals.minSizes.length > 0 ? Math.min(...totals.minSizes) : NA,
        totals.maxSizes.length > 0 ? Math.max(...totals.maxSizes) : NA
      ])

      const ws = XLSX.utils.aoa_to_sheet(rows)
      ws['!cols'] = headers.map((h, i) => ({ wch: i === 0 ? 28 : Math.max(h.length + 2, 8) }))
      return ws
    },

    buildSheet2(allData, selModDefs) {
      const passportHeaders = PATIENT_FIELDS
        .filter(f => this.selectedPatientFields.includes(f.key))
        .map(f => f.label)

      const modHeaders = []
      selModDefs.forEach(m => {
        modHeaders.push(
          `${m.label}: Кол-во исследований`, `${m.label}: Кол-во образований`,
          `${m.label}: Правая МЖ`, `${m.label}: Левая МЖ`,
          `${m.label}: Суммарный объём (мм³)`, `${m.label}: Средний объём (мм³)`,
          `${m.label}: Мин. размер (мм)`, `${m.label}: Макс. размер (мм)`
        )
      })

      const rows = [[...passportHeaders, ...modHeaders]]

      allData.forEach(({ patientFull, findings }) => {
        const passportCells = PATIENT_FIELDS
          .filter(f => this.selectedPatientFields.includes(f.key))
          .map(f => patientFull[f.key] !== null && patientFull[f.key] !== undefined ? patientFull[f.key] : NA)

        const modCells = []
        selModDefs.forEach(m => {
          const mF = findings[m.key]
          if (mF.length === 0) {
            modCells.push(NA, NA, NA, NA, NA, NA, NA, NA)
          } else {
            const s = this.computeStats(mF, m)
            modCells.push(
              s.studiesCount, s.findingsCount,
              s.rightCount, s.leftCount,
              s.sumVol !== null ? s.sumVol : NA,
              s.avgVol !== null ? s.avgVol : NA,
              s.minSize !== null ? s.minSize : NA,
              s.maxSize !== null ? s.maxSize : NA
            )
          }
        })

        rows.push([...passportCells, ...modCells])
      })

      const ws = XLSX.utils.aoa_to_sheet(rows)
      ws['!cols'] = rows[0].map(() => ({ wch: 22 }))
      return ws
    },

    buildSheet3(allData, selModDefs) {
      const passportHeaders = PATIENT_FIELDS
        .filter(f => this.selectedPatientFields.includes(f.key))
        .map(f => f.label)

      const commonHeaders = [
        'Метод', 'Дата исследования', 'Этап', 'Номер находки',
        'Сторона', 'Квадрант', 'Глубина', 'Группа ЛУ',
        'Размер X (мм)', 'Размер Y (мм)', 'Размер Z (мм)',
        'Объём (мм³)', 'Мин. размер (мм)', 'Макс. размер (мм)'
      ]

      // Build specific columns per modality and track offsets
      const specificHeaders = []
      const modSpecificOffset = {}
      selModDefs.forEach(m => {
        modSpecificOffset[m.key] = specificHeaders.length
        m.detailFields.forEach(f => specificHeaders.push(`${m.label}: ${f.label}`))
      })

      const header = [...passportHeaders, ...commonHeaders, ...specificHeaders]
      const rows = [header]

      allData.forEach(({ patientFull, findings }) => {
        const passportCells = PATIENT_FIELDS
          .filter(f => this.selectedPatientFields.includes(f.key))
          .map(f => patientFull[f.key] !== null && patientFull[f.key] !== undefined ? patientFull[f.key] : NA)

        selModDefs.forEach(m => {
          findings[m.key].forEach(f => {
            const commonCells = [
              m.label,
              f._studyDate || NA,
              f._studyStage || NA,
              f.finding_number || NA,
              f[m.sideField] || NA,
              (m.quadrantField && f[m.quadrantField]) ? f[m.quadrantField] : NA,
              (m.depthField && f[m.depthField]) ? f[m.depthField] : NA,
              (m.lymphGroupField && f[m.lymphGroupField]) ? f[m.lymphGroupField] : NA,
              f.size_x_mm || f.size_1_mm || NA,
              f.size_y_mm || f.size_2_mm || NA,
              f.size_z_mm || f.size_3_mm || NA,
              this.getVolume(f, m) || NA,
              this.getSizeMin(f, m) || NA,
              this.getSizeMax(f, m) || NA
            ]

            const specificCells = new Array(specificHeaders.length).fill(NA)
            const offset = modSpecificOffset[m.key]
            m.detailFields.forEach((df, i) => {
              const val = f[df.key]
              if (val !== null && val !== undefined && val !== '') specificCells[offset + i] = val
            })

            rows.push([...passportCells, ...commonCells, ...specificCells])
          })
        })
      })

      if (rows.length === 1) rows.push(new Array(header.length).fill('Нет данных по выбранным фильтрам'))

      const ws = XLSX.utils.aoa_to_sheet(rows)
      ws['!cols'] = header.map((h, i) => ({ wch: i < passportHeaders.length ? 20 : Math.max((String(h) || '').length + 2, 12) }))
      return ws
    }
  }
}
</script>

<style scoped>
.rb-overlay { background: rgba(0,0,0,0.5); display: flex; align-items: flex-start; justify-content: center; padding: 20px; overflow-y: auto; }
.rb-modal { background: #fff; border-radius: 8px; width: 100%; max-width: 860px; display: flex; flex-direction: column; max-height: 90vh; }
.rb-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid #e0e0e0; }
.rb-header h3 { margin: 0; font-size: 1.1rem; }
.rb-close { background: none; border: none; font-size: 1.4rem; cursor: pointer; color: #666; }
.rb-body { flex: 1; overflow-y: auto; padding: 16px 20px; display: flex; flex-direction: column; gap: 16px; }
.rb-section { border: 1px solid #e0e0e0; border-radius: 6px; padding: 14px; }
.rb-section-title { margin: 0 0 12px; font-size: 0.95rem; color: #333; }
.rb-row { display: flex; gap: 8px; align-items: center; margin-bottom: 10px; flex-wrap: wrap; }
.rb-search { flex: 1; min-width: 200px; }
.rb-patient-list { max-height: 180px; overflow-y: auto; border: 1px solid #e8e8e8; border-radius: 4px; padding: 6px; margin-bottom: 8px; }
.rb-patient-item { display: flex; align-items: center; gap: 6px; padding: 3px 0; cursor: pointer; font-size: 0.88rem; }
.rb-patient-item:hover { background: #f5f5f5; }
.rb-patient-item em { color: #888; }
.rb-count { font-size: 0.82rem; color: #555; margin-bottom: 12px; }
.rb-loading, .rb-empty { padding: 8px; color: #888; font-size: 0.85rem; }
.rb-subsection { border-top: 1px solid #eee; padding-top: 10px; margin-top: 4px; }
.rb-subsection-header { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; font-size: 0.88rem; }
.rb-checkboxes { display: flex; flex-wrap: wrap; gap: 6px 14px; }
.rb-cb-item { font-size: 0.85rem; display: flex; align-items: center; gap: 4px; }
.rb-modality-grid { display: flex; flex-wrap: wrap; gap: 6px 20px; margin-bottom: 12px; }
.rb-mod-item { font-size: 0.88rem; display: flex; align-items: center; gap: 5px; }
.rb-filter-panel { border: 1px solid #e0e0e0; border-radius: 4px; margin-bottom: 8px; }
.rb-fp-header { display: flex; align-items: center; gap: 8px; padding: 8px 12px; cursor: pointer; background: #f7f7f7; border-radius: 4px; font-size: 0.88rem; }
.rb-fp-header:hover { background: #efefef; }
.rb-fp-header strong { flex: 1; }
.rb-fp-body { padding: 10px 12px; }
.rb-ff { margin-bottom: 6px; border-bottom: 1px solid #f0f0f0; padding-bottom: 6px; }
.rb-ff:last-child { border-bottom: none; margin-bottom: 0; }
.rb-ff-header { display: flex; align-items: center; gap: 6px; cursor: pointer; padding: 4px 0; font-size: 0.85rem; }
.rb-ff-header:hover { color: #1976d2; }
.rb-ff-header span:first-child { flex: 1; }
.rb-ff-options { padding: 6px 0 0 8px; display: flex; flex-direction: column; gap: 3px; }
.rb-ff-actions { display: flex; gap: 6px; margin-bottom: 6px; }
.rb-opt { font-size: 0.82rem; display: flex; align-items: flex-start; gap: 5px; }
.rb-badge { background: #1976d2; color: #fff; border-radius: 10px; padding: 1px 7px; font-size: 0.75rem; }
.rb-badge-sm { background: #4caf50; color: #fff; border-radius: 10px; padding: 1px 6px; font-size: 0.72rem; }
.rb-chevron { margin-left: auto; font-size: 0.7rem; color: #777; }
.rb-chevron-sm { font-size: 0.7rem; color: #999; }
.rb-footer { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; border-top: 1px solid #e0e0e0; background: #fafafa; border-radius: 0 0 8px 8px; }
.rb-footer-btns { display: flex; gap: 10px; }
.rb-warn { color: #f57c00; font-size: 0.85rem; }
.rb-ok { color: #388e3c; font-size: 0.85rem; }
.btn-xs { padding: 2px 8px; font-size: 0.75rem; cursor: pointer; background: #f0f0f0; border: 1px solid #ccc; border-radius: 3px; }
.btn-xs:hover { background: #e0e0e0; }
</style>
