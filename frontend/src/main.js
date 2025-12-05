import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Patients from './components/Patients.vue'
import PatientDetail from './components/PatientDetail.vue'
import Mammographies from './components/Mammographies.vue'
import Ultrasounds from './components/Ultrasounds.vue'
import MRTs from './components/MRTs.vue'

const routes = [
  { path: '/', redirect: '/patients' },
  { path: '/patients', component: Patients },
  { path: '/patients/:id', component: PatientDetail },
  { path: '/mammographies', component: Mammographies },
  { path: '/ultrasounds', component: Ultrasounds },
  { path: '/mrts', component: MRTs }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)
app.use(router)
app.mount('#app')