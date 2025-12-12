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