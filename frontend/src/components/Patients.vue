<template>
  <div class="patients">
    <div class="header">
      <h2>Пациенты</h2>
      <div class="header-actions">
        <button @click="exportLymphNodesReport" class="btn btn-success" :disabled="exporting">
          <span v-if="!exporting">📊 Экспорт отчёта по ЛУ</span>
          <span v-else>⏳ Экспорт...</span>
        </button>
        <button @click="exportFormationsReport" class="btn btn-info" :disabled="exporting">
          <span v-if="!exporting">📋 Экспорт отчёта по образованиям</span>
          <span v-else>⏳ Экспорт...</span>
        </button>
        <button @click="showReportBuilder = true" class="btn btn-warning">🔧 Вариативный отчёт</button>
        <button @click="showAddModal = true" class="btn btn-primary">Добавить пациента</button>
      </div>
    </div>

    <div class="filters">
      <input v-model="filters.last_name" @input="loadPatients" placeholder="Фамилия" class="input">
      <input v-model="filters.first_name" @input="loadPatients" placeholder="Имя" class="input">
      <input v-model="filters.snils" @input="loadPatients" placeholder="СНИЛС" class="input">
    </div>

    <table class="data-table">
      <thead>
        <tr>
          <th @click="setSort('id')" class="sortable">
            ID <span class="sort-icon">{{ sortIcon('id') }}</span>
          </th>
          <th @click="setSort('snils')" class="sortable">
            СНИЛС <span class="sort-icon">{{ sortIcon('snils') }}</span>
          </th>
          <th @click="setSort('last_name')" class="sortable">
            ФИО <span class="sort-icon">{{ sortIcon('last_name') }}</span>
          </th>
          <th @click="setSort('gender')" class="sortable">
            Пол <span class="sort-icon">{{ sortIcon('gender') }}</span>
          </th>
          <th @click="setSort('date_of_birth')" class="sortable">
            Дата рождения <span class="sort-icon">{{ sortIcon('date_of_birth') }}</span>
          </th>
          <th @click="setSort('diagnosis')" class="sortable">
            Диагноз <span class="sort-icon">{{ sortIcon('diagnosis') }}</span>
          </th>
          <th @click="setSort('last_updated')" class="sortable">
            Последнее обновление <span class="sort-icon">{{ sortIcon('last_updated') }}</span>
          </th>
          <th>Действия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="patient in sortedPatients" :key="patient.id">
          <td>{{ patient.id }}</td>
          <td>{{ patient.snils }}</td>
          <td>{{ patient.last_name }} {{ patient.first_name }} {{ patient.middle_name }}</td>
          <td>{{ patient.gender }}</td>
          <td>{{ patient.date_of_birth }}</td>
          <td>{{ patient.diagnosis }}</td>
          <td>{{ formatDateTime(patient.last_updated) }}</td>
          <td class="actions">
            <button @click="viewPatient(patient.id)" class="btn-sm btn-info">Просмотр</button>
            <button @click="editPatient(patient)" class="btn-sm btn-warning">Редактировать</button>
            <button @click="deletePatientConfirm(patient.id)" class="btn-sm btn-danger">Удалить</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="showAddModal || editingPatient" class="modal" @click.self="closeModal">
      <div class="modal-content">
        <h3>{{ editingPatient ? 'Редактировать пациента' : 'Добавить пациента' }}</h3>
        <form @submit.prevent="savePatient">
          <div class="form-group">
            <label>ID пациента *</label>
            <input v-model="form.id" required class="input" placeholder="Например: P001">
            <small v-if="editingPatient && form.id !== editingPatient" class="text-warning">
              ⚠️ ID будет изменён с «{{ editingPatient }}» на «{{ form.id }}»
            </small>
          </div>
          <div class="form-group">
            <label>СНИЛС</label>
            <input
              v-model="form.snils"
              class="input"
              placeholder="XXX-XXX-XXX XX"
              @input="formatSnils"
              @blur="validateSnils"
              :class="{ 'error': !snilsValid && snilsTouched }"
              maxlength="14"
            >
            <div v-if="!snilsValid && snilsTouched" class="error-message">
              Введите 11 цифр
            </div>
            <div v-if="snilsValid && snilsTouched" class="success-message">
              ✓ Корректный формат
            </div>
          </div>
          <div class="form-group">
            <label>Фамилия *</label>
            <input
              v-model="form.last_name"
              @input="form.last_name = form.last_name.replace(/[^А-Яа-яЁё\s-]/g, '')"
              class="input"
            >
          </div>
          <div class="form-group">
            <label>Имя *</label>
            <input
              v-model="form.first_name"
              @input="form.first_name = form.first_name.replace(/[^А-Яа-яЁё\s-]/g, '')"
              class="input"
            >
          </div>
          <div class="form-group">
            <label>Отчество</label>
            <input
              v-model="form.middle_name"
              @input="form.middle_name = form.middle_name.replace(/[^А-Яа-яЁё\s-]/g, '')"
              class="input"
            >
          </div>
          <div class="form-group">
            <label>Пол *</label>
            <select v-model="form.gender" required class="input">
              <option value="">Выберите</option>
              <option value="Мужской">Мужской</option>
              <option value="Женский">Женский</option>
            </select>
          </div>
          <div class="form-group">
            <label>Дата рождения *</label>
            <input
              v-model="form.date_of_birth"
              type="date"
              required
              class="input"
              :min="minDate"
              :max="maxDate"
            >
            <small class="text-muted">От 01.01.1900 до {{ formatDate(maxDate) }}</small>
          </div>
          <div class="form-group">
            <label>Диагноз</label>
            <textarea v-model="form.diagnosis" class="input" rows="3"></textarea>
          </div>
          <div class="form-group">
            <label>Стадия по TNM</label>
            <input v-model="form.tnm_stage" class="input" placeholder="Например: T2N1M0">
          </div>
          <div class="form-group">
            <label>Код МКБ</label>
            <input v-model="form.mkb_code" class="input" placeholder="">
          </div>
          <div class="form-group">
            <label>Комментарий</label>
            <textarea v-model="form.comment" class="input" rows="3"></textarea>
          </div>
          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">Отмена</button>
            <button type="submit" class="btn btn-primary">Сохранить</button>
          </div>
        </form>
      </div>
    </div>

    <ReportBuilderModal v-if="showReportBuilder" @close="showReportBuilder = false" />
  </div>
