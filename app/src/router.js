import { createRouter, createWebHistory } from 'vue-router'
import Home from './pages/Home.vue'
import Journal from './pages/Journal.vue'
import Entry from './pages/Entry.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/:journal', component: Journal, props: true },
    { path: '/:journal/:date', component: Entry, props: true },
  ],
})
