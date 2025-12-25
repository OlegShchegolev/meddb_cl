<template>
  <div class="patient-detail" v-if="patient">
    <div class="header">
      <button @click="$router.back()" class="btn btn-secondary">← Назад</button>
      <h2>{{ patient.last_name }} {{ patient.first_name }} {{ patient.middle_name }}</h2>
    </div>

    <div class="patient-info card">
      <h3>Паспорт пациента</h3>
      <div class="info-grid">
        <div><strong>ID:</strong> {{ patient.id }}</div>
        <div><strong>СНИЛС:</strong> {{ patient.snils }}</div>
        <div><strong>Дата рождения:</strong> {{ patient.date_of_birth }}</div>
        <div><strong>Пол:</strong> {{ patient.gender }}</div>
        <div><strong>Диагноз:</strong> {{ patient.diagnosis }}</div>
        <div><strong>Стадия по TNM:</strong> {{ patient.tnm_stage }}</div>
        <div><strong>Код МКБ:</strong> {{ patient.mkb_code }}</div>
        <div><strong>Последнее обновление:</strong> {{ formatDateTime(patient.last_updated) }}</div>
      </div>
      <div v-if="patient.comment" style="margin-top: 1rem">
        <strong>Комментарий:</strong> {{ patient.comment }}
      </div>
    </div>

    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="['tab-btn', {active: activeTab === tab.id}]"
      >
        {{ tab.label }}
      </button>
    </div>

    <div class="tab-content">
      <!-- УЗИ -->
      <div v-if="activeTab === 'ultrasound'" class="section">
        <div class="section-header">
          <h3>УЗИ исследования</h3>
          <button @click="showUltrasoundModal = true" class="btn btn-primary btn-sm">Добавить</button>
        </div>
        <table class="data-table" v-if="patient.ultrasounds.length">
          <thead>
            <tr>
              <th>Дата</th>
              <th>Этап</th>
              <th>BI-RADS справа</th>
              <th>BI-RADS слева</th>
              <th>Находки</th>
              <th>Лимфоузлы</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in patient.ultrasounds" :key="item.id">
              <td>{{ item.exam_date }}</td>
              <td>{{ item.study_stage }}</td>
              <td>{{ item.birads_right }}</td>
              <td>{{ item.birads_left }}</td>
              <td>{{ item.findings?.length || 0 }}</td>
              <td>{{ item.lymph_nodes?.length || 0 }}</td>
              <td>
                <button @click="viewUltrasoundDetails(item)" class="btn-sm btn-info">Подробно</button>
                <button @click="editUltrasound(item)" class="btn-sm btn-warning">Редактировать</button>
                <button @click="deleteUltrasound(item.id)" class="btn-sm btn-danger">Удалить</button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data">Нет данных</p>
      </div>

      <!-- Маммография -->
      <div v-if="activeTab === 'mammography'" class="section">
        <div class="section-header">
          <h3>Маммография</h3>
          <button @click="showMammoModal = true" class="btn btn-primary btn-sm">Добавить</button>
        </div>
        <table class="data-table" v-if="patient.mammographies.length">
          <thead>
            <tr>
              <th>Дата</th>
              <th>Этап</th>
              <th>Сторона</th>
              <th>BI-RADS</th>
              <th>ACR</th>
              <th>Находки</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in patient.mammographies" :key="item.id">
              <td>{{ item.exam_date }}</td>
              <td>{{ item.study_stage }}</td>
              <td>{{ item.affected_side }}</td>
              <td>{{ item.birads_category }}</td>
              <td>{{ item.acr_density }}</td>
              <td>{{ item.findings?.length || 0 }}</td>
              <td>
                <button @click="viewMammoFindings(item)" class="btn-sm btn-info">Находки</button>
                <button @click="editMammo(item)" class="btn-sm btn-warning">Редактировать</button>
                <button @click="deleteMammo(item.id)" class="btn-sm btn-danger">Удалить</button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data">Нет данных</p>
      </div>

      <!-- Контрастная маммография -->
      <div v-if="activeTab === 'contrast'" class="section">
        <div class="section-header">
          <h3>Контрастная маммография</h3>
          <button @click="showContrastModal = true" class="btn btn-primary btn-sm">Добавить</button>
        </div>
        <table class="data-table" v-if="patient.contrast_mammographies.length">
          <thead>
            <tr>
              <th>Дата</th>
              <th>Этап</th>
              <th>Сторона</th>
              <th>BI-RADS</th>
              <th>ACR</th>
              <th>BPE</th>
              <th>Находки LE</th>
              <th>Находки RC</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in patient.contrast_mammographies" :key="item.id">
              <td>{{ item.exam_date }}</td>
              <td>{{ item.study_stage }}</td>
              <td>{{ item.affected_side }}</td>
              <td>{{ item.birads_category }}</td>
              <td>{{ item.acr_density }}</td>
              <td>{{ item.bpe_level }}</td>
              <td>{{ item.le_findings?.length || 0 }}</td>
              <td>{{ item.rc_findings?.length || 0 }}</td>
              <td>
                <button @click="viewContrastDetails(item)" class="btn-sm btn-info">Находки</button>
                <button @click="editContrast(item)" class="btn-sm btn-warning">Редактировать</button>
                <button @click="deleteContrast(item.id)" class="btn-sm btn-danger">Удалить</button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data">Нет данных</p>
      </div>

      <!-- Гистология по биопсии -->
      <div v-if="activeTab === 'histology_biopsy'" class="section">
        <div class="section-header">
          <h3>Гистология и ИГХ (по биопсии)</h3>
          <button @click="showHistBiopsyModal = true" class="btn btn-primary btn-sm">Добавить</button>
        </div>
        <table class="data-table" v-if="patient.histology_biopsies.length">
          <thead>
            <tr>
              <th>Дата</th>
              <th>Заключение</th>
              <th>ИГХ</th>
              <th>Комментарий</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in patient.histology_biopsies" :key="item.id">
              <td>{{ item.exam_date }}</td>
              <td>{{ item.findings }}</td>
              <td>{{ item.ihc_results }}</td>
              <td>{{ item.comment }}</td>
              <td><button @click="deleteHistBiopsy(item.id)" class="btn-sm btn-danger">Удалить</button></td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data">Нет данных</p>
      </div>

      <!-- Цитология по биопсии -->
      <div v-if="activeTab === 'cytology'" class="section">
        <div class="section-header">
          <h3>Цитология (по биопсии)</h3>
          <button @click="showCytoModal = true" class="btn btn-primary btn-sm">Добавить</button>
        </div>
        <table class="data-table" v-if="patient.cytology_biopsies.length">
          <thead>
            <tr>
              <th>Дата</th>
              <th>Заключение</th>
              <th>Комментарий</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in patient.cytology_biopsies" :key="item.id">
              <td>{{ item.exam_date }}</td>
              <td>{{ item.findings }}</td>
              <td>{{ item.comment }}</td>
              <td><button @click="deleteCyto(item.id)" class="btn-sm btn-danger">Удалить</button></td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data">Нет данных</p>
      </div>

      <!-- Гистология послеоперационная -->
      <div v-if="activeTab === 'histology_postop'" class="section">
        <div class="section-header">
          <h3>Гистология и ИГХ (послеоперационная)</h3>
          <button @click="showHistPostopModal = true" class="btn btn-primary btn-sm">Добавить</button>
        </div>
        <table class="data-table" v-if="patient.histology_postops.length">
          <thead>
            <tr>
              <th>Дата</th>
              <th>Заключение</th>
              <th>ИГХ</th>
              <th>Комментарий</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in patient.histology_postops" :key="item.id">
              <td>{{ item.exam_date }}</td>
              <td>{{ item.findings }}</td>
              <td>{{ item.ihc_results }}</td>
              <td>{{ item.comment }}</td>
              <td><button @click="deleteHistPostop(item.id)" class="btn-sm btn-danger">Удалить</button></td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data">Нет данных</p>
      </div>
    </div>

    <!-- Modal УЗИ -->
    <div v-if="showUltrasoundModal || editingUltrasound" class="modal" @click.self="closeUltrasoundModal">
      <div class="modal-content modal-large">
        <h3>{{ editingUltrasound ? 'Редактировать УЗИ' : 'Добавить УЗИ' }}</h3>
        <form @submit.prevent="saveUltrasound">
          <div class="form-row">
            <div class="form-group">
              <label>Дата исследования *</label>
              <input v-model="ultrasoundForm.exam_date" type="date" required class="input">
            </div>
            <div class="form-group">
              <label>Этап исследования (1-9)</label>
              <select v-model.number="ultrasoundForm.study_stage" class="input">
                <option :value="null">Выберите</option>
                <option :value="1">1</option>
                <option :value="2">2</option>
                <option :value="3">3</option>
                <option :value="4">4</option>
                <option :value="5">5</option>
                <option :value="6">6</option>
                <option :value="7">7</option>
                <option :value="8">8</option>
                <option :value="9">9</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>День менструального цикла</label>
              <input v-model.number="ultrasoundForm.menstrual_cycle_day" type="number" min="1" class="input">
            </div>
            <div class="form-group">
              <label>Положение пациента</label>
              <select v-model="ultrasoundForm.patient_position" class="input">
                <option value="">Выберите</option>
                <option value="Лежа на спине">Лежа на спине</option>
                <option value="Лежа на боку">Лежа на боку</option>
                <option value="Сидя">Сидя</option>
                <option value="Полипозиционно">Полипозиционно</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>BI-RADS справа</label>
              <select v-model="ultrasoundForm.birads_right" class="input">
                <option value="">Выберите</option>
                <option value="BI-RADS-0">BI-RADS-0</option>
                <option value="BI-RADS-1">BI-RADS-1</option>
                <option value="BI-RADS-2">BI-RADS-2</option>
                <option value="BI-RADS-3">BI-RADS-3</option>
                <option value="BI-RADS-4a">BI-RADS-4a</option>
                <option value="BI-RADS-4b">BI-RADS-4b</option>
                <option value="BI-RADS-4c">BI-RADS-4c</option>
                <option value="BI-RADS-5">BI-RADS-5</option>
                <option value="BI-RADS-6">BI-RADS-6</option>
              </select>
            </div>
            <div class="form-group">
              <label>BI-RADS слева</label>
              <select v-model="ultrasoundForm.birads_left" class="input">
                <option value="">Выберите</option>
                <option value="BI-RADS-0">BI-RADS-0</option>
                <option value="BI-RADS-1">BI-RADS-1</option>
                <option value="BI-RADS-2">BI-RADS-2</option>
                <option value="BI-RADS-3">BI-RADS-3</option>
                <option value="BI-RADS-4a">BI-RADS-4a</option>
                <option value="BI-RADS-4b">BI-RADS-4b</option>
                <option value="BI-RADS-4c">BI-RADS-4c</option>
                <option value="BI-RADS-5">BI-RADS-5</option>
                <option value="BI-RADS-6">BI-RADS-6</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Плотность ACR справа</label>
              <select v-model="ultrasoundForm.acr_density_right" class="input">
                <option value="">Выберите</option>
                <option value="A">A</option>
                <option value="B">B</option>
                <option value="C">C</option>
                <option value="D">D</option>
              </select>
            </div>
            <div class="form-group">
              <label>Плотность ACR слева</label>
              <select v-model="ultrasoundForm.acr_density_left" class="input">
                <option value="">Выберите</option>
                <option value="A">A</option>
                <option value="B">B</option>
                <option value="C">C</option>
                <option value="D">D</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Комментарий</label>
            <textarea v-model="ultrasoundForm.comment" class="input" rows="3"></textarea>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeUltrasoundModal" class="btn btn-secondary">Отмена</button>
            <button type="submit" class="btn btn-primary">Сохранить</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Маммография (упрощенная) -->
    <div v-if="showMammoModal || editingMammo" class="modal" @click.self="closeMammoModal">
      <div class="modal-content">
        <h3>{{ editingMammo ? 'Редактировать маммографию' : 'Добавить маммографию' }}</h3>
        <form @submit.prevent="saveMammo">
          <div class="form-group">
            <label>Дата исследования *</label>
            <input v-model="mammoForm.exam_date" type="date" required class="input">
          </div>
          <div class="form-group">
            <label>Этап исследования (1-9)</label>
              <select v-model="contrastForm.study_stage" class="input">
                <option value="1">Выберите</option>
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5">5</option>
                <option value="6">6</option>
                <option value="7">7</option>
                <option value="8">8</option>
                <option value="9">9</option>
              </select>
          </div>
          <div class="form-group">
            <label>Сторона поражения</label>
            <select v-model="mammoForm.affected_side" class="input">
              <option value="">Выберите</option>
              <option value="Правая">Правая</option>
              <option value="Левая">Левая</option>
              <option value="Обе">Обе</option>
            </select>
          </div>
          <div class="form-group">
            <label>Категория BI-RADS</label>
            <select v-model="mammoForm.birads_category" class="input">
              <option value="">Выберите</option>
              <option value="0">BI-RADS 0</option>
              <option value="1">BI-RADS 1</option>
              <option value="2">BI-RADS 2</option>
              <option value="3">BI-RADS 3</option>
              <option value="4">BI-RADS 4</option>
              <option value="5">BI-RADS 5</option>
              <option value="6">BI-RADS 6</option>
            </select>
          </div>
          <div class="form-group">
            <label>Плотность по ACR</label>
            <select v-model="mammoForm.acr_density" class="input">
              <option value="">Выберите</option>
              <option value="A">ACR A</option>
              <option value="B">ACR B</option>
              <option value="C">ACR C</option>
              <option value="D">ACR D</option>
            </select>
          </div>
          <div class="form-group">
            <label>Комментарий</label>
            <textarea v-model="mammoForm.comment" class="input" rows="3"></textarea>
          </div>
          <div class="form-actions">
            <button type="button" @click="closeMammoModal" class="btn btn-secondary">Отмена</button>
            <button type="submit" class="btn btn-primary">Сохранить</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Контрастная маммография -->
    <div v-if="showContrastModal || editingContrast" class="modal" @click.self="closeContrastModal">
      <div class="modal-content modal-large">
        <h3>{{ editingContrast ? 'Редактировать контрастную маммографию' : 'Добавить контрастную маммографию' }}</h3>
        <form @submit.prevent="saveContrast">
          <div class="form-row">
            <div class="form-group">
              <label>Дата исследования *</label>
              <input v-model="contrastForm.exam_date" type="date" required class="input">
            </div>
            <div class="form-group">
              <label>Этап исследования (1-9)</label>
              <select v-model="contrastForm.study_stage" class="input">
                <option value="1">Выберите</option>
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5">5</option>
                <option value="6">6</option>
                <option value="7">7</option>
                <option value="8">8</option>
                <option value="9">9</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Сторона поражения</label>
              <select v-model="contrastForm.affected_side" class="input">
                <option value="">Выберите</option>
                <option value="Правая">Правая</option>
                <option value="Левая">Левая</option>
                <option value="Обе">Обе</option>
              </select>
            </div>
            <div class="form-group">
              <label>Категория BI-RADS</label>
              <select v-model="contrastForm.birads_category" class="input">
                <option value="">Выберите</option>
                <option value="0">BI-RADS 0</option>
                <option value="1">BI-RADS 1</option>
                <option value="2">BI-RADS 2</option>
                <option value="3">BI-RADS 3</option>
                <option value="4">BI-RADS 4</option>
                <option value="5">BI-RADS 5</option>
                <option value="6">BI-RADS 6</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Плотность по ACR</label>
              <select v-model="contrastForm.acr_density" class="input">
                <option value="">Выберите</option>
                <option value="A">ACR A</option>
                <option value="B">ACR B</option>
                <option value="C">ACR C</option>
                <option value="D">ACR D</option>
              </select>
            </div>
            <div class="form-group">
              <label>Степень фонового контрастирования (BPE)</label>
              <select v-model="contrastForm.bpe_level" class="input">
                <option value="">Выберите</option>
                <option value="Минимальная">Минимальная</option>
                <option value="Слабая">Слабая</option>
                <option value="Умеренная">Умеренная</option>
                <option value="Выраженная">Выраженная</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Симметрия фонового контрастирования</label>
            <select v-model="contrastForm.bpe_symmetry" class="input">
              <option value="">Выберите</option>
              <option value="Симметричная">Симметричная</option>
              <option value="Асимметричная">Асимметричная</option>
            </select>
          </div>

          <div class="form-group">
            <label>Комментарий</label>
            <textarea v-model="contrastForm.comment" class="input" rows="3"></textarea>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeContrastModal" class="btn btn-secondary">Отмена</button>
            <button type="submit" class="btn btn-primary">Сохранить</button>
          </div>
        </form>
      </div>
    </div>

    <!-- МРТ -->
    <div v-if="activeTab === 'mrt'" class="section">
      <div class="section-header">
        <h3>МРТ исследования</h3>
        <button @click="showMRTModal = true" class="btn btn-primary btn-sm">Добавить</button>
      </div>
      <table class="data-table" v-if="patient.mrts.length">
        <thead>
          <tr>
            <th>Дата</th>
            <th>Этап</th>
            <th>BI-RADS справа</th>
            <th>BI-RADS слева</th>
            <th>BPE</th>
            <th>Находки</th>
            <th>Лимфоузлы</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in patient.mrts" :key="item.id">
            <td>{{ item.exam_date }}</td>
            <td>{{ item.study_stage }}</td>
            <td>{{ item.birads_right }}</td>
            <td>{{ item.birads_left }}</td>
            <td>{{ item.bpe_level }}</td>
            <td>
              {{ item.findings?.length || 0 }}
              <button @click="addMRTFinding(item)" class="btn-xs btn-success" title="Добавить находку">+</button>
            </td>
            <td>
              {{ item.lymph_nodes?.length || 0 }}
              <button @click="addMRTLymphNode(item)" class="btn-xs btn-success" title="Добавить лимфоузел">+</button>
            </td>
            <td>
              <button @click="viewMRTDetails(item)" class="btn-sm btn-info">Подробно</button>
              <button @click="editMRTStudy(item)" class="btn-sm btn-warning">Редактировать</button>
              <button @click="deleteMRT(item.id)" class="btn-sm btn-danger">Удалить</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else class="no-data">Нет данных</p>
    </div>


    <!-- Модал МРТ -->
    <div v-if="showMRTModal || editingMRT" class="modal" @click.self="closeMRTModal">
      <div class="modal-content modal-large">
        <h3>{{ editingMRT ? 'Редактировать МРТ' : 'Добавить МРТ' }}</h3>
        <form @submit.prevent="saveMRT">
          <div class="form-row">
            <div class="form-group">
              <label>Дата исследования *</label>
              <input v-model="mrtForm.exam_date" type="date" required class="input">
            </div>
            <div class="form-group">
              <label>Этап исследования (1-9)</label>
              <select v-model.number="mrtForm.study_stage" class="input">
                <option :value="null">Выберите</option>
                <option :value="1">1</option>
                <option :value="2">2</option>
                <option :value="3">3</option>
                <option :value="4">4</option>
                <option :value="5">5</option>
                <option :value="6">6</option>
                <option :value="7">7</option>
                <option :value="8">8</option>
                <option :value="9">9</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>День менструального цикла</label>
              <input v-model.number="mrtForm.menstrual_cycle_day" type="number" min="1" class="input">
            </div>
            <div class="form-group">
              <label>BI-RADS справа</label>
              <select v-model="mrtForm.birads_right" class="input">
                <option value="">Выберите</option>
                <option value="BI-RADS-0">BI-RADS-0</option>
                <option value="BI-RADS-1">BI-RADS-1</option>
                <option value="BI-RADS-2">BI-RADS-2</option>
                <option value="BI-RADS-3">BI-RADS-3</option>
                <option value="BI-RADS-4a">BI-RADS-4a</option>
                <option value="BI-RADS-4b">BI-RADS-4b</option>
                <option value="BI-RADS-4c">BI-RADS-4c</option>
                <option value="BI-RADS-5">BI-RADS-5</option>
                <option value="BI-RADS-6">BI-RADS-6</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>BI-RADS слева</label>
              <select v-model="mrtForm.birads_left" class="input">
                <option value="">Выберите</option>
                <option value="BI-RADS-0">BI-RADS-0</option>
                <option value="BI-RADS-1">BI-RADS-1</option>
                <option value="BI-RADS-2">BI-RADS-2</option>
                <option value="BI-RADS-3">BI-RADS-3</option>
                <option value="BI-RADS-4a">BI-RADS-4a</option>
                <option value="BI-RADS-4b">BI-RADS-4b</option>
                <option value="BI-RADS-4c">BI-RADS-4c</option>
                <option value="BI-RADS-5">BI-RADS-5</option>
                <option value="BI-RADS-6">BI-RADS-6</option>
              </select>
            </div>
            <div class="form-group">
              <label>Плотность ACR справа</label>
              <select v-model="mrtForm.acr_density_right" class="input">
                <option value="">Выберите</option>
                <option value="A">A</option>
                <option value="B">B</option>
                <option value="C">C</option>
                <option value="D">D</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Плотность ACR слева</label>
              <select v-model="mrtForm.acr_density_left" class="input">
                <option value="">Выберите</option>
                <option value="A">A</option>
                <option value="B">B</option>
                <option value="C">C</option>
                <option value="D">D</option>
              </select>
            </div>
            <div class="form-group">
              <label>Степень фонового контрастирования (BPE)</label>
              <select v-model="mrtForm.bpe_level" class="input">
                <option value="">Выберите</option>
                <option value="минимальная">минимальная</option>
                <option value="слабая">слабая</option>
                <option value="умеренная">умеренная</option>
                <option value="выраженная">выраженная</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Симметрия фонового контрастирования</label>
            <select v-model="mrtForm.bpe_symmetry" class="input">
              <option value="">Выберите</option>
              <option value="Симметричная">Симметричная</option>
              <option value="Асимметричная">Асимметричная</option>
            </select>
          </div>

          <div class="form-group">
            <label>Комментарий</label>
            <textarea v-model="mrtForm.comment" class="input" rows="3"></textarea>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeMRTModal" class="btn btn-secondary">Отмена</button>
            <button type="submit" class="btn btn-primary">Сохранить</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Модал деталей МРТ -->
    <MRTModal
      v-if="selectedMRT"
      ref="mrtModal"
      :mrt="selectedMRT"
      @close="selectedMRT = null"
      @updated="loadPatient"
    />

    <HistologyModal
      v-if="showHistBiopsyModal"
      title="Добавить гистологию (биопсия)"
      :form="histBiopsyForm"
      @close="showHistBiopsyModal = false"
      @save="saveHistBiopsy"
    />

    <SimpleModal
      v-if="showCytoModal"
      title="Добавить цитологию"
      :form="cytoForm"
      @close="showCytoModal = false"
      @save="saveCyto"
    />

    <HistologyModal
      v-if="showHistPostopModal"
      title="Добавить гистологию (послеоперационная)"
      :form="histPostopForm"
      @close="showHistPostopModal = false"
      @save="saveHistPostop"
    />
    <!-- Модал находок маммографии -->
    <MammographyFindingsModal
      v-if="selectedMammography"
      :mammography="selectedMammography"
      @close="selectedMammography = null"
      @updated="loadPatient"
    />

    <!-- Модал контрастной маммографии -->
    <ContrastMammographyModal
      v-if="selectedContrastMammo"
      :contrast-mammo="selectedContrastMammo"
      @close="selectedContrastMammo = null"
      @updated="loadPatient"
    />
  </div>
  <!-- Модал УЗИ с находками -->
  <UltrasoundModal
    v-if="selectedUltrasound"
    :ultrasound="selectedUltrasound"
    @close="selectedUltrasound = null"
    @updated="loadPatient"
  />