</template>

<script>
import api from '../api'
import * as XLSX from 'xlsx'
import ReportBuilderModal from './ReportBuilderModal.vue'

export default {
  components: { ReportBuilderModal },
  data() {
    return {
      patients: [],
      showReportBuilder: false,
      filters: {
        last_name: '',
        first_name: '',
        snils: ''
      },
      showAddModal: false,
      editingPatient: null,
      form: {
        id: '',
        snils: '',
        last_name: '',
        first_name: '',
        middle_name: '',
        gender: '',
        date_of_birth: '',
        diagnosis: '',
        tnm_stage: '',
        mkb_code: '',
        comment: ''
      },
      snilsValid: true,
      snilsTouched: false,
      maxDate: new Date().toISOString().split('T')[0],
      minDate: '1900-01-01',
      exporting: false,
      sortKey: '',
      sortDir: 1   // 1 = по возрастанию, -1 = по убыванию
    }
  },
  mounted() {
    this.loadPatients()
  },
  computed: {
    sortedPatients() {
      if (!this.sortKey) return this.patients

      return [...this.patients].sort((a, b) => {
        let valA = a[this.sortKey] ?? ''
        let valB = b[this.sortKey] ?? ''

        // Для дат сравниваем как строки ISO — они сортируются корректно
        // Для строк приводим к нижнему регистру
        if (typeof valA === 'string') valA = valA.toLowerCase()
        if (typeof valB === 'string') valB = valB.toLowerCase()

        if (valA < valB) return -1 * this.sortDir
        if (valA > valB) return 1 * this.sortDir
        return 0
      })
    }
  },
  methods: {
    setSort(key) {
      if (this.sortKey === key) {
        this.sortDir *= -1  // переключаем направление
      } else {
        this.sortKey = key
        this.sortDir = 1
      }
    },
    sortIcon(key) {
      if (this.sortKey !== key) return '⇅'
      return this.sortDir === 1 ? '↑' : '↓'
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('ru-RU');
    },
    async loadPatients() {
      try {
        const response = await api.getPatients(this.filters)
        this.patients = response.data
      } catch (error) {
        alert('Ошибка загрузки пациентов')
      }
    },
    viewPatient(id) {
      this.$router.push(`/patients/${id}`)
    },
    editPatient(patient) {
      this.editingPatient = patient.id
      this.form = {...patient}
      this.validateSnils()
    },
    async savePatient() {
      const validation = this.validateSnils()
      if (!validation.isValid) {
        this.snilsTouched = true
        alert('Пожалуйста, введите корректный СНИЛС (11 цифр)')
        return
      }

      try {
        const dataToSend = {
          ...this.form,
          snils: validation.clean
        }

        if (this.editingPatient) {
          const oldId = this.editingPatient  // сохраняем старый ID до закрытия модала
          await api.updatePatient(oldId, dataToSend)
        } else {
          await api.createPatient(dataToSend)
        }

        this.closeModal()
        this.loadPatients()
      } catch (error) {
        alert('Ошибка сохранения: ' + (error.response?.data?.detail || error.message))
      }
    },
    async deletePatientConfirm(id) {
      if (confirm('Удалить пациента и все связанные данные?')) {
        try {
          await api.deletePatient(id)
          this.loadPatients()
        } catch (error) {
          alert('Ошибка удаления')
        }
      }
    },
    closeModal() {
      this.showAddModal = false
      this.editingPatient = null
      this.form = {
        id: '',
        snils: '',
        last_name: '',
        first_name: '',
        middle_name: '',
        gender: '',
        date_of_birth: '',
        diagnosis: '',
        tnm_stage: '',
        mkb_code: '',
        comment: ''
      }
      this.snilsValid = true
      this.snilsTouched = false
    },
    formatDateTime(dt) {
      if (!dt) return ''
      return new Date(dt).toLocaleString('ru-RU')
    },
    formatSnils(event) {
      this.snilsTouched = true;
      let value = event.target.value.replace(/\D/g, '');
      value = value.substring(0, 11);

      let formatted = '';
      for (let i = 0; i < value.length; i++) {
        if (i === 3 || i === 6) {
          formatted += '-';
        } else if (i === 9) {
          formatted += ' ';
        }
        formatted += value[i];
      }

      this.form.snils = formatted;
      this.validateSnils();
    },
    validateSnils() {
      const cleanValue = this.form.snils.replace(/\D/g, '');
      this.snilsValid = /^\d{11}$/.test(cleanValue);

      return {
        formatted: this.form.snils,
        clean: cleanValue,
        isValid: this.snilsValid
      };
    },
    getCleanSnils() {
      return this.form.snils.replace(/\D/g, '');
    },

    async exportLymphNodesReport() {
      this.exporting = true;
      try {
        // Загружаем всех пациентов без фильтров
        const response = await api.getPatients({});
        const allPatients = response.data;

        if (allPatients.length === 0) {
          alert('Нет данных для экспорта');
          return;
        }

        // Собираем данные для всех пациентов
        const reportData = [];

        for (const patient of allPatients) {
          try {
            // Загружаем детальные данные пациента
            const detailResponse = await api.getPatient(patient.id);
            const patientData = detailResponse.data;

            // Обрабатываем УЗИ лимфоузлы
            if (patientData.ultrasounds && patientData.ultrasounds.length > 0) {
              patientData.ultrasounds.forEach((ultrasound, stageIdx) => {
                if (ultrasound.lymph_nodes && ultrasound.lymph_nodes.length > 0) {
                  ultrasound.lymph_nodes.forEach((ln, lnIdx) => {
                    reportData.push({
                      patientId: patient.id,
                      diagnosis: patient.diagnosis || '',
                      tnmStage: patient.tnm_stage || '',
                      mkbCode: patient.mkb_code || '',
                      studyStage: stageIdx + 1,
                      findingNumber: lnIdx + 1,
                      side: ln.side || '',
                      lymphNodeGroup: ln.lymph_node_group || '',
                      uziVolume: this.calculateVolume(ln.size_x_mm, ln.size_y_mm, ln.size_z_mm),
                      uziMinSize: ln.size_x_mm || '',
                      uziMaxSize: ln.size_z_mm || '',
                      mrtVolume: '',
                      mrtMinSize: '',
                      mrtMaxSize: '',
                      cytologyVolume: '',
                      cytologyMinSize: '',
                      cytologyMaxSize: '',
                      histologyVolume: '',
                      histologyMinSize: '',
                      histologyMaxSize: ''
                    });
                  });
                }
              });
            }

            // Обрабатываем МРТ лимфоузлы
            if (patientData.mrts && patientData.mrts.length > 0) {
              patientData.mrts.forEach((mrt, stageIdx) => {
                if (mrt.lymph_nodes && mrt.lymph_nodes.length > 0) {
                  mrt.lymph_nodes.forEach((ln, lnIdx) => {
                    reportData.push({
                      patientId: patient.id,
                      diagnosis: patient.diagnosis || '',
                      tnmStage: patient.tnm_stage || '',
                      mkbCode: patient.mkb_code || '',
                      studyStage: stageIdx + 1,
                      findingNumber: lnIdx + 1,
                      side: ln.side || '',
                      lymphNodeGroup: ln.lymph_node_group || '',
                      uziVolume: '',
                      uziMinSize: '',
                      uziMaxSize: '',
                      mrtVolume: this.calculateVolumeMRT(ln.size_cortical_mm),
                      mrtMinSize: ln.size_cortical_mm || '',
                      mrtMaxSize: ln.size_cortical_mm || '',
                      cytologyVolume: '',
                      cytologyMinSize: '',
                      cytologyMaxSize: '',
                      histologyVolume: '',
                      histologyMinSize: '',
                      histologyMaxSize: ''
                    });
                  });
                }
              });
            }

            // Обрабатываем Цитологию лимфоузлы
            if (patientData.cytology_biopsies && patientData.cytology_biopsies.length > 0) {
              patientData.cytology_biopsies.forEach((cytology, stageIdx) => {
                if (cytology.findings && cytology.findings.length > 0) {
                  cytology.findings.forEach((finding, lnIdx) => {
                    // Проверяем, что это находка ЛУ (lymph_node_group должна быть заполнена)
                    if (finding.lymph_node_group) {
                      reportData.push({
                        patientId: patient.id,
                        diagnosis: patient.diagnosis || '',
                        tnmStage: patient.tnm_stage || '',
                        mkbCode: patient.mkb_code || '',
                        studyStage: stageIdx + 1,
                        findingNumber: lnIdx + 1,
                        side: finding.affected_side || '',
                        lymphNodeGroup: finding.lymph_node_group || '',
                        uziVolume: '',
                        uziMinSize: '',
                        uziMaxSize: '',
                        mrtVolume: '',
                        mrtMinSize: '',
                        mrtMaxSize: '',
                        cytologyVolume: 'N/A', // Для цитологии объем обычно не измеряется
                        cytologyMinSize: 'N/A',
                        cytologyMaxSize: 'N/A',
                        histologyVolume: '',
                        histologyMinSize: '',
                        histologyMaxSize: ''
                      });
                    }
                  });
                }
              });
            }

          } catch (error) {
            console.error(`Ошибка загрузки данных пациента ${patient.id}:`, error);
          }
        }

        if (reportData.length === 0) {
          alert('Нет данных о лимфоузлах для экспорта');
          return;
        }

        // Создаем workbook
        const wb = XLSX.utils.book_new();

        // Создаем массив данных с мультииндексом
        const aoa = [];

        // Первая строка - основные заголовки (объединенные ячейки)
        const headerRow1 = [
          'ID Пациента',
          'Диагноз (клинический)',
          'Стадия по TNM',
          'Код МКБ',
          'Этап исследования',
          'Номер находки (биоматериала)',
          'Сторона',
          'Группа измененных ЛУ',
          'УЗИ ЛУ', '', '', // 3 колонки для УЗИ
          'МРТ ЛУ', '', '', // 3 колонки для МРТ
          'Цитология ЛУ', '', '', // 3 колонки для Цитологии
          'Гистология послеоперационная ЛУ', '', '' // 3 колонки для Гистологии
        ];

        // Вторая строка - подзаголовки
        const headerRow2 = [
          '', '', '', '', '', '', '', '', // Пустые для основных колонок
          'Объем поражения', 'Минимальный размер', 'Максимальный размер', // УЗИ
          'Объем поражения', 'Минимальный размер', 'Максимальный размер', // МРТ
          'Объем поражения', 'Минимальный размер', 'Максимальный размер', // Цитология
          'Объем поражения', 'Минимальный размер', 'Максимальный размер'  // Гистология
        ];

        aoa.push(headerRow1);
        aoa.push(headerRow2);

        // Добавляем данные
        reportData.forEach(row => {
          aoa.push([
            row.patientId,
            row.diagnosis,
            row.tnmStage,
            row.mkbCode,
            row.studyStage,
            row.findingNumber,
            row.side,
            row.lymphNodeGroup,
            row.uziVolume,
            row.uziMinSize,
            row.uziMaxSize,
            row.mrtVolume,
            row.mrtMinSize,
            row.mrtMaxSize,
            row.cytologyVolume,
            row.cytologyMinSize,
            row.cytologyMaxSize,
            row.histologyVolume,
            row.histologyMinSize,
            row.histologyMaxSize
          ]);
        });

        // Создаем worksheet из массива
        const ws = XLSX.utils.aoa_to_sheet(aoa);

        // Настраиваем объединение ячеек для мультииндекса
        const merges = [
          // Основные колонки (объединяем обе строки)
          { s: { r: 0, c: 0 }, e: { r: 1, c: 0 } }, // ID Пациента
          { s: { r: 0, c: 1 }, e: { r: 1, c: 1 } }, // Диагноз
          { s: { r: 0, c: 2 }, e: { r: 1, c: 2 } }, // Стадия по TNM
          { s: { r: 0, c: 3 }, e: { r: 1, c: 3 } }, // Код МКБ
          { s: { r: 0, c: 4 }, e: { r: 1, c: 4 } }, // Этап исследования
          { s: { r: 0, c: 5 }, e: { r: 1, c: 5 } }, // Номер находки
          { s: { r: 0, c: 6 }, e: { r: 1, c: 6 } }, // Сторона
          { s: { r: 0, c: 7 }, e: { r: 1, c: 7 } }, // Группа ЛУ

          // Объединяем заголовки для групп колонок
          { s: { r: 0, c: 8 }, e: { r: 0, c: 10 } },  // УЗИ ЛУ
          { s: { r: 0, c: 11 }, e: { r: 0, c: 13 } }, // МРТ ЛУ
          { s: { r: 0, c: 14 }, e: { r: 0, c: 16 } }, // Цитология ЛУ
          { s: { r: 0, c: 17 }, e: { r: 0, c: 19 } }  // Гистология
        ];

        ws['!merges'] = merges;

        // Устанавливаем ширину колонок
        const colWidths = [
          { wch: 15 }, // ID Пациента
          { wch: 30 }, // Диагноз
          { wch: 15 }, // Стадия по TNM
          { wch: 15 }, // Код МКБ
          { wch: 12 }, // Этап исследования
          { wch: 15 }, // Номер находки
          { wch: 15 }, // Сторона
          { wch: 30 }, // Группа ЛУ
          { wch: 18 }, // УЗИ объем
          { wch: 18 }, // УЗИ мин
          { wch: 18 }, // УЗИ макс
          { wch: 18 }, // МРТ объем
          { wch: 18 }, // МРТ мин
          { wch: 18 }, // МРТ макс
          { wch: 18 }, // Цитология объем
          { wch: 18 }, // Цитология мин
          { wch: 18 }, // Цитология макс
          { wch: 18 }, // Гистология объем
          { wch: 18 }, // Гистология мин
          { wch: 18 }  // Гистология макс
        ];
        ws['!cols'] = colWidths;

        // Применяем стили к заголовкам (делаем их жирными и с фоном)
        const range = XLSX.utils.decode_range(ws['!ref']);
        for (let C = range.s.c; C <= range.e.c; ++C) {
          // Первая строка заголовков
          const addr1 = XLSX.utils.encode_cell({ r: 0, c: C });
          if (!ws[addr1]) continue;
          if (!ws[addr1].s) ws[addr1].s = {};
          ws[addr1].s = {
            font: { bold: true },
            fill: { fgColor: { rgb: "4472C4" } },
            alignment: { horizontal: "center", vertical: "center" }
          };

          // Вторая строка заголовков
          const addr2 = XLSX.utils.encode_cell({ r: 1, c: C });
          if (!ws[addr2]) continue;
          if (!ws[addr2].s) ws[addr2].s = {};
          ws[addr2].s = {
            font: { bold: true },
            fill: { fgColor: { rgb: "B4C7E7" } },
            alignment: { horizontal: "center", vertical: "center" }
          };
        }

        XLSX.utils.book_append_sheet(wb, ws, 'Отчёт по ЛУ');

        // Сохраняем файл
        const fileName = `Отчет_по_ЛУ_${new Date().toISOString().split('T')[0]}.xlsx`;
        XLSX.writeFile(wb, fileName);

        alert(`Экспорт завершён! Выгружено записей: ${reportData.length}`);
      } catch (error) {
        console.error('Ошибка экспорта:', error);
        alert('Ошибка при экспорте данных: ' + error.message);
      } finally {
        this.exporting = false;
      }
    },

    calculateVolume(x, y, z) {
      if (!x || !y || !z) return '';
      // Простая формула объема эллипсоида: (4/3) * π * (x/2) * (y/2) * (z/2)
      const volume = (4/3) * Math.PI * (x/2) * (y/2) * (z/2);
      return Math.round(volume);
    },

    calculateVolumeMRT(cortical) {
      if (!cortical) return '';
      // Для МРТ используем упрощенную формулу
      return Math.round(cortical * cortical * cortical * 0.5);
    },

    async exportFormationsReport() {
      this.exporting = true;
      try {
        // Загружаем всех пациентов без фильтров
        const response = await api.getPatients({});
        const allPatients = response.data;

        if (allPatients.length === 0) {
          alert('Нет данных для экспорта');
          return;
        }

        // Собираем данные для всех пациентов
        const reportData = [];

        for (const patient of allPatients) {
          try {
            // Загружаем детальные данные пациента
            const detailResponse = await api.getPatient(patient.id);
            const patientData = detailResponse.data;

            // Обрабатываем Маммографию
            if (patientData.mammographies && patientData.mammographies.length > 0) {
              patientData.mammographies.forEach((mammo, stageIdx) => {
                if (mammo.findings && mammo.findings.length > 0) {
                  mammo.findings.forEach((finding, findingIdx) => {
                    reportData.push({
                      patientId: patient.id,
                      diagnosis: patient.diagnosis || '',
                      tnmStage: patient.tnm_stage || '',
                      mkbCode: patient.mkb_code || '',
                      studyStage: stageIdx + 1,
                      findingNumber: findingIdx + 1,
                      side: finding.affected_side || '',
                      quadrantLocation: finding.quadrant_location || '',
                      depthLocation: finding.depth_location || '',
                      mammoVolume: finding.volume_mm3 || this.calculateVolume(finding.size_x_mm, finding.size_y_mm, finding.size_z_mm),
                      mammoMinSize: finding.size_min_mm || finding.size_x_mm || '',
                      mammoMaxSize: finding.size_max_mm || finding.size_z_mm || '',
                      uziVolume: '',
                      uziMinSize: '',
                      uziMaxSize: '',
                      cmVolume: '',
                      cmMinSize: '',
                      cmMaxSize: '',
                      mrtVolume: '',
                      mrtMinSize: '',
                      mrtMaxSize: '',
                      histologyBiopsyVolume: '',
                      histologyBiopsyMinSize: '',
                      histologyBiopsyMaxSize: '',
                      cytologyVolume: '',
                      cytologyMinSize: '',
                      cytologyMaxSize: '',
                      histologyPostopVolume: '',
                      histologyPostopMinSize: '',
                      histologyPostopMaxSize: ''
                    });
                  });
                }
              });
            }

            // Обрабатываем УЗИ МЖ
            if (patientData.ultrasounds && patientData.ultrasounds.length > 0) {
              patientData.ultrasounds.forEach((uzi, stageIdx) => {
                if (uzi.findings && uzi.findings.length > 0) {
                  uzi.findings.forEach((finding, findingIdx) => {
                    reportData.push({
                      patientId: patient.id,
                      diagnosis: patient.diagnosis || '',
                      tnmStage: patient.tnm_stage || '',
                      mkbCode: patient.mkb_code || '',
                      studyStage: stageIdx + 1,
                      findingNumber: findingIdx + 1,
                      side: finding.side || '',
                      quadrantLocation: finding.quadrant_location || '',
                      depthLocation: finding.depth_location || '',
                      mammoVolume: '',
                      mammoMinSize: '',
                      mammoMaxSize: '',
                      uziVolume: finding.volume_mm3 || this.calculateVolume(finding.size_x_mm, finding.size_y_mm, finding.size_z_mm),
                      uziMinSize: finding.size_min_mm || finding.size_x_mm || '',
                      uziMaxSize: finding.size_max_mm || finding.size_z_mm || '',
                      cmVolume: '',
                      cmMinSize: '',
                      cmMaxSize: '',
                      mrtVolume: '',
                      mrtMinSize: '',
                      mrtMaxSize: '',
                      histologyBiopsyVolume: '',
                      histologyBiopsyMinSize: '',
                      histologyBiopsyMaxSize: '',
                      cytologyVolume: '',
                      cytologyMinSize: '',
                      cytologyMaxSize: '',
                      histologyPostopVolume: '',
                      histologyPostopMinSize: '',
                      histologyPostopMaxSize: ''
                    });
                  });
                }
              });
            }

            // Обрабатываем Контрастную маммографию (КМ)
            if (patientData.contrast_mammographies && patientData.contrast_mammographies.length > 0) {
              patientData.contrast_mammographies.forEach((cm, stageIdx) => {
                // LE findings (Low Energy)
                if (cm.le_findings && cm.le_findings.length > 0) {
                  cm.le_findings.forEach((finding, findingIdx) => {
                    reportData.push({
                      patientId: patient.id,
                      diagnosis: patient.diagnosis || '',
                      tnmStage: patient.tnm_stage || '',
                      mkbCode: patient.mkb_code || '',
                      studyStage: stageIdx + 1,
                      findingNumber: findingIdx + 1,
                      side: 'LE', // Low Energy
                      quadrantLocation: finding.quadrant_location || '',
                      depthLocation: finding.depth_location || '',
                      mammoVolume: '',
                      mammoMinSize: '',
                      mammoMaxSize: '',
                      uziVolume: '',
                      uziMinSize: '',
                      uziMaxSize: '',
                      cmVolume: finding.volume_mm3 || this.calculateVolume(finding.size_x_mm, finding.size_y_mm, finding.size_z_mm),
                      cmMinSize: finding.size_min_mm || finding.size_x_mm || '',
                      cmMaxSize: finding.size_max_mm || finding.size_z_mm || '',
                      mrtVolume: '',
                      mrtMinSize: '',
                      mrtMaxSize: '',
                      histologyBiopsyVolume: '',
                      histologyBiopsyMinSize: '',
                      histologyBiopsyMaxSize: '',
                      cytologyVolume: '',
                      cytologyMinSize: '',
                      cytologyMaxSize: '',
                      histologyPostopVolume: '',
                      histologyPostopMinSize: '',
                      histologyPostopMaxSize: ''
                    });
                  });
                }

                // RC findings (Recombined/Contrast)
                if (cm.rc_findings && cm.rc_findings.length > 0) {
                  cm.rc_findings.forEach((finding, findingIdx) => {
                    reportData.push({
                      patientId: patient.id,
                      diagnosis: patient.diagnosis || '',
                      tnmStage: patient.tnm_stage || '',
                      mkbCode: patient.mkb_code || '',
                      studyStage: stageIdx + 1,
                      findingNumber: findingIdx + 1,
                      side: 'RC', // Recombined
                      quadrantLocation: finding.quadrant_location || '',
                      depthLocation: finding.depth_location || '',
                      mammoVolume: '',
                      mammoMinSize: '',
                      mammoMaxSize: '',
                      uziVolume: '',
                      uziMinSize: '',
                      uziMaxSize: '',
                      cmVolume: finding.volume_mm3 || this.calculateVolume(finding.size_x_mm, finding.size_y_mm, finding.size_z_mm),
                      cmMinSize: finding.size_min_mm || finding.size_x_mm || '',
                      cmMaxSize: finding.size_max_mm || finding.size_z_mm || '',
                      mrtVolume: '',
                      mrtMinSize: '',
                      mrtMaxSize: '',
                      histologyBiopsyVolume: '',
                      histologyBiopsyMinSize: '',
                      histologyBiopsyMaxSize: '',
                      cytologyVolume: '',
                      cytologyMinSize: '',
                      cytologyMaxSize: '',
                      histologyPostopVolume: '',
                      histologyPostopMinSize: '',
                      histologyPostopMaxSize: ''
                    });
                  });
                }
              });
            }

            // Обрабатываем МРТ МЖ
            if (patientData.mrts && patientData.mrts.length > 0) {
              patientData.mrts.forEach((mrt, stageIdx) => {
                if (mrt.findings && mrt.findings.length > 0) {
                  mrt.findings.forEach((finding, findingIdx) => {
                    reportData.push({
                      patientId: patient.id,
                      diagnosis: patient.diagnosis || '',
                      tnmStage: patient.tnm_stage || '',
                      mkbCode: patient.mkb_code || '',
                      studyStage: stageIdx + 1,
                      findingNumber: findingIdx + 1,
                      side: finding.side || '',
                      quadrantLocation: finding.quadrant_location || '',
                      depthLocation: finding.depth_location || '',
                      mammoVolume: '',
                      mammoMinSize: '',
                      mammoMaxSize: '',
                      uziVolume: '',
                      uziMinSize: '',
                      uziMaxSize: '',
                      cmVolume: '',
                      cmMinSize: '',
                      cmMaxSize: '',
                      mrtVolume: finding.volume_mm3 || this.calculateVolume(finding.size_x_mm, finding.size_y_mm, finding.size_z_mm),
                      mrtMinSize: finding.size_min_mm || finding.size_x_mm || '',
                      mrtMaxSize: finding.size_max_mm || finding.size_z_mm || '',
                      histologyBiopsyVolume: '',
                      histologyBiopsyMinSize: '',
                      histologyBiopsyMaxSize: '',
                      cytologyVolume: '',
                      cytologyMinSize: '',
                      cytologyMaxSize: '',
                      histologyPostopVolume: '',
                      histologyPostopMinSize: '',
                      histologyPostopMaxSize: ''
                    });
                  });
                }
              });
            }

            // Обрабатываем Гистологию биопсии
            if (patientData.histology_biopsies && patientData.histology_biopsies.length > 0) {
              patientData.histology_biopsies.forEach((histology, stageIdx) => {
                if (histology.findings && histology.findings.length > 0) {
                  histology.findings.forEach((finding, findingIdx) => {
                    reportData.push({
                      patientId: patient.id,
                      diagnosis: patient.diagnosis || '',
                      tnmStage: patient.tnm_stage || '',
                      mkbCode: patient.mkb_code || '',
                      studyStage: stageIdx + 1,
                      findingNumber: findingIdx + 1,
                      side: finding.affected_side || '',
                      quadrantLocation: finding.quadrant_location || '',
                      depthLocation: finding.depth_location || '',
                      mammoVolume: '',
                      mammoMinSize: '',
                      mammoMaxSize: '',
                      uziVolume: '',
                      uziMinSize: '',
                      uziMaxSize: '',
                      cmVolume: '',
                      cmMinSize: '',
                      cmMaxSize: '',
                      mrtVolume: '',
                      mrtMinSize: '',
                      mrtMaxSize: '',
                      histologyBiopsyVolume: 'N/A', // Гистология обычно не содержит размеры
                      histologyBiopsyMinSize: 'N/A',
                      histologyBiopsyMaxSize: 'N/A',
                      cytologyVolume: '',
                      cytologyMinSize: '',
                      cytologyMaxSize: '',
                      histologyPostopVolume: '',
                      histologyPostopMinSize: '',
                      histologyPostopMaxSize: ''
                    });
                  });
                }
              });
            }

            // Обрабатываем Цитологию
            if (patientData.cytology_biopsies && patientData.cytology_biopsies.length > 0) {
              patientData.cytology_biopsies.forEach((cytology, stageIdx) => {
                if (cytology.findings && cytology.findings.length > 0) {
                  cytology.findings.forEach((finding, findingIdx) => {
                    // Проверяем, что это находка молочной железы (не ЛУ)
                    if (finding.cytology_body_part && finding.cytology_body_part.includes('МЖ')) {
                      reportData.push({
                        patientId: patient.id,
                        diagnosis: patient.diagnosis || '',
                        tnmStage: patient.tnm_stage || '',
                        mkbCode: patient.mkb_code || '',
                        studyStage: stageIdx + 1,
                        findingNumber: findingIdx + 1,
                        side: finding.affected_side || '',
                        quadrantLocation: finding.quadrant_location || '',
                        depthLocation: finding.depth_location || '',
                        mammoVolume: '',
                        mammoMinSize: '',
                        mammoMaxSize: '',
                        uziVolume: '',
                        uziMinSize: '',
                        uziMaxSize: '',
                        cmVolume: '',
                        cmMinSize: '',
                        cmMaxSize: '',
                        mrtVolume: '',
                        mrtMinSize: '',
                        mrtMaxSize: '',
                        histologyBiopsyVolume: '',
                        histologyBiopsyMinSize: '',
                        histologyBiopsyMaxSize: '',
                        cytologyVolume: 'N/A', // Цитология обычно не содержит размеры
                        cytologyMinSize: 'N/A',
                        cytologyMaxSize: 'N/A',
                        histologyPostopVolume: '',
                        histologyPostopMinSize: '',
                        histologyPostopMaxSize: ''
                      });
                    }
                  });
                }
              });
            }

            // Обрабатываем Гистологию послеоперационную
            if (patientData.histology_postops && patientData.histology_postops.length > 0) {
              patientData.histology_postops.forEach((histology, stageIdx) => {
                // Для послеоперационной гистологии может не быть структурированных находок
                // но мы можем добавить запись если есть данные
                if (histology.findings || histology.ihc_results) {
                  reportData.push({
                    patientId: patient.id,
                    diagnosis: patient.diagnosis || '',
                    tnmStage: patient.tnm_stage || '',
                    mkbCode: patient.mkb_code || '',
                    studyStage: stageIdx + 1,
                    findingNumber: 1,
                    side: '',
                    quadrantLocation: '',
                    depthLocation: '',
                    mammoVolume: '',
                    mammoMinSize: '',
                    mammoMaxSize: '',
                    uziVolume: '',
                    uziMinSize: '',
                    uziMaxSize: '',
                    cmVolume: '',
                    cmMinSize: '',
                    cmMaxSize: '',
                    mrtVolume: '',
                    mrtMinSize: '',
                    mrtMaxSize: '',
                    histologyBiopsyVolume: '',
                    histologyBiopsyMinSize: '',
                    histologyBiopsyMaxSize: '',
                    cytologyVolume: '',
                    cytologyMinSize: '',
                    cytologyMaxSize: '',
                    histologyPostopVolume: 'N/A', // Послеоперационная гистология - размеры из операции
                    histologyPostopMinSize: 'N/A',
                    histologyPostopMaxSize: 'N/A'
                  });
                }
              });
            }

          } catch (error) {
            console.error(`Ошибка загрузки данных пациента ${patient.id}:`, error);
          }
        }

        if (reportData.length === 0) {
          alert('Нет данных об образованиях для экспорта');
          return;
        }

        // Создаем workbook
        const wb = XLSX.utils.book_new();

        // Создаем массив данных с мультииндексом
        const aoa = [];

        // Первая строка - основные заголовки (объединенные ячейки)
        const headerRow1 = [
          'ID Пациента',
          'Диагноз (клинический)',
          'Стадия по TNM',
          'Код МКБ',
          'Этап исследования',
          'Номер находки (биоматериала)',
          'Сторона',
          'Локализация находки по квадрантам',
          'Локализация находки по глубине МЖ',
          'Маммография', '', '', // 3 колонки
          'УЗИ МЖ', '', '', // 3 колонки
          'КМ', '', '', // 3 колонки
          'МРТ МЖ', '', '', // 3 колонки
          'Гистология биопсии', '', '', // 3 колонки
          'Цитология', '', '', // 3 колонки
          'Гистология послеоперационная МЖ', '', '' // 3 колонки
        ];

        // Вторая строка - подзаголовки
        const headerRow2 = [
          '', '', '', '', '', '', '', '', '', // Пустые для основных колонок
          'Объем поражения', 'Минимальный размер', 'Максимальный размер', // Маммография
          'Объем поражения', 'Минимальный размер', 'Максимальный размер', // УЗИ МЖ
          'Объем поражения', 'Минимальный размер', 'Максимальный размер', // КМ
          'Объем поражения', 'Минимальный размер', 'Максимальный размер', // МРТ МЖ
          'Объем поражения', 'Минимальный размер', 'Максимальный размер', // Гистология биопсии
          'Объем поражения', 'Минимальный размер', 'Максимальный размер', // Цитология
          'Объем поражения', 'Минимальный размер', 'Максимальный размер'  // Гистология послеоп
        ];

        aoa.push(headerRow1);
        aoa.push(headerRow2);

        // Добавляем данные
        reportData.forEach(row => {
          aoa.push([
            row.patientId,
            row.diagnosis,
            row.tnmStage,
            row.mkbCode,
            row.studyStage,
            row.findingNumber,
            row.side,
            row.quadrantLocation,
            row.depthLocation,
            row.mammoVolume,
            row.mammoMinSize,
            row.mammoMaxSize,
            row.uziVolume,
            row.uziMinSize,
            row.uziMaxSize,
            row.cmVolume,
            row.cmMinSize,
            row.cmMaxSize,
            row.mrtVolume,
            row.mrtMinSize,
            row.mrtMaxSize,
            row.histologyBiopsyVolume,
            row.histologyBiopsyMinSize,
            row.histologyBiopsyMaxSize,
            row.cytologyVolume,
            row.cytologyMinSize,
            row.cytologyMaxSize,
            row.histologyPostopVolume,
            row.histologyPostopMinSize,
            row.histologyPostopMaxSize
          ]);
        });

        // Создаем worksheet из массива
        const ws = XLSX.utils.aoa_to_sheet(aoa);

        // Настраиваем объединение ячеек для мультииндекса
        const merges = [
          // Основные колонки (объединяем обе строки)
          { s: { r: 0, c: 0 }, e: { r: 1, c: 0 } }, // ID Пациента
          { s: { r: 0, c: 1 }, e: { r: 1, c: 1 } }, // Диагноз
          { s: { r: 0, c: 2 }, e: { r: 1, c: 2 } }, // Стадия по TNM
          { s: { r: 0, c: 3 }, e: { r: 1, c: 3 } }, // Код МКБ
          { s: { r: 0, c: 4 }, e: { r: 1, c: 4 } }, // Этап исследования
          { s: { r: 0, c: 5 }, e: { r: 1, c: 5 } }, // Номер находки
          { s: { r: 0, c: 6 }, e: { r: 1, c: 6 } }, // Сторона
          { s: { r: 0, c: 7 }, e: { r: 1, c: 7 } }, // Локализация по квадрантам
          { s: { r: 0, c: 8 }, e: { r: 1, c: 8 } }, // Локализация по глубине

          // Объединяем заголовки для групп колонок
          { s: { r: 0, c: 9 }, e: { r: 0, c: 11 } },   // Маммография
          { s: { r: 0, c: 12 }, e: { r: 0, c: 14 } },  // УЗИ МЖ
          { s: { r: 0, c: 15 }, e: { r: 0, c: 17 } },  // КМ
          { s: { r: 0, c: 18 }, e: { r: 0, c: 20 } },  // МРТ МЖ
          { s: { r: 0, c: 21 }, e: { r: 0, c: 23 } },  // Гистология биопсии
          { s: { r: 0, c: 24 }, e: { r: 0, c: 26 } },  // Цитология
          { s: { r: 0, c: 27 }, e: { r: 0, c: 29 } }   // Гистология послеоп
        ];

        ws['!merges'] = merges;

        // Устанавливаем ширину колонок
        const colWidths = [
          { wch: 15 }, // ID Пациента
          { wch: 30 }, // Диагноз
          { wch: 15 }, // Стадия по TNM
          { wch: 15 }, // Код МКБ
          { wch: 12 }, // Этап исследования
          { wch: 15 }, // Номер находки
          { wch: 15 }, // Сторона
          { wch: 30 }, // Локализация квадранты
          { wch: 30 }, // Локализация глубина
          { wch: 18 }, // Маммография объем
          { wch: 18 }, // Маммография мин
          { wch: 18 }, // Маммография макс
          { wch: 18 }, // УЗИ объем
          { wch: 18 }, // УЗИ мин
          { wch: 18 }, // УЗИ макс
          { wch: 18 }, // КМ объем
          { wch: 18 }, // КМ мин
          { wch: 18 }, // КМ макс
          { wch: 18 }, // МРТ объем
          { wch: 18 }, // МРТ мин
          { wch: 18 }, // МРТ макс
          { wch: 18 }, // Гистология биопсии объем
          { wch: 18 }, // Гистология биопсии мин
          { wch: 18 }, // Гистология биопсии макс
          { wch: 18 }, // Цитология объем
          { wch: 18 }, // Цитология мин
          { wch: 18 }, // Цитология макс
          { wch: 18 }, // Гистология послеоп объем
          { wch: 18 }, // Гистология послеоп мин
          { wch: 18 }  // Гистология послеоп макс
        ];
        ws['!cols'] = colWidths;

        // Применяем стили к заголовкам
        const range = XLSX.utils.decode_range(ws['!ref']);
        for (let C = range.s.c; C <= range.e.c; ++C) {
          // Первая строка заголовков
          const addr1 = XLSX.utils.encode_cell({ r: 0, c: C });
          if (!ws[addr1]) continue;
          if (!ws[addr1].s) ws[addr1].s = {};
          ws[addr1].s = {
            font: { bold: true },
            fill: { fgColor: { rgb: "70AD47" } },
            alignment: { horizontal: "center", vertical: "center" }
          };

          // Вторая строка заголовков
          const addr2 = XLSX.utils.encode_cell({ r: 1, c: C });
          if (!ws[addr2]) continue;
          if (!ws[addr2].s) ws[addr2].s = {};
          ws[addr2].s = {
            font: { bold: true },
            fill: { fgColor: { rgb: "A9D08E" } },
            alignment: { horizontal: "center", vertical: "center" }
          };
        }

        XLSX.utils.book_append_sheet(wb, ws, 'Отчёт по образованиям');

        // Сохраняем файл
        const fileName = `Отчет_по_образованиям_${new Date().toISOString().split('T')[0]}.xlsx`;
        XLSX.writeFile(wb, fileName);

        alert(`Экспорт завершён! Выгружено записей: ${reportData.length}`);
      } catch (error) {
        console.error('Ошибка экспорта:', error);
        alert('Ошибка при экспорте данных: ' + error.message);
      } finally {
        this.exporting = false;
      }
    }
  }
}
</script>

<style scoped>
.patients {
  padding: 1rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
}

.data-table th {
  background: #f8f9fa;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #495057;
}

.data-table td {
  padding: 1rem;
  border-top: 1px solid #dee2e6;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5568d3;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #218838;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}

.btn-sm {
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
}

.btn-info {
  background: #17a2b8;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
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

.input {
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  width: 100%;
}

.input.error {
  border-color: #ff3860;
  box-shadow: 0 0 0 0.125em rgba(255, 56, 96, 0.25);
}

.error-message {
  color: #ff3860;
  font-size: 12px;
  margin-top: 4px;
}

.success-message {
  color: #23d160;
  font-size: 12px;
  margin-top: 4px;
}

.text-muted {
  color: #6c757d;
  font-size: 0.875rem;
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

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.text-warning {
  color: #e67e00;
  font-size: 0.8rem;
  display: block;
  margin-top: 4px;
}

.sortable {
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}

.sortable:hover {
  background: #e9ecef;
}

.sort-icon {
  font-size: 0.8rem;
  color: #6c757d;
  margin-left: 4px;
}
</style>