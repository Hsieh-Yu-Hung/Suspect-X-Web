const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/IndexPage.vue') },                     // Index page
      { path: 'login', component: () => import('pages/LoginPage.vue') },                // Login page
      { path: 'page-not-active', component: () => import('pages/NotActivePage.vue') },  // Not active page
      { path: 'page-preview', component: () => import('pages/MainPagePreview.vue') },   // Preview
      { path: 'page-analysis', component: () => import('pages/MainPageAnalysis.vue') }, // Analysis
      { path: 'page-export', component: () => import('pages/MainPageExport.vue') },     // Export
      { path: 'page-admin', component: () => import('pages/AdminPage.vue') }            // Admin page
    ]
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  },
]

export default routes