</template>

<script>
import api from '../api'
import MammographyFindingsModal from './MammographyFindingsModal.vue'
import ContrastMammographyModal from './ContrastMammographyModal.vue'
import UltrasoundModal from './UltrasoundModal.vue'
import MRTModal from './MRTModal.vue' // Добавьте этот импорт

export default {
  components: {
    MammographyFindingsModal,
    ContrastMammographyModal,
    UltrasoundModal,
    MRTModal
  },
  data() {
    return {
      patient: null,
      activeTab: 'ultrasound',
      tabs: [
        { id: 'ultrasound', label: 'УЗИ' },
        { id: 'mammography', label: 'Маммография' },
        { id: 'contrast', label: 'Контрастная маммография' },
        { id: 'mrt', label: 'МРТ' },
        { id: 'histology_biopsy', label: 'Гистология (биопсия)' },
        { id: 'cytology', label: 'Цитология' },
        { id: 'histology_postop', label: 'Гистология (послеоп.)' }
      ],
      showUltrasoundModal: false,
      showMammoModal: false,
      showContrastModal: false,
      showMRTModal: false,
      showHistBiopsyModal: false,
      showCytoModal: false,
      showHistPostopModal: false,
      selectedMammography: null,
      selectedContrastMammo: null,
      selectedUltrasound: null,
      editingMammo: null,
      editingContrast: null,
      editingUltrasound: null,
      editingMRT: null,
      editingHistBiopsy: null,
      editingCyto: null,
      editingHistPostop: null,
      ultrasoundForm: {
        exam_date: '',
        study_stage: null,
        menstrual_cycle_day: null,
        patient_position: '',
        birads_right: '',
        birads_left: '',
        acr_density_right: '',
        acr_density_left: '',
        comparison_available: false,
        dynamics: '',
        comment: ''
      },
      mammoForm: {
        exam_date: '',
        study_stage: null,
        affected_side: '',
        birads_category: '',
        acr_density: '',
        comment: ''
      },
      contrastForm: {
        exam_date: '',
        study_stage: null,
        affected_side: '',
        birads_category: '',
        acr_density: '',
        bpe_level: '',
        bpe_symmetry: '',
        comparison_available: false,
        dynamics: '',
        comment: ''
      },
      selectedMRT: null,
      editingMRT: null,
      mrtForm: {
        exam_date: '',
        study_stage: null,
        menstrual_cycle_day: null,
        birads_right: '',
        birads_left: '',
        acr_density_right: '',
        acr_density_left: '',
        bpe_level: '',
        bpe_symmetry: '',
        comparison_available: false,
        dynamics: '',
        comment: ''
      },
      histBiopsyForm: { exam_date: '', findings: '', ihc_results: '', comment: '' },
      cytoForm: { exam_date: '', findings: '', comment: '' },
      histPostopForm: { exam_date: '', findings: '', ihc_results: '', comment: '' }
    }
  },
  mounted() {
    this.loadPatient()
  },
  methods: {
    async loadPatient() {
      try {
        const response = await api.getPatient(this.$route.params.id)
        this.patient = response.data
      } catch (error) {
        alert('Ошибка загрузки данных пациента')
        this.$router.push('/patients')
      }
    },
    formatDateTime(dt) {
      if (!dt) return ''
      return new Date(dt).toLocaleString('ru-RU')
    },
    async saveUltrasound() {
      try {
        if (this.editingUltrasound) {
          await api.updateUltrasound(this.editingUltrasound, { ...this.ultrasoundForm, patient_id: this.patient.id })
        } else {
          await api.createUltrasound({ ...this.ultrasoundForm, patient_id: this.patient.id })
        }
        this.closeUltrasoundModal()
        this.loadPatient()
      } catch (error) {
        console.error('Ошибка сохранения УЗИ:', error)
        console.error('Данные формы:', this.ultrasoundForm)
        // alert('Ошибка сохранения')
        alert('Ошибка сохранения: ' + (error.response?.data?.detail || error.message))
      }
    },
    editUltrasound(item) {
      this.editingUltrasound = item.id
      this.ultrasoundForm = { ...item }
      this.showUltrasoundModal = true
    },
    closeUltrasoundModal() {
      this.showUltrasoundModal = false
      this.editingUltrasound = null
      this.ultrasoundForm = {
        exam_date: '',
        study_stage: null,
        menstrual_cycle_day: null,
        patient_position: '',
        birads_right: '',
        birads_left: '',
        acr_density_right: '',
        acr_density_left: '',
        comparison_available: false,
        dynamics: '',
        comment: ''
      }
    },
    viewUltrasoundDetails(item) {
      this.selectedUltrasound = item
    },
    async deleteUltrasound(id) {
      if (confirm('Удалить запись?')) {
        await api.deleteUltrasound(id)
        this.loadPatient()
      }
    },
    async saveMammo() {
      try {
        if (this.editingMammo) {
          await api.updateMammography(this.editingMammo, { ...this.mammoForm, patient_id: this.patient.id })
        } else {
          await api.createMammography({ ...this.mammoForm, patient_id: this.patient.id })
        }
        this.closeMammoModal()
        this.loadPatient()
      } catch (error) {
        alert('Ошибка сохранения')
      }
    },
    editMammo(item) {
      this.editingMammo = item.id
      this.mammoForm = { ...item }
      this.showMammoModal = true
    },
    closeMammoModal() {
      this.showMammoModal = false
      this.editingMammo = null
      this.mammoForm = {
        exam_date: '',
        study_stage: null,
        affected_side: '',
        birads_category: '',
        acr_density: '',
        comment: ''
      }
    },
    async deleteMammo(id) {
      if (confirm('Удалить запись?')) {
        await api.deleteMammography(id)
        this.loadPatient()
      }
    },
    viewMammoFindings(mammography) {
      this.selectedMammography = mammography
    },
    async saveContrast() {
      try {
        if (this.editingContrast) {
          await api.updateContrastMammography(this.editingContrast, { ...this.contrastForm, patient_id: this.patient.id })
        } else {
          await api.createContrastMammography({ ...this.contrastForm, patient_id: this.patient.id })
        }
        this.closeContrastModal()
        this.loadPatient()
      } catch (error) {
        alert('Ошибка сохранения')
      }
    },
    editContrast(item) {
      this.editingContrast = item.id
      this.contrastForm = { ...item }
      this.showContrastModal = true
    },
    closeContrastModal() {
      this.showContrastModal = false
      this.editingContrast = null
      this.contrastForm = {
        exam_date: '',
        study_stage: null,
        affected_side: '',
        birads_category: '',
        acr_density: '',
        bpe_level: '',
        bpe_symmetry: '',
        comparison_available: false,
        dynamics: '',
        comment: ''
      }
    },
    viewContrastDetails(item) {
      this.selectedContrastMammo = item
    },
    async deleteContrast(id) {
      if (confirm('Удалить запись?')) {
        await api.deleteContrastMammography(id)
        this.loadPatient()
      }
    },
    viewMRTDetails(item) {
      this.selectedMRT = item
    },

    editMRTStudy(item) {
      this.editingMRT = item.id
      this.mrtForm = { ...item }
      this.showMRTModal = true
    },

    addMRTFinding(mrtItem) {
      // Открываем модал с деталями МРТ и автоматически открываем форму добавления находки
      this.selectedMRT = mrtItem
      this.$nextTick(() => {
        if (this.$refs.mrtModal) {
          this.$refs.mrtModal.openAddFinding()
        }
      })
    },

    addMRTLymphNode(mrtItem) {
      // Открываем модал с деталями МРТ и автоматически открываем форму добавления лимфоузла
      this.selectedMRT = mrtItem
      this.$nextTick(() => {
        if (this.$refs.mrtModal) {
          this.$refs.mrtModal.openAddLymphNode()
        }
      })
    },

    async saveMRT() {
      try {
        if (this.editingMRT) {
          await api.updateMRT(this.editingMRT, { ...this.mrtForm, patient_id: this.patient.id })
        } else {
          await api.createMRT({ ...this.mrtForm, patient_id: this.patient.id })
        }
        this.closeMRTModal()
        this.loadPatient()
      } catch (error) {
        alert('Ошибка сохранения')
      }
    },

    closeMRTModal() {
      this.showMRTModal = false
      this.editingMRT = null
      this.mrtForm = {
        exam_date: '',
        study_stage: null,
        menstrual_cycle_day: null,
        birads_right: '',
        birads_left: '',
        acr_density_right: '',
        acr_density_left: '',
        bpe_level: '',
        bpe_symmetry: '',
        comparison_available: false,
        dynamics: '',
        comment: ''
      }
    },

    async deleteMRT(id) {
      if (confirm('Удалить запись?')) {
        await api.deleteMRT(id)
        this.loadPatient()
      }
    },
    async saveHistBiopsy() {
      await api.createHistologyBiopsy({ ...this.histBiopsyForm, patient_id: this.patient.id })
      this.showHistBiopsyModal = false
      this.loadPatient()
    },
    async deleteHistBiopsy(id) {
      if (confirm('Удалить запись?')) {
        await api.deleteHistologyBiopsy(id)
        this.loadPatient()
      }
    },
    async saveCyto() {
      await api.createCytologyBiopsy({ ...this.cytoForm, patient_id: this.patient.id })
      this.showCytoModal = false
      this.loadPatient()
    },
    async deleteCyto(id) {
      if (confirm('Удалить запись?')) {
        await api.deleteCytologyBiopsy(id)
        this.loadPatient()
      }
    },
    async saveHistPostop() {
      await api.createHistologyPostop({ ...this.histPostopForm, patient_id: this.patient.id })
      this.showHistPostopModal = false
      this.loadPatient()
    },
    async deleteHistPostop(id) {
      if (confirm('Удалить запись?')) {
        await api.deleteHistologyPostop(id)
        this.loadPatient()
      }
    }
  }
}
</script>

