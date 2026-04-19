import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import ProjectsView from '../views/ProjectsView.vue'
import ProjectNewView from '../views/ProjectNewView.vue'
import ProjectDetailView from '../views/ProjectDetailView.vue'

const routes = [
  { path: '/', name: 'login', component: LoginView },
  { path: '/u/:userId/p', name: 'projects', component: ProjectsView },
  { path: '/u/:userId/p/new', name: 'project-new', component: ProjectNewView },
  { path: '/u/:userId/p/:projectId', name: 'project-detail', component: ProjectDetailView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const storedUserId = localStorage.getItem('user_id')

  // If user has localStorage data and visits login, redirect to their projects
  if (storedUserId && to.path === '/') {
    return `/u/${storedUserId}/p`
  }

  // If no localStorage data and trying to access protected route, redirect to login
  if (!storedUserId && to.path !== '/') {
    return '/'
  }
})

export default router
