import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: () => import('@/views/DashboardView.vue'),
    },
    {
      path: '/setup',
      component: () => import('@/views/SetupView.vue'),
    },
    {
      path: '/basket/:id',
      component: () => import('@/views/BasketDetailView.vue'),
      props: true,
    },
    {
      path: '/scan/:token',
      component: () => import('@/views/ScanView.vue'),
      props: true,
    },
    {
      path: '/firstaid',
      component: () => import('@/views/firstaid/FirstAidHub.vue'),
    },
    {
      path: '/firstaid/cpr',
      component: () => import('@/views/firstaid/CprView.vue'),
    },
    {
      path: '/firstaid/poison',
      component: () => import('@/views/firstaid/PoisonView.vue'),
    },
    {
      path: '/firstaid/family',
      component: () => import('@/views/firstaid/FamilyMedView.vue'),
    },
    {
      path: '/firstaid/kit/basic',
      component: () => import('@/views/firstaid/BasicKitView.vue'),
    },
    {
      path: '/firstaid/kit/advanced',
      component: () => import('@/views/firstaid/AdvancedKitView.vue'),
    },
    {
      path: '/cleaning',
      component: () => import('@/views/cleaning/RoomListView.vue'),
    },
    {
      path: '/cleaning/:room',
      component: () => import('@/views/cleaning/ChecklistView.vue'),
      props: true,
    },
    {
      path: '/:pathMatch(.*)*',
      component: () => import('@/views/NotFoundView.vue'),
    },
  ],
})

export default router