<style scoped>
.patient-detail { padding: 1rem; }
.header { display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem; }
.card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 2rem; }
.info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 1rem; }
.tabs { display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap; }
.tab-btn { padding: 0.75rem 1.5rem; border: none; background: #e9ecef; cursor: pointer; border-radius: 4px 4px 0 0; font-weight: 500; }
.tab-btn.active { background: #667eea; color: white; }
.tab-content { background: white; padding: 1.5rem; border-radius: 0 4px 4px 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { background: #f8f9fa; padding: 0.75rem; text-align: left; font-weight: 600; }
.data-table td { padding: 0.75rem; border-top: 1px solid #dee2e6; }
.no-data { color: #6c757d; font-style: italic; padding: 1rem; }
.btn { padding: 0.5rem 1rem; border: none; border-radius: 4px; cursor: pointer; font-weight: 500; }
.btn-primary { background: #667eea; color: white; }
.btn-secondary { background: #6c757d; color: white; }
.btn-sm { padding: 0.25rem 0.75rem; font-size: 0.875rem; }
.btn-danger { background: #dc3545; color: white; }
.modal { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-content { background: white; padding: 2rem; border-radius: 8px; max-width: 600px; width: 90%; max-height: 90vh; overflow-y: auto; }
.modal-large { max-width: 800px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
.input { padding: 0.5rem; border: 1px solid #ced4da; border-radius: 4px; width: 100%; }
.form-actions { display: flex; gap: 1rem; justify-content: flex-end; margin-top: 1.5rem; }
.btn-info {
  background: #17a2b8;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 0.5rem;
}

.btn-warning {
  background: #ffc107;
  color: #212529;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 0.5rem;
}

/* Маленькая кнопка для добавления в ячейках таблицы */
.btn-xs {
  padding: 0.15rem 0.4rem;
  font-size: 0.75rem;
  margin-left: 0.5rem;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-weight: bold;
  vertical-align: middle;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-success:hover {
  background: #218838;
}

/* Улучшенный вид для колонок с количеством */
.data-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #dee2e6;
  vertical-align: middle;
}

/* Группировка кнопок действий */
.data-table td button {
  white-space: nowrap;
}
</style>