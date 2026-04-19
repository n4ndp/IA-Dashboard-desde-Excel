// ── Router ──
// 4 routes + beforeEach auth guard.

import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import ProjectsView from '../views/ProjectsView.vue'
import ProjectNewView from '../views/ProjectNewView.vue'
import DashboardView from '../views/DashboardView.vue'

const routes = [
  { path: '/', name: 'login', component: LoginView },
  { path: '/u/:userId/p', name: 'projects', component: ProjectsView },
  { path: '/u/:userId/p/new', name: 'project-new', component: ProjectNewView },
  { path: '/u/:userId/p/:projectId', name: 'dashboard', component: DashboardView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const storedUserId = localStorage.getItem('user_id')

  // Has stored ID + visits login → redirect to their projects
  if (storedUserId && to.path === '/') {
    return `/u/${storedUserId}/p`
  }

  // No stored ID + not login → redirect to login
  if (!storedUserId && to.path !== '/') {
    return '/'
  }

  // Has stored ID + URL userId mismatches → redirect to correct user
  if (storedUserId && to.params.userId && String(to.params.userId) !== storedUserId) {
    if (to.name === 'project-new') {
      return `/u/${storedUserId}/p/new`
    }
    if (to.name === 'dashboard' && to.params.projectId) {
      return `/u/${storedUserId}/p/${to.params.projectId}`
    }
    return `/u/${storedUserId}/p`
  }
})

export default router
